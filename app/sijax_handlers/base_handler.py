import traceback
import app.model

from app.apic_manager import apic
from app.routefunc import get_values
from flask import g, session
from app.access_switch_manager import switch_controller

__author__ = 'Santiago Flores Kanter (sfloresk@cisco.com)'
COMMAND_WAIT_TIME = 1
handler_app = None

class base_handler:

    @staticmethod
    def init_connections(formvalues):
        values = get_values(formvalues)
        apic_object = apic.Apic()
        apic_object.login(
            session['login_apic_url'],
            session['username'],
            session['password'],
        )
        g.db = app.model.database
        g.db.connect()
        return apic_object, values