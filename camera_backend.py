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
<html lang="en">
<head>
<meta charset="UTF-8">
<title>Camera Admin Login</title>
<meta name="viewport" content="width=device-width, initial-scale=1" />
<style>
  @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@400;700&display=swap');
  body {
    background: linear-gradient(135deg, #0f2027, #203a43, #2c5364);
    color: #e0e7ff;
    font-family: 'Montserrat', sans-serif;
    display: flex;
    flex-direction: column;
    min-height: 100vh;
    align-items: center;
    justify-content: center;
    margin: 0;
  }
  .login-container {
    background: rgba(40,60,80,0.95);
    border-radius: 1.2rem;
    box-shadow: 0 0 40px #1e90ff55, 0 0 0.5rem #27374a77;
    padding: 2.5rem 2rem 2rem 2rem;
    margin-top: 4rem;
    max-width: 340px;
    width: 100%;
    text-align: center;
  }
  h2 {
    letter-spacing: 0.08em;
    text-transform: uppercase;
    font-size: 2rem;
    margin-bottom: 2rem;
    color: #a3cdfd;
    text-shadow: 0 0 6px #3f9eff99;
  }
  input[type="text"], input[type="password"] {
    width: 90%;
    padding: 0.7rem 1rem;
    border-radius: 0.7rem;
    border: none;
    background: #14233a;
    color: #e0e7ff;
    font-size: 1.1rem;
    margin-bottom: 1.3rem;
    transition: box-shadow 0.2s;
    box-shadow: 0 0 0 #4b9fff00;
  }
  input[type="text"]:focus, input[type="password"]:focus {
    outline: none;
    box-shadow: 0 0 10px #46a2ff55;
  }
  input[type="submit"] {
    background: linear-gradient(90deg, #63b3ed, #4299e1 60%, #3182ce);
    color: #fff;
    border: none;
    border-radius: 0.7rem;
    font-size: 1.1rem;
    padding: 0.7rem 2.1rem;
    margin-top: 0.5rem;
    cursor: pointer;
    font-weight: 700;
    letter-spacing: 0.05em;
    box-shadow: 0 3px 15px #1e90ff33;
    transition: background 0.2s, box-shadow 0.2s;
  }
  input[type="submit"]:hover {
    background: linear-gradient(90deg, #4299e1, #3182ce 80%);
    box-shadow: 0 6px 25px #1e90ff66;
  }
  .error {
    color: #ff6b81;
    background: #2f2329cc;
    border-radius: 0.5rem;
    padding: 0.5rem 1rem;
    margin-bottom: 1rem;
    font-weight: 600;
    letter-spacing: 0.03em;
  }
</style>
</head>
<body>
<div class="login-container">
    <h2>Admin Login</h2>
    {% if error %}<div class="error">{{ error }}</div>{% endif %}
    <form method="post" autocomplete="off">
        <input name="username" type="text" placeholder="Username" required autofocus><br>
        <input name="password" type="password" placeholder="Password" required><br>
        <input type="submit" value="Log In">
    </form>
</div>
</body>
</html>
'''


SETTINGS_HTML = '''
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>Camera Control Panel</title>
<meta name="viewport" content="width=device-width, initial-scale=1" />
<style>
  @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@400;700&display=swap');
  body {
    background: linear-gradient(120deg, #373B44 0%, #4286f4 100%);
    color: #e0e7ff;
    font-family: 'Montserrat', sans-serif;
    margin: 0;
    min-height: 100vh;
    display: flex;
    flex-direction: column;
    align-items: center;
  }
  .panel-container {
    background: rgba(40,60,80,0.97);
    border-radius: 1.5rem;
    box-shadow: 0 0 40px #1e90ff66, 0 0 1.5rem #27374a44;
    padding: 2.5rem 2rem 2rem 2rem;
    margin-top: 3.5rem;
    max-width: 410px;
    width: 100%;
    text-align: center;
  }
  h2 {
    letter-spacing: 0.08em;
    text-transform: uppercase;
    font-size: 2rem;
    margin-bottom: 2rem;
    color: #a3cdfd;
    text-shadow: 0 0 6px #3f9eff99;
  }
  form {
    display: flex;
    flex-direction: column;
    gap: 1.1rem;
    align-items: center;
  }
  label {
    display: block;
    margin-bottom: 0.3rem;
    color: #8ab4f8;
    font-size: 1.09rem;
    letter-spacing: 0.01em;
    font-weight: 500;
  }
  input[type="number"], select {
    padding: 0.6rem 1rem;
    border-radius: 0.7rem;
    border: none;
    background: #14233a;
    color: #e0e7ff;
    font-size: 1.1rem;
    margin-bottom: 0.1rem;
    width: 80%;
    box-sizing: border-box;
    transition: box-shadow 0.2s;
    box-shadow: 0 0 0 #4b9fff00;
  }
  input[type="number"]:focus, select:focus {
    outline: none;
    box-shadow: 0 0 10px #46a2ff55;
  }
  input[type="submit"] {
    background: linear-gradient(90deg, #63b3ed, #4299e1 60%, #3182ce);
    color: #fff;
    border: none;
    border-radius: 0.7rem;
    font-size: 1.11rem;
    padding: 0.7rem 2.1rem;
    margin-top: 0.6rem;
    cursor: pointer;
    font-weight: 700;
    letter-spacing: 0.05em;
    box-shadow: 0 3px 15px #1e90ff33;
    transition: background 0.2s, box-shadow 0.2s;
  }
  input[type="submit"]:hover {
    background: linear-gradient(90deg, #4299e1, #3182ce 80%);
    box-shadow: 0 6px 25px #1e90ff66;
  }
  .message {
    color: #51ffb0;
    background: #1d2b3aee;
    border-radius: 0.5rem;
    padding: 0.5rem 1rem;
    margin-bottom: 1.2rem;
    font-weight: 600;
    letter-spacing: 0.03em;
  }
  .logout-link {
    margin-top: 2rem;
    color: #a3cdfd;
    text-decoration: none;
    font-weight: 500;
    letter-spacing: 0.03em;
    font-size: 1.07rem;
    transition: color 0.2s;
    display: inline-block;
  }
  .logout-link:hover {
    color: #d1e9ff;
    text-decoration: underline;
  }
</style>
</head>
<body>
  <div class="panel-container">
    <h2>Camera Control</h2>
    {% if message %}<div class="message">{{ message }}</div>{% endif %}
    <form method="post">
      <div>
        <label for="brightness">Brightness (0-100):</label>
        <input name="brightness" id="brightness" type="number" min="0" max="100" value="{{ config['brightness'] }}">
      </div>
      <div>
        <label for="exposure_mode">Exposure Mode:</label>
        <select name="exposure_mode" id="exposure_mode">
          {% for mode in ['auto','night','backlight','spotlight','sports','snow','beach','verylong','fixedfps','antishake','fireworks'] %}
          <option value="{{mode}}" {% if config['exposure_mode']==mode %}selected{% endif %}>{{mode}}</option>
          {% endfor %}
        </select>
      </div>
      <div>
        <label>Zoom (x, y, w, h):</label>
        <input name="zoom_x" type="number" step="0.01" min="0" max="1" value="{{ config['zoom'][0] }}" style="width:22%">
        <input name="zoom_y" type="number" step="0.01" min="0" max="1" value="{{ config['zoom'][1] }}" style="width:22%">
        <input name="zoom_w" type="number" step="0.01" min="0.01" max="1" value="{{ config['zoom'][2] }}" style="width:22%">
        <input name="zoom_h" type="number" step="0.01" min="0.01" max="1" value="{{ config['zoom'][3] }}" style="width:22%">
      </div>
      <input type="submit" value="Update">
    </form>
    <a class="logout-link" href="{{ url_for('logout') }}">Logout</a>
  </div>
</body>
</html>
'''

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
