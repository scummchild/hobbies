import mongoengine

def global_init():
    mongoengine.register_connection(alias='core',name='turtle_tank', host='10.0.0.250')