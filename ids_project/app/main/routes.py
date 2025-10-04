from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from flask_mail import Message
from app import mail, db
from app.models import User
from config import Config

main_bp = Blueprint("main", __name__)

@main_bp.route("/")
@main_bp.route("/home")
def home():
    return render_template("home.html")

@main_bp.route("/about")
def about():
    return render_template("about.html")

@main_bp.route("/features")
def features():
    return render_template("features.html")

@main_bp.route("/contact", methods=["GET", "POST"])
def contact():
    if request.method == "POST":
        if "user" not in session:
            flash("You must be logged in to send a message.", "error")
            return redirect(url_for("auth.login"))

        name = session["user"]
        user = User.query.filter_by(username=name).first()
        email = user.email if user else "unknown@example.com"
        message = request.form.get("message")

        if not message:
            flash("Message cannot be empty.", "error")
            return redirect(url_for("main.contact"))

        try:
            msg = Message(
                subject=f"📩 Message from {name}",
                sender=Config.MAIL_DEFAULT_SENDER,
                recipients=[Config.MAIL_DEFAULT_SENDER],
                body=f"Name: {name}\nEmail: {email}\n\n{message}"
            )
            mail.send(msg)
            flash("Your message was sent successfully!", "success")
        except Exception:
            flash("Failed to send message. Please try again later.", "error")

        return redirect(url_for("main.contact"))

    user_email = None
    if "user" in session:
        user = User.query.filter_by(username=session["user"]).first()
        user_email = user.email if user else None

    return render_template("contact.html", user_email=user_email)
