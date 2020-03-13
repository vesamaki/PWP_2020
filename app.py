from flask import Flask, request, abort, json
from sqlalchemy.exc import IntegrityError
from sqlalchemy.engine import Engine
from werkzeug.exceptions import BadRequest
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import event


app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///bike_API.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)

@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), nullable=False, unique=True)

    hasEquip = db.relationship("Equipment", back_populates="ownedBy")
    rode = db.relationship("Ride",
                           back_populates="riddenBy",
                           # One-to-One, only one rider per ride.
                           # Tandem not supported.
                           uselist=False
                           )

class Equipment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), nullable=True)
    category = db.Column(db.String(64), nullable=False)
    brand = db.Column(db.String(64), nullable=False)
    model = db.Column(db.String(128), nullable=False)
    date_added = db.Column(db.DateTime, nullable=False)
    date_retired = db.Column(db.DateTime, nullable=True)
    owner = db.Column(db.Integer,
                      # Keep equipment just in case.
                      db.ForeignKey("user.id", ondelete="SET NULL"),
                      unique=False
                      )

    ownedBy = db.relationship("User", back_populates="hasEquip")
    hasCompos = db.relationship("Component",
                                cascade="all, delete-orphan",
                                back_populates="installedTo"
                                )
    inRide = db.relationship("Ride",
                             back_populates="riddenWith",
                             # One-to-One, only one bike used per ride.
                             uselist=False
                             )

class Component(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), nullable=True)
    category = db.Column(db.String(64), nullable=False)
    brand = db.Column(db.String(64), nullable=False)
    model = db.Column(db.String(128), nullable=False)
    date_added = db.Column(db.DateTime, nullable=False)
    date_retired = db.Column(db.DateTime, nullable=True)
    equipment_id = db.Column(db.Integer,
                             # Bike is a sum of its parts,
                             # thus delete parts if equipment is deleted
                             db.ForeignKey("equipment.id", ondelete="CASCADE")
                             )

    installedTo = db.relationship("Equipment", back_populates="hasCompos")

class Ride(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), nullable=True)
    duration = db.Column(db.Integer, nullable=False)
    datetime = db.Column(db.DateTime, nullable=False)
    # A rider (or riders in case of a tandem-bike) can only use one equipment
    #   per ride.
    equipment_id = db.Column(db.Integer,
                             # Keep ride data even if bike is gone.
                             db.ForeignKey("equipment.id", ondelete="SET NULL")
                             )

    rider = db.Column(db.Integer,
                      # Keep ride data even if rider is gone.
                      db.ForeignKey("user.id", ondelete="SET NULL"),
                      unique=False
                      )

    riddenWith = db.relationship("Equipment",
                                 back_populates="inRide"
                                 )
    riddenBy = db.relationship("User", back_populates="rode")
