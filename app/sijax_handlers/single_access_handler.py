"""

Helper for views.py

"""
from base_handler import base_handler
import traceback
import app.model
from flask import g

class single_access_handler(base_handler):

    @staticmethod
    def single_access_handler(obj_response, formvalues):
        """
        Manages all the operations that are involved with a single port association with EPGs
        (for virtual port channel association the vpc_access_handler is used)
        :param obj_response:
        :param formvalues:
        :return:
        """
        try:
            apic_object, values = single_access_handler.init_connections(formvalues)
        except Exception as e:
            print traceback.print_exc()
            obj_response.script("create_notification('Connection problem', '" + str(e).replace("'", "").
                                    replace('"', '').replace("\n", "")[0:100] + "', 'danger', 0)")
            return
        if values['operation'] == 'get_create_single_access_networks':
            # Load the sel_create_single_access_network select with the networks within the selected group
            try:
                network_aps = apic_object.get_ap_by_tenant(values['sel_create_single_access_group'])
                if len(network_aps) > 0:
                    networks = apic_object.get_epg_by_ap(str(network_aps[0].dn))
                    option_list = '<option value="">Select</option>'
                    for network in networks:
                        option_list += '<option value="' + str(network.dn) + '">' + network.name + '</option>'
                    obj_response.html("#sel_create_single_access_network", option_list)
            except Exception as e:
                print traceback.print_exc()
                obj_response.script("create_notification('Can not retrieve networks', '" + str(e).replace("'", "").
                                    replace('"', '').replace("\n", "")[0:100] + "', 'danger', 0)")
            finally:
                g.db.close()
                obj_response.html("#create_single_access_response", '')

        elif values['operation'] == 'get_create_single_access_ports':
            # Load the sel_create_single_access_port select with the available ports within the selected leaf
            try:
                ports = apic_object.get_available_ports(values['sel_create_single_access_leaf'])
                option_list = '<option value="">Select</option>'
                for i in range(0, len(ports[0])):
                    option_list += '<option value="' + ports[0][i] + '">' + ports[1][i] + '</option>'
                obj_response.html("#sel_create_single_access_port", option_list)
            except Exception as e:
                print traceback.print_exc()
                obj_response.script("create_notification('Can not retrieve ports', '" + str(e).replace("'", "").
                                    replace('"', '').replace("\n", "")[0:100] + "', 'danger', 0)")
            finally:
                g.db.close()
                obj_response.html("#create_single_access_response", '')

        elif values['operation'] == 'create_single_access':
            # Creates switch profiles, interface profiles, policy groups and static bindings to associate a port
            # to an EPG
            try:
                port_id = values['sel_create_single_access_port'].split('[')[-1][:-1].replace('/','-')
                switch_id = values['sel_create_single_access_leaf'].split('/')[-1]
                if values['create_port_access_type'] == 'single_vlan':
                    network_o = app.model.network.select().where(app.model.network.epg_dn ==
                                                                 values['sel_create_single_access_network'])
                    if len(network_o) > 0:
                        apic_object.create_single_access(network_o[0].epg_dn,
                                                             values['sel_create_single_access_leaf'],
                                                             values['sel_create_single_access_port'],
                                                             network_o[0].encapsulation,
                                                         'migration-tool',
                                                         'if_policy_' + switch_id + '_' + port_id,
                                                         'single_access_' + switch_id + '_' + port_id)
                        obj_response.script("create_notification('Assigned', '', 'success', 5000)")
                    else:
                        obj_response.script(
                                "create_notification('Network not found in local database', '', 'danger', 0)")
                elif values['create_port_access_type'] == 'vlan_profile':
                    network_profilexnetworks = app.model.network_profilexnetwork.select().where(
                        app.model.network_profilexnetwork.network_profile == int(values['sel_profile_create_port_access']))
                    for network_profile in network_profilexnetworks:
                        network_o = app.model.network.select().where(app.model.network.id == network_profile.network.id)
                        if len(network_o) > 0:
                            apic_object.create_single_access(network_o[0].epg_dn,
                                                             values['sel_create_single_access_leaf'],
                                                             values['sel_create_single_access_port'],
                                                             network_o[0].encapsulation,
                                                         'migration-tool',
                                                         'if_policy_' + switch_id + '_' + port_id,
                                                         'single_access_' + switch_id + '_' + port_id)
                        else:
                            ex = Exception()
                            ex.message = 'Some networks where not assigned because they are not in the local database'
                            raise ex
                    obj_response.script("create_notification('Assigned', '', 'success', 5000)")
            except Exception as e:
                print traceback.print_exc()
                obj_response.script("create_notification('Can not create single access', '" + str(e).replace("'", "").
                                    replace('"', '').replace("\n", "")[0:100] + "', 'danger', 0)")
            finally:
                g.db.close()
                obj_response.html("#create_single_access_response", '')

        elif values['operation'] == 'get_delete_single_access_networks':
            # Load the sel_delete_single_access_network select with the network within the selected group
            try:
                network_aps = apic_object.get_ap_by_tenant(values['sel_delete_single_access_group'])
                if len(network_aps) > 0:
                    networks = apic_object.get_epg_by_ap(str(network_aps[0].dn))
                    option_list = '<option value="">Select</option>'
                    for network in networks:
                        option_list += '<option value="' + str(network.dn) + '">' + network.name + '</option>'
                    obj_response.html("#sel_delete_single_access_network", option_list)
            except Exception as e:
                print traceback.print_exc()
                obj_response.script("create_notification('Can not retrieve networks', '" + str(e).replace("'", "").
                                    replace('"', '').replace("\n", "")[0:100] + "', 'danger', 0)")
            finally:
                g.db.close()
                obj_response.html("#delete_single_access_response", '')

        elif values['operation'] == 'get_delete_single_access_ports':
            # Load the sel_delete_single_access_port select with the available ports from the selected leaf
            try:
                ports = apic_object.get_available_ports(values['sel_delete_single_access_leaf'])
                option_list = '<option value="">Select</option>'
                for i in range(0, len(ports[0])):
                    option_list += '<option value="' + ports[0][i] + '">' + ports[1][i] + '</option>'
                obj_response.html("#sel_delete_single_access_port", option_list)
            except Exception as e:
                print traceback.print_exc()
                obj_response.script("create_notification('Can not retrieve ports', '" + str(e).replace("'", "").
                                    replace('"', '').replace("\n", "")[0:100] + "', 'danger', 0)")
            finally:
                g.db.close()
                obj_response.html("#delete_single_access_response", '')

        elif values['operation'] == 'delete_single_access':
            # Removes the static binding between a port and an EPG. If no other EPG is using this port the system
            # removes also the switch profile, interface profile and policy group associated with the port
            try:
                port_id = values['sel_delete_single_access_port'].split('[')[-1][:-1].replace('/','-')
                switch_id = values['sel_delete_single_access_leaf'].split('/')[-1]
                if values['delete_port_access_type'] == 'single_vlan':
                    network_o = app.model.network.select().where(app.model.network.epg_dn ==
                                                                 values['sel_delete_single_access_network'])
                    if len(network_o) > 0:
                        apic_object.delete_single_access(values['sel_delete_single_access_network'],
                                                         values['sel_delete_single_access_port'],
                                                         'if_policy_' + switch_id + '_' + port_id,
                                                         'single_access_' + switch_id + '_' + port_id)
                        obj_response.script("create_notification('Removed', '', 'success', 5000)")
                    else:
                        obj_response.script(
                            "create_notification('Network not found in local database', '', 'danger', 0)")
                elif values['delete_port_access_type'] == 'vlan_profile':
                    network_profilexnetworks = app.model.network_profilexnetwork.select().where(
                        app.model.network_profilexnetwork.network_profile == int(values['sel_profile_delete_port_access']))
                    for network_profile in network_profilexnetworks:
                        network_o = app.model.network.select().where(app.model.network.id == network_profile.network.id)
                        if len(network_o) > 0:
                            apic_object.delete_single_access(network_o[0].epg_dn,
                                                             values['sel_delete_single_access_port'],
                                                             'if_policy_' + switch_id + '_' + port_id,
                                                             'single_access_' + switch_id + '_' + port_id)

                    obj_response.script("create_notification('Removed', '', 'success', 5000)")



            except Exception as e:
                print traceback.print_exc()
                obj_response.script(
                    "create_notification('Can not delete single access', '" + str(e).replace("'", "").replace('"', '').
                    replace("\n", "")[0:100] + "', 'danger', 0)")
            finally:
                g.db.close()
                obj_response.html("#delete_single_access_response", '')