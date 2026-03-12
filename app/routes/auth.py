from datetime import datetime
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
from app.models import db, User, AuditLog

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/', methods=['GET', 'POST'])
@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    # Redirect if already logged in
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        remember = request.form.get('remember', False)
        
        if not username or not password:
            flash('Please enter both username and password.', 'error')
            return render_template('login.html')
        
        user = User.query.filter_by(username=username).first()
        
        if user and user.check_password(password):
            if not user.is_active:
                flash('Your account has been deactivated. Please contact an administrator.', 'error')
                return render_template('login.html')
            
            # Log the user in
            login_user(user, remember=remember)
            
            # Update last login time
            user.last_login = datetime.utcnow()
            
            # Create audit log for login
            audit = AuditLog(
                user_id=user.id,
                action='login',
                table_name='users',
                record_id=user.id,
                ip_address=request.remote_addr,
                user_agent=str(request.user_agent)[:255]
            )
            db.session.add(audit)
            db.session.commit()
            
            flash(f'Welcome back, {user.username}!', 'success')
            
            # Redirect to the page they were trying to access, or dashboard
            next_page = request.args.get('next')
            if next_page:
                return redirect(next_page)
            return redirect(url_for('main.dashboard'))
        else:
            flash('Invalid username or password.', 'error')
    
    return render_template('login.html')

@auth_bp.route('/logout')
@login_required
def logout():
    # Create audit log for logout
    audit = AuditLog(
        user_id=current_user.id,
        action='logout',
        table_name='users',
        record_id=current_user.id,
        ip_address=request.remote_addr,
        user_agent=str(request.user_agent)[:255]
    )
    db.session.add(audit)
    db.session.commit()
    
    logout_user()
    flash('You have been logged out successfully.', 'info')
    return redirect(url_for('auth.login'))
