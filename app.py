import os
from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from functools import wraps
from datetime import datetime

from config import config
from models import db, User, Role, Permission

def create_app(config_name=None):
    """应用工厂函数"""
    if config_name is None:
        config_name = os.environ.get('FLASK_ENV', 'development')
    
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    
    # 初始化扩展
    db.init_app(app)
    
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message = '请先登录'
    login_manager.login_message_category = 'warning'
    
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))
    
    # 注册蓝图
    from routes import auth_bp, member_bp, product_bp, sales_bp, inventory_bp, return_bp, report_bp
    
    app.register_blueprint(auth_bp)
    app.register_blueprint(member_bp)
    app.register_blueprint(product_bp)
    app.register_blueprint(sales_bp)
    app.register_blueprint(inventory_bp)
    app.register_blueprint(return_bp)
    app.register_blueprint(report_bp)
    
    # 首页路由
    @app.route('/')
    def index():
        if current_user.is_authenticated:
            return redirect(url_for('dashboard'))
        return redirect(url_for('auth.login'))
    
    @app.route('/dashboard')
    @login_required
    def dashboard():
        """仪表板"""
        from models import Order, Member, ReturnExchange
        from sqlalchemy import func
        
        # 获取统计数据
        today = datetime.today().date()
        today_sales = db.session.query(func.sum(Order.final_amount)).filter(
            db.cast(Order.created_at, db.Date) == today,
            Order.status == 'completed'
        ).scalar() or 0
        
        today_orders = Order.query.filter(
            db.cast(Order.created_at, db.Date) == today,
            Order.status == 'completed'
        ).count()
        
        member_count = Member.query.filter_by(status='approved').count()
        
        pending_returns = ReturnExchange.query.filter_by(status='pending').count()
        
        return render_template('dashboard.html',
                             today_sales=today_sales,
                             today_orders=today_orders,
                             member_count=member_count,
                             pending_returns=pending_returns)
    
    # 错误处理
    @app.errorhandler(404)
    def not_found(error):
        return render_template('errors/404.html'), 404
    
    @app.errorhandler(500)
    def server_error(error):
        db.session.rollback()
        return render_template('errors/500.html'), 500
    
    # 创建数据库表
    with app.app_context():
        db.create_all()
        # 初始化默认数据
        _init_default_data()
    
    return app

def _init_default_data():
    """初始化默认数据"""
    from models import User, Category, ReturnReason
    
    # 创建默认用户
    if User.query.count() == 0:
        admin = User()
        admin.username = 'admin'
        admin.email = 'admin@supermarket.com'
        admin.real_name = '管理员'
        admin.role = Role.ADMIN.value
        admin.is_active = True
        admin.set_password('admin123')
        
        cashier = User()
        cashier.username = 'cashier'
        cashier.email = 'cashier@supermarket.com'
        cashier.real_name = '收银员'
        cashier.role = Role.CASHIER.value
        cashier.is_active = True
        cashier.set_password('cashier123')
        
        inventory_manager = User()
        inventory_manager.username = 'inventory'
        inventory_manager.email = 'inventory@supermarket.com'
        inventory_manager.real_name = '库存管理员'
        inventory_manager.role = Role.INVENTORY_MANAGER.value
        inventory_manager.is_active = True
        inventory_manager.set_password('inventory123')
        
        db.session.add_all([admin, cashier, inventory_manager])
        db.session.commit()
    
    # 创建默认分类
    if Category.query.count() == 0:
        categories = [
            Category(name='日用品', code='DAILY', description='日常生活用品'),
            Category(name='食品饮料', code='FOOD', description='食品和饮料'),
            Category(name='电子产品', code='ELECTRONICS', description='电子产品'),
            Category(name='衣服鞋帽', code='APPAREL', description='衣服和鞋类'),
        ]
        db.session.add_all(categories)
        db.session.commit()
    
    # 创建默认退换货原因
    if ReturnReason.query.count() == 0:
        reasons = [
            ReturnReason(reason='商品质量问题', description='商品本身存在质量问题'),
            ReturnReason(reason='物流损坏', description='商品在物流过程中被损坏'),
            ReturnReason(reason='与描述不符', description='收到的商品与描述不相符'),
            ReturnReason(reason='误购', description='消费者误购'),
            ReturnReason(reason='不满意', description='消费者对商品不满意'),
        ]
        db.session.add_all(reasons)
        db.session.commit()

def permission_required(permission):
    """权限检查装饰器"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                return redirect(url_for('auth.login'))
            
            if not current_user.has_permission(permission):
                flash('您没有权限访问此页面', 'danger')
                return redirect(url_for('dashboard'))
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, host='0.0.0.0', port=5000)
