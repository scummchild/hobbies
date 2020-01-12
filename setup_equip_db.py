"""This script helps me add records to my
mongo db about turtle tank maintenece"""

from tankdb.tankequipment import TankEquipment
from tankdb.equipmentpart import EquipmentPart
import tankdb.mongo_setup as mongo_setup

import datetime

mongo_setup.global_init()

oldwater = EquipmentPart()
water = EquipmentPart()

oldwater.name = 'water'
oldwater.brand = 'Zoo Med Reptisafe Water Conditioner'
oldwater.add_date = datetime.datetime(2020, 1, 1, 14)
oldwater.replaced_date = datetime.datetime(2020, 1, 11, 19)
oldwater.target_days_to_replace = 7

water.name = 'water'
water.brand = 'Zoo Med Reptisafe Water Conditioner'
water.add_date = datetime.datetime(2020, 1, 11, 19)
water.target_days_to_replace = 7

tank = TankEquipment()

tank.name = 'main tank'
tank.brand = 'Thrive Reptile Terrarium'
tank.size = 40
tank.size_unit = 'gallon'
tank.notes = 'Size 36"L X 18"W X 18"H'

tank.parts = [oldwater, water]
tank.save()

basking_bulb = EquipmentPart()
uvb_bulb = EquipmentPart()

basking_bulb.name = 'basking bulb'
basking_bulb.brand = 'Zoo Med Repti Basking Spot Lamp 150W'
basking_bulb.add_date = datetime.datetime(2020, 1, 5, 15)
basking_bulb.target_days_to_replace = 180

uvb_bulb.name = 'uvb bulb'
uvb_bulb.brand = 'Zoo Med Reptisun 10.0 UVB 13W'
uvb_bulb.add_date = datetime.datetime(2020, 1, 12, 16)
uvb_bulb.target_days_to_replace = 240

fixture = TankEquipment()

fixture.name = 'light fixture'
fixture.brand = 'Zoo Med Combo Deep Dome Dual Light Fixture'
fixture.size = 8.5
fixture.size_unit = 'inch'
fixture.notes = 'Size is for one Dome'

fixture.parts = [basking_bulb, uvb_bulb]
fixture.save()

fine_filter = EquipmentPart()
coarse_filter = EquipmentPart()
carbon = EquipmentPart()


fine_filter.name = 'fine filter'
fine_filter.brand = 'Zoo Med Turle Clean 30 Fine Mechanical Filter Sponge'
fine_filter.add_date = datetime.datetime(2020, 1, 12, 15)
fine_filter.target_days_to_replace = 180

coarse_filter.name = 'coarse filter'
coarse_filter.brand = 'Zoo Med Turle Clean 30 Coarse Pre-Filter Sponge'
coarse_filter.add_date = datetime.datetime(2020, 1, 12, 15)
coarse_filter.target_days_to_replace = 180

carbon.name = 'carbon insert'
carbon.brand = 'Zoo Med Turle Clean 15 Activated Carbon Insert'
carbon.add_date = datetime.datetime(2020, 1, 12, 15)
carbon.target_days_to_replace = 30

canister_filter = TankEquipment()

canister_filter.name = 'canister filter'
canister_filter.brand = 'Zoo Med Turle Clean 30 External Canister Filter'
canister_filter.size = 30
canister_filter.size_unit = 'gallon'

canister_filter.parts = [fine_filter, coarse_filter, carbon]

canister_filter.save()

small_filter = EquipmentPart()

small_filter.name = 'tank filter cartridge'
small_filter.brand = 'Aqueon Medium Filter Cartidge'
small_filter.add_date = datetime.datetime(2020, 1, 12, 15)
small_filter.target_days_to_replace = 14

tank_filter = TankEquipment()

tank_filter.name = 'tank filter'
tank_filter.brand = 'Aqueon Filter and Pump'

tank_filter.parts = [small_filter]

tank_filter.save()
