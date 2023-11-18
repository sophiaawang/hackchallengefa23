import json
import time

from db import db, Sleep, Dream
from flask import Flask, request, jsonify

app = Flask(__name__)
db_filename = "cms.db"

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///%s" % db_filename
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_ECHO"] = True

db.init_app(app)
with app.app_context():
    db.create_all()


def success_response(data, code=200):
    return jsonify(data), code


def failure_response(message, code=404):
    return jsonify({"error": message}), code


# your routes here


@app.route("/")
@app.route("/api/sleeps/")
def get_all_sleeps():
    """
    Endpoint for getting all sleeps
    """
    sleeps = [sleep.serialize() for sleep in Sleep.query.all()]
    return success_response({"sleeps": sleeps})


@app.route("/api/sleeps/", methods=["POST"])
def create_sleep():
    """
    Endpoint for creating a new sleep
    """
    body = json.loads(request.data)
    if body.get("hours_slept") is None or body.get("sleep_quality") is None or body.get("date") is None:
        return failure_response("missing fields for sleep description", 400)
    new_sleep= Sleep(
        hours_slept=body.get("hours_slept"),
        sleep_quality=body.get("sleep_quality"),
        date=body.get("date")
    )
    db.session.add(new_sleep)
    db.session.commit()
    return success_response(new_sleep.serialize(), 201)


@app.route("/api/sleeps/<int: sleep_id>/", methods=["POST"])
def update_sleep(sleep_id):
    """
    Endpoint for updating an existing sleep
    """
    body = json.loads(request.data)
    sleep = Sleep.query.filter_by(id=sleep_id).first()
    if sleep is None:
        return failure_response("sleep not found")
    
    if body.get("hours_slept") is not None:
        setattr(sleep, 'hours_slept', body.get("hours_slept"))
    if body.get("sleep_quality") is not None:
        setattr(sleep, 'sleep_quality', body.get("sleep_quality"))
    if body.get("date") is not None:
        setattr(sleep, 'date', body.get("date"))
    db.session.commit()
    updated_sleep = Sleep.query.filter_by(id=sleep_id).first()
    return success_response(updated_sleep.serialize(), 201)


@app.route("/api/sleeps/<int:sleep_id>/")
def get_sleep(sleep_id):
    """
    Endpoint for getting sleep by id
    """
    sleep = Sleep.query.filter_by(id=sleep_id).first()
    if sleep is None:
        return failure_response("sleep not found")
    return success_response(sleep.serialize())


@app.route("/api/courses/<int:sleep_id>/", methods=["DELETE"])
def delete_sleep(sleep_id):
    """
    Endpoint for deleting a sleep by id
    """
    sleep = Sleep.query.filter_by(id=sleep_id).first()
    if sleep is None:
        return failure_response("sleep not found")
    db.session.delete(sleep)
    db.session.commit()
    return success_response(sleep.serialize())


# USER ROUTES


@app.route("/api/users/", methods=["POST"])
def create_user():
    """
    Endpoint for creating a user
    """
    body = json.loads(request.data)
    name = body.get("name")
    netid = body.get("netid")

    if name is None or netid is None:
        return failure_response("name and/or netid field(s) not provided", 400)
    new_user = User(name=name, netid=netid)
    db.session.add(new_user)
    db.session.commit()
    return success_response(new_user.serialize(), 201)


@app.route("/api/users/<int:user_id>/")
def get_user(user_id):
    """
    Endpoint for getting user by id
    """
    user = User.query.filter_by(id=user_id).first()
    if user is None:
        return failure_response("user not found")
    return success_response(user.serialize())


@app.route("/api/courses/<int:course_id>/add/", methods=["POST"])
def assign_course(course_id):
    """
    Endpoint for assigning a course
    to a user by id
    """
    course = Course.query.filter_by(id=course_id).first()
    if course is None:
        return failure_response("course not found")
    body = json.loads(request.data)
    user_id = body.get("user_id")
    user_type = body.get("type")

    user = User.query.filter_by(id=user_id).first()
    if user is None:
        return failure_response("user not found")
    if user_type == "instructor":
        course.instructors.append(user)
    else:
        course.students.append(user)
    db.session.commit()
    return success_response(course.serialize())


# ASSIGNMENT ROUTES
@app.route("/api/courses/<int:course_id>/assignment/", methods=["POST"])
def create_assignment(course_id):
    """
    Endpoint for creating a assignment
    for a course by id
    """
    course = Course.query.filter_by(id=course_id).first()
    if course is None:
        return failure_response("course not found")
    body = json.loads(request.data)
    title = body.get("title")
    due_date = body.get("due_date")
    if title is None or due_date is None:
        return failure_response("no title and/or due date provided", 400)
    new_assignment = Assignment(
        title=title,
        due_date=due_date,
        course_id=course_id,
    )
    db.session.add(new_assignment)
    db.session.commit()
    return success_response(new_assignment.serialize(), 201)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)
