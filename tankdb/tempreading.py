import mongoengine
import datetime

class TempReading(mongoengine.Document):
    reading_time = mongoengine.DateTimeField(default=datetime.datetime.now)
    reading_location = mongoengine.StringField()
    temp_c = mongoengine.FloatField()
    temp_f = mongoengine.FloatField()

    meta = {'db_alias': 'core', 'collection': 'temp_readings'}
