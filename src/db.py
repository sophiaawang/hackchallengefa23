# Create db Sleeps with id, hours_slept, sleep_qual, dream, date
# Create db Dream with id, sleep_id, has_description, and description (set empty string if no linked sleep)
# Get all sleeps
# Post sleep
# Post sleep by id
# Delete sleep by id
# Post dream by sleep_id
# Get dream by sleep_id


from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

association_table = db.Table(
    "association",
    db.Model.metadata,
    db.Column("course_id", db.Integer, db.ForeignKey("course.id")),
    db.Column("user_id", db.Integer, db.ForeignKey("user.id")),
)


# your classes here
class Course(db.Model):
    """
    Course Model
    """

    __tablename__ = "course"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    code = db.Column(db.String, nullable=False)
    name = db.Column(db.String, nullable=False)
    assignments = db.relationship("Assignment", cascade="delete")
    instructors = db.relationship(
        "User",
        secondary=association_table,
        back_populates="courses_as_instructor",
    )
    students = db.relationship(
        "User",
        secondary=association_table,
        back_populates="courses_as_student",
    )

    def __init__(self, **kwargs):
        """
        Initialize a Course object
        """
        self.code = kwargs.get("code")
        self.name = kwargs.get("name")

    def serialize(self):
        """
        Serialize a Course object
        """
        return {
            "id": self.id,
            "code": self.code,
            "name": self.name,
            "assignments": [a.simple_serialize() for a in self.assignments],
            "instructors": [i.simple_serialize() for i in self.instructors],
            "students": [s.simple_serialize() for s in self.students],
        }

    def simple_serialize(self):
        """
        Serialize a Course object without assignments, students, or instructors
        """
        return {
            "id": self.id,
            "code": self.code,
            "name": self.name,
        }


class Assignment(db.Model):
    """
    Assignment Model
    """

    __tablename__ = "assignment"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String, nullable=False)
    due_date = db.Column(db.Integer)
    course_id = db.Column(db.Integer, db.ForeignKey("course.id"), nullable=False)

    def __init__(self, **kwargs):
        """
        Initialize a assignment object
        """
        self.title = kwargs.get("title")
        self.due_date = kwargs.get("due_date")
        self.course_id = kwargs.get("course_id")

    def serialize(self):
        course = Course.query.filter_by(id=self.course_id).first()
        return {
            "id": self.id,
            "title": self.title,
            "due_date": self.due_date,
            "course": course.simple_serialize(),
        }

    def simple_serialize(self):
        return {
            "id": self.id,
            "title": self.title,
            "due_date": self.due_date,
        }


class User(db.Model):
    """
    User Model
    """

    __tablename__ = "user"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String, nullable=False)
    netid = db.Column(db.String, nullable=False)
    courses_as_instructor = db.relationship(
        "Course",
        secondary=association_table,
        back_populates="instructors",
    )
    courses_as_student = db.relationship(
        "Course",
        secondary=association_table,
        back_populates="students",
    )

    def __init__(self, **kwargs):
        """
        Initalize a User object
        """
        self.name = kwargs.get("name")
        self.netid = kwargs.get("netid")

    def serialize(self):
        """
        Serialize a User object
        """
        all_courses = list(set(self.courses_as_instructor + self.courses_as_student))
        return {
            "id": self.id,
            "name": self.name,
            "netid": self.netid,
            "courses": [c.simple_serialize() for c in all_courses],
        }

    def simple_serialize(self):
        """
        Serialize user object without the course field
        """
        return {
            "id": self.id,
            "name": self.name,
            "netid": self.netid,
        }
