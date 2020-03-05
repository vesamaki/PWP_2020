



class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), nullable=False, unique=True)

    hasEquip = db.relationship("Equipment", back_populates="ownedBy")
    rode = db.relationship("Ride", back_populates="riddenBy")

class Equipment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), nullable=True)
    category = db.Column(db.String(64), nullable=False)
    brand = db.Column(db.String(64), nullable=False)
    model = db.Column(db.String(128), nullable=False)
    date_added = db.Column(db.DateTime, nullable=False)
    date_retired = db.Column(db.DateTime, nullable=True)
    owner = db.Column(db.Integer, db.ForeignKey("User.id"), unique=False)

    ownedBy = db.relationship("User", back_populates="hasEquip")
    hasCompos = db.relationship("Component", back_populates="installedTo")
    inRide = db.relationship("Ride", back_populates="riddenWith")


class Component(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), nullable=True)
    category = db.Column(db.String(64), nullable=False)
    brand = db.Column(db.String(64), nullable=False)
    model = db.Column(db.String(128), nullable=False)
    date_added = db.Column(db.DateTime, nullable=False)
    date_retired = db.Column(db.DateTime, nullable=True)
    equipment_id = db.Column(db.Integer,
                             db.ForeignKey("Equipment.id"),
                             unique=True)

    installedTo = db.relationship("Equipment", back_populates="hasCompos")

class Ride(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), nullable=True)
    duration = db.Column(db.Integer, nullable=False)
    datetime = db.Column(db.DateTime, nullable=False)
    # A rider (or riders in case of a tandem-bike) can only use one equipment
    #   per ride.
    equipment_id = db.Column(db.Integer,
                             db.ForeignKey("Equipment.id"),
                             unique=True)
    rider = db.Column(db.Integer,
                      db.ForeignKey("User.id"),
                      unique=False)

    riddenWith = db.relationship("Equipment", back_populates="inRide")
    riddenBy = db.relationship("User", back_populates="rode")
