"""Script to add a new water "part" to the turtle tank.
Change the replaced_date variable as appropriate"""

from datetime import datetime

from tankdb.tankequipment import TankEquipment
from tankdb.equipmentpart import EquipmentPart
import tankdb.mongo_setup as mongo_setup

mongo_setup.global_init()

tank = TankEquipment.objects().filter(name='main tank').first()

replaced_date = datetime(2020, 1, 29, 19)

old_water = tank.parts[-1]
old_water.replaced_date = replaced_date

new_water = EquipmentPart(name=old_water.name,
                          brand=old_water.brand,
                          add_date=replaced_date,
                          target_days_to_replace=old_water.target_days_to_replace)

tank.parts.append(new_water)

tank.save()
