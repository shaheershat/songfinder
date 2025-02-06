from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
import json
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

app = Flask(__name__, static_folder="static")
app.secret_key = "mysecretkey"
app.permanent_session_lifetime = 3600  # Session lasts for 1 hour

# Spotify API Credentials (Replace with actual credentials)
SPOTIPY_CLIENT_ID = "135b52048f4c4ce4801c9be8346fe9e1"
SPOTIPY_CLIENT_SECRET = "a51270e0529646cca51f9ab1d3cc28cf"

# Initialize Spotify API client
sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(
    client_id=SPOTIPY_CLIENT_ID,
    client_secret=SPOTIPY_CLIENT_SECRET
))

USER_FILE = "users.json"

def load_users():
    try:
        with open(USER_FILE, "r") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Error loading users: {e}")
        return {}

def save_users(users):
    with open(USER_FILE, "w") as f:
        json.dump(users, f, indent=4)

@app.before_request
def make_session_permanent():
    session.permanent = True  # Keep user logged in

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        confirm_password = request.form.get("confirm_password")
        users = load_users()

        if username in users:
            flash("Username already exists", "error")
        elif password != confirm_password:
            flash("Passwords do not match", "error")
        else:
            users[username] = {"password": password, "blocked": False}
            save_users(users)
            flash("Account created successfully. Please log in.", "success")
            return redirect(url_for("login"))

    return render_template("signup.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        users = load_users()

        if username not in users or users[username]["password"] != password:
            flash("Invalid username or password", "error")
            return redirect(url_for("login"))

        elif users[username]["blocked"]:
            flash("Your account has been blocked.", "error")
            return redirect(url_for("login"))

        else:
            session["user_logged_in"] = username
            if username == "admin":
                session["admin_logged_in"] = True
            return redirect(url_for("admin_panel") if username == "admin" else url_for("search"))

    return render_template("login.html")

@app.route("/logout")
def logout():
    session.clear()
    flash("You have logged out successfully", "success")
    return redirect(url_for("login"))

@app.route("/admin")
def admin_panel():
    if not session.get("admin_logged_in"):
        flash("Access Denied. Admins only.", "error")
        return redirect(url_for("login"))
    
    return render_template("admin.html", users=load_users())

@app.route("/toggle_block_user", methods=["POST"])
def toggle_block_user():
    if not session.get("admin_logged_in"):
        return jsonify(success=False, error="Access Denied")

    username = request.form.get("username")
    users = load_users()

    if username in users and username != "admin":  # Prevent admin blocking
        users[username]["blocked"] = not users[username].get("blocked", False)
        save_users(users)
        return jsonify(success=True, blocked=users[username]["blocked"])

    return jsonify(success=False, error="User not found")

@app.route("/remove_user", methods=["POST"])
def remove_user():
    if not session.get("admin_logged_in"):
        return jsonify(success=False, error="Access Denied")

    username = request.form.get("username")
    users = load_users()

    if username in users and username != "admin":  # Prevent admin deletion
        del users[username]
        save_users(users)
        return jsonify(success=True)

    return jsonify(success=False, error="Cannot remove this user")

@app.route('/add_user', methods=['POST'])
def add_user():
    if not session.get("admin_logged_in"):
        flash("Access Denied", "error")
        return redirect(url_for("login"))

    username = request.form['username']
    password = request.form['password']

    users = load_users()

    if username in users:
        flash("Username already exists", "error")
        return redirect(url_for("admin_panel"))

    # Add the new user
    users[username] = {"password": password, "blocked": False}
    save_users(users)

    flash("User added successfully.", "success")
    return redirect(url_for("admin_panel"))

@app.route("/search", methods=["GET", "POST"])
def search():
    if "user_logged_in" not in session:
        flash("Please log in to access this page", "warning")
        return redirect(url_for("login"))

    if request.method == "POST":
        theme = request.form.get("theme")
        if theme:
            songs = get_spotify_songs(theme)
            return render_template("search_results.html", songs=songs, theme=theme)
        flash("Please enter a search term.", "warning")

    return render_template("search.html")

def get_spotify_songs(theme):
    try:
        results = sp.search(q=theme, limit=12, type="track")
        return [
            {
                "name": track["name"],
                "artist": track["artists"][0]["name"],
                "url": track["external_urls"]["spotify"],
                "album": track["album"]["name"],
                "image": track["album"]["images"][0]["url"] if track["album"]["images"] else None
            }
            for track in results["tracks"]["items"]
        ]
    except spotipy.SpotifyException as e:
        print(f"Spotify API Error: {e}")
        flash("An error occurred while searching for songs. Please try again later.", "error")
        return []

if __name__ == "__main__":
    app.run(debug=True)
