import mongoengine
from tankdb.equipmentpart import EquipmentPart

class TankEquipment(mongoengine.Document):
    name = mongoengine.StringField()
    brand = mongoengine.StringField()
    size = mongoengine.FloatField()
    size_unit = mongoengine.StringField()
    notes = mongoengine.StringField()

    parts = mongoengine.EmbeddedDocumentListField(EquipmentPart)

    meta = {'db_alias': 'core', 'collection': 'tank_equipment'}
