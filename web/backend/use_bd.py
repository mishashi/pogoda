import os
import sys
from pathlib import Path
if os.getenv('INSIDE_DOCKER'):
    from models import *
else:
    root = Path(__file__).resolve().parents[2]
    sys.path.insert(0, str(root))
    from web.backend.models import *

def ghash(p):
    return bcrypt.generate_password_hash(p).decode('utf-8')

def check_hash(p,h):
    return bcrypt.check_password_hash(p,h)

def clear_logs(days_old=None, log_type=None, user_id=None):
    from datetime import datetime, timedelta
    with app.app_context():
        query = Log.query
        if days_old is not None:
            cutoff_date = datetime.utcnow() - timedelta(days=days_old)
            query = query.filter(Log.timestamp < cutoff_date)
        if log_type is not None:
            query = query.filter_by(type=log_type)
        if user_id is not None:
            query = query.filter_by(user_id=user_id)
        count = query.delete()
        db.session.commit()
        return count

#clear_logs(log_type="Send mail")
def get_users(role=None, include_deleted=False):
    with app.app_context():
        query = User.query
        if not include_deleted:
            query = query.filter_by(is_deleted=False)
        if role:
            query = query.filter_by(role=role)
        users = query.all()
        return [
            {
                'id': u.id,
                'name': u.name,
                'email': u.email,
                'role': u.role
            }
            for u in users
        ]

def get_cities():
    with app.app_context():
        cc = City.query.all()
    cc = [x.name for x in cc]
    print(cc)
    return list(cc)

def newlog(u,t,d):
    with app.app_context():
        user = User.query.get(u)
        log = Log(user=user,type=t,description=d)
        print('add log',t,d)
        db.session.add(log)
        db.session.commit()

def subscribe_dict():
    with app.app_context():
        ans = {}
        ms = City.query.all()
        for i in ms:
            s = i.subscribers
            e = []
            for j in s:
                e.append(j.email)
            ans[i.name] = e
    return ans

def subscriptions(u):
    with app.app_context():
        res = []
        c = u.cities
        for cc in c:
            res.append(cc.name)
    return res

def last_mail_log_ts():
    with app.app_context():
        ll = Log.query.filter_by(type='Send mail').order_by(Log.timestamp.desc()).first()
    if ll:
        return ll.timestamp
    return None

def rename_user(old_name: str, new_name: str) -> dict:
    with app.app_context():
        if str(old_name).isdigit():
       		user = User.query.get(int(old_name))
        else:
               	user = User.query.filter_by(name=old_name).first()
        if not user:
            return {'success': False, 'message': f'Пользователь {old_name} не найден'}
        
        if User.query.filter_by(name=new_name).first():
            return {'success': False, 'message': f'Имя {new_name} уже занято'}
        
        old_name_original = user.name
        user.name = new_name
        db.session.commit()

        newlog(user.id, 'Rename', f'Пользователь переименован с {old_name_original} на {new_name}')
        return {'success': True, 'message': f'Пользователь {old_name} успешно переименован в {new_name}'}

def set_new_password(identifier, new_password, identifier_type='id'):
    with app.app_context():
        if identifier_type == 'id':
            user = User.query.get(int(identifier))
        elif identifier_type == 'name':
            user = User.query.filter_by(name=identifier).first()
        elif identifier_type == 'email':
            user = User.query.filter_by(email=identifier).first()
        else:
            return {'success': False, 'message': 'Неверный тип идентификатора'}
        
        if not user:
            return {'success': False, 'message': f'Пользователь не найден по {identifier_type}: {identifier}'}
        
        user.pswd_hash = ghash(new_password)
        db.session.commit()
        
        newlog(user.id, 'Change password', f'Пароль изменён для {user.name}')
        
        return {'success': True, 'message': f'Пароль для {user.name} успешно изменён'}

def add_cities(c):
    with app.app_context():
        for name in c:
            fl = City.query.filter_by(name=name).first()
            if not fl:
                city = City(name=name)
                db.session.add(city)
        db.session.commit()

"""add_cities(["Нижний Новгород", "Владивосток", "Мурманск", "Новосибирск",
    "Красноярск", "Новый Уренгой", "Омск", "Рязань", "Тверь",
    "Якутск", "Краснодар", "Ростов-на-Дону", "Пятигорск", "Иркутск",
    "Киров", "Севастополь", "Челябинск", "Уфа", "Магадан", "Астрахань",
    "Петропавловск-Камчатский", "Воронеж", "Калининград", "Сургут"])"""

#print(get_users())
#print(rename_user(5, 'Круглик МН'))
#print(set_new_password(5,'гагага'))


#print(subscribe_dict())
#print(last_mail_log_ts())
