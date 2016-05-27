import traceback
import app.model

from app.apic_manager import cobra_apic_l2_tool, api_apic_base
from app.routefunc import get_values
from flask import g, session

__author__ = 'Santiago Flores Kanter (sfloresk@cisco.com)'
COMMAND_WAIT_TIME = 1
handler_app = None
REMOVED_TENANTS=['mgmt','common','infra']

class base_handler:
    """
    Base class that all handlers inherit
    """
    @staticmethod
    def init_connections(formvalues):
        """
        Connects to the APIC and set the form values to a dictionary
        :param formvalues:
        :return:
        """
        values = get_values(formvalues)
        apic_object = cobra_apic_l2_tool.cobra_apic_l2_tool()
        apic_object.login(
            session['login_apic_url'],
            session['username'],
            session['password'],
        )
        g.db = app.model.database
        g.db.connect()
        return apic_object, values


class base_handler2:

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

    def create_api_apic(self):
        return api_apic_base.api_apic_base(session['login_apic_url'], session['username'], session['password'])



