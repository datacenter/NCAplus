"""

Model and database definition

"""
from peewee import *
__author__ = 'Santiago Flores Kanter (sfloresk@cisco.com)'
database = SqliteDatabase('l2-integration.db')


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

class access_switch(base):
    ip = CharField(unique=True)
    user = CharField()
    hostname = CharField()

def create_tables():
    database.connect()
    database.create_tables([network, vpc, port, portxnetwork, network_profile, network_profilexnetwork, access_switch])





