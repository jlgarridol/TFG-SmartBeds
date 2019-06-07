import smartbeds.vars as v
from flask import (request, render_template, redirect, url_for)
from flask_login import (login_user, logout_user, login_required, current_user)
from smartbeds.routes import webapi as api
from smartbeds.api import api as _api
from smartbeds.routes import user_loader
from base64 import b64encode as encoder
from smartbeds import utils


@v.app.route('/', methods=['GET'])
def home():
    context = {"page": {"page": 'home'}, "info": get_info(), "title": "Inicio"}
    if context['info']['login']:
        mod_request()
        response, code = api.beds()
        context['beds'] = response.get_json()["beds"]
        try:
            for b in context['beds']:
                mod_request({"bedname": b["bed_name"]})
                b['namespace'] = api.bed()[0].get_json()['namespace']
        except KeyError:
            return logout()
    return render_template('home.html', **context)


@v.app.route('/auth', methods=['GET', 'POST'])
def login():
    context = {"page": {"page": 'login', "bad": False}, "info": get_info(), "title": "Iniciar Sesión"}
    if request.method == "POST":
        response, code = api.auth()
        if code == 200:
            response_json = response.get_json()
            login_user(user_loader(response_json['token']))
            return redirect(url_for("home"))
        context["page"]['nick'] = request.form['user']
        context["page"]['bad'] = True
        return render_template('auth/login.html', **context)
    else:
        return render_template('auth/login.html', **context)


@v.app.route('/logout', methods=['GET'])
@login_required
def logout():
    logout_user()
    return redirect(url_for("home"))


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
def modifica_cama():
    mod_request()  # Introducimos el token
    return api.bedmod()


@v.app.route('/bed/add', methods=['PUT'])
def nueva_cama():
    mod_request()  # Introducimos el token
    return api.bedadd()


@v.app.route('/bed/del', methods=['DELETE'])
def borrar_cama():
    mod_request()  # Introducimos el token
    return api.beddel()


@v.app.route('/bed/perm', methods=['PUT'])
def permisos_cama():
    mod_request()
    return api.bedperm()


@v.app.route('/users', methods=['GET'])
def usuarios():
    mod_request()
    context = {"page": {"page": 'admin_users'}, "info": get_info(), "title": "Administrar usuarios"}
    response, code = api.users()
    if code != 200:
        return error(code, response.get_json()['message'])
    context["users"] = response.get_json()['users']
    return render_template('usuarios.html', **context)


@v.app.route('/user', methods=['GET', 'POST'])
@login_required
def usuario_info():
    mod_request()
    info = get_info()
    if info["login"]:
        msg = ""
        if request.method == "POST":
            response, code = api.usermod()
            if code != 200:
                msg = response.get_json()['message']
        context = {"page": {"page": 'own_user'}, "info": info, "title": current_user.get_username(), "message": msg}
        return render_template('usuario.html', **context)
    else:
        return logout()


@v.app.route('/user/add', methods=['PUT'])
def user_add():
    mod_request()
    return api.useradd()


@v.app.route('/user/del', methods=['DELETE'])
def user_del():
    mod_request()
    return api.userdel()


@v.app.route('/user/mod', methods=['PUT'])
def user_mod():
    mod_request()
    return api.usermod()


@v.app.route('/beds', methods=['GET'])
def camas():
    context = {"page": {"page": 'admin_beds'}, "info": get_info(), "title": "Administrar camas"}
    mod_request({"mode": "info"})
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


@v.app.route('/generate_user', methods=['GET'])
def user_gen():
    context = {"page": {"page": "generator"}, "info": get_info(), "title": "Generador de usuarios"}
    API = _api.API.get_instance()
    tkn = utils.get_secret_key()
    user = "user"
    password = "123456"
    API.useradd(tkn)


def error(code, message):
    return render_template('error.html',
                           page={"page": "none"},
                           code=code,
                           message=message,
                           info=get_info(),
                           title="Error " + str(code))


def get_info():
    if current_user is not None and current_user.is_authenticated:
        try:
            return {"login": True, "role": current_user.get_role(), "user": current_user.get_username()}
        except KeyError:
            return {"login": False}
    else:
        return {"login": False}


def mod_request(params=None):
    data = dict(request.form)
    data['token'] = current_user.get_token()

    if params is not None:
        for p in params:
            data[p] = params[p]
    request.form = data  # Técnicamente esta operación no es legal, pero funciona


def b64encode(text):
    text = str.encode(text)
    based = encoder(text).decode('utf-8')
    return based


v.app.add_template_filter(b64encode)
