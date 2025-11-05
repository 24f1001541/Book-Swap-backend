from flask import Flask, redirect, url_for, session, request
from authlib.integrations.flask_client import OAuth
from dotenv import load_dotenv
import os

load_dotenv()

app = Flask(__name__)
app.secret_key = "my_super_secret_flask_key_2025"
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
app.config['SESSION_COOKIE_SECURE'] = False

oauth = OAuth(app)

# ✅ Use correct metadata and domain
oauth.register(
    name='cognito',
    client_id='4reaubt2s2r3qifnunm4aqlug6',
    client_secret='1rmja0sjqh4o6tefq72frdfkaptp9l7t3ucq8ml0pd50agoeolfv',
    server_metadata_url='https://cognito-idp.eu-north-1.amazonaws.com/eu-north-1_Ns7ux0ggM/.well-known/openid-configuration',
    client_kwargs={'scope': 'openid email phone profile'}
)

@app.route('/')
def index():
    user = session.get('user')
    if user:
        return f"👋 Hello, {user['email']}! <a href='/logout'>Logout</a>"
    return '<a href="/login">Login with Cognito</a>'

@app.route('/login')
def login():
    redirect_uri = url_for('authorize', _external=True)
    print("Redirect URI:", redirect_uri)
    return oauth.cognito.authorize_redirect(redirect_uri)

@app.route('/authorize')
def authorize():
    token = oauth.cognito.authorize_access_token()
    user = token['userinfo']
    session['user'] = user
    return redirect(url_for('index'))

@app.route('/logout')
def logout():
    session.pop('user', None)
    cognito_domain = "https://eu-north-1ns7ux0ggm.auth.eu-north-1.amazoncognito.com"
    return redirect(f"{cognito_domain}/logout?client_id=4reaubt2s2r3qifnunm4aqlug6&logout_uri=http://localhost:5000/")

if __name__ == '__main__':
    app.run(debug=True, port=5000)
