from flask import (session, request, redirect, url_for, copy_current_request_context)
from smartbeds import utils
from base64 import b64encode as encoder


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