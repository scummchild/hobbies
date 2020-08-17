'''TODO: create a "get_part_list" function that makes a dictionary
(1: 'main tank water', 2: 'light fixture basking bulb')
then show those values (press 1 to replace main tank water....alternate colors)...maybe a confirm
'Replace main tank water? Y/N'
'''

from datetime import date
from typing import cast

from tankdb import mongo_setup as mongo_setup
from tankdb.tankequipment import TankEquipment
from tankdb.equipmentpart import EquipmentPart

mongo_setup.global_init()

# parts_list = set(f'{equipment.name} {part.name}' for equipment in TankEquipment.objects()
#     for part in equipment.parts)

equipment_part_list = list(set((equipment.name, part.name) for equipment in TankEquipment.objects()
    for part in equipment.parts))

menu_option_list =  {option_number: part for option_number, part in list(enumerate([f'{part[0]} {part[1]}' for part in equipment_part_list]))}

# menu_options = {option_number: part for option_number,
#     part in enumerate(parts_list)}


print('Welcome to the Turtle Tank Maintence System')
print('Which part would you like to replace?')
print('')
# TODO: Print out in a nicer, colored format
print(menu_option_list)
print('(Enter the number you would like to change)')

menu_option = int(input())

equipment_name = equipment_part_list[menu_option][0]

equipment_found = TankEquipment.objects().filter(name=equipment_name).first()

for part in reversed(equipment_found.parts):
    if part.name == equipment_part_list[menu_option][1] and not part.replaced_date:
        replaced_date = date.today()

        part.replaced_date = replaced_date

        new_part = EquipmentPart()
        new_part.name = part.name
        new_part.add_date = part.replaced_date
        new_part.brand = part.brand
        new_part.target_days_to_replace = part.target_days_to_replace

        equipment_found.parts.append(new_part)

        break

equipment_found.save()


