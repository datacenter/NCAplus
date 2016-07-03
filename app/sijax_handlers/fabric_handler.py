"""
Helper for views.py

"""
from base_handler import base_handler
import traceback
import app.model
from flask import g, render_template

class fabric_handler(base_handler):

    def __init__(self):
        """
        Handles all operations related to the fabric hardware such as
        get the ports or switches within ACI
        """
        try:
            self.cobra_apic_object = fabric_handler.init_connections()
            self.api_apic_object = fabric_handler.create_api_apic()
            self.exception = None
        except Exception as e:
            self.exception = e
            print traceback.print_exc()

    def get_leafs(self, obj_response):
        # Check if there has been connection errors
        if self.exception is not None:
            obj_response.script("create_notification('Connection problem', '" + str(self.exception).replace("'", "").
                                    replace('"', '').replace("\n", "")[0:100] + "', 'danger', 0)")
            return
        # Load the select that show all the leafs within the fabric
        try:
            item_list = []
            leafs = self.cobra_apic_object.get_leafs()
            for i in range(0, len(leafs[0])):
                # Creates a dynamic object
                leaf_do = type('leaf_do', (object,), {})
                leaf_do.key = str(leafs[0][i])
                leaf_do.text = leafs[1][i]
                item_list.append(leaf_do)
            html_response = render_template('select_partial.html', item_list=item_list)
            obj_response.html(".sel-leaf", html_response)
        except Exception as e:
            print traceback.print_exc()
            obj_response.script("create_notification('Can not retrieve leafs', '" + str(e).replace("'", "").
                                replace('"', '').replace("\n", "")[0:100] + "', 'danger', 0)")
        finally:
            g.db.close()
            obj_response.html("#create_vpc_response", '')

    def get_ports(self, obj_response, form_values):
        # Check if there has been connection errors
        if self.exception is not None:
            obj_response.script("create_notification('Connection problem', '" + str(self.exception).replace("'", "").
                                    replace('"', '').replace("\n", "")[0:100] + "', 'danger', 0)")
            return
        # Load the sel_port_create_vpc select, only with available ports that are not used in virtual port channels
        try:
            item_list = []
            ports = self.cobra_apic_object.get_available_ports(form_values['sel_leaf_create_vpc'])
            for i in range(0, len(ports[0])):
                port_list = app.model.port.select().where(app.model.port.port_dn == ports[0][i])
                if len(port_list) > 0:
                    # Port already exists in database.. checking availability
                    port_o = port_list[0]
                    portxnetwork_list = app.model.portxnetwork.select().where(
                        app.model.portxnetwork.switch_port == port_o.id)
                    if port_o.assigned_vpc is None and len(portxnetwork_list) == 0:
                        # Creates a dynamic object
                        port_do = type('port_do', (object,), {})
                        port_do.key = ports[0][i]
                        port_do.text = ports[1][i]
                        item_list.append(port_do)
                else:
                    # Port does not exist, it is available
                    # Creates a dynamic object
                    port_do = type('port_do', (object,), {})
                    port_do.key = ports[0][i]
                    port_do.text = ports[1][i]
                    item_list.append(port_do)
            html_response = render_template('select_partial.html', item_list=item_list)
            obj_response.html("#sel_port_create_vpc", html_response)
        except Exception as e:
            print traceback.print_exc()
            obj_response.script("create_notification('Can not retrieve ports', '" + str(e).replace("'", "").
                                replace('"', '').replace("\n", "")[0:100] + "', 'danger', 0)")
        finally:
            g.db.close()
            obj_response.html("#create_vpc_response", '')

    def get_cobra_compatibility(self, obj_response):
        # Check if there has been connection errors
        if self.exception is not None:
            obj_response.script("create_notification('Connection problem', '" + str(self.exception).replace("'", "").
                                    replace('"', '').replace("\n", "")[0:100] + "', 'danger', 0)")
            return
        # Check if APIC and Cobra are in the same version
        if self.cobra_apic_object.get_cobra_version() != self.api_apic_object.apic_version.replace('(','-').replace(')',''):
            obj_response.script(
                "compatibility_check(false,'" + self.cobra_apic_object.get_cobra_version() +
                "','" + self.api_apic_object.apic_version.replace('(','-').replace(')','') + "');")
