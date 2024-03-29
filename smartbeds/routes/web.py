import smartbeds.vars as v
from flask import request
from flask import render_template
from flask import session
from flask import redirect
from flask import url_for
from smartbeds.routes import webapi as api
from smartbeds.routes import (garanteed_logged, get_info, mod_request, b64encode, modify_request)
from smartbeds.routes import logout as rlogout


@v.app.route('/', methods=['GET'])
def home():
    context = {"page": {"page": 'home'}, "info": get_info(), "title": "Inicio"}
    if context['info']['login']:
        mod_request()
        response, code = api.beds()
        if code != 200:
            return error(code, response.get_json()['message'])
        context['beds'] = response.get_json()["beds"]
        for b in context['beds']:
            mod_request({"bedname": b["bed_name"]})
            b['namespace'] = api.bed()[0].get_json()['namespace']
    return render_template('home.html', **context)


@v.app.route('/auth', methods=['GET', 'POST'])
def login():
    context = {"page": {"page": 'login', "bad": False}, "info": get_info(), "title": "Iniciar Sesión"}
    if request.method == "POST":
        response, code = api.auth()
        if code == 200:
            response_json = response.get_json()
            session['token'] = response_json['token']
            session['role'] = response_json['role']
            session['username'] = response_json['username']
            return redirect(url_for("home"))
        context["page"]['nick'] = request.form['user']
        context["page"]['bad'] = True
        return render_template('auth/login.html', **context)
    else:
        return render_template('auth/login.html', **context)


@v.app.route('/logout', methods=['GET'])
def logout():
    return rlogout()


@v.app.route('/bed/<bedname>', methods=['GET'])
def cama(bedname):
    mod_request({"bedname": bedname})
    response, code = api.bed()
    if code != 200:
        return error(code, response.get_json()['message'])
    namespace = response.get_json()['namespace']
    context = {'page': {'page': 'bed', 'bedname': bedname, 'namespace': namespace}, 'info': get_info(),
               "title": bedname}
    return render_template('cama.html', **context)


@v.app.route('/bed/mod', methods=['PUT'])
@modify_request
def modifica_cama():
    return api.bedmod()


@v.app.route('/bed/add', methods=['PUT'])
@modify_request
def nueva_cama():
    return api.bedadd()


@v.app.route('/bed/del', methods=['DELETE'])
@modify_request
def borrar_cama():
    return api.beddel()


@v.app.route('/bed/perm', methods=['PUT'])
@modify_request
def permisos_cama():
    return check_login(api.bedperm)


@v.app.route('/users', methods=['GET'])
@modify_request
def usuarios():
    context = {"page": {"page": 'admin_users'}, "info": get_info(), "title": "Administrar usuarios"}
    response, code = api.users()
    if code != 200:
        return error(code, response.get_json()['message'])
    context["users"] = response.get_json()['users']
    return render_template('usuarios.html', **context)


@v.app.route('/user', methods=['GET', 'POST'])
def usuario_info():
    logged = garanteed_logged()
    if logged is None:
        info = get_info()
        msg = "La contraseña se ha actualizado correctamente"
        mode = "default"
        if request.method == "POST":
            response, code = api.usermod()
            if code != 200:
                msg = response.get_json()['message']
                mode = "error"
            else:
                mode = "update"

        context = {"page": {"page": 'own_user',
                            "mode": mode},
                   "info": info,
                   "title": session['username'],
                   "message": msg}
        return render_template('usuario.html', **context)
    else:
        return logged


@v.app.route('/user/add', methods=['PUT'])
@modify_request
def user_add():
    return check_login(api.useradd)


@v.app.route('/user/del', methods=['DELETE'])
@modify_request
def user_del():
    return check_login(api.userdel)


@v.app.route('/user/mod', methods=['PUT'])
@modify_request
def user_mod():
    return check_login(api.usermod)


@v.app.route('/beds', methods=['GET'])
@modify_request(params={"mode": "info"})
def camas():
    context = {"page": {"page": 'admin_beds'}, "info": get_info(), "title": "Administrar camas"}
    response, code = api.beds()
    if code != 200:
        return error(code, response.get_json()['message'])

    # Lista de camas
    context['beds'] = response.get_json()["beds"]
    response, code = api.users()
    # Lista de usuarios
    context['users'] = response.get_json()["users"]
    # Lista de permisos
    response, code = api.bedperm()
    context['perm'] = response.get_json()["permission"]
    return render_template('camas.html', **context)


@v.app.route('/about', methods=['GET'])
def sobre():
    context = {"page": {"page": 'about'}, "info": get_info(), "title": "Acerca de"}
    return render_template('sobre.html', **context)


"""#Código para la generación de usuarios
@v.app.route('/generate_user', methods=['GET'])
def user_gen():
    context = {"page": {"page": "generator"}, "info": get_info(), "title": "Generador de usuarios"}
    API = _api.API.get_instance()
    tkn = utils.get_secret_key()
    v.testusers += 1
    user = "user"+str(v.testusers)
    password = "123456"
    API.useradd(tkn, user, password)
    API.bedmodperm(tkn, "Cama 1", user)
    API.bedmodperm(tkn, "Cama 2", user)

    context["user"] = user
    context["password"] = password
    return render_template("genuser.html", **context)
"""


def error(code, message):
    return render_template('error.html',
                           page={"page": "none"},
                           code=code,
                           message=message,
                           info=get_info(),
                           title="Error " + str(code))


def check_login(func):
    response, code = func()
    if code != 200:
        return error(code, response.get_json()['message'])
    else:
        return response, code


v.app.add_template_filter(b64encode)
