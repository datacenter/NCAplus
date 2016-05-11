"""
*************************************************************************
 Copyright (c) 2016 Cisco Systems, Inc.  All rights reserved.
*************************************************************************
Helper for views.py

"""
from base_handler import base_handler
import traceback
import app.model
from flask import g

class fabric_handler(base_handler):

    @staticmethod
    def fabric_handler(obj_response, formvalues):
        """
        Handles all operations related to the fabric hardware such as get the ports or switches within ACI
        :param obj_response:
        :param formvalues:
        :return:
        """
        try:
            apic_object, values = fabric_handler.init_connections(formvalues)
        except Exception as e:
            print traceback.print_exc()
            obj_response.script("create_notification('Connection problem', '" + str(e).replace("'", "").
                                    replace('"', '').replace("\n", "")[0:100] + "', 'danger', 0)")
            return
        if values['operation'] == 'get_leafs':
            # Load the select that show all the leafs within the fabric
            try:
                option_list = '<option value="">Select</option>'
                leafs = apic_object.get_leafs()
                for i in range(0, len(leafs[0])):
                    option_list += '<option value="' + leafs[0][i] + '">' + leafs[1][i] + '</option>'
                obj_response.html(".sel-leaf", option_list)
            except Exception as e:
                print traceback.print_exc()
                obj_response.script("create_notification('Can not retrieve leafs', '" + str(e).replace("'", "").
                                    replace('"', '').replace("\n", "")[0:100] + "', 'danger', 0)")
            finally:
                g.db.close()
                obj_response.html("#create_vpc_response", '')

        elif values['operation'] == 'get_ports':
            # Load the sel_port_create_vpc select, only with available ports that are not used in virtual port channels
            try:
                option_list = '<option value="">Select</option>'
                ports = apic_object.get_available_ports(values['sel_leaf_create_vpc'])
                for i in range(0, len(ports[0])):
                    port_list = app.model.port.select().where(app.model.port.port_dn == ports[0][i])
                    if len(port_list) > 0:
                        # Port already exists in database.. checking availability
                        port_o = port_list[0]
                        portxnetwork_list = app.model.portxnetwork.select().where(
                            app.model.portxnetwork.switch_port == port_o.id)
                        if port_o.assigned_vpc is None and len(portxnetwork_list) == 0:
                            option_list += '<option value="' + ports[0][i] + '">' + ports[1][i] + '</option>'
                    else:
                        # Port does not exist, it is available
                        option_list += '<option value="' + ports[0][i] + '">' + ports[1][i] + '</option>'
                obj_response.html("#sel_port_create_vpc", option_list)
            except Exception as e:
                print traceback.print_exc()
                obj_response.script("create_notification('Can not retrieve ports', '" + str(e).replace("'", "").
                                    replace('"', '').replace("\n", "")[0:100] + "', 'danger', 0)")
            finally:
                g.db.close()
                obj_response.html("#create_vpc_response", '')

        elif values['operation'] == 'get_health_dashboard':
            # Load the web page that shows the health scores of the system and of the switches (/monitor)
            try:
                system_health = apic_object.get_system_health()
                if int(system_health) < 90:
                    html_class = 'panel-danger'
                else:
                    html_class = 'panel-success'
                html_response = '<div id="system_health" class="panel ' + html_class + '">' \
                                        '<div class="panel-heading"> System' \
                                        '</div>' \
                                        '<div class="panel-body">'\
                                    '<div class="form-group">' \
                                            '<label class="col-lg-6 col-md-6 col-sm-6 col-xs-12">Health' \
                                            '</label>' \
                                            '<div class="col-lg-6 col-md-6 col-sm-6 col-xs-12">' \
                                                '<label class="col-lg-6 col-md-6 col-sm-6 col-xs-12">' \
                                                + system_health + \
                                                '</label>' \
                                            '</div>' \
                                        '</div>' \
                                        '<hr>'
                html_response += '</div></div>'
                dashboard = apic_object.get_health_dashboard()
                for item in dashboard.keys():
                    for sub_item in dashboard[item].keys():
                        if sub_item == 'Health':
                            if int(dashboard[item][sub_item]) < 90:
                                html_class = 'panel-danger'
                            else:
                                html_class = 'panel-success'
                    html_response += '<div id="' + item.replace(' ','_') + '" class="panel ' + html_class + '">' \
                                        '<div class="panel-heading">' + item + \
                                        '</div>' \
                                        '<div class="panel-body">'
                    for sub_item in dashboard[item].keys():
                        html_response +='<div class="form-group">' \
                                            '<label class="col-lg-6 col-md-6 col-sm-6 col-xs-12">' + sub_item + \
                                            '</label>' \
                                            '<div class="col-lg-6 col-md-6 col-sm-6 col-xs-12">' \
                                                '<label class="col-lg-6 col-md-6 col-sm-6 col-xs-12">' \
                                                + dashboard[item][sub_item] + \
                                                '</label>' \
                                            '</div>' \
                                        '</div>' \
                                        '<hr>'
                    html_response += '</div></div>'
                obj_response.html('#noc_monitor_tab', html_response)
            except Exception as e:
                print traceback.print_exc()
                obj_response.script("create_notification('Can not retrieve health scores', '" + str(e).replace("'", "").
                                    replace('"', '').replace("\n", "")[0:100] + "', 'danger', 0)")
            finally:
                g.db.close()
                obj_response.html("#noc_monitor_response", '')
