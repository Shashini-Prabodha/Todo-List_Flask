# from flask import Flask, render_template, session, request, redirect
#
# app=Flask(__name__)
#
# @app.route("/")
# def index():
#     return render_template("index.html")
#
#
# @app.route("/login",methods=["POST","GET"])
# def login():
#
#     if request.method == "POST":
#         session["username"]=request.form["username"]
#         return redirect("/task")
#
#     return render_template("login.html")
#
#
# @app.route("/task")
# def task():
#     logged_user=session["username"]
#     return render_template("task.html",username=logged_user)
#
# @app.route("/logout",methods=["POST"])
# def logout():
#
#     if request.method == "POST":
#         session["username"]=None
#         return redirect("/")
#
#
#
# if __name__ == "__main__":
#     app.run(debug=True)



from flask import Flask, redirect,render_template, request, session
from flask_sqlalchemy import SQLAlchemy
import os
import enum

app = Flask(__name__)
app.secret_key = "super secret key"

db_path = os.path.join(os.path.dirname(__file__), 'app.db')

app.config["SQLALCHEMY_DATABASE_URI"]=f'sqlite:///{db_path}'
db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    task = db.relationship("Task",backref="user",lazy=True)

class TaskStatus(enum.Enum):
    COMPLETED = "Completed"
    CLOSED = "Closed"
    OPENED = "Opened"


class Task(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    task = db.Column(db.String(250), nullable=False)
    status = db.Column(db.Enum(TaskStatus), default=TaskStatus.OPENED)
    user_id = db.Column(db.Integer,db.ForeignKey("user.id"),nullable=True)

db.create_all()

@app.route('/')
def index():
    return render_template("index.html")

@app.route('/task',methods=["POST","GET"])
def task():
    if request.method == "GET":
        logged_user = session["user_id"]
        logged_user_name = User.query.filter_by(id=logged_user).first()

        task_list = Task.query.filter_by(user_id=logged_user).all()
        return render_template("task.html",username=logged_user_name.username,tasks=task_list)

    if request.method == "POST":
        logged_user = session["user_id"]
        task = request.form["taskname"]
        status = TaskStatus.OPENED
        newTask = Task(task=task,status=status,user_id=logged_user)
        db.session.add(newTask)
        db.session.commit()
        return redirect("/task")



@app.route('/task/done/<task_id>',methods=["POST","GET"])
def done(task_id):
    if request.method == 'GET':
        logged_user = session["user_id"]
        finded_task = Task.query.filter_by(user_id=logged_user,id=task_id).first()
        finded_task.status = TaskStatus.COMPLETED
        db.session.commit()
        return redirect("/task")

@app.route('/task/cancel/<task_id>',methods=["POST","GET"])
def cancel(task_id):
    if request.method == 'GET':
        logged_user = session["user_id"]
        finded_task = Task.query.filter_by(user_id=logged_user,id=task_id).first()
        finded_task.status = TaskStatus.CLOSED
        db.session.commit()
        return redirect("/task")



@app.route('/logout',methods=["POST"])
def logout():
    if request.method == "POST":
        session["user_id"]=None
        return redirect("/")


@app.route('/login',methods=["POST","GET"])
def login():
    if request.method == "POST":
        username = request.form["username"]

        existing_user = User.query.filter_by(username=username).first()
        print(existing_user)
        if existing_user is None:
            user = User(username=username)
            db.session.add(user)
            db.session.commit()
            existing_user=user

        session["user_id"]= existing_user.id
        return redirect("/task")
    return render_template("login.html")

if __name__ == "__main__":
    app.run(debug=True)
