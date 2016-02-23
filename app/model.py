from peewee import *

database = SqliteDatabase('fedex-hub.db')

# model definitions -- the standard "pattern" is to define a base model class
# that specifies which database to use.  then, any subclasses will automatically
# use the correct storage.
class base(Model):
    class Meta:
        database = database

class group(base):
    name = CharField(unique=True)


class network(base):
    encapsulation = IntegerField(unique=True)
    name = CharField()
    group = ForeignKeyField(group)


def create_tables():
    database.connect()
    database.create_tables([network, group])


class vlan:
    def __init__(self, vlan_number, tenant_name, ap_name, epg_name):
        self.tenant_name = tenant_name
        self.vlan_number = vlan_number
        self.ap_name = ap_name
        self.epg_name = epg_name




