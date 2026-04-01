from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from app.models import db, Product, Category, StockMovement, AuditLog
from app.utils.decorators import staff_required, admin_required
from app.utils.helpers import validate_positive_number, validate_positive_integer, log_audit
import json

products_bp = Blueprint('products', __name__)

@products_bp.route('/')
@login_required
def list_products():
    """List all products with filtering and search."""
    page = request.args.get('page', 1, type=int)
    per_page = 20
    
    # Get filter parameters
    category_id = request.args.get('category', type=int)
    search = request.args.get('search', '').strip()
    stock_filter = request.args.get('stock')  # 'low', 'out', 'all'
    
    # Build query
    query = Product.query.filter_by(is_active=True)
    
    if category_id:
        query = query.filter_by(category_id=category_id)
    
    if search:
        query = query.filter(
            db.or_(
                Product.name.ilike(f'%{search}%'),
                Product.sku.ilike(f'%{search}%'),
                Product.isbn.ilike(f'%{search}%')
            )
        )
    
    if stock_filter == 'low':
        query = query.filter(Product.quantity <= Product.reorder_level, Product.quantity > 0)
    elif stock_filter == 'out':
        query = query.filter(Product.quantity == 0)
    
    # Order by name
    query = query.order_by(Product.name)
    
    # Paginate
    products = query.paginate(page=page, per_page=per_page, error_out=False)
    categories = Category.query.all()
    
    return render_template('products/list.html',
        products=products,
        categories=categories,
        current_category=category_id,
        search=search,
        stock_filter=stock_filter
    )

@products_bp.route('/add', methods=['GET', 'POST'])
@login_required
@staff_required
def add_product():
    """Add a new product."""
    categories = Category.query.all()
    
    if request.method == 'POST':
        # Get form data
        sku = request.form.get('sku', '').strip()
        name = request.form.get('name', '').strip()
        description = request.form.get('description', '').strip()
        category_id = request.form.get('category_id', type=int)
        cost_price = request.form.get('cost_price', 0)
        selling_price = request.form.get('selling_price', 0)
        quantity = request.form.get('quantity', 0)
        reorder_level = request.form.get('reorder_level', 10)
        isbn = request.form.get('isbn', '').strip()
        author = request.form.get('author', '').strip()
        publisher = request.form.get('publisher', '').strip()
        
        # Validation
        errors = []
        
        if not sku:
            errors.append('SKU is required.')
        elif Product.query.filter_by(sku=sku).first():
            errors.append('A product with this SKU already exists.')
        
        if not name:
            errors.append('Product name is required.')
        
        if not category_id:
            errors.append('Please select a category.')
        
        # Validate numbers
        valid, result = validate_positive_number(cost_price, 'Cost price')
        if not valid:
            errors.append(result)
        else:
            cost_price = result
        
        valid, result = validate_positive_number(selling_price, 'Selling price')
        if not valid:
            errors.append(result)
        else:
            selling_price = result
        
        valid, result = validate_positive_integer(quantity, 'Quantity')
        if not valid:
            errors.append(result)
        else:
            quantity = result
        
        valid, result = validate_positive_integer(reorder_level, 'Reorder level')
        if not valid:
            errors.append(result)
        else:
            reorder_level = result
        
        if errors:
            for error in errors:
                flash(error, 'error')
            return render_template('products/form.html',
                categories=categories,
                product=None,
                form_data=request.form
            )
        
        # Create product
        product = Product(
            sku=sku,
            name=name,
            description=description,
            category_id=category_id,
            cost_price=cost_price,
            selling_price=selling_price,
            quantity=quantity,
            reorder_level=reorder_level,
            isbn=isbn or None,
            author=author or None,
            publisher=publisher or None
        )
        
        db.session.add(product)
        db.session.flush()  # Get the product ID
        
        # Create initial stock movement if quantity > 0
        if quantity > 0:
            movement = StockMovement(
                product_id=product.id,
                user_id=current_user.id,
                movement_type='adjustment',
                quantity_change=quantity,
                quantity_before=0,
                quantity_after=quantity,
                reference='Initial stock',
                notes='Product created with initial stock'
            )
            db.session.add(movement)
        
        # Create audit log
        audit = AuditLog(
            user_id=current_user.id,
            action='create',
            table_name='products',
            record_id=product.id,
            new_values=json.dumps({
                'sku': sku,
                'name': name,
                'category_id': category_id,
                'quantity': quantity,
                'selling_price': selling_price
            }),
            ip_address=request.remote_addr,
            user_agent=str(request.user_agent)[:255]
        )
        db.session.add(audit)
        db.session.commit()
        
        flash(f'Product "{name}" has been added successfully.', 'success')
        return redirect(url_for('products.list_products'))
    
    return render_template('products/form.html',
        categories=categories,
        product=None,
        form_data={}
    )

