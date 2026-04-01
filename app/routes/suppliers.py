from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from app.models import db, Supplier, AuditLog, Transaction
from app.utils.decorators import admin_required
import json

suppliers_bp = Blueprint('suppliers', __name__)

@suppliers_bp.route('/')
@login_required
@admin_required
def list_suppliers():
    """List all suppliers (Admin only)."""
    suppliers = Supplier.query.filter_by(is_active=True).order_by(Supplier.name).all()
    return render_template('suppliers/list.html', suppliers=suppliers)

@suppliers_bp.route('/add', methods=['GET', 'POST'])
@login_required
@admin_required
def add_supplier():
    """Add a new supplier (Admin only)."""
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        contact_person = request.form.get('contact_person', '').strip()
        email = request.form.get('email', '').strip()
        phone = request.form.get('phone', '').strip()
        address = request.form.get('address', '').strip()
        notes = request.form.get('notes', '').strip()
        
        # Validation
        errors = []
        
        if not name:
            errors.append('Supplier name is required.')
        elif Supplier.query.filter_by(name=name).first():
            errors.append('Supplier name already exists.')
        
        if errors:
            for error in errors:
                flash(error, 'error')
            return render_template('suppliers/form.html', supplier=None)
        
        # Create supplier
        supplier = Supplier(
            name=name,
            contact_person=contact_person,
            email=email,
            phone=phone,
            address=address,
            notes=notes
        )
        
        db.session.add(supplier)
        db.session.flush()
        
        # Audit log
        audit = AuditLog(
            user_id=current_user.id,
            action='create',
            table_name='suppliers',
            record_id=supplier.id,
            new_values=json.dumps({
                'name': name,
                'contact_person': contact_person,
                'email': email,
                'phone': phone
            }),
            ip_address=request.remote_addr,
            user_agent=str(request.user_agent)[:255]
        )
        db.session.add(audit)
        db.session.commit()
        
        flash(f'Supplier "{name}" has been created successfully.', 'success')
        return redirect(url_for('suppliers.list_suppliers'))
    
    return render_template('suppliers/form.html', supplier=None)

@suppliers_bp.route('/<int:id>')
@login_required
@admin_required
def view_supplier(id):
    """View supplier details."""
    supplier = db.get_or_404(Supplier, id)
    transactions = supplier.transactions.order_by(Transaction.created_at.desc()).limit(10).all()
    return render_template('suppliers/view.html', supplier=supplier, recent_transactions=transactions)

@suppliers_bp.route('/<int:id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_supplier(id):
    """Edit an existing supplier (Admin only)."""
    supplier = db.get_or_404(Supplier, id)
    
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        contact_person = request.form.get('contact_person', '').strip()
        email = request.form.get('email', '').strip()
        phone = request.form.get('phone', '').strip()
        address = request.form.get('address', '').strip()
        notes = request.form.get('notes', '').strip()
        
        # Store old values for audit
        old_values = {
            'name': supplier.name,
            'contact_person': supplier.contact_person,
            'email': supplier.email,
            'phone': supplier.phone
        }
        
        # Validation
        errors = []
        
        if not name:
            errors.append('Supplier name is required.')
        else:
            existing = Supplier.query.filter_by(name=name).first()
            if existing and existing.id != id:
                errors.append('Supplier name already exists.')
        
        if errors:
            for error in errors:
                flash(error, 'error')
            return render_template('suppliers/form.html', supplier=supplier)
        
        # Update supplier
        supplier.name = name
        supplier.contact_person = contact_person
        supplier.email = email
        supplier.phone = phone
        supplier.address = address
        supplier.notes = notes
        
        # Audit log
        new_values = {
            'name': name,
            'contact_person': contact_person,
            'email': email,
            'phone': phone
        }
        
        audit = AuditLog(
            user_id=current_user.id,
            action='update',
            table_name='suppliers',
            record_id=supplier.id,
            old_values=json.dumps(old_values),
            new_values=json.dumps(new_values),
            ip_address=request.remote_addr,
            user_agent=str(request.user_agent)[:255]
        )
        db.session.add(audit)
        db.session.commit()
        
        flash(f'Supplier "{name}" has been updated successfully.', 'success')
        return redirect(url_for('suppliers.list_suppliers'))
    
    return render_template('suppliers/form.html', supplier=supplier)

@suppliers_bp.route('/<int:id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_supplier(id):
    """Deactivate a supplier (Admin only)."""
    supplier = db.get_or_404(Supplier, id)
    
    # Soft delete (deactivate)
    supplier.is_active = False
    
    # Audit log
    audit = AuditLog(
        user_id=current_user.id,
        action='delete',
        table_name='suppliers',
        record_id=supplier.id,
        old_values=json.dumps({'name': supplier.name}),
        ip_address=request.remote_addr,
        user_agent=str(request.user_agent)[:255]
    )
    db.session.add(audit)
    db.session.commit()
    
    flash(f'Supplier "{supplier.name}" has been deactivated.', 'success')
    return redirect(url_for('suppliers.list_suppliers'))
