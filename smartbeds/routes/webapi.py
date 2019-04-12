from smartbeds.api import api
from smartbeds import app
from flask import request
from json import dumps

_api: api.API = api.API.get_instance()


@app.route("/api/auth", methods=['POST'])
def auth():
    response = basic_response()
    error = None
    try:
        user = request.form["user"]
        password = request.form['pass']
        token = _api.auth(user, password)
        response['token'] = token
    except KeyError as err:
        print(err)
        error = err
        response['status'] = 400
    except api.BadCredentialsError as err:
        error = err
        response['status'] = 401
    except Exception as err:
        error = err
        response['status'] = 500

    if error is not None:
        response['message'] = str(error)

    return dumps(response)


@app.route("/api/beds", methods=["POST"])
def beds():
    response = basic_response()
    error = None
    try:
        token = request.form['token']
        response['beds'] = _api.beds(token)
    except KeyError as err:
        error = err
        response['status'] = 400
    except api.BadCredentialsError as err:
        error = err
        response['status'] = 401
    except Exception as err:
        error = err
        response['status'] = 500

    if error is not None:
        response['message'] = str(error)

    return dumps(response)


@app.route("/api/bed", methods=["POST"])
def bed():
    response = basic_response()
    error = None
    try:
        token = request.form['token']
        bedname = request.form['bedname']
        response['namespace'] = _api.bed(token, bedname)
    except KeyError as err:
        error = err
        response['status'] = 400
    except api.BadCredentialsError as err:
        error = err
        response['status'] = 401
    except api.PermissionsError as err:
        error = err
        response['status'] = 403
    except Exception as err:
        error = err
        response['status'] = 500

    if error is not None:
        response['message'] = str(error)

    return dumps(response)


@app.route("/api/users", methods=["POST"])
def users():
    response = basic_response()
    error = None
    try:
        token = request.form['token']
        response['users'] = _api.users(token)
    except KeyError as err:
        error = err
        response['status'] = 400
    except api.BadCredentialsError as err:
        error = err
        response['status'] = 401
    except api.PermissionsError as err:
        error = err
        response['status'] = 403
    except Exception as err:
        error = err
        response['status'] = 500

    if error is not None:
        response['message'] = str(error)

    return dumps(response)


@app.route("/api/user/add", methods=["POST"])
def useradd():
    response = basic_response()
    error = None
    try:
        token = request.form['token']
        username = request.form['username']
        password = request.form['password']
        password_re = request.form['password-re']
        if password != password_re:
            raise KeyError("Las contraseñas no coinciden")
        _api.useradd(token, username, password)
    except (KeyError, api.UsernameExistsError) as err:
        error = err
        response['status'] = 400
    except api.BadCredentialsError as err:
        error = err
        response['status'] = 401
    except api.PermissionsError as err:
        error = err
        response['status'] = 403
    except Exception as err:
        error = err
        response['status'] = 500

    if error is not None:
        response['message'] = str(error)

    return dumps(response)


@app.route("/api/user/mod", methods=["POST"])
def usermod():
    response = basic_response()
    error = None
    try:
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
    except (KeyError, api.ElementNotExistsError) as err:
        error = err
        response['status'] = 400
    except api.BadCredentialsError as err:
        error = err
        response['status'] = 401
    except (api.PermissionsError, api.IllegalOperationError) as err:
        error = err
        response['status'] = 403
    except Exception as err:
        error = err
        response['status'] = 500

    if error is not None:
        response['message'] = str(error)

    return dumps(response)


@app.route("/api/user/del", methods=["POST"])
def userdel():
    response = basic_response()
    error = None
    try:
        token = request.form['token']
        username = request.form['username']

        _api.userdel(token, username)
    except (KeyError, api.ElementNotExistsError) as err:
        error = err
        response['status'] = 400
    except api.BadCredentialsError as err:
        error = err
        response['status'] = 401
    except (api.PermissionsError, api.IllegalOperationError) as err:
        error = err
        response['status'] = 403
    except Exception as err:
        error = err
        response['status'] = 500

    if error is not None:
        response['message'] = str(error)

    return dumps(response)


def basic_response() -> dict:
    response = dict()
    response['status'] = 200
    response['message'] = "OK"
    return response