@products_bp.route('/<int:id>')
@login_required
def view_product(id):
    """View product details."""
    product = db.get_or_404(Product, id)
    
    # Get recent stock movements
    movements = StockMovement.query.filter_by(product_id=id).order_by(
        StockMovement.created_at.desc()
    ).limit(10).all()
    
    return render_template('products/view.html',
        product=product,
        movements=movements
    )

@products_bp.route('/<int:id>/edit', methods=['GET', 'POST'])
@login_required
@staff_required
def edit_product(id):
    """Edit an existing product."""
    product = db.get_or_404(Product, id)
    categories = Category.query.all()
    
    if request.method == 'POST':
        # Store old values for audit
        old_values = {
            'sku': product.sku,
            'name': product.name,
            'category_id': product.category_id,
            'cost_price': product.cost_price,
            'selling_price': product.selling_price,
            'reorder_level': product.reorder_level
        }
        
        # Get form data
        sku = request.form.get('sku', '').strip()
        name = request.form.get('name', '').strip()
        description = request.form.get('description', '').strip()
        category_id = request.form.get('category_id', type=int)
        cost_price = request.form.get('cost_price', 0)
        selling_price = request.form.get('selling_price', 0)
        reorder_level = request.form.get('reorder_level', 10)
        isbn = request.form.get('isbn', '').strip()
        author = request.form.get('author', '').strip()
        publisher = request.form.get('publisher', '').strip()
        
        # Validation
        errors = []
        
        if not sku:
            errors.append('SKU is required.')
        else:
            existing = Product.query.filter_by(sku=sku).first()
            if existing and existing.id != id:
                errors.append('A product with this SKU already exists.')
        
        if not name:
            errors.append('Product name is required.')
        
        if not category_id:
            errors.append('Please select a category.')
        
        # Validate numbers
        valid, result = validate_positive_number(cost_price, 'Cost price')
        if not valid:
            errors.append(result)
        else:
            cost_price = result
        
        valid, result = validate_positive_number(selling_price, 'Selling price')
        if not valid:
            errors.append(result)
        else:
            selling_price = result
        
        valid, result = validate_positive_integer(reorder_level, 'Reorder level')
        if not valid:
            errors.append(result)
        else:
            reorder_level = result
        
        if errors:
            for error in errors:
                flash(error, 'error')
            return render_template('products/form.html',
                categories=categories,
                product=product,
                form_data=request.form
            )
        
        # Update product (not quantity - that's done via stock adjustment)
        product.sku = sku
        product.name = name
        product.description = description
        product.category_id = category_id
        product.cost_price = cost_price
        product.selling_price = selling_price
        product.reorder_level = reorder_level
        product.isbn = isbn or None
        product.author = author or None
        product.publisher = publisher or None
        
        # Create audit log
        new_values = {
            'sku': sku,
            'name': name,
            'category_id': category_id,
            'cost_price': cost_price,
            'selling_price': selling_price,
            'reorder_level': reorder_level
        }
        
        audit = AuditLog(
            user_id=current_user.id,
            action='update',
            table_name='products',
            record_id=product.id,
            old_values=json.dumps(old_values),
            new_values=json.dumps(new_values),
            ip_address=request.remote_addr,
            user_agent=str(request.user_agent)[:255]
        )
        db.session.add(audit)
        db.session.commit()
        
        flash(f'Product "{name}" has been updated successfully.', 'success')
        return redirect(url_for('products.view_product', id=id))
    
    return render_template('products/form.html',
        categories=categories,
        product=product,
        form_data={}
    )

