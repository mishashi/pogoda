from flask import *
from flask_migrate import Migrate
from flask_bcrypt import Bcrypt
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from functools import wraps
from sqlalchemy.orm import joinedload
import platform
import subprocess
import jwt
import os
from pathlib import Path
from datetime import *
from dotenv import load_dotenv

root_dir = Path(__file__).parent.parent.parent
load_dotenv(dotenv_path=root_dir / '.env')

app = Flask(__name__)
BASE_DIR = Path(__file__).resolve().parent
DB_DIR = BASE_DIR / 'instance'
DB_DIR.mkdir(exist_ok=True)
DB_PATH = DB_DIR / 'pogoda.db'

app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DB_PATH}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = os.environ['FLASK_KEY']
db = SQLAlchemy(app)
migrate = Migrate(app, db)
bcrypt = Bcrypt(app)
CORS(app)
