from flask import Flask, render_template_string, request, redirect, url_for, session
import json
import os

CONFIG_PATH = '/home/pi/camera_config.json'
SECRET_KEY = 'change_this_to_a_random_secret'
USERNAME = 'admin'
PASSWORD = 'your_strong_password'  # Change this!

app = Flask(__name__)
app.secret_key = SECRET_KEY

def get_config():
    if os.path.exists(CONFIG_PATH):
        with open(CONFIG_PATH) as f:
            return json.load(f)
    # fallback defaults
    return {
        "brightness": 0.5,
        "exposure_time": None,
        "analogue_gain": None,
        "zoom": [0.0, 0.0, 1.0, 1.0]
    }

def set_config(cfg):
    with open(CONFIG_PATH, 'w') as f:
        json.dump(cfg, f)

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        if request.form['username'] == USERNAME and request.form['password'] == PASSWORD:
            session['logged_in'] = True
            return redirect(url_for('settings'))
        else:
            error = 'Invalid credentials'
    return render_template_string(LOGIN_HTML, error=error)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/', methods=['GET', 'POST'])
def settings():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    config = get_config()
    message = None
    if request.method == 'POST':
        config['brightness'] = float(request.form['brightness'])
        config['exposure_time'] = int(request.form['exposure_time']) if request.form['exposure_time'] else None
        config['analogue_gain'] = float(request.form['analogue_gain']) if request.form['analogue_gain'] else None
        config['zoom'] = [
            float(request.form['zoom_x']),
            float(request.form['zoom_y']),
            float(request.form['zoom_w']),
            float(request.form['zoom_h'])
        ]
        set_config(config)
        message = "Settings updated!"
    return render_template_string(SETTINGS_HTML, config=config, message=message)

LOGIN_HTML = '''
<!DOCTYPE html>
<html>
<head><title>Login</title></head>
<body>
    <h2>Login</h2>
    {% if error %}<p style="color:red;">{{ error }}</p>{% endif %}
    <form method="post">
        Username: <input name="username" type="text"><br>
        Password: <input name="password" type="password"><br>
        <input type="submit" value="Login">
    </form>
</body>
</html>
'''

SETTINGS_HTML = '''
<!DOCTYPE html>
<html>
<head><title>Camera Settings</title></head>
<body>
    <h2>Camera Settings</h2>
    {% if message %}<p style="color:green;">{{ message }}</p>{% endif %}
    <form method="post">
        Brightness (0.0-1.0): <input name="brightness" type="number" min="0" max="1" step="0.01" value="{{ config['brightness'] }}"><br>
        Exposure Time (μs, blank=auto): <input name="exposure_time" type="number" min="1" step="1" value="{{ config['exposure_time'] or '' }}"><br>
        Analogue Gain (blank=auto): <input name="analogue_gain" type="number" min="0" step="0.01" value="{{ config['analogue_gain'] or '' }}"><br>
        <b>Zoom:</b> <br>
        X: <input name="zoom_x" type="number" min="0" max="1" step="0.01" value="{{ config['zoom'][0] }}"> 
        Y: <input name="zoom_y" type="number" min="0" max="1" step="0.01" value="{{ config['zoom'][1] }}"> 
        W: <input name="zoom_w" type="number" min="0.01" max="1" step="0.01" value="{{ config['zoom'][2] }}">
        H: <input name="zoom_h" type="number" min="0.01" max="1" step="0.01" value="{{ config['zoom'][3] }}"><br>
        <input type="submit" value="Update">
    </form>
    <a href="{{ url_for('logout') }}">Logout</a>
</body>
</html>
'''

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)