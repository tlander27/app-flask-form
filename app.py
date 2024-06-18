from flask import Flask, render_template, request, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from flask_mail import Mail, Message
import os

app = Flask(__name__)

# Set database security
app.config["SECRET_KEY"] = os.getenv("app_sqlite_secret_key")
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///data.db"
app.config["MAIL_SERVER"] = "smtp.gmail.com"
app.config["MAIL_PORT"] = 465
app.config["MAIL_USE_SSL"] = True
app.config["MAIL_USERNAME"] = os.getenv("app_email_gmail")
app.config["MAIL_PASSWORD"] = os.getenv("app_email_password_gmail")

db = SQLAlchemy(app)
mail = Mail(app)


# Create database database structure
class Form(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(50))
    last_name = db.Column(db.String(50))
    email = db.Column(db.String(50))
    position = db.Column(db.String(80))
    status = db.Column(db.String(50))
    file_upload = db.Column(db.String(5))
    start_date = db.Column(db.Date)
    change_date = db.Column(db.Date)


# Route to handle GET & POST, capture form data, send email w/attachment
@app.route("/", methods=["GET", "POST"])
def index():
    file_upload = "no"
    if request.method == "POST":
        first_name = request.form["first_name"]
        last_name = request.form["last_name"]
        email = request.form["email"]
        position = request.form["position"]
        status = request.form["status"]
        file = request.files["file"]
        start_date = request.form["date"]
        date_obj = datetime.strptime(start_date, "%Y-%m-%d")

        if file.filename != "":
            file_upload = "yes"
            file.save("files/" + file.filename)

        form = Form(first_name=first_name,
                    last_name=last_name,
                    email=email,
                    position=position,
                    status=status,
                    file_upload=file_upload,
                    start_date=date_obj,
                    change_date=datetime.now())
        db.session.add(form)
        db.session.commit()

        now = f"{datetime.now().year}-{datetime.now().month}-{datetime.now().day}"
        message_body = f"Hello {first_name},\n" \
                       "Thank you for your interest in DevCompany! Your application has been submitted.\n\n" \
                       f"Name: {first_name} {last_name}\n" \
                       f"Email: {email}\n" \
                       f"Position: {position}\n" \
                       f"Employment Status: {status}\n" \
                       f"File Uploaded: {file.filename}\n" \
                       f"Start Date: {start_date}\n" \
                       f"Submission Date: {now}\n\n" \
                       f"" \
                       "Our team will review your qualifications and be in touch.\n\n" \
                       "Thank you,\n\n" \
                       "-Hiring Team"
        message = Message(subject="New Application Submission",
                          sender=("DevCompany HR", app.config["MAIL_USERNAME"]),
                          recipients=[email],
                          body=message_body)
        message.attach(filename=file.filename,
                       content_type=None,
                       data="files/" + file.filename,
                       disposition=None,
                       headers=None)
        mail.send(message)

        flash(f"Thank you, {first_name}! Your application has been submitted.", "success")
    return render_template("index.html")


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
        app.run(debug=True, port=5001)