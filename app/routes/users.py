from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from app.models import db, User, Role, AuditLog
from app.utils.decorators import admin_required
import json

users_bp = Blueprint('users', __name__)

@users_bp.route('/')
@login_required
@admin_required
def list_users():
    """List all users (Admin only)."""
    users = User.query.order_by(User.username).all()
    return render_template('users/list.html', users=users)

@users_bp.route('/add', methods=['GET', 'POST'])
@login_required
@admin_required
def add_user():
    """Add a new user (Admin only)."""
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')
        role = request.form.get('role', Role.STAFF)
        
        # Validation
        errors = []
        
        if not username:
            errors.append('Username is required.')
        elif len(username) < 3:
            errors.append('Username must be at least 3 characters.')
        elif User.query.filter_by(username=username).first():
            errors.append('Username already exists.')
        
        if not email:
            errors.append('Email is required.')
        elif User.query.filter_by(email=email).first():
            errors.append('Email already exists.')
        
        if not password:
            errors.append('Password is required.')
        elif len(password) < 6:
            errors.append('Password must be at least 6 characters.')
        elif password != confirm_password:
            errors.append('Passwords do not match.')
        
        if role not in [Role.ADMIN, Role.STAFF]:
            errors.append('Invalid role selected.')
        
        if errors:
            for error in errors:
                flash(error, 'error')
            return render_template('users/form.html', user=None, roles=[Role.ADMIN, Role.STAFF])
        
        # Create user
        user = User(
            username=username,
            email=email,
            role=role
        )
        user.set_password(password)
        
        db.session.add(user)
        db.session.flush()
        
        # Audit log
        audit = AuditLog(
            user_id=current_user.id,
            action='create',
            table_name='users',
            record_id=user.id,
            new_values=json.dumps({
                'username': username,
                'email': email,
                'role': role
            }),
            ip_address=request.remote_addr,
            user_agent=str(request.user_agent)[:255]
        )
        db.session.add(audit)
        db.session.commit()
        
        flash(f'User "{username}" has been created successfully.', 'success')
        return redirect(url_for('users.list_users'))
    
    return render_template('users/form.html', user=None, roles=[Role.ADMIN, Role.STAFF])

@users_bp.route('/<int:id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_user(id):
    """Edit an existing user (Admin only)."""
    user = db.get_or_404(User, id)
    
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip()
        role = request.form.get('role', Role.STAFF)
        new_password = request.form.get('new_password', '')
        is_active = request.form.get('is_active') == 'on'
        
        # Store old values for audit
        old_values = {
            'username': user.username,
            'email': user.email,
            'role': user.role,
            'is_active': user.is_active
        }
        
        # Validation
        errors = []
        
        if not username:
            errors.append('Username is required.')
        elif len(username) < 3:
            errors.append('Username must be at least 3 characters.')
        else:
            existing = User.query.filter_by(username=username).first()
            if existing and existing.id != id:
                errors.append('Username already exists.')
        
        if not email:
            errors.append('Email is required.')
        else:
            existing = User.query.filter_by(email=email).first()
            if existing and existing.id != id:
                errors.append('Email already exists.')
        
        if new_password and len(new_password) < 6:
            errors.append('Password must be at least 6 characters.')
        
        if role not in [Role.ADMIN, Role.STAFF]:
            errors.append('Invalid role selected.')
        
        # Prevent disabling your own admin account
        if user.id == current_user.id:
            if not is_active:
                errors.append('You cannot deactivate your own account.')
            if role != Role.ADMIN:
                errors.append('You cannot change your own role.')
        
        if errors:
            for error in errors:
                flash(error, 'error')
            return render_template('users/form.html', user=user, roles=[Role.ADMIN, Role.STAFF])
        
        # Update user
        user.username = username
        user.email = email
        user.role = role
        user.is_active = is_active
        
        if new_password:
            user.set_password(new_password)
        
        # Audit log
        new_values = {
            'username': username,
            'email': email,
            'role': role,
            'is_active': is_active,
            'password_changed': bool(new_password)
        }
        
        audit = AuditLog(
            user_id=current_user.id,
            action='update',
            table_name='users',
            record_id=user.id,
            old_values=json.dumps(old_values),
            new_values=json.dumps(new_values),
            ip_address=request.remote_addr,
            user_agent=str(request.user_agent)[:255]
        )
        db.session.add(audit)
        db.session.commit()
        
        flash(f'User "{username}" has been updated successfully.', 'success')
        return redirect(url_for('users.list_users'))
    
    return render_template('users/form.html', user=user, roles=[Role.ADMIN, Role.STAFF])

@users_bp.route('/<int:id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_user(id):
    """Deactivate a user (Admin only)."""
    user = db.get_or_404(User, id)
    
    if user.id == current_user.id:
        flash('You cannot delete your own account.', 'error')
        return redirect(url_for('users.list_users'))
    
    # Soft delete (deactivate)
    user.is_active = False
    
    # Audit log
    audit = AuditLog(
        user_id=current_user.id,
        action='delete',
        table_name='users',
        record_id=user.id,
        old_values=json.dumps({'username': user.username, 'is_active': True}),
        new_values=json.dumps({'is_active': False}),
        ip_address=request.remote_addr,
        user_agent=str(request.user_agent)[:255]
    )
    db.session.add(audit)
    db.session.commit()
    
    flash(f'User "{user.username}" has been deactivated.', 'success')
    return redirect(url_for('users.list_users'))

@users_bp.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    """View and edit own profile."""
    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        current_password = request.form.get('current_password', '')
        new_password = request.form.get('new_password', '')
        confirm_password = request.form.get('confirm_password', '')
        
        errors = []
        
        # Validate email
        if not email:
            errors.append('Email is required.')
        else:
            existing = User.query.filter_by(email=email).first()
            if existing and existing.id != current_user.id:
                errors.append('Email already exists.')
        
        # Password change validation
        if new_password:
            if not current_password:
                errors.append('Current password is required to set a new password.')
            elif not current_user.check_password(current_password):
                errors.append('Current password is incorrect.')
            elif len(new_password) < 6:
                errors.append('New password must be at least 6 characters.')
            elif new_password != confirm_password:
                errors.append('New passwords do not match.')
        
        if errors:
            for error in errors:
                flash(error, 'error')
            return render_template('users/profile.html')
        
        # Update profile
        current_user.email = email
        if new_password:
            current_user.set_password(new_password)
        
        # Audit log
        audit = AuditLog(
            user_id=current_user.id,
            action='update',
            table_name='users',
            record_id=current_user.id,
            new_values=json.dumps({
                'email': email,
                'password_changed': bool(new_password)
            }),
            ip_address=request.remote_addr,
            user_agent=str(request.user_agent)[:255]
        )
        db.session.add(audit)
        db.session.commit()
        
        flash('Profile updated successfully.', 'success')
        return redirect(url_for('users.profile'))
    
    return render_template('users/profile.html')
