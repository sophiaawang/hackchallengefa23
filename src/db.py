# git add . (to add all -> or just use ui)
# git commit -m "message here"
# git push
# git pull

# also helpful: git status to check what files you added

# Create db Sleeps with id, hours_slept, sleep_qual, dream, date
# Create db Dream with id, sleep_id, has_description, and description (set empty string if no linked sleep)
# Get all sleeps
# Post sleep
# Post sleep by id
# Delete sleep by id
# Post dream by sleep_id
# Get dream by sleep_id

# testing git ...

from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

# probs don't need ...
association_table = db.Table(
    "association",
    db.Model.metadata,
    db.Column("course_id", db.Integer, db.ForeignKey("course.id")),
    db.Column("user_id", db.Integer, db.ForeignKey("user.id")),
)


# your sleeps here
class Sleep(db.Model):
    """
    Sleep Model
    """

    # id, hours_slept, sleep_qual, dream, date

    __tablename__ = "sleep"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    hours_slept = db.Column(db.Integer, nullable=False)
    sleep_quality = db.Column(db.Integer, nullable=False)
    date = db.Column(db.String, nullable=False)
    dreams = db.relationship("Dream", cascade="delete")

    # instructors = db.relationship(
    #     "User",
    #     secondary=association_table,
    #     back_populates="courses_as_instructor",
    # )
    # students = db.relationship(
    #     "User",
    #     secondary=association_table,
    #     back_populates="courses_as_student",
    # )

    def __init__(self, **kwargs):
        """
        Initialize a Sleep object
        """
        self.hours_slept = kwargs.get("hours_slept")
        self.sleep_quality = kwargs.get("sleep_quality")
        self.date = kwargs.get("date")

    def serialize(self):
        """
        Serialize a Sleep object
        """
        return {
            # TODO: fill in...
            "id": self.id,
            "hours_slept": self.code,
            "sleep_quality": self.name,
            "date": self.date,
            "dreams": [d.serialize() for d in self.dreams],
            #do we do something different for a one-to-one relationship than one-to-many?
        }

 

class Dream(db.Model):
    """
    Dream Model
    """

    # id, sleep_id, has_description, and description

    __tablename__ = "dream"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    has_description = db.Column(db.Boolean, nullable=False)
    description = db.Column(db.String, nullable=False)
    sleep_id = db.Column(db.Integer, db.ForeignKey("sleep.id"), nullable=False)

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
