"""
This module initializes the database of
    Cycling equipment usage API.

See https://github.com/vesamaki/PWP_2020 for details
"""

from app import db, User, Equipment, Component, Ride
from datetime import datetime

db.create_all()


###### THE REST IS JUST EXAMPLE DATA ######

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

comp1 = Component(category="Rear Shock",
                  brand="Fox",
                  model="Factory Float",
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

ride1 = Ride(name="Tahko MTB",
             duration=33540,
             datetime=datetime(2018, 7, 16, 8, 15, 0),
             equipment_id=1,
             rider=1
             )

ride2 = Ride(name="Himos MTB",
             duration=23540,
             datetime=datetime(2018, 8, 16, 16, 15, 0),
             equipment_id=1,
             rider=1
             )

ride3 = Ride(name="Vätternrundan",
             duration=33540, # 9h 19min
             datetime=datetime(2018, 6, 16, 4, 15, 0),
             equipment_id=2,
             rider=2
             )

ride4 = Ride(name="Lohjanjärven pyöräily",
             duration=11540, # 9h 19min
             datetime=datetime(2018, 5, 24, 10, 15, 0),
             equipment_id=2,
             rider=2
             )


db.session.add_all([user1, user2])
db.session.add_all([mtb, oldieroadie, newieroadie])
db.session.add_all([comp1, comp2, comp3])
db.session.add_all([ride1, ride2, ride3, ride4])
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
