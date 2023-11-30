import json
import time

from db import db, Sleep, Dream
from flask import Flask, request, jsonify

import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from collections import Counter

app = Flask(__name__)
db_filename = "sneep.db"

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///%s" % db_filename
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_ECHO"] = True

db.init_app(app)
with app.app_context():
    db.create_all()

nltk.download("stopwords")
nltk.download("punkt")


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
    return success_response(sleeps)


@app.route("/api/sleeps/", methods=["POST"])
def create_sleep():
    """
    Endpoint for creating a new sleep
    """
    body = json.loads(request.data)
    if (
        body.get("hours_slept") is None
        or body.get("sleep_quality") is None
        or body.get("date") is None
    ):
        return failure_response("missing fields for sleep description", 400)
    new_sleep = Sleep(
        hours_slept=body.get("hours_slept"),
        sleep_quality=body.get("sleep_quality"),
        date=body.get("date"),
    )
    db.session.add(new_sleep)
    db.session.commit()
    return success_response(new_sleep.serialize(), 201)


@app.route("/api/sleeps/<int:sleep_id>/", methods=["POST"])
def update_sleep(sleep_id):
    """
    Endpoint for updating an existing sleep
    """
    body = json.loads(request.data)
    sleep = Sleep.query.filter_by(id=sleep_id).first()
    if sleep is None:
        return failure_response("sleep not found")

    if body.get("hours_slept") is not None:
        setattr(sleep, "hours_slept", body.get("hours_slept"))
    if body.get("sleep_quality") is not None:
        setattr(sleep, "sleep_quality", body.get("sleep_quality"))
    if body.get("date") is not None:
        setattr(sleep, "date", body.get("date"))
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


@app.route("/api/sleeps/<int:sleep_id>/", methods=["DELETE"])
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


@app.route("/api/dreams/<int:sleep_id>/", methods=["POST"])
def create_dream(sleep_id):
    """
    Endpoint for creating a dream linked to a sleep with sleep_id
    """
    # create dream
    body = json.loads(request.data)
    has_description = body.get("has_description")
    description = body.get("description")

    sleep = Sleep.query.filter_by(id=sleep_id).first()
    if sleep is None:
        return failure_response("sleep not found")
    if has_description is None or description is None:
        has_description = False
        description = ""
    new_dream = Dream(
        has_description=has_description, description=description, sleep_id=sleep_id
    )
    db.session.add(new_dream)
    db.session.commit()

    # assign dream
    sleep.dreams.append(new_dream)
    db.session.commit()
    return success_response(new_dream.serialize(), 201)


@app.route("/api/dreams/<int:dream_id>/")
def get_dream(dream_id):
    """
    Endpoint for getting dream by id
    """
    dream = Dream.query.filter_by(id=dream_id).first()
    if dream is None:
        return failure_response("dream not found")
    return success_response(dream.serialize())


@app.route("/api/dreams/common-words/")
def get_common_words():
    """
    Endpoint for returning the five most common words in all the logged dreams
    """
    sleeps = [sleep.serialize() for sleep in Sleep.query.all()]
    dreams_words = " ".join([sleep["dreams"] for sleep in sleeps])
    # stop words are words like the, and, etc. that we don't want to analyze
    stop_words = set(stopwords.words("english"))

    punct = {",", ".", "-"}
    word_tokens = word_tokenize(dreams_words)

    filtered_sentence = []
    for w in word_tokens:
        if w not in stop_words and w not in punct:
            filtered_sentence.append(w)

    # print(word_tokens)
    # print(filtered_sentence)

    Counters = Counter(filtered_sentence)
    most_common = Counters.most_common(5)
    return success_response([word for word, count in most_common])


@app.route("/api/sleeps/best-hours-slept/")
def get_best_hours_slept():
    """
    Endpoint for returning the min hours slept to get the max sleep quality
    """
    # get hours slept for max sleep quality (if tie - get the first instance of the max)
    sleeps = [sleep.serialize() for sleep in Sleep.query.all()]
    max_qual_sleep = max(sleeps, key=lambda sleep: sleep["sleep_quality"])
    print(max_qual_sleep["hours_slept"])
    return success_response(max_qual_sleep["hours_slept"])


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)
