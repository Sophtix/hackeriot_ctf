
# --- Imports ---
import os
import subprocess
import datetime
import threading
import time
import requests
from flask import Flask, render_template, session, redirect, url_for, jsonify, request
from flask_socketio import SocketIO, emit, join_room, leave_room



# --- App Initialization ---
app = Flask(__name__)
app.secret_key = 'replace_this_with_a_secure_random_key'
socketio = SocketIO(app, async_mode='threading', manage_session=False)

# --- WebSocket Events ---

@socketio.on('join_timer')
def handle_join_timer(data):
    """
    Client joins timer updates for their session. Pass expiry as argument.
    """
    sid = request.sid
    join_room(sid)
    # Get expiry from data (sent by client on join)
    expiry_str = data.get('expiry')
    if not expiry_str:
        socketio.emit('time_left', {'expired': True}, to=sid)
        return
    try:
        expiry = datetime.datetime.fromisoformat(expiry_str)
    except Exception:
        socketio.emit('time_left', {'expired': True}, to=sid)
        return
    def send_time_left():
        while True:
            now = datetime.datetime.utcnow()
            expired = now >= expiry
            if expired:
                socketio.emit('time_left', {'expired': True}, to=sid)
                break
            delta = expiry - now
            total_seconds = int(delta.total_seconds())
            hours = total_seconds // 3600
            minutes = (total_seconds % 3600) // 60
            seconds = total_seconds % 60
            if hours:
                time_left_str = f"{hours}:{minutes:02}:{seconds:02}"
            else:
                time_left_str = f"{minutes}:{seconds:02}"
            socketio.emit('time_left', {'time_left': time_left_str, 'expired': False}, to=sid)
            time.sleep(1)
    threading.Thread(target=send_time_left, daemon=True).start()

# --- Error Handlers ---
@app.errorhandler(500)
def internal_error(error):
    """
    Handle 500 Internal Server Error and show a generic error page.
    """
    return render_template("error.html", message="An unexpected error occurred. Please try again later."), 500

@app.errorhandler(404)
def not_found_error(error):
    """
    Handle 404 Not Found Error and show a generic error page.
    """
    return render_template("error.html", message="The requested page was not found."), 404

# --- Config ---
COMPOSE_FILE = "../ctf/docker-compose.yml"
WORKDIR = "../ctf/envs/"
FLAG = "flag{this_is_a_secure_flag}"
os.makedirs(WORKDIR, exist_ok=True)

## --- Utility Functions ---


# Use a global dict to track stack progress by username
import threading as _threading
_stack_progress = {}

def _deploy_stack_async(username):
    """
    Deploy the stack in a background thread and update global progress dict when ready.
    """
    try:
        subprocess.run([
            "docker", "compose",
            "-p", username,
            "-f", COMPOSE_FILE,
            "up", "-d"
        ], check=True)
        host_port = get_kali_host_port(username)
        host_ip = get_public_ip()
        open_firewall_port(host_port)
        # Store connection info in global dict
        _stack_progress[username] = {
            "status": "ready",
            "host_ip": host_ip,
            "host_port": host_port,
            "ssh_username": "root",
            "ssh_password": "root"
        }
    except Exception as e:
        _stack_progress[username] = {"status": "error", "error": str(e)}


def get_public_ip() -> str | None:
    """
    Get the machine's public IP address using an external service (ipify).
    Returns:
        str | None: Public IP as a string, or None if failed.
    """
    try:
        response = requests.get("https://api.ipify.org?format=text", timeout=5)
        response.raise_for_status()
        return response.text.strip()
    except requests.RequestException as e:
        print(f"Error fetching public IP: {e}")
        return None
    

def get_kali_host_port(project_name: str, container_port: int = 22) -> int | None:
    """
    Get the host port bound to the given container port of the 'kali' service for a specific Docker Compose project.
    Args:
        project_name (str): The Docker Compose project name.
        container_port (int): The container port to look up (default: 22).
    Returns:
        int | None: Host port as integer, or None if not found.
    """
    try:
        result = subprocess.run(
            ["docker", "compose", "-p", project_name, "port", "kali", str(container_port)],
            capture_output=True,
            text=True,
            check=True
        )
        output = result.stdout.strip()
        if not output:
            return None
        host_port = output.split(":")[-1]
        return int(host_port)
    except subprocess.CalledProcessError as e:
        print(f"Error running docker compose: {e.stderr}")
        return None
    except ValueError:
        return None
        

def open_firewall_port(port):
    """
    Open a firewall port using ufw.
    Args:
        port (int): Port number to allow.
    """
    subprocess.run(["ufw", "allow", str(port)], check=False)

