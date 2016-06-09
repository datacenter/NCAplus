"""

Helper for views.py

"""
from base_handler import base_handler
import traceback
import app.model
from flask import g, render_template

class vpc_access_handler(base_handler):

    def __init__(self):
        """
        Handles all operations related to virtual port channels association with EPGs (for single port associations
        single_access_handler is used)
        """
        try:
            self.cobra_apic_object = vpc_access_handler.init_connections()
            self.exception = None
        except Exception as e:
            self.exception = e
            print traceback.print_exc()

    def create_vpc_access(self, obj_response, form_values):
        # Creates an static binding between a virtual port channel and a EPG
        try:
            if form_values['create_vpc_access_type'] == 'single_vlan':
                network_o = app.model.network.select().where(app.model.network.epg_dn ==
                                                             form_values['sel_network_create_vpc_access'])
                if len(network_o) > 0:
                    self.cobra_apic_object.associate_epg_vpc(form_values['sel_network_create_vpc_access'],
                                                  form_values['sel_vpc_create_vpc_access'], network_o[0].encapsulation)
                    obj_response.script("create_notification('Assigned', '', 'success', 5000)")
                else:
                    obj_response.script(
                            "create_notification('Can not create VPC access', "
                            "'Network not found in local database', 'danger', 0)"
                        )
            elif form_values['create_vpc_access_type'] == 'vlan_profile':
                network_profilexnetworks = app.model.network_profilexnetwork.select().where(
                    app.model.network_profilexnetwork.network_profile == int(form_values['sel_profile_create_vpc_access']))
                for network_profile in network_profilexnetworks:
                    network_o = app.model.network.select().where(app.model.network.id == network_profile.network.id)
                    if len(network_o) > 0:
                        self.cobra_apic_object.associate_epg_vpc(network_o[0].epg_dn,
                                                      form_values['sel_vpc_create_vpc_access'],
                                                      network_o[0].encapsulation)
                    else:
                        ex = Exception()
                        ex.message = 'Some networks where not assigned because they are not in the local database'
                        raise ex
                obj_response.script("create_notification('Assigned', '', 'success', 5000)")
            obj_response.script("get_vpc_assignment_list();")
        except Exception as e:
            print traceback.print_exc()
            obj_response.script("create_notification('Can not create VPC access', '" + str(e).replace("'", "").
                                replace('"', '').replace("\n", "")[0:100] + "', 'danger', 0)")
        finally:
            g.db.close()
            obj_response.html("#div_create_vpc_access_response", '')

    def get_create_vpc_access_networks(self, obj_response, form_values):
        # Load the sel_network_create_vpc_access with the networks within the selected group
        try:
            network_aps = self.cobra_apic_object.get_ap_by_tenant(form_values['sel_group_create_vpc_access'])
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
                obj_response.html("#sel_network_create_vpc_access", html_response)
        except Exception as e:
            print traceback.print_exc()
            obj_response.script("create_notification('Can not retrieve networks', '" + str(e).replace("'", "").
                                replace('"', '').replace("\n", "")[0:100] + "', 'danger', 0)")
        finally:
            g.db.close()
            obj_response.html("#div_create_vpc_access_response", '')

    def get_delete_vpc_access_networks(self, obj_response, form_values):
        # Load the sel_network_delete_vpc_access with the networks within the selected group
        try:
            network_aps = self.cobra_apic_object.get_ap_by_tenant(form_values['sel_group_delete_vpc_access'])
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
                obj_response.html("#sel_network_delete_vpc_access", html_response)
        except Exception as e:
            print traceback.print_exc()
            obj_response.script("create_notification('Can not retrieve networks', '" + str(e).replace("'", "").
                                replace('"', '').replace("\n", "")[0:100] + "', 'danger', 0)")
        finally:
            g.db.close()
            obj_response.html("#div_delete_vpc_access_response", '')

    def get_delete_vpc_access_assignments(self, obj_response, form_values):
        # Load the sel_vpc_delete_vpc_access select with the vpc static bindings associated to the selected network
        try:
            vpc_assignments = self.cobra_apic_object.get_vpc_assignments_by_epg(form_values['sel_network_delete_vpc_access'])
            item_list = []
            for vpc_assignment in vpc_assignments:
                # Creates a dynamic object
                vpc_assignment_do = type('vpc_assignment_do', (object,), {})
                vpc_assignment_do.key = str(vpc_assignment.dn)
                vpc_assignment_do.text = str(vpc_assignment.tDn).split('[')[1][:-1]
                item_list.append(vpc_assignment_do)
            html_response = render_template('select_partial.html', item_list=item_list)
            obj_response.html("#sel_vpc_delete_vpc_access", html_response)
        except Exception as e:
            print traceback.print_exc()
            obj_response.script("create_notification('Can not retrieve networks', '" + str(e).replace("'", "").
                                replace('"', '').replace("\n", "")[0:100] + "', 'danger', 0)")
        finally:
            g.db.close()
            obj_response.html("#div_delete_vpc_access_response", '')

    def delete_vpc_access(self, obj_response, form_values):
        # Deletes a static binding between the selected network and the selected virtual port channel
        try:
            if form_values['delete_vpc_access_type'] == 'single_vlan':
                self.cobra_apic_object.delete_vpc_assignment(form_values['sel_vpc_delete_vpc_access'])
                obj_response.script("create_notification('Removed', '', 'success', 5000)")
                obj_response.script('get_delete_vpc_access_assignments()')
            elif form_values['delete_vpc_access_type'] == 'vlan_profile':
                network_profile_o = app.model.network_profile.select().where(
                    app.model.network_profile.id == int(form_values['sel_profile_delete_vpc_access'])
                )[0]
                network_profilexnetwork_list = app.model.network_profilexnetwork.select().where(
                    app.model.network_profilexnetwork.network_profile == network_profile_o)

                for network_profilexnetwork in network_profilexnetwork_list:
                    vpc_assignments = self.cobra_apic_object.get_vpc_assignments_by_epg(network_profilexnetwork.network.epg_dn)
                    for vpc_assignment in vpc_assignments:
                        if str(vpc_assignment.tDn) == form_values['sel_vpc_delete_vpc_access_profile']:
                            self.cobra_apic_object.delete_vpc_assignment(str(vpc_assignment.dn))
                obj_response.script("create_notification('Removed', '', 'success', 5000)")
            obj_response.script("get_vpc_assignment_list();")
        except Exception as e:
            print traceback.print_exc()
            obj_response.script("create_notification('Can not delete VPC access', '" + str(e).replace("'", "").
                                replace('"', '').replace("\n", "")[0:100] + "', 'danger', 0)")
        finally:
            g.db.close()
            obj_response.html("#div_delete_vpc_access_response", '')

    def get_vpc_assignment_list(self, obj_response):
        # load the vpc_assigment_list with all the vpc static bindings grouped by vpc
        try:
            vpc_list = self.cobra_apic_object.get_vpcs()
            vpc_assignments = self.cobra_apic_object.get_vpc_assignments()
            item_list = []
            for vpc in vpc_list:
                # Creates a dynamic object
                item = type('item', (object,), {})
                item.name = vpc.name
                item.sub_item_list = []
                if vpc.name in vpc_assignments.keys():
                    for epg_name in vpc_assignments[vpc.name]:
                        # Creates a dynamic object
                        sub_item = type('item', (object,), {})
                        sub_item.name = epg_name
                        item.sub_item_list.append(sub_item)
                item_list.append(item)
            html_response = render_template('collapse_list_partial.html', item_list=item_list)
            obj_response.html("#vpc_assignment_list", html_response)
        except Exception as e:
            print traceback.print_exc()
            obj_response.script("create_notification('Can not retrieve VPC assignments', '" + str(e).replace("'", "").
                                replace('"', '').replace("\n", "")[0:100] + "', 'danger', 0)")
        finally:
            g.db.close()
