from flask import (session, request, redirect, url_for, copy_current_request_context)
from smartbeds import utils
from base64 import b64encode as encoder
import functools


def garanteed_logged():
    mod_request()
    info = get_info()
    if not info["login"]:
        return logout()
    else:
        return


def logout():
    session.clear()
    return redirect(url_for("home"))


def get_info():
    if 'token' in session:
        try:
            return {"login": True, "role": session['role'], "user": session['username'], "mode": utils.get_mode()}
        except KeyError:
            return {"login": False, "mode": utils.get_mode()}
    else:
        return {"login": False, "mode": utils.get_mode()}


def modify_request(_func=None, *, params=None, route_params=None):
    def wrapper(func):
        @functools.wraps(func)
        def wrapper_modifier(*args, **kwargs):
            mod_request(params)
            if route_params is None:
                return func()
            else:
                return func(route_params)
        return wrapper_modifier

    if _func is None:
        return wrapper
    else:
        return wrapper(_func)


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