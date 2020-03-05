from app import db, Deployment, Location, Sensor
from datetime import datetime


db.create_all()

A = Location(latitude=10.10,
             longitude=10.10,
             altitude=10,
             description="location A"
             )

B = Location(latitude=20.20,
             longitude=20.20,
             altitude=20,
             description="location B"
             )

s1 = Sensor(name="s1",
            model="s1sensor",
            location_id=1
            )

s2 = Sensor(name="s2",
            model="s2sensor",
            location_id=2
            )

db.session.add_all([A, B])
db.session.add_all([s1, s2])
db.session.commit()

d1 = Deployment(start=datetime(2018, 11, 21, 11, 20, 30),
                end=datetime(2018, 12, 21, 11, 20, 30),
                name="janne"
                )

d1.sensors.append(s1)
d1.sensors.append(s2)
db.session.commit()

sensor1 = Sensor.query.get(1)
sensor1.location.id
sensor1.location.id = 2
sensor2 = Sensor.query.get(2)
sensor2.location
db.session.commit()
db.session.rollback()
d1.sensors.append(s1)
d1.sensors
db.session.commit()
d1.sensors
db.session.rollback()
