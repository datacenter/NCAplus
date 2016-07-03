import traceback
import app.model

from app.apic_manager import cobra_apic_l2_tool, api_apic_base
from flask import g, session

__author__ = 'Santiago Flores Kanter (sfloresk@cisco.com)'
COMMAND_WAIT_TIME = 1
REMOVED_TENANTS=['mgmt','common','infra']


class base_handler:
    @staticmethod
    def init_connections():
        print "Initializing apic connections from base_handler2()"
        """
        Connects to the APIC and return the APIC connection as an object
        :return:
        """
        cobra_apic_object = cobra_apic_l2_tool.cobra_apic_l2_tool()
        cobra_apic_object.login(
            session['login_apic_url'],
            session['username'],
            session['password'],
        )
        g.db = app.model.database
        g.db.connect()
        return cobra_apic_object

    @staticmethod
    def create_api_apic():
        return api_apic_base.api_apic_base(session['login_apic_url'], session['username'], session['password'])

