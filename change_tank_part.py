'''TODO: create a "get_part_list" function that makes a dictionary
(1: 'main tank water', 2: 'light fixture basking bulb')
then show those values (press 1 to replace main tank water....alternate colors)...maybe a confirm
'Replace main tank water? Y/N'
'''

from datetime import datetime
from typing import cast

from tankdb import mongo_setup as mongo_setup
from tankdb.tankequipment import TankEquipment
from tankdb.equipmentpart import EquipmentPart

mongo_setup.global_init()

parts_list = set(f'{equipment.name} {part.name}' for equipment in TankEquipment.objects()
    for part in equipment.parts)

menu_options = {option_number: part for option_number,
    part in enumerate(parts_list)}


print('Welcome to the Turtle Tank Maintence System')
print('Which part would you like to replace?')
print('')
# TODO: Print out in a nicer, colored format
print(menu_options)
print('(Enter the number you would like to change)')

menu_option = int(input())

part_to_replace = menu_options.get(menu_option)

print(part_to_replace)

# for part in reversed(equipment_to_update.parts):
#     count += 1
#     if part.name == 'water' and not part.replaced_date:
#         print(part.add_date)
#         break

# print(count)
