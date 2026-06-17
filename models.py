from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from enum import Enum

db = SQLAlchemy()

class Role(Enum):
    """角色枚举"""
    ADMIN = 'admin'
    CASHIER = 'cashier'
    INVENTORY_MANAGER = 'inventory_manager'
    SALES_MANAGER = 'sales_manager'
    MEMBER = 'member'

class Permission:
    """权限常量"""
    # 用户管理权限
    MANAGE_USERS = 'manage_users'
    VIEW_USERS = 'view_users'
    
    # 产品管理权限
    MANAGE_PRODUCTS = 'manage_products'
    VIEW_PRODUCTS = 'view_products'
    
    # 销售权限
    PROCESS_SALES = 'process_sales'
    VIEW_SALES = 'view_sales'
    
    # 库存权限
    MANAGE_INVENTORY = 'manage_inventory'
    VIEW_INVENTORY = 'view_inventory'
    
    # 会员权限
    MANAGE_MEMBERS = 'manage_members'
    VIEW_MEMBERS = 'view_members'
    
    # 退换货权限
    MANAGE_RETURNS = 'manage_returns'
    VIEW_RETURNS = 'view_returns'
    
    # 报表权限
    VIEW_REPORTS = 'view_reports'

# 定义角色权限映射
ROLE_PERMISSIONS = {
    Role.ADMIN.value: [
        Permission.MANAGE_USERS, Permission.VIEW_USERS,
        Permission.MANAGE_PRODUCTS, Permission.VIEW_PRODUCTS,
        Permission.PROCESS_SALES, Permission.VIEW_SALES,
        Permission.MANAGE_INVENTORY, Permission.VIEW_INVENTORY,
        Permission.MANAGE_MEMBERS, Permission.VIEW_MEMBERS,
        Permission.MANAGE_RETURNS, Permission.VIEW_RETURNS,
        Permission.VIEW_REPORTS,
    ],
    Role.CASHIER.value: [
        Permission.VIEW_PRODUCTS,
        Permission.PROCESS_SALES, Permission.VIEW_SALES,
        Permission.VIEW_INVENTORY,
        Permission.VIEW_MEMBERS,
    ],
    Role.INVENTORY_MANAGER.value: [
        Permission.VIEW_PRODUCTS,
        Permission.MANAGE_INVENTORY, Permission.VIEW_INVENTORY,
        Permission.VIEW_REPORTS,
    ],
    Role.SALES_MANAGER.value: [
        Permission.VIEW_PRODUCTS, Permission.VIEW_SALES,
        Permission.VIEW_INVENTORY,
        Permission.MANAGE_MEMBERS, Permission.VIEW_MEMBERS,
        Permission.VIEW_REPORTS,
    ],
}

