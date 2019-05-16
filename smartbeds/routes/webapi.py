from smartbeds.api import api
import smartbeds.vars as v
from flask import request
from flask import jsonify

_api: api.API = api.API.get_instance()


@v.app.teardown_appcontext
def teardown_db(_):
    if v.db is not None:
        v.db.close()
        v.db = None


@v.app.route("/api/auth", methods=['GET', 'POST'])
def auth():

    def func(response):
        user = request.form["user"]
        password = request.form['pass']
        token, nick, role = _api.auth(user, password)
        response['token'] = token
        response['role'] = role
        response['username'] = nick

    return make_response(func)


@v.app.route("/api/beds", methods=['GET', 'POST'])
def beds():

    def func(response):
        token = request.form['token']
        response['beds'] = _api.beds(token)

    return make_response(func)


@v.app.route("/api/bed", methods=['GET', 'POST'])
def bed():

    def func(response):
        token = request.form['token']
        bedname = request.form['bedname']
        response['namespace'] = _api.bed(token, bedname)

    return make_response(func)


@v.app.route("/api/users", methods=['GET', 'POST'])
def users():
    
    def func(response):
        token = request.form['token']
        response['users'] = _api.users(token)

    return make_response(func)


@v.app.route("/api/user/add", methods=['GET', 'POST'])
def useradd():
    
    def func(response):
        token = request.form['token']
        username = request.form['username']
        password = request.form['password']
        password_re = request.form['password-re']
        if password != password_re:
            raise KeyError("Las contraseñas no coinciden")
        _api.useradd(token, username, password)

    return make_response(func)


@v.app.route("/api/user/mod", methods=['GET', 'POST'])
def usermod():
    
    def func(response):
        token = request.form['token']
        username = request.form['username']
        password = request.form['password']
        password_re = request.form['password-re']
        password_old = None
        if "password-old" in request.form:
            password_old = request.form['password-old']
        if password != password_re:
            raise KeyError("Las contraseñas no coinciden")
        _api.usermod(token, username, password, password_old)

    return make_response(func)


@v.app.route("/api/user/del", methods=['GET', 'POST'])
def userdel():
    
    def func(response):
        token = request.form['token']
        username = request.form['username']

        _api.userdel(token, username)

    return make_response(func)
    

@v.app.route("/api/bed/add", methods=['GET', 'POST'])
def bedadd():
    
    def func(response):
        token = request.form['token']
        params = request.form
        params.pop('token')

        if v.version < 1:
            raise api.SmartBedError("La creación de camas no está disponible para esta versión")
        else:
            _api.bedadd(token, params)
        
    return make_response(func)


@v.app.route("/api/bed/mod", methods=['GET', 'POST'])
def bedmod():

    def func(response):
        token = request.form['token']
        params = request.form
        params.pop('token')

        if v.version < 1:
            raise api.SmartBedError("La modificación de camas no está disponible para esta versión")
        else:
            _api.bedmod(token, params)
        
    return make_response(func)


@v.app.route("/api/bed/del", methods=['GET', 'POST'])
def beddel():

    def func(response):
        token = request.form['token']
        bedname = response.form['bed_name']

        if v.version < 1:
            raise api.SmartBedError("La eliminación de camas no está disponible para esta versión")
        else:
            _api.beddel(token, bedname)

    return make_response(func)


@v.app.route("/api/bed/perm", methods=['GET', 'POST'])
def bedperm():
    def func(response):
        token = request.form['token']
        mode = request.form['mode']

        if mode == 'info':
            response['permission'] = _api.bedgetperm(token)
        elif mode == 'change':
            bedname = request.form['bed_name']
            username = request.form['username']
            _api.bedmodperm(token, bedname, username)
        else:
            raise api.SmartBedError("Modo no válido")

    return make_response(func)


@v.app.errorhandler(404)
def notfound(e):
    response = dict()
    response['status'] = 404
    response['message'] = "Procedure Not Found"
    return jsonify(response), response['status']


def make_response(func):
    response = basic_response()
    error = None
    try:
        func(response)
    except api.BadCredentialsError as err:
        error = err
        response['status'] = 401
    except (api.PermissionsError, api.IllegalOperationError) as err:
        error = err
        response['status'] = 403
    except (KeyError, api.SmartBedError) as err:
        error = err
        response['status'] = 400
    except Exception as err:
        error = err
        response['status'] = 500
        raise

    if error is not None:
        response['message'] = str(error)

    return jsonify(response), response['status']


def basic_response() -> dict:
    response = dict()
    response['status'] = 200
    response['message'] = "OK"
    return response
