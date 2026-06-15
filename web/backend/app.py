from use_bd import *

def get_data(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No input data'}), 433
        return func(data,*args,**kwargs)
    return wrapper

def get_user(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        auth_header = request.headers.get('Authorization')
        if not auth_header:
            return jsonify({'error': 'Missing token'}), 433
        try:
            token = auth_header.split(' ')[1]
            payload = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
            u_id = payload['user']
        except (IndexError, jwt.InvalidTokenError, KeyError):
            return jsonify({'error': 'Invalid token'}), 433

        u = User.query.get(u_id)
        if not u:
            return jsonify({'error': 'Access denied'}), 431
        return func(u,*args,**kwargs)
    return wrapper


def check_invite(invite):
    if invite == os.environ['ADMIN_KEY']:
        return True
    return False

@app.route('/api/reg', methods=['POST'])
@get_data
def reg(data):
    login = data.get('name')
    email = data.get('email')
    pswd = data.get('password')
    invite = data.get('invite')
    if not login or not pswd or not email:
        return jsonify({'error': 'No correct data'}), 433
    if User.query.filter_by(name=login).first() or User.query.filter_by(email=email).first():
        return jsonify({'error': 'User already exists'}), 437
    if login.isdigit():
        return jsonify({'error': 'Username must be string'}), 433
    if invite:
        if check_invite(invite):
            user = User(name=login, email=email, pswd_hash=ghash(pswd), role = 'ADMIN')
        else:
            return jsonify({'error': 'Incorrect invite'}), 433
    else:
        user = User(name=login, email=email, pswd_hash=ghash(pswd))
    db.session.add(user)
    db.session.flush()
    log = Log(user_id=user.id,type='Registration',description=f'User {login} registered')
    db.session.add(log)
    db.session.commit()
    u = user
    token = jwt.encode({'user': u.id, 'time': datetime.now().isoformat()}, app.config['SECRET_KEY'], algorithm='HS256')
    return jsonify({'token': token, 'role':u.role})

@app.route('/api/login', methods=['POST'])
@get_data
def login(data):
    uname = data['name']
    pswd = data['password']
    u = User.query.filter_by(name=uname).first()
    if not u:
        u = User.query.filter_by(email=uname).first()
    if not u or not check_hash(u.pswd_hash, pswd):
        return jsonify({'error': 'Wrong login/password'}), 431
    log = Log(user_id=u.id, type='Login', description=f'User {u.name} signed in successfully')
    db.session.add(log)
    db.session.commit()
    token = jwt.encode({'user':u.id, 'time':datetime.now().isoformat()},app.config['SECRET_KEY'], algorithm='HS256')
    return jsonify({'token': token, 'role':u.role})

@app.route('/api/logs', methods=['GET'])
@get_user
def get_logs(u):
    if u.role == 'USER':
        return jsonify({'error': 'Access denied'}), 431

    uu = request.args.get('user')
    lt = request.args.get('type')
    ns = request.args.get('nosystem')

    query = Log.query

    if uu is not None:
        if uu.isdigit():
            # передан id
            user_id = int(uu)
            user_obj = User.query.get(user_id)
            if user_obj:
                query = query.filter_by(user_id=user_id)
            else:
                return jsonify({'logs': []})
        else:
            # передан username
            user_obj = User.query.filter_by(name=uu).first()
            if user_obj:
                query = query.filter_by(user_id=user_obj.id)
            else:
                return jsonify({'logs': []})

    if lt:
        query = query.filter_by(type=lt)

    if ns and ns.lower() == 'true':
        query = query.filter(Log.type.notin_(['Run','Send mail']))

    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 50, type=int)
    logs = query.order_by(Log.timestamp.desc()).paginate(page=page, per_page=per_page, error_out=False)

    res = []
    for log in logs.items:
        res.append({
        'timestamp': log.timestamp.isoformat() + 'Z',
        'user': log.user.name if log.user else None,
        'type': log.type,
        'message': log.description
    })

    return jsonify({
        'logs': res,
        'total': logs.total,
        'page': logs.page,
        'per_page': logs.per_page,
        'pages': logs.pages
    })

@app.route('/api/subscribe', methods=['GET'])
@get_user
def subscribes(u):
    if u.role != 'USER' and request.args.get('user'):
        u = User.query.get(request.args.get('user'))
    sub = subscriptions(u)
    return jsonify({"subscriptions":  sub})

@app.route('/api/subscribe', methods=['POST'])
@get_data
@get_user
def add_subscribe(u,data):
    uu = data.get('user')
    if u.role != 'USER' and uu:
        u = User.query.get(uu)
    c = data.get('city')
    if not c:
        return jsonify({'error': 'Missing city'}), 433
    c = City.query.filter_by(name=c).first()
    if not c:
        return jsonify({'error': 'City not found'}), 439
    if u in c.subscribers:
        return jsonify({'error': 'Subscribe already exists'}), 437
    c.subscribers.append(u)
    db.session.add(c)
    db.session.commit()
    newlog(u.id,'Add subscribe','Добавлена подписка на город '+c.name)

    sub = subscriptions(u)
    return jsonify({"subscriptions":  sub})


@app.route('/api/subscribe', methods=['DELETE'])
@get_data
@get_user
def del_subscribe(u,data):
    uu = data.get('user')
    if u.role != 'USER' and uu:
        u = User.query.get(uu)
    c = data.get('city')
    if not c:
        return jsonify({'error': 'Missing city'}), 433
    c = City.query.filter_by(name=c).first()
    if not c:
        return jsonify({'error': 'City not found'}), 439
    if u not in c.subscribers:
        return jsonify({'error': 'Subscribe not exist'}), 437
    c.subscribers.remove(u)
    db.session.add(c)
    db.session.commit()

    sub = subscriptions(u)
    newlog(u.id,'Delete subscribe','Отменена подписка на город '+c.name)
    return jsonify({"subscriptions":  sub})

@app.route('/api/stat',methods=['GET'])
@get_user
def stat(u):
    t = request.args.get('type')
    c = request.args.get('city')
    if not c or not t or '/' in t or '/' in c or '.' in c or '.' in t:
        return jsonify({'error': 'Missing city or type'}), 433
    path = '../frontend/public/graphs/'+t+'_'+c+'.png'
    mod_ts = os.path.getmtime(path)
    mod_dt = datetime.fromtimestamp(mod_ts)
    now = datetime.now()
    delta = now - mod_dt
    days = delta.days
    qf = open('../../analys/status.txt','r')
    q = int(qf.read())
    qf.close()
    days = 0
    #print((not q or q != 1) and days >= 1)
    if (not q or q != 1) and days >= 1:
        print(q)
        run_script = os.path.join(os.path.dirname(__file__), '../../analys/run.py')
        try:
            subprocess.run(['python', run_script], check=True, capture_output=True, text=True)
            print("run.py выполнен успешно")
        except subprocess.CalledProcessError as e:
            print(f"Ошибка выполнения run.py: {e.stderr}")
    if not os.path.exists(path):
        return jsonify({'error': 'Incorrect city or type'}), 433
    if c != 'all':
        newlog(u.id,'stat','Получен график '+t+' для города '+c)
    else:
        newlog(u.id,'stat','Получен усреднённый график '+t)
    return jsonify({'graph_url':t+'_'+c+'.png'})

@app.route('/api/cities',methods=['GET'])
def get_c():
    return jsonify(get_cities())

