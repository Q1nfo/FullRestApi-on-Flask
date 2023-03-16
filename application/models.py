from application.setup.db import db, models

# ===============# .=================MODELS FOR OUR DATABASE================================================

type_ = db.Table('type',
    db.Column('animal_id', db.Integer, db.ForeignKey('animal.id')),
    db.Column('type_animal_id', db.Integer, db.ForeignKey('type_animal.id'))
)

location_animals = db.Table('location_animals',
    db.Column('animal_id', db.Integer, db.ForeignKey('animal.id')),
    db.Column('location_id', db.Integer, db.ForeignKey('location.id'))
)


class User(models.Base):
    __tablename__ = 'users'

    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    firstName = db.Column(db.String(50), nullable=True)
    lastName = db.Column(db.String(50), nullable=True)


class Location(models.Base):

    latitude = db.Column(db.Integer(), nullable=False)
    longitude = db.Column(db.Integer(), nullable=False)

    animals = db.relationship('Animal', secondary=location_animals,
                                        backref=db.backref('locations', lazy='dynamic'))


class TypeAnimals(models.Base):
    __tablename__ = 'type_animal'

    type = db.Column(db.String(50), nullable=False)

    animals = db.relationship('Animal', secondary=type_,
                                  backref=db.backref('types_animals', lazy='dynamic'))


class Animal(models.Base):
    __tablename__ = 'animal'

    type_animals = db.relationship('TypeAnimals', secondary=type_,
        backref=db.backref('animals_type', lazy='dynamic'))
    weight = db.Column(db.Float())
    length = db.Column(db.Float())
    height = db.Column(db.Float())
    gender = db.Column(db.String())
    lifeStatus = db.Column(db.String())
    chippingDatetime = db.Column(db.DateTime())
    chipperId = db.Column(db.Integer())
    chippingLocationId = db.Column(db.Integer())
    visited_locations = db.relationship('Location', secondary=location_animals,
        backref=db.backref('animals_location', lazy='dynamic'))
    deathDatetime = db.Column(db.DateTime())


class LocationTime(models.Base):
    animal_id = db.Column(db.Integer())
    location_id = db.Column(db.Integer())
    startDateTime = db.Column(db.DateTime())
    endDateTime = db.Column(db.DateTime())








