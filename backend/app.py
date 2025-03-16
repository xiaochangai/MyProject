from flask import Flask, jsonify, request, session, g
from flask_cors import CORS
from models import db, Transaction, User, LoginAttempt
import os
from datetime import datetime, timedelta
from sqlalchemy import extract
from functools import wraps
import jwt
import time

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///accounting.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'your-secret-key-here'
app.config['JWT_SECRET_KEY'] = 'jwt-secret-key-here'
app.config['JWT_EXPIRATION_DELTA'] = 24 * 60 * 60  # 24小时过期

CORS(app)
db.init_app(app)

# IP封禁列表
banned_ips = {}

# 认证中间件
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        
        # 检查请求头中是否有token
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            if auth_header.startswith('Bearer '):
                token = auth_header[7:]
        
        if not token:
            return jsonify({'message': 'Token is missing!'}), 401
        
        try:
            # 解码token
            data = jwt.decode(token, app.config['JWT_SECRET_KEY'], algorithms=['HS256'])
            current_user = User.query.get(data['user_id'])
            if not current_user:
                return jsonify({'message': 'User not found!'}), 401
            g.current_user = current_user
        except Exception as e:
            app.logger.error(f"Token validation error: {str(e)}")
            return jsonify({'message': 'Token is invalid!'}), 401
            
        return f(*args, **kwargs)
    
    return decorated

# 检查IP是否被封禁
def check_ip_banned():
    client_ip = request.remote_addr
    current_time = time.time()
    
    if client_ip in banned_ips:
        ban_time, ban_duration = banned_ips[client_ip]
        if current_time - ban_time < ban_duration:
            # IP仍在封禁期内
            remaining = int(ban_duration - (current_time - ban_time))
            return jsonify({
                'error': 'IP已被封禁',
                'remaining_seconds': remaining
            }), 403
        else:
            # 封禁期已过，移除IP
            del banned_ips[client_ip]
    
    return None

# 用户注册接口
@app.route('/api/auth/register', methods=['POST'])
def register():
    data = request.json
    
    # 验证必填字段
    if not all(key in data for key in ['username', 'password']):
        return jsonify({'error': '缺少必填字段'}), 400
    
    # 检查用户名是否已存在
    existing_user = User.query.filter_by(username=data['username']).first()
    if existing_user:
        return jsonify({'error': '用户名已存在'}), 400
    
    # 创建新用户
    new_user = User(username=data['username'])
    new_user.set_password(data['password'])
    
    db.session.add(new_user)
    db.session.commit()
    
    return jsonify({'message': '注册成功', 'user': new_user.to_dict()}), 201

# 用户登录接口
@app.route('/api/auth/login', methods=['POST'])
def login():
    data = request.json
    
    # 验证必填字段
    if not all(key in data for key in ['username', 'password']):
        return jsonify({'error': '缺少必填字段'}), 400
    
    # 查找用户
    user = User.query.filter_by(username=data['username']).first()
    
    # 验证用户名和密码
    if not user or not user.check_password(data['password']):
        return jsonify({'error': '用户名或密码错误'}), 401
    
    # 生成JWT令牌
    token_payload = {
        'user_id': user.id,
        'username': user.username,
        'exp': datetime.utcnow() + timedelta(seconds=app.config['JWT_EXPIRATION_DELTA'])
    }
    token = jwt.encode(token_payload, app.config['JWT_SECRET_KEY'], algorithm='HS256')
    
    return jsonify({
        'message': '登录成功',
        'token': token,
        'user': user.to_dict()
    })

# 获取当前用户信息
@app.route('/api/auth/me', methods=['GET'])
@token_required
def get_current_user():
    return jsonify(g.current_user.to_dict())

# 添加认证到交易接口
@app.route('/api/transactions', methods=['GET'])
@token_required
def get_transactions():
    # 获取分页参数
    page = request.args.get('page', 1, type=int)
    per_page = 10
    
    # 查询当前用户的交易记录，按日期倒序排序
    pagination = Transaction.query.filter_by(user_id=g.current_user.id)\
        .order_by(Transaction.date.desc())\
        .paginate(page=page, per_page=per_page, error_out=False)
    
    transactions = pagination.items
    
    return jsonify({
        'items': [t.to_dict() for t in transactions],
        'total': pagination.total,
        'pages': pagination.pages,
        'current_page': page
    })

@app.route('/api/transactions/<int:id>', methods=['GET'])
@token_required
def get_transaction(id):
    transaction = Transaction.query.get_or_404(id)
    # 确保只能访问自己的交易记录
    if transaction.user_id != g.current_user.id:
        return jsonify({'error': '无权访问此交易记录'}), 403
    return jsonify(transaction.to_dict())

