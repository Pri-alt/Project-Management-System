
from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3

app = Flask(__name__)
app.secret_key = "pm_dashboard"

def get_db():
    return sqlite3.connect("project.db")

def init_db():
    conn = get_db()
    c = conn.cursor()

    c.execute("""CREATE TABLE IF NOT EXISTS users(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT,
        password TEXT)""")

    c.execute("""CREATE TABLE IF NOT EXISTS projects(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        description TEXT,
        status TEXT)""")

    c.execute("""CREATE TABLE IF NOT EXISTS tasks(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        project_id INTEGER,
        task_name TEXT,
        status TEXT)""")

    c.execute("SELECT * FROM users WHERE username='admin'")
    if not c.fetchone():
        c.execute("INSERT INTO users(username,password) VALUES('admin','admin123')")

    conn.commit()
    conn.close()

init_db()

@app.route("/", methods=["GET","POST"])
def login():
    if request.method=="POST":
        conn=get_db()
        c=conn.cursor()
        c.execute("SELECT * FROM users WHERE username=? AND password=?",
                  (request.form["username"],request.form["password"]))
        user=c.fetchone()
        conn.close()
        if user:
            session["user"]=user[1]
            return redirect("/dashboard")
    return render_template("login.html")

@app.route("/dashboard")
def dashboard():
    conn=get_db()
    c=conn.cursor()
    projects=c.execute("SELECT COUNT(*) FROM projects").fetchone()[0]
    active=c.execute("SELECT COUNT(*) FROM projects WHERE status='Active'").fetchone()[0]
    completed=c.execute("SELECT COUNT(*) FROM projects WHERE status='Completed'").fetchone()[0]
    tasks=c.execute("SELECT COUNT(*) FROM tasks").fetchone()[0]
    conn.close()
    return render_template("dashboard.html",projects=projects,active=active,completed=completed,tasks=tasks)

@app.route("/projects", methods=["GET","POST"])
def projects():
    conn=get_db()
    c=conn.cursor()
    if request.method=="POST":
        c.execute("INSERT INTO projects(name,description,status) VALUES(?,?,?)",
                  (request.form["name"],request.form["description"],request.form["status"]))
        conn.commit()
    data=c.execute("SELECT * FROM projects").fetchall()
    conn.close()
    return render_template("projects.html",projects=data)

@app.route("/tasks/<int:pid>", methods=["GET","POST"])
def tasks(pid):
    conn=get_db()
    c=conn.cursor()
    if request.method=="POST":
        c.execute("INSERT INTO tasks(project_id,task_name,status) VALUES(?,?,?)",
                  (pid,request.form["task_name"],request.form["status"]))
        conn.commit()
    data=c.execute("SELECT * FROM tasks WHERE project_id=?",(pid,)).fetchall()
    conn.close()
    return render_template("tasks.html",tasks=data,pid=pid)

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

if __name__=="__main__":
    app.run(debug=True)
