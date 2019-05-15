import smartbeds.vars as v
from flask import request
from flask import render_template
from flask import session
from flask import redirect
from flask import url_for
from smartbeds.routes import webapi as api
from base64 import b64encode as encoder


@v.app.route('/', methods=['GET'])
def home():
    context = {"page": {"page": 'home'}, "info": get_info(), "title": "Inicio"}
    if context['info']['login']:
        mod_request()
        response, code = api.beds()
        context['beds'] = response.get_json()["beds"]
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
    session.clear()
    return redirect(url_for("home"))


@v.app.route('/bed/<bedname>', methods=['GET'])
def cama(bedname):
    mod_request({"bedname": bedname})
    response, code = api.bed()
    namespace = response.get_json()['namespace']
    context = {'page': {'page': 'bed', 'bedname': bedname, 'namespace': namespace}, 'info': get_info(), "title": bedname}
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
def borrar_cama(bedname):
    mod_request()  # Introducimos el token
    return api.beddel()

@v.app.route('/bed/perm', methods=['PUT'])
def permisos_cama():
    mod_request()
    print(request.form)
    return api.bedperm()


@v.app.route('/beds', methods=['GET'])
def camas():
    context = {"page": {"page": 'admin_beds'}, "info": get_info(), "title": "Administrar camas"}
    mod_request({"mode": "info"})
    response, code = api.beds()
    #Lista de camas
    context['beds'] = response.get_json()["beds"]
    response, code = api.users()
    #Lista de usuarios
    context['users'] = response.get_json()["users"]
    #Lista de permisos
    response, code = api.bedperm()
    context['perm'] = response.get_json()["permission"]
    return render_template('camas.html', **context)


def error(code, message):
    return render_template('error.html',
                           code=code,
                           message=message,
                           info=get_info(),
                           title="Error "+str(code))


def get_info():
    if 'token' in session:
        try:
            return {"login": True, "role": session['role'], "user": session['username']}
        except KeyError:
            return {"login": False}
    else:
        return {"login": False}


def mod_request(params=None):
    data = dict(request.form)
    data['token'] = session['token']
    if params is not None:
        for p in params:
            data[p] = params[p]
    request.form = data  # Técnicamente esta operación no es legal, pero funciona


def b64encode(text):
    text = str.encode(text)
    based = encoder(text).decode('utf-8')
    return based


v.app.add_template_filter(b64encode)
