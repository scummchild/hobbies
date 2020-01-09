import mongoengine

class Guest(mongoengine.Document):
    name = mongoengine.StringField()
    known_for = mongoengine.StringField()
    url = mongoengine.StringField()

    meta = {'db_alias': 'core', 'collection': 'guests'}