@products_bp.route('/<int:id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_product(id):
    """Soft delete a product (set is_active to False)."""
    product = db.get_or_404(Product, id)
    
    # Soft delete
    product.is_active = False
    
    # Create audit log
    audit = AuditLog(
        user_id=current_user.id,
        action='delete',
        table_name='products',
        record_id=product.id,
        old_values=json.dumps({'name': product.name, 'sku': product.sku}),
        ip_address=request.remote_addr,
        user_agent=str(request.user_agent)[:255]
    )
    db.session.add(audit)
    db.session.commit()
    
    flash(f'Product "{product.name}" has been deleted.', 'success')
    return redirect(url_for('products.list_products'))

@products_bp.route('/<int:id>/adjust-stock', methods=['GET', 'POST'])
@login_required
@staff_required
def adjust_stock(id):
    """Adjust stock quantity for a product."""
    product = db.get_or_404(Product, id)
    
    if request.method == 'POST':
        adjustment_type = request.form.get('adjustment_type')  # 'add' or 'subtract'
        quantity = request.form.get('quantity', 0)
        reason = request.form.get('reason', '').strip()
        
        # Validation
        valid, result = validate_positive_integer(quantity, 'Quantity')
        if not valid:
            flash(result, 'error')
            return render_template('products/adjust_stock.html', product=product)
        
        quantity = result
        
        if quantity == 0:
            flash('Please enter a quantity greater than 0.', 'error')
            return render_template('products/adjust_stock.html', product=product)
        
        if not reason:
            flash('Please provide a reason for the adjustment.', 'error')
            return render_template('products/adjust_stock.html', product=product)
        
        # Calculate change
        if adjustment_type == 'subtract':
            if quantity > product.quantity:
                flash(f'Cannot subtract {quantity} units. Only {product.quantity} in stock.', 'error')
                return render_template('products/adjust_stock.html', product=product)
            quantity_change = -quantity
        else:
            quantity_change = quantity
        
        # Record stock movement
        movement = StockMovement(
            product_id=product.id,
            user_id=current_user.id,
            movement_type='adjustment',
            quantity_change=quantity_change,
            quantity_before=product.quantity,
            quantity_after=product.quantity + quantity_change,
            reference='Manual adjustment',
            notes=reason
        )
        db.session.add(movement)
        
        # Update product quantity
        product.quantity += quantity_change
        
        # Audit log
        audit = AuditLog(
            user_id=current_user.id,
            action='update',
            table_name='products',
            record_id=product.id,
            old_values=json.dumps({'quantity': product.quantity - quantity_change}),
            new_values=json.dumps({'quantity': product.quantity, 'adjustment_reason': reason}),
            ip_address=request.remote_addr,
            user_agent=str(request.user_agent)[:255]
        )
        db.session.add(audit)
        db.session.commit()
        
        flash(f'Stock adjusted successfully. New quantity: {product.quantity}', 'success')
        return redirect(url_for('products.view_product', id=id))
    
    return render_template('products/adjust_stock.html', product=product)

@products_bp.route('/low-stock')
@login_required
def low_stock():
    """View all low stock products."""
    products = Product.query.filter(
        Product.quantity <= Product.reorder_level,
        Product.is_active == True
    ).order_by(Product.quantity).all()
    
    return render_template('products/low_stock.html', products=products)

@products_bp.route('/api/search')
@login_required
def api_search():
    """API endpoint for product search (used in transactions)."""
    query = request.args.get('q', '').strip()
    
    if len(query) < 2:
        return jsonify([])
    
    products = Product.query.filter(
        Product.is_active == True,
        db.or_(
            Product.name.ilike(f'%{query}%'),
            Product.sku.ilike(f'%{query}%'),
            Product.isbn.ilike(f'%{query}%')
        )
    ).limit(10).all()
    
    return jsonify([{
        'id': p.id,
        'sku': p.sku,
        'name': p.name,
        'price': p.selling_price,
        'quantity': p.quantity,
        'category': p.category.name
    } for p in products])
