from smartbeds import app
from flask import request
from flask import render_template
from flask import session
from flask import redirect
from flask import url_for
from smartbeds.routes import webapi as api
from smartbeds import TEMPLATE_DIR


@app.route('/', methods=['GET'])
def home():
    page = {"page": 'home'}
    info = get_info()
    #return TEMPLATE_DIR
    return render_template('home.html', page=page, info=info)


@app.route('/auth', methods=['GET', 'POST'])
def login():
    page = {"page": 'login', "bad": False}
    info = get_info()
    if request.method == "POST":
        response, code = api.auth()
        if code == 200:
            session['token'] = response.get_json()['token']
            return redirect(url_for("home"))
        page['nick'] = request.form['user']
        page['bad'] = True
        return render_template('auth/login.html', page=page, info=info)
    else:
        return render_template('auth/login.html', page=page, info=info)

@app.route('/logout', methods=['GET'])
def logout():
    session.pop("token")
    return redirect(url_for("home"))

@app.route('/bed')
def cama():
    context = {'page': {'page': 'bed'}, 'info': get_info()}
    return render_template('cama.html', **context)

def get_info():
    if 'token' in session:
        return {"login": True}
    else:
        return {"login": False}
