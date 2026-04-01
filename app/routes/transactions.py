from datetime import datetime
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from app.models import db, Transaction, TransactionItem, Product, StockMovement, AuditLog, Supplier, CashLedger
from app.utils.decorators import staff_required
from app.utils.helpers import generate_reference_number, validate_positive_integer
from sqlalchemy import or_
import json

transactions_bp = Blueprint('transactions', __name__)


def _record_cash_entry(entry_type, amount, notes=None, transaction_id=None):
    """Create a cash ledger entry with updated running balance."""
    latest = CashLedger.query.order_by(CashLedger.id.desc()).first()
    current_balance = latest.running_balance if latest else 0.0
    new_balance = current_balance + amount

    entry = CashLedger(
        entry_type=entry_type,
        amount=amount,
        running_balance=new_balance,
        transaction_id=transaction_id,
        user_id=current_user.id,
        notes=notes
    )
    db.session.add(entry)

@transactions_bp.route('/')
@login_required
def list_transactions():
    """List all transactions with filtering."""
    page = request.args.get('page', 1, type=int)
    per_page = 20
    
    # Get filter parameters
    transaction_type = request.args.get('type')  # 'sale' or 'purchase'
    date_from = request.args.get('date_from')
    date_to = request.args.get('date_to')
    search = request.args.get('search', '').strip()
    
    # Build query
    query = Transaction.query
    
    if transaction_type:
        query = query.filter_by(transaction_type=transaction_type)
    
    if date_from:
        try:
            date_from = datetime.strptime(date_from, '%Y-%m-%d')
            query = query.filter(Transaction.created_at >= date_from)
        except ValueError:
            pass
    
    if date_to:
        try:
            date_to = datetime.strptime(date_to, '%Y-%m-%d')
            # Add one day to include the entire end date
            date_to = datetime.combine(date_to.date(), datetime.max.time())
            query = query.filter(Transaction.created_at <= date_to)
        except ValueError:
            pass
    
    if search:
        query = query.outerjoin(Supplier).filter(
            or_(
                Transaction.reference_number.ilike(f'%{search}%'),
                Transaction.customer_name.ilike(f'%{search}%'),
                Supplier.name.ilike(f'%{search}%')
            )
        )
    
    # Order by date (newest first)
    query = query.order_by(Transaction.created_at.desc())
    
    transactions = query.paginate(page=page, per_page=per_page, error_out=False)
    
    return render_template('transactions/list.html',
        transactions=transactions,
        transaction_type=transaction_type,
        date_from=request.args.get('date_from', ''),
        date_to=request.args.get('date_to', ''),
        search=search
    )

