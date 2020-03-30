"""
This module includes the functionality of
    Cycling equipment usage API.
Run with:
    flask run
See https://github.com/vesamaki/PWP_2020 for details
"""

from flask import Flask, request, abort, json
from sqlalchemy.exc import IntegrityError
from sqlalchemy.engine import Engine
from werkzeug.exceptions import BadRequest
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import event


# Utilized from PWP Ex1
app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///bike_API.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)

@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()

class Component(db.Model):
    # Check that date_retired is not before date_added.
    # Category and equipment_id form a unique entity.
    __table_args__ = (db.CheckConstraint('date_retired > date_added',
                                         name='_c_add_bfr_retire_cc'),
                      db.UniqueConstraint("category", "equipment_id",
                                          name="_compo_in_equip_uc")
                      )

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), nullable=False)
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
    # Adapted from PWP Ex2
    def __repr__(self):
        return "[{}] {} brand {} and model {}" \
            " added on {} and retired on {}," \
            " part of equip {}".format(self.id,
                                       self.name,
                                       self.brand,
                                       self.model,
                                       self.date_added,
                                       self.date_retired,
                                       self.equipment_id
                                       )

class Ride(db.Model):
    # Check that 0 duration rides are not accepted.
    __table_args__ = (db.CheckConstraint('duration > 0',
                                         name='_no_zero_duration_cc'),
                      db.UniqueConstraint("name", "equipment_id",
                                          name="_compo_in_equip_uc")
                      )

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), nullable=False, unique=True)
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
    # Adapted from PWP Ex2
    def __repr__(self):
        return "[{}] {} duration {}" \
            " ridden on {} with {} by {}".format(self.id,
                                                 self.name,
                                                 self.duration,
                                                 self.datetime,
                                                 self.equipment_id,
                                                 self.rider
                                                 )

class Equipment(db.Model):
    # Check that date_retired is not before date_added.
    __table_args__ = (db.CheckConstraint('date_retired > date_added',
                                         name='_e_add_bfr_retire_cc'),
                      db.UniqueConstraint("name", "owner",
                                          name="_owned_bike_uc")
                      )

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), nullable=False, unique=True)
    category = db.Column(db.String(64), nullable=False)
    brand = db.Column(db.String(64), nullable=False)
    model = db.Column(db.String(128), nullable=False)
    date_added = db.Column(db.DateTime, nullable=False)
    date_retired = db.Column(db.DateTime, nullable=True,)
    owner = db.Column(db.Integer,
                      # Keep equipment just in case.
                      db.ForeignKey("user.id", ondelete="SET NULL"),
                      unique=False
                      )

    ownedBy = db.relationship("User", back_populates="hasEquip")
    # Components will be deleted if equipment they belong to is deleted.
    hasCompos = db.relationship("Component",
                                cascade="all, delete-orphan",
                                back_populates="installedTo",
                                order_by=(Component.category)
                                )
    inRide = db.relationship("Ride",
                             back_populates="riddenWith",
                             # One-to-One, only one bike used per ride.
                             uselist=False,
                             order_by=(Ride.datetime, Ride.name)
                             )
    # Adapted from PWP Ex2
    def __repr__(self):
        return "[{}] {}, brand {} and model {}" \
            " added on {} and retired on {}," \
            " owned by {}".format(self.id,
                                  self.name,
                                  self.brand,
                                  self.model,
                                  self.date_added,
                                  self.date_retired,
                                  self.owner
                                  )

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), nullable=False, unique=True)

    hasEquip = db.relationship("Equipment",
                               back_populates="ownedBy",
                               order_by=(Equipment.category, Equipment.name)
                               )
    rode = db.relationship("Ride",
                           back_populates="riddenBy",
                           # One-to-One, only one rider per ride.
                           # Tandem not supported.
                           uselist=False,
                           order_by=(Ride.datetime, Ride.name)
                           )
    # Adapted from PWP Ex2
    def __repr__(self):
        return "[{}] {}".format(self.id, self.name)
