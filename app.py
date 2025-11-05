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

oauth.register(
    name='cognito',
    client_id=os.getenv('COGNITO_CLIENT_ID'),
    client_secret=os.getenv('COGNITO_CLIENT_SECRET'),
    server_metadata_url=os.getenv('COGNITO_METADATA_URL'),
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
    return oauth.cognito.authorize_redirect(redirect_uri)

@app.route('/authorize')
def authorize():
    print("Incoming query params:", request.args)
    token = oauth.cognito.authorize_access_token()
    user = token['userinfo']
    session['user'] = user
    return redirect(url_for('index'))

@app.route('/logout')
def logout():
    session.pop('user', None)
    cognito_domain = os.getenv('COGNITO_DOMAIN')
    return redirect(f"{cognito_domain}/logout?client_id={os.getenv('COGNITO_CLIENT_ID')}&logout_uri=http://localhost:5000/")

if __name__ == '__main__':
    app.run(debug=True, port=5000)
