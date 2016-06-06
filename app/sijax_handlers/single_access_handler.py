"""

Helper for views.py

"""
from base_handler import base_handler2
import traceback
import app.model
from flask import g, render_template

class single_access_handler(base_handler2):

    def __init__(self):
        """
        Manages all the operations that are involved with a single port association with EPGs
        (for virtual port channel association the vpc_access_handler is used)
        :return:
        """
        try:
            self.cobra_apic_object = single_access_handler.init_connections()
            self.exception = None
        except Exception as e:
            self.exception = e
            print traceback.print_exc()

    def get_create_single_access_networks(self, obj_response, form_values):
        # Check if there has been connection errors
        if self.exception is not None:
            obj_response.script("create_notification('Connection problem', '" + str(self.exception).replace("'", "").
                                    replace('"', '').replace("\n", "")[0:100] + "', 'danger', 0)")
            return
        # Load the sel_create_single_access_network select with the networks within the selected group
        try:
            network_aps = self.cobra_apic_object.get_ap_by_tenant(form_values['sel_create_single_access_group'])
            if len(network_aps) > 0:
                networks = self.cobra_apic_object.get_epg_by_ap(str(network_aps[0].dn))
                item_list = []
                for network in networks:
                    # Creates a dynamic object
                    network_do = type('network_do', (object,), {})
                    network_do.key = str(network.dn)
                    network_do.text = network.name
                    item_list.append(network_do)
                html_response = render_template('select_partial.html', item_list=item_list)
                obj_response.html("#sel_create_single_access_network", html_response)
        except Exception as e:
            print traceback.print_exc()
            obj_response.script("create_notification('Can not retrieve networks', '" + str(e).replace("'", "").
                                replace('"', '').replace("\n", "")[0:100] + "', 'danger', 0)")
        finally:
            g.db.close()
            obj_response.html("#create_single_access_response", '')

    def get_create_single_access_ports(self, obj_response, form_values):
        # Check if there has been connection errors
        if self.exception is not None:
            obj_response.script("create_notification('Connection problem', '" + str(self.exception).replace("'", "").
                                    replace('"', '').replace("\n", "")[0:100] + "', 'danger', 0)")
            return
        # Load the sel_create_single_access_port select with the available ports within the selected leaf
        try:
            ports = self.cobra_apic_object.get_available_ports(form_values['sel_create_single_access_leaf'])
            item_list = []
            for i in range(0, len(ports[0])):
                # Creates a dynamic object
                port_do = type('port_do', (object,), {})
                port_do.key = ports[0][i]
                port_do.text = ports[1][i]
                item_list.append(port_do)
            html_response = render_template('select_partial.html', item_list=item_list)
            obj_response.html("#sel_create_single_access_port", html_response)
        except Exception as e:
            print traceback.print_exc()
            obj_response.script("create_notification('Can not retrieve ports', '" + str(e).replace("'", "").
                                replace('"', '').replace("\n", "")[0:100] + "', 'danger', 0)")
        finally:
            g.db.close()
            obj_response.html("#create_single_access_response", '')

    def create_single_access(self, obj_response, form_values):
        # Check if there has been connection errors
        if self.exception is not None:
            obj_response.script("create_notification('Connection problem', '" + str(self.exception).replace("'", "").
                                    replace('"', '').replace("\n", "")[0:100] + "', 'danger', 0)")
            return
        # Creates switch profiles, interface profiles, policy groups and static bindings to associate a port
        # to an EPG
        try:
            port_id = form_values['sel_create_single_access_port'].split('[')[-1][:-1].replace('/','-')
            switch_id = form_values['sel_create_single_access_leaf'].split('/')[-1]
            if form_values['create_port_access_type'] == 'single_vlan':
                network_o = app.model.network.select().where(app.model.network.epg_dn ==
                                                             form_values['sel_create_single_access_network'])
                if len(network_o) > 0:
                    self.cobra_apic_object.create_single_access(network_o[0].epg_dn,
                                                         form_values['sel_create_single_access_leaf'],
                                                         form_values['sel_create_single_access_port'],
                                                         network_o[0].encapsulation,
                                                     'migration-tool',
                                                     'if_policy_' + switch_id + '_' + port_id,
                                                     'single_access_' + switch_id + '_' + port_id)
                    obj_response.script("create_notification('Assigned', '', 'success', 5000)")
                else:
                    obj_response.script(
                            "create_notification('Network not found in local database', '', 'danger', 0)")
            elif form_values['create_port_access_type'] == 'vlan_profile':
                network_profilexnetworks = app.model.network_profilexnetwork.select().where(
                    app.model.network_profilexnetwork.network_profile == int(form_values['sel_profile_create_port_access']))
                for network_profile in network_profilexnetworks:
                    network_o = app.model.network.select().where(app.model.network.id == network_profile.network.id)
                    if len(network_o) > 0:
                        self.cobra_apic_object.create_single_access(network_o[0].epg_dn,
                                                         form_values['sel_create_single_access_leaf'],
                                                         form_values['sel_create_single_access_port'],
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

    def get_delete_single_access_networks(self, obj_response, form_values):
        # Check if there has been connection errors
        if self.exception is not None:
            obj_response.script("create_notification('Connection problem', '" + str(self.exception).replace("'", "").
                                    replace('"', '').replace("\n", "")[0:100] + "', 'danger', 0)")
            return
        # Load the sel_delete_single_access_network select with the network within the selected group
        try:
            network_aps = self.cobra_apic_object.get_ap_by_tenant(form_values['sel_delete_single_access_group'])
            if len(network_aps) > 0:
                networks = self.cobra_apic_object.get_epg_by_ap(str(network_aps[0].dn))
                item_list = []
                for network in networks:
                    # Creates a dynamic object
                    network_do = type('network_do', (object,), {})
                    network_do.key = str(network.dn)
                    network_do.text = network.name
                    item_list.append(network_do)
                html_response = render_template('select_partial.html', item_list=item_list)
                obj_response.html("#sel_delete_single_access_network", html_response)
        except Exception as e:
            print traceback.print_exc()
            obj_response.script("create_notification('Can not retrieve networks', '" + str(e).replace("'", "").
                                replace('"', '').replace("\n", "")[0:100] + "', 'danger', 0)")
        finally:
            g.db.close()
            obj_response.html("#delete_single_access_response", '')

    def get_delete_single_access_ports(self, obj_response, form_values):
        # Check if there has been connection errors
        if self.exception is not None:
            obj_response.script("create_notification('Connection problem', '" + str(self.exception).replace("'", "").
                                    replace('"', '').replace("\n", "")[0:100] + "', 'danger', 0)")
            return
        # Load the sel_delete_single_access_port select with the available ports from the selected leaf
        try:
            ports = self.cobra_apic_object.get_available_ports(form_values['sel_delete_single_access_leaf'])
            item_list = []
            for i in range(0, len(ports[0])):
                # Creates a dynamic object
                port_do = type('port_do', (object,), {})
                port_do.key = ports[0][i]
                port_do.text = ports[1][i]
                item_list.append(port_do)
            html_response = render_template('select_partial.html', item_list=item_list)
            obj_response.html("#sel_delete_single_access_port", html_response)
        except Exception as e:
            print traceback.print_exc()
            obj_response.script("create_notification('Can not retrieve ports', '" + str(e).replace("'", "").
                                replace('"', '').replace("\n", "")[0:100] + "', 'danger', 0)")
        finally:
            g.db.close()
            obj_response.html("#delete_single_access_response", '')

    def delete_single_access(self, obj_response, form_values):
        # Check if there has been connection errors
        if self.exception is not None:
            obj_response.script("create_notification('Connection problem', '" + str(self.exception).replace("'", "").
                                    replace('"', '').replace("\n", "")[0:100] + "', 'danger', 0)")
            return
        # Removes the static binding between a port and an EPG. If no other EPG is using this port the system
        # removes also the switch profile, interface profile and policy group associated with the port
        try:
            port_id = form_values['sel_delete_single_access_port'].split('[')[-1][:-1].replace('/','-')
            switch_id = form_values['sel_delete_single_access_leaf'].split('/')[-1]
            if form_values['delete_port_access_type'] == 'single_vlan':
                network_o = app.model.network.select().where(app.model.network.epg_dn ==
                                                             form_values['sel_delete_single_access_network'])
                if len(network_o) > 0:
                    self.cobra_apic_object.delete_single_access(form_values['sel_delete_single_access_network'],
                                                     form_values['sel_delete_single_access_port'],
                                                     'if_policy_' + switch_id + '_' + port_id,
                                                     'single_access_' + switch_id + '_' + port_id)
                    obj_response.script("create_notification('Removed', '', 'success', 5000)")
                else:
                    obj_response.script(
                        "create_notification('Network not found in local database', '', 'danger', 0)")
            elif form_values['delete_port_access_type'] == 'vlan_profile':
                network_profilexnetworks = app.model.network_profilexnetwork.select().where(
                    app.model.network_profilexnetwork.network_profile == int(form_values['sel_profile_delete_port_access']))
                for network_profile in network_profilexnetworks:
                    network_o = app.model.network.select().where(app.model.network.id == network_profile.network.id)
                    if len(network_o) > 0:
                        self.cobra_apic_object.delete_single_access(network_o[0].epg_dn,
                                                         form_values['sel_delete_single_access_port'],
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