@app.route('/api/transactions', methods=['POST'])
def create_transaction():
    data = request.json
    print("create_transaction{}",data)
    # 验证必填字段
    if not all(key in data for key in ['amount', 'category', 'date', 'type']):
        return jsonify({'error': 'Missing required fields'}), 400
    
    # 转换日期字符串为日期对象
    try:
        date = datetime.strptime(data['date'], '%Y-%m-%d').date()
    except ValueError:
        return jsonify({'error': 'Invalid date format. Use YYYY-MM-DD'}), 400
    if g.current_user is None:
        g.current_user.id=1
    transaction = Transaction(
        amount=data['amount'],
        category=data['category'],
        description=data.get('description', ''),
        date=date,
        type=data['type'],
        user_id=g.current_user.id  # 关联到当前登录用户
    )
    
    db.session.add(transaction)
    db.session.commit()
    
    return jsonify(transaction.to_dict()), 201

@app.route('/api/transactions/<int:id>', methods=['PUT'])
@token_required
def update_transaction(id):
    transaction = Transaction.query.get_or_404(id)
    
    # 确保只能修改自己的交易记录
    if transaction.user_id != g.current_user.id:
        return jsonify({'error': '无权修改此交易记录'}), 403
        
    data = request.json
    
    # 更新字段
    if 'amount' in data:
        transaction.amount = data['amount']
    if 'category' in data:
        transaction.category = data['category']
    if 'description' in data:
        transaction.description = data['description']
    if 'date' in data:
        try:
            transaction.date = datetime.strptime(data['date'], '%Y-%m-%d').date()
        except ValueError:
            return jsonify({'error': 'Invalid date format. Use YYYY-MM-DD'}), 400
    if 'type' in data:
        transaction.type = data['type']
    
    db.session.commit()
    
    return jsonify(transaction.to_dict())

@app.route('/api/transactions/<int:id>', methods=['DELETE'])
@token_required
def delete_transaction(id):
    transaction = Transaction.query.get_or_404(id)
    
    # 确保只能删除自己的交易记录
    if transaction.user_id != g.current_user.id:
        return jsonify({'error': '无权删除此交易记录'}), 403
    
    db.session.delete(transaction)
    db.session.commit()
    
    return jsonify({'message': 'Transaction deleted'})

@app.route('/api/statistics/monthly', methods=['GET'])
def monthly_statistics():
    year = request.args.get('year', datetime.now().year, type=int)
    
    result = []
    for month in range(1, 13):
        income = db.session.query(db.func.sum(Transaction.amount)).\
            filter(extract('year', Transaction.date) == year,
                  extract('month', Transaction.date) == month,
                  Transaction.type == 'income').scalar() or 0
                  
        expense = db.session.query(db.func.sum(Transaction.amount)).\
            filter(extract('year', Transaction.date) == year,
                  extract('month', Transaction.date) == month,
                  Transaction.type == 'expense').scalar() or 0
        
        result.append({
            'month': month,
            'income': income,
            'expense': expense,
            'balance': income - expense
        })
    
    return jsonify(result)

@app.route('/api/statistics/yearly', methods=['GET'])
def yearly_statistics():
    years = db.session.query(extract('year', Transaction.date).distinct()).\
        order_by(extract('year', Transaction.date)).all()
    
    result = []
    for (year,) in years:
        income = db.session.query(db.func.sum(Transaction.amount)).\
            filter(extract('year', Transaction.date) == year,
                  Transaction.type == 'income').scalar() or 0
                  
        expense = db.session.query(db.func.sum(Transaction.amount)).\
            filter(extract('year', Transaction.date) == year,
                  Transaction.type == 'expense').scalar() or 0
        
        result.append({
            'year': int(year),
            'income': income,
            'expense': expense,
            'balance': income - expense
        })
    
    return jsonify(result)

@app.route('/api/statistics/categories', methods=['GET'])
def category_statistics():
    year = request.args.get('year', datetime.now().year, type=int)
    month = request.args.get('month', datetime.now().month, type=int)
    
    # 构建过滤条件
    filters = [Transaction.type == 'expense']
    if year:
        filters.append(extract('year', Transaction.date) == year)
    if month:
        filters.append(extract('month', Transaction.date) == month)
    
    # 按类别分组查询
    categories = db.session.query(
        Transaction.category,
        db.func.sum(Transaction.amount).label('total')
    ).filter(*filters).group_by(Transaction.category).all()
    
    result = [{'category': category, 'amount': total} for category, total in categories]
    
    return jsonify(result)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(host='0.0.0.0', port=8000, debug=True)
