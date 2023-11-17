import json
import time

from db import db, Course, Assignment, User
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
@app.route("/api/courses/")
def get_courses():
    """
    Endpoint for getting all courses
    """
    courses = [course.serialize() for course in Course.query.all()]
    return success_response({"courses": courses})


@app.route("/api/courses/", methods=["POST"])
def create_course():
    """
    Endpoint for creating a new course
    """
    body = json.loads(request.data)
    if body.get("code") is None or body.get("name") is None:
        return failure_response("class code and/or name field(s) not provided", 400)
    new_course = Course(
        code=body.get("code"),
        name=body.get("name"),
    )
    db.session.add(new_course)
    db.session.commit()
    return success_response(new_course.serialize(), 201)


@app.route("/api/courses/<int:course_id>/")
def get_course(course_id):
    """
    Endpoint for getting course by id
    """
    course = Course.query.filter_by(id=course_id).first()
    if course is None:
        return failure_response("course not found")
    return success_response(course.serialize())


@app.route("/api/courses/<int:course_id>/", methods=["DELETE"])
def delete_course(course_id):
    """
    Endpoint for deleting a course by id
    """
    course = Course.query.filter_by(id=course_id).first()
    if course is None:
        return failure_response("course not found")
    db.session.delete(course)
    db.session.commit()
    return success_response(course.serialize())


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
