from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

# probs don't need ...
association_table = db.Table(
    "association",
    db.Model.metadata,
    db.Column("sleep_id", db.Integer, db.ForeignKey("sleep.id")),
    db.Column("dream_id", db.Integer, db.ForeignKey("dream.id")),
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
            "id": self.id,
            "hours_slept": self.hours_slept,
            "sleep_quality": self.sleep_quality,
            "date": self.date,
            "dreams": [d.serialize() for d in self.dreams],
            # do we do something different for a one-to-one relationship than one-to-many?
        }

    def simple_serialize(self):
        """
        Serialize a Sleep object without the dreams field
        """
        return {
            "id": self.id,
            "hours_slept": self.hours_slept,
            "sleep_quality": self.sleep_quality,
            "date": self.date,
            # do we do something different for a one-to-one relationship than one-to-many?
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
        Initialize a dream object
        """
        self.has_description = kwargs.get("has_description")
        self.description = kwargs.get("description")
        self.sleep_id = kwargs.get("sleep_id")

    def serialize(self):
        """
        Serialize a Dream object
        """
        sleep = Sleep.query.filter_by(id=self.sleep_id).first()
        return {
            "id": self.id,
            "has_description": self.has_description,
            "description": self.description,
            "sleep": sleep.simple_serialize(),
        }

    def simple_serialize(self):
        """
        Serialize a Dream object without the sleep field
        """
        return {
            "id": self.id,
            "has_description": self.has_description,
            "description": self.description,
        }