## --- Routes ---
@app.route("/", methods=["GET", "POST"])
def index():
    """
    Home page route: allows user to register and start a Docker Compose stack.
    Handles form submission and stack deployment, and displays status messages.
    Returns:
        str: Rendered HTML page.
    """
    # If user is already authenticated and stack deployed, redirect to dashboard
    if session.get("authenticated") and session.get("stack_deployed"):
        return redirect(url_for("dashboard"))

    # Show progress if stack is being created
    if session.get("progress"):
        username = session.get("username")
        progress = _stack_progress.get(username)
        if progress and progress.get("status") == "ready":
            # Stack is ready, finalize session and show info
            session["authenticated"] = True
            session["stack_deployed"] = True
            session["ssh_username"] = progress["ssh_username"]
            session["ssh_password"] = progress["ssh_password"]
            session["host_ip"] = progress["host_ip"]
            session["host_port"] = progress["host_port"]
            # Set timer: 1 hour from now
            session["expiry"] = (datetime.datetime.utcnow() + datetime.timedelta(hours=1)).isoformat()
            session.pop("progress", None)
            _stack_progress.pop(username, None)
            # redirect to dashboard
            return redirect(url_for("dashboard"))
        elif progress and progress.get("status") == "error":
            error_msg = progress.get("error", "Unknown error")
            session.pop("progress", None)
            _stack_progress.pop(username, None)
            return render_template("index.html", error=f"Error launching stack: {error_msg}")
        else:
            return render_template("index.html", progress=True)

    if request.method == "POST":
        username = request.form.get("name")
        if not session.get("username"):
            # Start stack creation in background
            session["progress"] = True
            session["username"] = username
            session.modified = True
            _threading.Thread(target=_deploy_stack_async, args=(username,)).start()
            return render_template("index.html", progress=True)
        else:
            return render_template("index.html", error="Username already taken. Please choose another one.")
    return render_template("index.html")

@app.route("/stack_status")
def stack_status():
    """
    Endpoint for AJAX polling of stack creation progress.
    """
    username = session.get("username")
    progress = _stack_progress.get(username)
    if progress:
        if progress.get("status") == "ready":
            return jsonify({"status": "ready"})
        elif progress.get("status") == "error":
            return jsonify({"status": "error", "error": progress.get("error", "Unknown error")})
    return jsonify({"status": "pending"})




@app.route("/check_flag", methods=["GET", "POST"])
def check_flag():
    """
    Route to check the submitted flag against the correct flag.
    Returns:
        str: Rendered HTML page with result message.
    """
    message = ""
    if request.method == "POST":
        submitted_flag = request.form.get("flag")
        if submitted_flag == FLAG:
            message = "Success! The flag is correct."
        else:
            message = "Failure! The flag is incorrect."
    return render_template("check_flag.html", message=message)



@app.route("/dashboard")
def dashboard():
    """
    Dashboard page for authenticated users with deployed stack.
    Shows stack info, timer, and provides logout/extend options.
    Removes stack if timer expired.
    """
    if not (session.get("authenticated") and session.get("stack_deployed")):
        return redirect(url_for("index"))
    expiry_str = session.get("expiry")
    username = session.get("username", "root")
    expired = False
    time_left = None
    if expiry_str:
        expiry = datetime.datetime.fromisoformat(expiry_str)
        now = datetime.datetime.now()
        if now >= expiry:
            expired = True
        else:
            time_left = expiry - now
    if expired:
        # Remove stack and clear session
        try:
            subprocess.run([
                "docker", "compose",
                "-p", username,
                "-f", COMPOSE_FILE,
                "down"
            ], check=True)
        except Exception:
            pass
        session.clear()
        return render_template("index.html", error="Your time has expired. The stack has been removed.")
    # Show dashboard with timer
    return render_template(
                "dashboard.html",
                success=True,
                username=session.get("ssh_username"),
                password=session.get("ssh_password"),
                host_ip=session.get("host_ip"),
                host_port=session.get("host_port"),
                time_left=time_left
            )

@app.route("/extend_time", methods=["POST"])
def extend_time():
    """
    Allow authenticated users to extend their timer by 30 minutes.
    """
    if not (session.get("authenticated") and session.get("stack_deployed")):
        return redirect(url_for("index"))
    expiry_str = session.get("expiry")
    if expiry_str:
        expiry = datetime.datetime.fromisoformat(expiry_str)
        new_expiry = expiry + datetime.timedelta(minutes=30)
        session["expiry"] = new_expiry.isoformat()
    return redirect(url_for("dashboard"))

@app.route("/submit_flag", methods=["GET", "POST"])
def submit_flag():
    """
    Allow authenticated users to submit the flag. Only accessible if logged in.
    """
    if not (session.get("authenticated") and session.get("stack_deployed")):
        return redirect(url_for("index"))
    message = ""
    if request.method == "POST":
        submitted_flag = request.form.get("flag")
        if submitted_flag == FLAG:
            message = "Success! The flag is correct."
        else:
            message = "Failure! The flag is incorrect."
    return render_template("submit_flag.html", message=message)

@app.route("/logout", methods=["POST"])
def logout():
    """
    Log out the user by clearing the session and redirecting to registration page.
    """
    session.clear()
    return redirect(url_for("index"))

if __name__ == "__main__":
    """
    Run the Flask-SocketIO development server.
    """
    socketio.run(app, host="0.0.0.0", port=5000)