@transactions_bp.route('/new-sale', methods=['GET', 'POST'])
@login_required
@staff_required
def new_sale():
    """Create a new sale transaction."""
    if request.method == 'POST':
        customer_name = request.form.get('customer_name', '').strip()
        notes = request.form.get('notes', '').strip()
        discount = float(request.form.get('discount', 0) or 0)
        
        # Get items from form
        product_ids = request.form.getlist('product_id[]')
        quantities = request.form.getlist('quantity[]')
        
        if not product_ids or not any(product_ids):
            flash('Please add at least one product to the sale.', 'error')
            return render_template('transactions/sale_form.html')
        
        # Validate and prepare items
        items = []
        subtotal = 0
        errors = []
        
        for i, (pid, qty) in enumerate(zip(product_ids, quantities)):
            if not pid:
                continue
            
            try:
                product_id = int(pid)
                quantity = int(qty)
            except ValueError:
                errors.append(f'Invalid product or quantity at row {i+1}.')
                continue
            
            if quantity <= 0:
                errors.append(f'Quantity must be greater than 0 at row {i+1}.')
                continue
            
            product = db.session.get(Product, product_id)
            if not product:
                errors.append(f'Product not found at row {i+1}.')
                continue
            
            if product.quantity < quantity:
                errors.append(f'Insufficient stock for "{product.name}". Available: {product.quantity}')
                continue
            
            item_total = product.selling_price * quantity
            items.append({
                'product': product,
                'quantity': quantity,
                'unit_price': product.selling_price,
                'total_price': item_total
            })
            subtotal += item_total
        
        if errors:
            for error in errors:
                flash(error, 'error')
            return render_template('transactions/sale_form.html')
        
        # Calculate totals
        tax = 0  # Can be configured if needed
        total = subtotal - discount + tax
        
        # Create transaction
        transaction = Transaction(
            transaction_type='sale',
            reference_number=generate_reference_number('SAL'),
            user_id=current_user.id,
            subtotal=subtotal,
            tax=tax,
            discount=discount,
            total=total,
            customer_name=customer_name or None,
            notes=notes or None
        )
        db.session.add(transaction)
        db.session.flush()
        
        # Create transaction items and update stock
        for item in items:
            product = item['product']
            quantity = item['quantity']
            unit_cost_at_sale = product.cost_price
            
            # Create transaction item
            trans_item = TransactionItem(
                transaction_id=transaction.id,
                product_id=product.id,
                quantity=quantity,
                unit_price=item['unit_price'],
                total_price=item['total_price'],
                unit_cost_at_sale=unit_cost_at_sale
            )
            db.session.add(trans_item)
            
            # Record stock movement
            movement = StockMovement(
                product_id=product.id,
                user_id=current_user.id,
                movement_type='sale',
                quantity_change=-quantity,
                quantity_before=product.quantity,
                quantity_after=product.quantity - quantity,
                reference=transaction.reference_number,
                notes=f'Sale to {customer_name}' if customer_name else 'Sale'
            )
            db.session.add(movement)
            
            # Update product quantity
            product.quantity -= quantity

        _record_cash_entry(
            entry_type='sale_inflow',
            amount=total,
            notes=f'Sale {transaction.reference_number}',
            transaction_id=transaction.id
        )
        
        # Audit log
        audit = AuditLog(
            user_id=current_user.id,
            action='create',
            table_name='transactions',
            record_id=transaction.id,
            new_values=json.dumps({
                'type': 'sale',
                'reference': transaction.reference_number,
                'total': total,
                'items_count': len(items)
            }),
            ip_address=request.remote_addr,
            user_agent=str(request.user_agent)[:255]
        )
        db.session.add(audit)
        db.session.commit()
        
        flash(f'Sale {transaction.reference_number} completed successfully. Total: ₱{total:,.2f}', 'success')
        return redirect(url_for('transactions.view_transaction', id=transaction.id))
    
    return render_template('transactions/sale_form.html')

