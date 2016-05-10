import traceback
import app.model

from app.apic_manager import apic_l2_tool
from app.routefunc import get_values
from flask import g, session
from app.access_switch_manager import switch_controller

__author__ = 'Santiago Flores Kanter (sfloresk@cisco.com)'
COMMAND_WAIT_TIME = 1
handler_app = None
SHOW_DEFAULT_TENANTS=False # True will show infra, common and mgmt tennat

class base_handler:

    @staticmethod
    def init_connections(formvalues):
        values = get_values(formvalues)
        apic_object = apic_l2_tool.Apic_l2_tool()
        apic_object.login(
            session['login_apic_url'],
            session['username'],
            session['password'],
        )
        g.db = app.model.database
        g.db.connect()
        return apic_object, values