import mongoengine

def global_init():
    mongoengine.register_connection(alias='core',name='galaxycon_mn_2020',host='10.0.0.250')