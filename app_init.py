from API_flask_db import db, User, Equipment, Component, Ride
from datetime import datetime

db.create_all()

user1 = User(name="janne")
user2 = User(name="jenni")

mtb = Equipment(name="Jannen maastis",
                category="Mountain Bike",
                brand="Kona",
                model="HeiHei",
                date_added=datetime(2018, 11, 21, 11, 20, 30),
                #date_retired=datetime(2019, 11, 21, 11, 20, 30),
                owner=1 # Janne
                )

oldieroadie = Equipment(name="Jennin vanha kilpuri",
                        category="Road Bike",
                        brand="Focus",
                        model="jokumalli",
                        date_added=datetime(2016, 11, 21, 11, 20, 30),
                        date_retired=datetime(2019, 11, 21, 11, 20, 30),
                        owner=2 # Jenni
                        )

newieroadie = Equipment(name="Jennin uus kilpuri",
                        category="Road Bike",
                        brand="Bianchi",
                        model="Intenso",
                        date_added=datetime(2020, 1, 1, 0, 0, 0),
                        #date_retired=datetime(2019, 11, 21, 11, 20, 30),
                        owner=2 # Jenni
                        )

comp1 = Component(category="Fork",
                  brand="Fox",
                  model="34 Factory",
                  date_added=datetime(2018, 11, 21, 11, 20, 30),
                  date_retired=datetime(2019, 11, 21, 11, 20, 30),
                  equipment_id=1    # Jannen mtb
                  )

comp2 = Component(category="Fork",
                  brand="RockShox",
                  model="Pike RCT3",
                  date_added=datetime(2019, 11, 29, 11, 20, 30),
                  #date_retired=datetime(2019, 11, 21, 11, 20, 30),
                  equipment_id=1    # Jannen mtb
                  )

comp3 = Component(category="Saddle",
                  brand="Specialized",
                  model="enmuista",
                  date_added=datetime(2020, 1, 1, 0, 0, 0),
                  #date_retired=datetime(2019, 11, 21, 11, 20, 30),
                  equipment_id=3    # Jennin newieroadie
                  )

db.session.add_all([user1, user2])
db.session.add_all([mtb, oldieroadie, newieroadie])
db.session.add_all([comp1, comp2, comp3])
db.session.commit()

#sensor1 = Sensor.query.get(1)
#sensor1.location.id
#sensor1.location.id = 2
#sensor2 = Sensor.query.get(2)
#sensor2.location
#db.session.commit()
#db.session.rollback()
#d1.sensors.append(s1)
#d1.sensors
#db.session.commit()
#d1.sensors
#db.session.rollback()
