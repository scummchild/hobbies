import datetime
from tankdb.tankequipment import TankEquipment
from tankdb.equipmentpart import EquipmentPart
import tankdb.mongo_setup as mongo_setup

mongo_setup.global_init()

tank = TankEquipment.objects().filter(name='main tank').first()

replaced_date = datetime.datetime(2020, 1, 29, 19)
old_water = tank.parts[-1]
old_water.replaced_date = replaced_date

new_water = EquipmentPart()
new_water.name = old_water.name
new_water.brand = old_water.brand
new_water.add_date = replaced_date
new_water.target_days_to_replace = old_water.target_days_to_replace

tank.parts.append(new_water)

tank.save()