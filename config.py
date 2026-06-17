import os
from datetime import timedelta

class Config:
    """基础配置"""
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_RECORD_QUERIES = True
    REMEMBER_COOKIE_DURATION = timedelta(days=30)
    JSON_AS_ASCII = False
    JSON_SORT_KEYS = False
    
    # 系统配置
    ITEMS_PER_PAGE = 20
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB
    
    # 库存预警配置
    LOW_INVENTORY_THRESHOLD = 0.2  # 20%
    CRITICAL_INVENTORY_THRESHOLD = 0.1  # 10%
    
    # 退换货配置
    RETURN_DAYS_LIMIT = 30  # 购买后30天内可退换
    
    # 支付方式
    PAYMENT_METHODS = ['cash', 'card', 'wechat', 'alipay']

class DevelopmentConfig(Config):
    """开发环境配置"""
    DEBUG = True
    SQLALCHEMY_ECHO = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///supermarket.db'

class ProductionConfig(Config):
    """生产环境配置"""
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'mysql+pymysql://user:password@localhost/supermarket_db'

class TestingConfig(Config):
    """测试环境配置"""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = False

config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}
