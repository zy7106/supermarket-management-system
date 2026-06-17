# 超市商品管理系统

## 系统概述

一个功能完整的超市商品管理系统，包含会员管理、商品销售、库存管理、退换货处理、数据统计等核心功能。

## 主要功能模块

### 1. 会员信息管理
- 会员注册与审核
- 会员信息修改
- 会员查询
- 购物统计
- 消费记录查看

### 2. 商品销售管理
- 商品快速录入
- 订单结算
- 多种支付方式（现金、刷卡、微信、支付宝）
- 小票生成
- 销售记录保存

### 3. 商品货架管理
- 库存预警
- 销量统计
- 自动补货提示
- 库存信息查询

### 4. 退换货管理
- 退换货登记
- 原因记录
- 处理状态追踪
- 统计与历史查询

### 5. 商品基础信息管理
- 商品新增、编辑、删除
- 分类管理
- 价格设置

### 6. 数据统计报表
- 日/月/年销售额统计
- 销量排行
- 会员消费统计
- 退换货率统计

### 7. 权限管理
- 管理员、收银员、库存管理员分级操作权限控制

### 8. 综合查询
- 按商品、会员、时间、订单号多条件组合查询

## 技术栈

- **后端**: Python + Flask
- **数据库**: SQLite（开发）/ MySQL（生产）
- **前端**: HTML5 + CSS3 + Bootstrap5 + JavaScript
- **ORM**: SQLAlchemy
- **容器**: Docker + Docker Compose

## 项目结构

```
supermarket-management-system/
├── app.py                    # Flask应用入口
├── config.py                 # 配置文件
├── requirements.txt          # 依赖包
├── Dockerfile               # Docker配置
├── docker-compose.yml       # Docker编排
├── .gitignore              # Git忽略文件
│
├── models/                  # 数据模型层
│   ├── __init__.py
│   ├── user.py             # 用户和权限
│   ├── member.py           # 会员管理
│   ├── product.py          # 商品管理
│   ├── order.py            # 订单管理
│   ├── inventory.py        # 库存管理
│   └── return_exchange.py  # 退换货管理
│
├── routes/                  # 路由层
│   ├── __init__.py
│   ├── auth_routes.py      # 登录认证
│   ├── member_routes.py    # 会员管理
│   ├── product_routes.py   # 商品管理
│   ├── sales_routes.py     # 销售管理
│   ├── inventory_routes.py # 库存管理
│   ├── return_routes.py    # 退换货管理
│   └── report_routes.py    # 数据报表
│
├── services/                # 业务逻辑层
│   ├── __init__.py
│   └── auth_service.py     # 认证服务
│
├── templates/              # HTML模板
│   ├── layout.html         # 基础布局
│   ├── dashboard.html      # 仪表板
│   ├── auth/
│   │   └── login.html      # 登录页
│   ├── member/             # 会员模板
│   ├── product/            # 商品模板
│   ├── sales/              # 销售模板
│   ├── inventory/          # 库存模板
│   ├── return/             # 退换货模板
│   ├── report/             # 报表模板
│   └── errors/             # 错误页面
│
├── static/                 # 静态资源
│   ├── css/
│   ├── js/
│   └── images/
│
└── utils/                  # 工具函数
    ├── __init__.py
    ├── decorators.py
    └── helpers.py
```

## 快速开始

### 方式一：直接运行

#### 1. 安装依赖
```bash
pip install -r requirements.txt
```

#### 2. 初始化数据库
```bash
python
>>> from app import create_app, db
>>> app = create_app()
>>> with app.app_context():
>>>     db.create_all()
>>> exit()
```

#### 3. 运行应用
```bash
python app.py
```

应用将运行在 `http://localhost:5000`

### 方式二：使用Docker

```bash
docker-compose up -d
```

然后访问 `http://localhost:5000`

## 默认登录账户

