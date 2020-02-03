import mongoengine


def mongo_init(alias: str, name: str, host: str):
    mongoengine.register_connection(alias=alias, name=name, host=host)