@transactions_bp.route('/new-purchase', methods=['GET', 'POST'])
@login_required
@staff_required
def new_purchase():
    """Create a new purchase/restock transaction."""
    suppliers = Supplier.query.filter_by(is_active=True).order_by(Supplier.name).all()
    
    if request.method == 'POST':
        supplier_id = request.form.get('supplier_id')
        notes = request.form.get('notes', '').strip()
        
        # Get items from form
        product_ids = request.form.getlist('product_id[]')
        quantities = request.form.getlist('quantity[]')
        unit_costs = request.form.getlist('unit_cost[]')
        
        if not product_ids or not any(product_ids):
            flash('Please add at least one product to the purchase.', 'error')
            return render_template('transactions/purchase_form.html', suppliers=suppliers)
        
        if not supplier_id:
            flash('Please select a supplier.', 'error')
            return render_template('transactions/purchase_form.html', suppliers=suppliers)
        
        try:
            supplier_id = int(supplier_id)
            supplier = db.get_or_404(Supplier, supplier_id)
        except (ValueError, TypeError):
            flash('Invalid supplier selected.', 'error')
            return render_template('transactions/purchase_form.html', suppliers=suppliers)
        
        # Validate and prepare items
        items = []
        subtotal = 0
        errors = []
        
        for i, (pid, qty, cost) in enumerate(zip(product_ids, quantities, unit_costs)):
            if not pid:
                continue
            
            try:
                product_id = int(pid)
                quantity = int(qty)
                unit_cost = float(cost)
            except ValueError:
                errors.append(f'Invalid data at row {i+1}.')
                continue
            
            if quantity <= 0:
                errors.append(f'Quantity must be greater than 0 at row {i+1}.')
                continue
            
            if unit_cost < 0:
                errors.append(f'Unit cost cannot be negative at row {i+1}.')
                continue
            
            product = db.session.get(Product, product_id)
            if not product:
                errors.append(f'Product not found at row {i+1}.')
                continue
            
            item_total = unit_cost * quantity
            items.append({
                'product': product,
                'quantity': quantity,
                'unit_price': unit_cost,
                'total_price': item_total
            })
            subtotal += item_total
        
        if errors:
            for error in errors:
                flash(error, 'error')
            return render_template('transactions/purchase_form.html', suppliers=suppliers)
        
        # Create transaction
        transaction = Transaction(
            transaction_type='purchase',
            reference_number=generate_reference_number('PUR'),
            user_id=current_user.id,
            supplier_id=supplier_id,
            subtotal=subtotal,
            tax=0,
            discount=0,
            total=subtotal,
            notes=notes or None
        )
        db.session.add(transaction)
        db.session.flush()
        
        # Create transaction items and update stock
        for item in items:
            product = item['product']
            quantity = item['quantity']
            
            # Create transaction item
            trans_item = TransactionItem(
                transaction_id=transaction.id,
                product_id=product.id,
                quantity=quantity,
                unit_price=item['unit_price'],
                total_price=item['total_price']
            )
            db.session.add(trans_item)
            
            # Record stock movement
            movement = StockMovement(
                product_id=product.id,
                user_id=current_user.id,
                movement_type='purchase',
                quantity_change=quantity,
                quantity_before=product.quantity,
                quantity_after=product.quantity + quantity,
                reference=transaction.reference_number,
                notes=f'Purchase from {supplier.name}'
            )
            db.session.add(movement)
            
            # Update product quantity
            product.quantity += quantity
            
            # Optionally update cost price
            product.cost_price = item['unit_price']

        _record_cash_entry(
            entry_type='purchase_outflow',
            amount=-subtotal,
            notes=f'Purchase {transaction.reference_number} from {supplier.name}',
            transaction_id=transaction.id
        )
        
        # Audit log
        audit = AuditLog(
            user_id=current_user.id,
            action='create',
            table_name='transactions',
            record_id=transaction.id,
            new_values=json.dumps({
                'type': 'purchase',
                'reference': transaction.reference_number,
                'total': subtotal,
                'supplier_id': supplier_id,
                'supplier_name': supplier.name,
                'items_count': len(items)
            }),
            ip_address=request.remote_addr,
            user_agent=str(request.user_agent)[:255]
        )
        db.session.add(audit)
        db.session.commit()
        
        flash(f'Purchase {transaction.reference_number} recorded successfully. Total: ₱{subtotal:,.2f}', 'success')
        return redirect(url_for('transactions.view_transaction', id=transaction.id))
    
    return render_template('transactions/purchase_form.html', suppliers=suppliers)

@transactions_bp.route('/<int:id>')
@login_required
def view_transaction(id):
    """View transaction details."""
    transaction = db.get_or_404(Transaction, id)
    items = transaction.items.all()
    
    return render_template('transactions/view.html',
        transaction=transaction,
        items=items
    )

@transactions_bp.route('/sales')
@login_required
def sales():
    """View sales transactions."""
    return redirect(url_for('transactions.list_transactions', type='sale'))

@transactions_bp.route('/purchases')
@login_required
def purchases():
    """View purchase transactions."""
    return redirect(url_for('transactions.list_transactions', type='purchase'))
