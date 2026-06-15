import os
import sys
from pathlib import Path

if os.getenv('INSIDE_DOCKER') == '1':
    from start import *
else:
    root = Path(__file__).resolve().parents[2]
    sys.path.insert(0, str(root))
    from web.backend.start import *

subscribes = db.Table('subscribes',
                     db.Column('user_id',db.Integer, db.ForeignKey('users.id',ondelete='CASCADE'),primary_key=True),
                     db.Column('city_id',db.Integer, db.ForeignKey('cities.id',ondelete='CASCADE'),primary_key=True))

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    email = db.Column(db.String(100), nullable=False, unique=True)
    pswd_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), nullable=False, default='USER')
    cities = db.relationship('City', secondary='subscribes', backref='subscribers')
    is_deleted = db.Column(db.Boolean, nullable=False, default=False)

class Log(db.Model):
    __tablename__ = 'logs'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    user = db.relationship('User', backref=db.backref('logs', lazy='dynamic'))
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, index=True)
    type = db.Column(db.String(20), nullable=False, default='INFO', index=True)
    description = db.Column(db.Text, nullable=True)
    __table_args__ = (
        db.Index('ix_log_user_timestamp', 'user_id', 'timestamp'),
        db.Index('ix_log_type_timestamp', 'type', 'timestamp'),
    )

class City(db.Model):
    __tablename__ = 'cities'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)

def present_user(c):
    return {
        'id': c.id,
        'name': c.name,
        'email': c.email,
        'role': c.role,
    }

def ghash(p):
    return bcrypt.generate_password_hash(p).decode('utf-8')

def check_hash(p,h):
    return bcrypt.check_password_hash(p,h)

