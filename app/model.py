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


def create_tables():
    database.connect()
    database.create_tables([network, group, vpc, vpcxnetwork, port, portxnetwork])