class User(UserMixin, db.Model):
    """用户模型"""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    real_name = db.Column(db.String(120))
    role = db.Column(db.String(50), nullable=False, default=Role.MEMBER.value)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def set_password(self, password):
        """设置密码"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """验证密码"""
        return check_password_hash(self.password_hash, password)
    
    def has_permission(self, permission):
        """检查是否有权限"""
        permissions = ROLE_PERMISSIONS.get(self.role, [])
        return permission in permissions
    
    def __repr__(self):
        return f'<User {self.username}>'

class Category(db.Model):
    """产品分类模型"""
    __tablename__ = 'categories'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    code = db.Column(db.String(50), unique=True, nullable=False)
    description = db.Column(db.Text)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    products = db.relationship('Product', backref='category', lazy=True)
    
    def __repr__(self):
        return f'<Category {self.name}>'

class Product(db.Model):
    """产品模型"""
    __tablename__ = 'products'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    code = db.Column(db.String(100), unique=True, nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'), nullable=False)
    description = db.Column(db.Text)
    price = db.Column(db.Float, nullable=False)
    cost = db.Column(db.Float)
    stock = db.Column(db.Integer, default=0)
    minimum_stock = db.Column(db.Integer, default=0)
    supplier = db.Column(db.String(200))
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    order_items = db.relationship('OrderItem', backref='product', lazy=True)
    
    def __repr__(self):
        return f'<Product {self.name}>'

class Member(db.Model):
    """会员模型"""
    __tablename__ = 'members'
    
    id = db.Column(db.Integer, primary_key=True)
    phone = db.Column(db.String(20), unique=True, nullable=False, index=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120))
    member_level = db.Column(db.String(50), default='regular')  # regular, silver, gold, platinum
    points = db.Column(db.Integer, default=0)
    status = db.Column(db.String(50), default='pending')  # pending, approved, rejected, blocked
    total_purchase = db.Column(db.Float, default=0)
    birthday = db.Column(db.Date)
    address = db.Column(db.Text)
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    orders = db.relationship('Order', backref='member', lazy=True)
    
    def __repr__(self):
        return f'<Member {self.name}>'

class Order(db.Model):
    """订单模型"""
    __tablename__ = 'orders'
    
    id = db.Column(db.Integer, primary_key=True)
    order_number = db.Column(db.String(100), unique=True, nullable=False, index=True)
    member_id = db.Column(db.Integer, db.ForeignKey('members.id'))
    cashier_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    
    # 金额信息
    subtotal = db.Column(db.Float, default=0)  # 小计
    discount = db.Column(db.Float, default=0)  # 折扣
    tax = db.Column(db.Float, default=0)  # 税
    final_amount = db.Column(db.Float, default=0)  # 最终金额
    
    # 支付信息
    payment_method = db.Column(db.String(50))  # cash, card, online
    payment_status = db.Column(db.String(50), default='unpaid')  # unpaid, paid, refunded
    
    # 订单状态
    status = db.Column(db.String(50), default='pending')  # pending, completed, cancelled, refunded
    
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    cashier = db.relationship('User', backref='orders')
    order_items = db.relationship('OrderItem', backref='order', lazy=True, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Order {self.order_number}>'

class OrderItem(db.Model):
    """订单项目模型"""
    __tablename__ = 'order_items'
    
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    
    quantity = db.Column(db.Integer, nullable=False)
    unit_price = db.Column(db.Float, nullable=False)
    discount = db.Column(db.Float, default=0)
    subtotal = db.Column(db.Float, nullable=False)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<OrderItem {self.id}>'

class ReturnReason(db.Model):
    """退换原因模型"""
    __tablename__ = 'return_reasons'
    
    id = db.Column(db.Integer, primary_key=True)
    reason = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    returns = db.relationship('ReturnExchange', backref='reason', lazy=True)
    
    def __repr__(self):
        return f'<ReturnReason {self.reason}>'

class ReturnExchange(db.Model):
    """退换货模型"""
    __tablename__ = 'return_exchanges'
    
    id = db.Column(db.Integer, primary_key=True)
    return_number = db.Column(db.String(100), unique=True, nullable=False, index=True)
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'))
    member_id = db.Column(db.Integer, db.ForeignKey('members.id'))
    
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'))
    quantity = db.Column(db.Integer, nullable=False)
    
    return_reason_id = db.Column(db.Integer, db.ForeignKey('return_reasons.id'))
    notes = db.Column(db.Text)
    
    return_type = db.Column(db.String(50))  # return, exchange
    status = db.Column(db.String(50), default='pending')  # pending, approved, rejected, completed
    
    return_date = db.Column(db.DateTime, default=datetime.utcnow)
    processed_date = db.Column(db.DateTime)
    
    processed_by_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    processed_by = db.relationship('User', backref='processed_returns')
    
    refund_amount = db.Column(db.Float)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    order = db.relationship('Order', backref='returns')
    member = db.relationship('Member', backref='returns')
    product = db.relationship('Product')
    
    def __repr__(self):
        return f'<ReturnExchange {self.return_number}>'

class InventoryLog(db.Model):
    """库存日志模型"""
    __tablename__ = 'inventory_logs'
    
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    operation_type = db.Column(db.String(50))  # in, out, adjust
    quantity = db.Column(db.Integer, nullable=False)
    old_stock = db.Column(db.Integer)
    new_stock = db.Column(db.Integer)
    reason = db.Column(db.String(200))
    notes = db.Column(db.Text)
    
    operator_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    operator = db.relationship('User', backref='inventory_operations')
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    
    product = db.relationship('Product')
    
    def __repr__(self):
        return f'<InventoryLog {self.id}>'
