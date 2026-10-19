from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import inspect, text
import datetime


app = Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///task.db"
app.config["SQLALCHEMY_TRACK_MODIFICATION"] = False

db = SQLAlchemy(app)


class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text(250), nullable=True)
    priority = db.Column(db.String(20), nullable=False)
    end_date = db.Column(db.Date, nullable=True)
    completed = db.Column(db.Boolean, default=False)


with app.app_context():
    db.create_all()
    with db.engine.begin() as connection:
        task_columns = {
            column["name"] for column in inspect(connection).get_columns("task")
        }
        if "end_date" not in task_columns:
            connection.execute(text("ALTER TABLE task ADD COLUMN end_date DATE"))


@app.route("/")
def index():
    tasks = Task.query.all()
    return render_template("index.html", tasks=tasks)


@app.route("/add", methods=["POST"])
def add_task():
    title = request.form.get("title")
    description = request.form.get("description")
    priority = request.form.get("priority")
    end_date_str = request.form.get('end_date')

    # Convert HTML date string (YYYY-MM-DD) into Python date object
    parsed_end_date = None
    if end_date_str:
        parsed_end_date = datetime.datetime.strptime(
            end_date_str, "%Y-%m-%d"
        ).date()

    if title and priority:
        new_task = Task(title=title, description=description,
                        priority=priority,end_date=parsed_end_date)

        db.session.add(new_task)
        db.session.commit()
    return redirect(url_for("index"))

@app.route("/complete/<int:task_id>")
def complete_task(task_id):
    task = Task.query.get(task_id)
    if task :
        task.completed = not task.completed
        db.session.commit()
    return redirect(url_for("index"))

@app.route("/delete/<int:task_id>")
def delete_task(task_id):
    task = Task.query.get(task_id)
    if task:
        db.session.delete(task)
        db.session.commit()
    return redirect(url_for("index"))

if __name__ == "__main__":
    app.run(debug=True)