| 角色 | 用户名 | 密码 | 权限 |
|------|---------|------|------|
| 管理员 | admin | admin123 | 所有权限 |
| 收银员 | cashier | cashier123 | 销售、库存查询、报表查看 |
| 库存管理员 | inventory | inventory123 | 库存管理、报表查看 |

## 功能演示

### 1. 会员管理
- 在"会员管理"页面点击"添加会员"进行会员注册
- 管理员可以批准或拒绝待审核的会员
- 查看会员详情、消费记录和等级信息

### 2. 商品销售
- 在"快速结算"页面扫描商品条形码或输入商品代码
- 选择付款方式
- 完成订单结算

### 3. 库存管理
- 查看所有商品的库存状态
- 库存预警显示低库存商品
- 进行库存调整和补货

### 4. 数据报表
- 查看日/月/年销售统计
- 查看销量排行
- 查看会员消费统计
- 查看退换货统计

## 配置说明

### 环境变量
在根目录创建 `.env` 文件（可复制 `.env.example`）：

```
FLASK_ENV=development
FLASK_APP=app.py
SECRET_KEY=your-secret-key
DATABASE_URL=sqlite:///supermarket.db
```

### 数据库配置

**开发环境**（SQLite）：
```python
DATABASE_URL = 'sqlite:///supermarket.db'
```

**生产环境**（MySQL）：
```python
DATABASE_URL = 'mysql+pymysql://user:password@localhost/supermarket_db'
```

## API文档

### 会员管理 API

#### 获取会员列表
```
GET /member/list?page=1&status=approved&search=keyword
```

#### 注册新会员
```
POST /member/register
```

#### 批准会员
```
POST /member/<member_id>/approve
```

#### 获取会员详情
```
GET /member/<member_id>/detail
```

### 销售管理 API

#### 获取销售记录
```
GET /sales/list?page=1&search=keyword
```

#### 创建订单
```
POST /sales/checkout
Content-Type: application/json

{
    "member_id": 1,
    "total_amount": 100.00,
    "discount_amount": 10.00,
    "final_amount": 90.00,
    "payment_method": "cash",
    "items": [
        {
            "product_id": 1,
            "unit_price": 50.00,
            "quantity": 2,
            "subtotal": 100.00
        }
    ]
}
```

### 库存管理 API

#### 获取库存列表
```
GET /inventory/list?page=1&search=keyword
```

#### 调整库存
```
POST /inventory/adjust
```

#### 获取库存日志
```
GET /inventory/log?product_id=1
```

### 报表 API

#### 销售报表
```
GET /report/sales?type=daily|monthly|yearly
```

#### 销量排行
```
GET /report/top-products?days=30
```

#### 会员消费统计
```
GET /report/member-consumption
```

#### 退换货统计
```
GET /report/return-exchange?days=30
```

## 开发指南

### 添加新功能

1. 在 `models/` 下创建数据模型
2. 在 `routes/` 下创建路由处理器
3. 在 `services/` 下创建业务逻辑
4. 在 `templates/` 下创建HTML模板
5. 更新 `routes/__init__.py` 注册新的蓝图

### 添加新权限

在 `models/user.py` 的 `Permission` 类中添加新权限：

```python
class Permission(Enum):
    NEW_PERMISSION = 'new_permission'
```

## 故障排除

### 问题1：导入模块错误
确保已安装所有依赖：
```bash
pip install -r requirements.txt
```

### 问题2：数据库连接错误
检查 `config.py` 中的数据库配置是否正确。

### 问题3：登录失败
确保已初始化默认用户，运行以下命令：
```python
from app import create_app, db, User, Role
app = create_app()
with app.app_context():
    # 检查admin用户是否存在
    admin = User.query.filter_by(username='admin').first()
    if not admin:
        print("默认用户未创建")
```

## 贡献

欢迎提交Issue和Pull Request！

## 许可证

MIT License

## 联系方式

如有任何问题或建议，请提交Issue或联系开发者。
