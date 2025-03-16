from app import app, db
from models import User
with app.app_context():
    
    # 创建新用户
    user = User(username='wuz11')
    user.set_password('wu8898308')
    db.session.add(user)
    db.session.commit()
    print('用户 wuz11 创建成功')