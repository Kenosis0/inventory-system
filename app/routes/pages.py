from flask import Blueprint, render_template, request, redirect, url_for, flash

pages_bp = Blueprint("pages", __name__)

@pages_bp.route("/", methods=["GET", "POST"])
@pages_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        
        # Demo credentials check
        valid_users = {
            "admin": "admin123",
            "user": "user123"
        }
        
        if username in valid_users and valid_users[username] == password:
            # TODO: Implement proper session management
            return redirect(url_for("pages.login"))  # Replace with dashboard later
        else:
            flash("Invalid username or password", "error")
    
    return render_template("login.html")
