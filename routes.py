"""
超市管理系统 - 路由模块
包含所有蓝图的定义和路由处理
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, current_app
from flask_login import login_required, current_user
from functools import wraps
from datetime import datetime, timedelta
from sqlalchemy import func, desc

from models import db, User, Member, Product, Category, Order, OrderItem, Inventory, ReturnExchange, ReturnReason

# ==================== 认证蓝图 ====================
auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """登录页面"""
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        user = User.query.filter_by(username=username).first()
        
        if user and user.check_password(password):
            if user.is_active:
                from flask_login import login_user
                login_user(user)
                next_page = request.args.get('next')
                return redirect(next_page) if next_page else redirect(url_for('dashboard'))
            else:
                flash('账户已被禁用', 'danger')
        else:
            flash('用户名或密码错误', 'danger')
    
    return render_template('auth/login.html')

@auth_bp.route('/logout')
@login_required
def logout():
    """登出"""
    from flask_login import logout_user
    logout_user()
    flash('已成功登出', 'success')
    return redirect(url_for('auth.login'))

@auth_bp.route('/profile')
@login_required
def profile():
    """个人资料"""
    return render_template('auth/profile.html', user=current_user)

@auth_bp.route('/change-password', methods=['POST'])
@login_required
def change_password():
    """修改密码"""
    old_password = request.form.get('old_password')
    new_password = request.form.get('new_password')
    confirm_password = request.form.get('confirm_password')
    
    if not current_user.check_password(old_password):
        flash('原密码错误', 'danger')
        return redirect(url_for('auth.profile'))
    
    if new_password != confirm_password:
        flash('两次输入的密码不一致', 'danger')
        return redirect(url_for('auth.profile'))
    
    if len(new_password) < 6:
        flash('密码长度至少为 6 位', 'danger')
        return redirect(url_for('auth.profile'))
    
    current_user.set_password(new_password)
    db.session.commit()
    flash('密码已修改', 'success')
    return redirect(url_for('auth.profile'))

# ==================== 会员蓝图 ====================
member_bp = Blueprint('member', __name__, url_prefix='/member')

@member_bp.route('/')
@login_required
def list_members():
    """会员列表"""
    page = request.args.get('page', 1, type=int)
    search = request.args.get('search', '')
    status = request.args.get('status', '')
    
    query = Member.query
    
    if search:
        query = query.filter(
            (Member.name.ilike(f'%{search}%')) |
            (Member.phone.ilike(f'%{search}%')) |
            (Member.member_no.ilike(f'%{search}%'))
        )
    
    if status:
        query = query.filter_by(status=status)
    
    members = query.paginate(page=page, per_page=20)
    
    return render_template('member/list.html', members=members, search=search, status=status)

@member_bp.route('/create', methods=['GET', 'POST'])
@login_required
def create_member():
    """创建会员"""
    if request.method == 'POST':
        member = Member()
        member.name = request.form.get('name')
        member.phone = request.form.get('phone')
        member.email = request.form.get('email')
        member.address = request.form.get('address')
        member.status = 'approved'
        member.created_at = datetime.now()
        
        db.session.add(member)
        db.session.commit()
        
        flash(f'会员 {member.name} 创建成功', 'success')
        return redirect(url_for('member.list_members'))
    
    return render_template('member/create.html')

@member_bp.route('/<int:member_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_member(member_id):
    """编辑会员"""
    member = Member.query.get_or_404(member_id)
    
    if request.method == 'POST':
        member.name = request.form.get('name')
        member.phone = request.form.get('phone')
        member.email = request.form.get('email')
        member.address = request.form.get('address')
        member.status = request.form.get('status')
        
        db.session.commit()
        flash('会员信息已更新', 'success')
        return redirect(url_for('member.list_members'))
    
    return render_template('member/edit.html', member=member)

@member_bp.route('/<int:member_id>/delete', methods=['POST'])
@login_required
def delete_member(member_id):
    """删除会员"""
    member = Member.query.get_or_404(member_id)
    db.session.delete(member)
    db.session.commit()
    flash('会员已删除', 'success')
    return redirect(url_for('member.list_members'))

# ==================== 产品蓝图 ====================
product_bp = Blueprint('product', __name__, url_prefix='/product')

@product_bp.route('/')
@login_required
def list_products():
    """产品列表"""
    page = request.args.get('page', 1, type=int)
    search = request.args.get('search', '')
    category = request.args.get('category', '')
    
    query = Product.query
    
    if search:
        query = query.filter(
            (Product.name.ilike(f'%{search}%')) |
            (Product.sku.ilike(f'%{search}%'))
        )
    
    if category:
        query = query.filter_by(category_id=category)
    
    products = query.paginate(page=page, per_page=20)
    categories = Category.query.all()
    
    return render_template('product/list.html', products=products, categories=categories, search=search, category=category)

@product_bp.route('/create', methods=['GET', 'POST'])
@login_required
def create_product():
    """创建产品"""
    if request.method == 'POST':
        product = Product()
        product.name = request.form.get('name')
        product.sku = request.form.get('sku')
        product.category_id = request.form.get('category_id')
        product.unit_price = float(request.form.get('unit_price', 0))
        product.description = request.form.get('description')
        product.status = 'active'
        
        db.session.add(product)
        db.session.commit()
        
        flash(f'产品 {product.name} 创建成功', 'success')
        return redirect(url_for('product.list_products'))
    
    categories = Category.query.all()
    return render_template('product/create.html', categories=categories)

@product_bp.route('/<int:product_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_product(product_id):
    """编辑产品"""
    product = Product.query.get_or_404(product_id)
    
    if request.method == 'POST':
        product.name = request.form.get('name')
        product.sku = request.form.get('sku')
        product.category_id = request.form.get('category_id')
        product.unit_price = float(request.form.get('unit_price', 0))
        product.description = request.form.get('description')
        product.status = request.form.get('status')
        
        db.session.commit()
        flash('产品信息已更新', 'success')
        return redirect(url_for('product.list_products'))
    
    categories = Category.query.all()
    return render_template('product/edit.html', product=product, categories=categories)

@product_bp.route('/<int:product_id>/delete', methods=['POST'])
@login_required
def delete_product(product_id):
    """删除产品"""
    product = Product.query.get_or_404(product_id)
    db.session.delete(product)
    db.session.commit()
    flash('产品已删除', 'success')
    return redirect(url_for('product.list_products'))

# ==================== 销售蓝图 ====================
sales_bp = Blueprint('sales', __name__, url_prefix='/sales')

@sales_bp.route('/')
@login_required
def list_sales():
    """销售订单列表"""
    page = request.args.get('page', 1, type=int)
    search = request.args.get('search', '')
    status = request.args.get('status', '')
    
    query = Order.query
    
    if search:
        query = query.filter(
            (Order.order_no.ilike(f'%{search}%')) |
            (Order.member_id == search if search.isdigit() else False)
        )
    
    if status:
        query = query.filter_by(status=status)
    
    orders = query.order_by(desc(Order.created_at)).paginate(page=page, per_page=20)
    
    return render_template('sales/list.html', orders=orders, search=search, status=status)

@sales_bp.route('/create', methods=['GET', 'POST'])
@login_required
def create_order():
    """创建销售订单"""
    if request.method == 'POST':
        order = Order()
        order.member_id = request.form.get('member_id') or None
        order.created_by = current_user.id
        order.status = 'pending'
        order.created_at = datetime.now()
        
        db.session.add(order)
        db.session.flush()
        
        # 添加订单项
        product_ids = request.form.getlist('product_id[]')
        quantities = request.form.getlist('quantity[]')
        
        total_amount = 0
        for product_id, quantity in zip(product_ids, quantities):
            if product_id and quantity:
                product = Product.query.get(product_id)
                if product:
                    qty = int(quantity)
                    item = OrderItem()
                    item.order_id = order.id
                    item.product_id = product_id
                    item.quantity = qty
                    item.unit_price = product.unit_price
                    item.subtotal = product.unit_price * qty
                    
                    db.session.add(item)
                    total_amount += item.subtotal
        
        order.final_amount = total_amount
        order.status = 'completed'
        db.session.commit()
        
        flash(f'订单 {order.order_no} 创建成功', 'success')
        return redirect(url_for('sales.list_sales'))
    
    members = Member.query.filter_by(status='approved').all()
    products = Product.query.filter_by(status='active').all()
    
    return render_template('sales/create.html', members=members, products=products)

@sales_bp.route('/<int:order_id>')
@login_required
def view_order(order_id):
    """查看订单详情"""
    order = Order.query.get_or_404(order_id)
    return render_template('sales/view.html', order=order)

# ==================== 库存蓝图 ====================
inventory_bp = Blueprint('inventory', __name__, url_prefix='/inventory')

@inventory_bp.route('/')
@login_required
def list_inventory():
    """库存列表"""
    page = request.args.get('page', 1, type=int)
    search = request.args.get('search', '')
    
    query = Inventory.query
    
    if search:
        query = query.join(Product).filter(
            (Product.name.ilike(f'%{search}%')) |
            (Product.sku.ilike(f'%{search}%'))
        )
    
    inventories = query.paginate(page=page, per_page=20)
    
    return render_template('inventory/list.html', inventories=inventories, search=search)

@inventory_bp.route('/<int:inventory_id>/adjust', methods=['GET', 'POST'])
@login_required
def adjust_inventory(inventory_id):
    """调整库存"""
    inventory = Inventory.query.get_or_404(inventory_id)
    
    if request.method == 'POST':
        adjustment_qty = int(request.form.get('adjustment_qty', 0))
        reason = request.form.get('reason')
        
        old_qty = inventory.quantity
        inventory.quantity += adjustment_qty
        
        if inventory.quantity < 0:
            flash('库存不能为负数', 'danger')
            return redirect(url_for('inventory.list_inventory'))
        
        db.session.commit()
        
        flash(f'库存已调整: {old_qty} → {inventory.quantity}', 'success')
        return redirect(url_for('inventory.list_inventory'))
    
    return render_template('inventory/adjust.html', inventory=inventory)

# ==================== 退货蓝图 ====================
return_bp = Blueprint('return', __name__, url_prefix='/return')

@return_bp.route('/')
@login_required
def list_returns():
    """退货列表"""
    page = request.args.get('page', 1, type=int)
    status = request.args.get('status', '')
    
    query = ReturnExchange.query
    
    if status:
        query = query.filter_by(status=status)
    
    returns = query.order_by(desc(ReturnExchange.created_at)).paginate(page=page, per_page=20)
    
    return render_template('return/list.html', returns=returns, status=status)

@return_bp.route('/create', methods=['GET', 'POST'])
@login_required
def create_return():
    """创建退货申请"""
    if request.method == 'POST':
        order_id = request.form.get('order_id')
        product_id = request.form.get('product_id')
        reason_id = request.form.get('reason_id')
        quantity = int(request.form.get('quantity', 1))
        notes = request.form.get('notes')
        
        return_item = ReturnExchange()
        return_item.order_id = order_id
        return_item.product_id = product_id
        return_item.reason_id = reason_id
        return_item.quantity = quantity
        return_item.notes = notes
        return_item.status = 'pending'
        return_item.created_at = datetime.now()
        return_item.created_by = current_user.id
        
        db.session.add(return_item)
        db.session.commit()
        
        flash('退货申请已创建', 'success')
        return redirect(url_for('return.list_returns'))
    
    orders = Order.query.filter_by(status='completed').all()
    reasons = ReturnReason.query.all()
    
    return render_template('return/create.html', orders=orders, reasons=reasons)

@return_bp.route('/<int:return_id>/approve', methods=['POST'])
@login_required
def approve_return(return_id):
    """批准退货"""
    return_item = ReturnExchange.query.get_or_404(return_id)
    
    return_item.status = 'approved'
    return_item.approved_at = datetime.now()
    return_item.approved_by = current_user.id
    
    # 调整库存
    inventory = Inventory.query.filter_by(product_id=return_item.product_id).first()
    if inventory:
        inventory.quantity += return_item.quantity
    
    db.session.commit()
    
    flash('退货已批准', 'success')
    return redirect(url_for('return.list_returns'))

@return_bp.route('/<int:return_id>/reject', methods=['POST'])
@login_required
def reject_return(return_id):
    """拒绝退货"""
    return_item = ReturnExchange.query.get_or_404(return_id)
    
    return_item.status = 'rejected'
    return_item.approved_at = datetime.now()
    return_item.approved_by = current_user.id
    
    db.session.commit()
    
    flash('退货已拒绝', 'success')
    return redirect(url_for('return.list_returns'))

# ==================== 报告蓝图 ====================
report_bp = Blueprint('report', __name__, url_prefix='/report')

@report_bp.route('/sales')
@login_required
def sales_report():
    """销售报告"""
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    
    query = Order.query.filter_by(status='completed')
    
    if start_date:
        query = query.filter(Order.created_at >= datetime.strptime(start_date, '%Y-%m-%d'))
    
    if end_date:
        end_datetime = datetime.strptime(end_date, '%Y-%m-%d') + timedelta(days=1)
        query = query.filter(Order.created_at < end_datetime)
    
    orders = query.all()
    
    total_sales = sum(order.final_amount for order in orders)
    total_orders = len(orders)
    avg_order = total_sales / total_orders if total_orders > 0 else 0
    
    return render_template('report/sales.html',
                         orders=orders,
                         total_sales=total_sales,
                         total_orders=total_orders,
                         avg_order=avg_order,
                         start_date=start_date,
                         end_date=end_date)

@report_bp.route('/inventory')
@login_required
def inventory_report():
    """库存报告"""
    inventories = Inventory.query.all()
    
    total_items = len(inventories)
    low_stock = sum(1 for inv in inventories if inv.quantity < 10)
    
    return render_template('report/inventory.html',
                         inventories=inventories,
                         total_items=total_items,
                         low_stock=low_stock)

@report_bp.route('/member')
@login_required
def member_report():
    """会员报告"""
    members = Member.query.filter_by(status='approved').all()
    
    total_members = len(members)
    active_members = total_members  # 可根据需要定义"活跃"
    
    return render_template('report/member.html',
                         members=members,
                         total_members=total_members,
                         active_members=active_members)
