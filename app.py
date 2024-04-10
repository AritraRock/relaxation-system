import threading
from flask import Flask, render_template, request, redirect, url_for
from posture_detection import app as dash_app  # Import Dash app instance
from thermal_tracking import app as thermal_app
from eye_motion_tracking import app as eye_app

app = Flask(__name__, template_folder='templates')

# Function to start the server for a given module
def start_server(server_instance, port):
    thread = threading.Thread(target=server_instance.run, kwargs={'host': '127.0.0.1', 'port': port})
    thread.daemon = True
    thread.start()

# Route to serve the index.html page
@app.route('/')
def index():
    return render_template('index.html')

# Route to serve the login page
@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/logout')
def logout():
    # Perform logout action, such as clearing session data
    # For example:
    # session.clear()  # Clear session data if you're using Flask sessions
    # Redirect user to login page or any other desired page
    return redirect(url_for('index'))  # Redirect to index page or login page


# Route to serve the landing page
@app.route('/landing-page')
def landing_page():
    return render_template('landing_page.html')

# Route to start the dashboard server
@app.route('/start-dashboard', methods=['GET', 'POST'])
def start_dashboard():
    if request.method == 'POST':
        start_server(dash_app.server, 8051)
        print("dash_app.server fetched successfully")
        return redirect(url_for('landing_page'))
    else:
        return redirect(url_for('index'))  # Redirect to index if accessed via GET

# Route to start the thermal tracking server
@app.route('/start-thermal', methods=['GET', 'POST'])
def start_thermal():
    if request.method == 'POST':
        start_server(thermal_app.server, 8052)
        print("thermal_app.server fetched successfully")

        return redirect(url_for('landing_page'))
    else:
        return redirect(url_for('index'))

# Route to start the eye tracking server
@app.route('/start-eye', methods=['GET', 'POST'])
def start_eye():
    if request.method == 'POST':
        start_server(eye_app.server, 8053)
        print("eye_app.server fetched successfully")
        return redirect(url_for('landing_page'))
    else:
        return redirect(url_for('index'))

# Route to serve the Dash application
@app.route('/dash-app')
def dash_app_route():
    return dash_app.index()  # Return Dash application index page

# Route to serve the thermal tracking application
@app.route('/thermal-app')
def thermal_app_route():
    return thermal_app.index()  # Return thermal tracking application index page

# Route to serve the eye tracking application
@app.route('/eye-app')
def eye_app_route():
    return eye_app.index()  # Return eye tracking application index page

# Route to handle other URLs
@app.route('/<path:path>')
def other_routes(path):
    return redirect(url_for('index'))  # Redirect to index page for other URLs

if __name__ == '__main__':
    app.run(debug=False,port=5500,host='0.0.0.0')  # You can set debug=False in production
