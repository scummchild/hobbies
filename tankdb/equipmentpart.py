import mongoengine
import datetime

class EquipmentPart(mongoengine.EmbeddedDocument):
    name = mongoengine.StringField()
    brand = mongoengine.StringField()
    add_date = mongoengine.DateTimeField(default=datetime.datetime.now)
    replaced_date = mongoengine.DateTimeField()
    target_days_to_replace = mongoengine.IntField()

    meta = {'db_alias': 'core', 'collection': 'equipment_parts'}
