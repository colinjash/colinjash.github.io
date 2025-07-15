from flask import Flask, render_template_string, request, redirect, url_for, session, jsonify
import json
import os

app = Flask(__name__)
app.secret_key = 'your_super_secret_key_here'  # CHANGE THIS!

CONFIG_PATH = '/home/pi/camera_config.json'
LATEST_IMAGE_PATH = '/home/pi/latest.jpg'  # Path to latest image
USERNAME = 'admin'            # Change these!
PASSWORD = 'your_password'    # Change these!

# Default config for first run
DEFAULT_CONFIG = {
    'brightness': 50,
    'exposure_comp': 0.0,
    'contrast': 0,
    'sharpness': 0,
    'saturation': 0,
    'zoom': [0.0, 0.0, 1.0, 1.0],
    'ai_enhance': False
}

def load_config():
    if os.path.exists(CONFIG_PATH):
        try:
            with open(CONFIG_PATH, 'r') as f:
                config = json.load(f)
                # Ensure all keys are present
                for k, v in DEFAULT_CONFIG.items():
                    if k not in config:
                        config[k] = v
                return config
        except Exception as e:
            print("Error loading config:", e)
    return DEFAULT_CONFIG.copy()

def save_config(config):
    with open(CONFIG_PATH, 'w') as f:
        json.dump(config, f, indent=2)

def is_logged_in():
    return session.get('logged_in', False)

def login_required(func):
    from functools import wraps
    @wraps(func)
    def wrapper(*args, **kwargs):
        if not is_logged_in():
            return redirect(url_for('login'))
        return func(*args, **kwargs)
    return wrapper

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        username = request.form.get('username', '')
        password = request.form.get('password', '')
        if username == USERNAME and password == PASSWORD:
            session['logged_in'] = True
            return redirect(url_for('settings'))
        else:
            error = "Invalid username or password."
    return render_template_string(LOGIN_HTML, error=error)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/', methods=['GET', 'POST'])
@login_required
def settings():
    config = load_config()
    message = None
    if request.method == 'POST':
        try:
            config['brightness'] = int(request.form['brightness'])
            config['exposure_comp'] = float(request.form['exposure_comp'])
            config['contrast'] = int(request.form['contrast'])
            config['sharpness'] = int(request.form['sharpness'])
            config['saturation'] = int(request.form['saturation'])
            config['zoom'] = [
                float(request.form['zoom_x']),
                float(request.form['zoom_y']),
                float(request.form['zoom_w']),
                float(request.form['zoom_h'])
            ]
            config['ai_enhance'] = 'ai_enhance' in request.form
            save_config(config)
            message = "Settings updated!"
        except Exception as e:
            message = f"Error saving settings: {e}"

    # Construct image URL with timestamp to avoid caching
    image_url = "/latest.jpg?ts=" + str(int(os.path.getmtime(LATEST_IMAGE_PATH))) if os.path.exists(LATEST_IMAGE_PATH) else ""

    return render_template_string(SETTINGS_HTML, config=config, message=message, image_url=image_url)

@app.route('/latest.jpg')
@login_required
def latest_image():
    # Serve the latest image file securely
    from flask import send_file
    if os.path.exists(LATEST_IMAGE_PATH):
        return send_file(LATEST_IMAGE_PATH, mimetype='image/jpeg')
    return "Image not found", 404

# Optional: an API endpoint for feedback from frontend if needed
@app.route('/api/feedback', methods=['POST'])
def api_feedback():
    data = request.json
    print(f"Feedback received: {data}")
    # You could save feedback to a file or DB here
    return jsonify({"message": "Thanks for your feedback!"})

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
    max-width: 430px;
    width: 100%;
    text-align: center;
  }
  h2 {
    letter-spacing: 0.08em;
    text-transform: uppercase;
    font-size: 2rem;
    margin-bottom: 1.8rem;
    color: #a3cdfd;
    text-shadow: 0 0 6px #3f9eff99;
  }
  form {
    display: flex;
    flex-direction: column;
    gap: 1.3rem;
    align-items: center;
  }
  .slider-group {
    width: 100%;
    margin-bottom: 0.7rem;
  }
  label {
    display: block;
    margin-bottom: 0.35rem;
    color: #8ab4f8;
    font-size: 1.08rem;
    letter-spacing: 0.01em;
    font-weight: 500;
    text-align: left;
  }
  input[type="range"] {
    width: 85%;
    margin: 0.3rem 0;
    accent-color: #4299e1;
  }
  .slider-value {
    display: inline-block;
    min-width: 2.2em;
    text-align: right;
    margin-left: 0.6em;
    color: #51ffb0;
    font-weight: 700;
    font-size: 1.07rem;
  }
  .zoom-group {
    display: flex;
    flex-direction: row;
    gap: 0.35rem;
    margin-top: 0.3rem;
    justify-content: center;
    align-items: center;
  }
  .zoom-label {
    width: 3.2em;
    color: #8ab4f8;
    font-size: 1.01rem;
    font-weight: 500;
    text-align: right;
  }
  input[type="number"].zoom-input {
    width: 3.6em;
    padding: 0.
