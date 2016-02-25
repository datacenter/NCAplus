from peewee import *

database = SqliteDatabase('fedex-hub.db')

# model definitions -- the standard "pattern" is to define a base model class
# that specifies which database to use.  then, any subclasses will automatically
# use the correct storage.
class base(Model):
    class Meta:
        database = database


class network(base):
    encapsulation = IntegerField()
    name = CharField()
    group = CharField()
    epg_dn = CharField()
    network_profile = CharField(null=True)

class vpc(base):
    name = CharField(unique=True)


class vpcxnetwork(base):
    network = ForeignKeyField(network)
    vpc = ForeignKeyField(vpc)


class port(base):
    port_dn = CharField()
    assigned_vpc = ForeignKeyField(vpc, null=True)


class portxnetwork(base):
    switch_port = ForeignKeyField(port)
    network = ForeignKeyField(network)


class network_profile(base):
    name = CharField(unique=True)


class network_profilexnetwork(base):
    network_profile = ForeignKeyField(network_profile)
    network = ForeignKeyField(network)


def create_tables():
    database.connect()
    database.create_tables([network, vpc, vpcxnetwork, port, portxnetwork, network_profile, network_profilexnetwork])





