"""

Helper for views.py

"""
from base_handler import base_handler2, REMOVED_TENANTS
import traceback
import app.model
from flask import g, render_template


class network_handler(base_handler2):

    def __init__(self):
        """
        Manages all the operations related with VLANs/Networks or VLAN profiles
        :return:
        """
        try:
            self.cobra_apic_object = network_handler.init_connections()
            self.exception = None
        except Exception as e:
            self.exception = e
            print traceback.print_exc()

    def create_network(self, obj_response, form_values):
        # Check if there has been connection errors
        if self.exception is not None:
            obj_response.script("create_notification('Connection problem', '" + str(self.exception).replace("'", "").
                                    replace('"', '').replace("\n", "")[0:100] + "', 'danger', 0)")
            return
        # Creates a network in the local database and in ACI creates bridge domains, EPGs and if it
        # is not created, application profiles and VRFs
        try:
            network_object = app.model.network.create(name=form_values['create_network_name'],
                                                      encapsulation=int(form_values['create_network_encapsulation']),
                                                      group=form_values['sel_create_network_group'],
                                                      epg_dn='')
            self.cobra_apic_object.add_vlan(network_object.encapsulation, 'migration-tool')
            epg = self.cobra_apic_object.create_network(network_object)
            self.cobra_apic_object.associate_epg_physical_domain(str(epg.dn), 'migration-tool')
            network_object.update(epg_dn=str(epg.dn)).where(
                app.model.network.id == network_object.id).execute()
            obj_response.script("create_notification('Created', '', 'success', 5000);")
            # Executes javascript function (only after the response is received by the browser)
            obj_response.script("get_sel_delete_networks();get_network_list();")
        except Exception as e:
            print traceback.print_exc()
            obj_response.script("create_notification('Can not create network', '" + str(e).replace("'", "").
                                replace('"', '').replace("\n", "")[0:100] + "', 'danger', 0)")
        finally:
            g.db.close()
            obj_response.html("#create_network_response", '')

    def get_sel_delete_networks(self, obj_response, form_values):
        # Check if there has been connection errors
        if self.exception is not None:
            obj_response.script("create_notification('Connection problem', '" + str(self.exception).replace("'", "").
                                    replace('"', '').replace("\n", "")[0:100] + "', 'danger', 0)")
            return
        # Load the sel_delete_network_name select with the networks available within the tenant selected
        try:
            network_aps = self.cobra_apic_object.get_ap_by_tenant(form_values['sel_delete_network_group'])
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
                obj_response.html("#sel_delete_network_name", html_response)
        except Exception as e:
            print traceback.print_exc()
            obj_response.script("create_notification('Can not retrieve networks', '" + str(e).replace("'", "").
                                replace('"', '').replace("\n", "")[0:100] + "', 'danger', 0)")
        finally:
            g.db.close()
            obj_response.html("#delete_network_response", '')

    def delete_network(self, obj_response, form_values):
        # Check if there has been connection errors
        if self.exception is not None:
            obj_response.script("create_notification('Connection problem', '" + str(self.exception).replace("'", "").
                                    replace('"', '').replace("\n", "")[0:100] + "', 'danger', 0)")
            return
        # Removes a network from the local database and from ACI removes EPGs and bridge domains
        try:
            # Get the network from local database
            network_list = app.model.network.select().where(
                app.model.network.epg_dn == form_values['sel_delete_network_name'])
            if len(network_list) > 0:
                self.cobra_apic_object.remove_vlan(network_list[0].encapsulation, 'migration-tool')
                self.cobra_apic_object.delete_network(network_list[0])
                # Executes javascript functions (only after the response is received by the browser)
                obj_response.script('get_sel_delete_networks();get_network_list()')
                obj_response.script("create_notification('Deleted', '', 'success', 5000)")
                # Delete the network from any network profile
                app.model.network_profilexnetwork.delete().where(
                    app.model.network_profilexnetwork.network == network_list[0].id).execute()
                # Delete network from database
                app.model.network.delete().where(app.model.network.id == network_list[0].id).execute()
            else:
                obj_response.script(
                    "create_notification('Can not delete network', "
                    "'Network not found in local database', 'danger', 0)")
        except Exception as e:
            print traceback.print_exc()
            obj_response.script("create_notification('Can not delete network', '" + str(e).replace("'", "").
                                replace('"', '').replace("\n", "")[0:100] + "', 'danger', 0)")
        finally:
            g.db.close()
            obj_response.html("#delete_network_response", '')

    def get_create_network_profile_networks(self, obj_response, form_values):
        # Check if there has been connection errors
        if self.exception is not None:
            obj_response.script("create_notification('Connection problem', '" + str(self.exception).replace("'", "").
                                    replace('"', '').replace("\n", "")[0:100] + "', 'danger', 0)")
            return
        # Load the select sel_create_network_profile_network with the available EPGs within the selected tenant
        try:
            network_aps = self.cobra_apic_object.get_ap_by_tenant(form_values['sel_create_network_profile_group'])
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
                obj_response.html("#sel_create_network_profile_network", html_response)
        except Exception as e:
            print traceback.print_exc()
            obj_response.script(
                "create_notification('Can not retrieve networks', '" + str(e).replace("'", "").replace('"', '').
                replace("\n", "")[0:100] + "', 'danger', 0)")
        finally:
            g.db.close()
            obj_response.html("#create_network_profile_response", '')

    def create_network_profile(self, obj_response, form_values):
        # Check if there has been connection errors
        if self.exception is not None:
            obj_response.script("create_notification('Connection problem', '" + str(self.exception).replace("'", "").
                                    replace('"', '').replace("\n", "")[0:100] + "', 'danger', 0)")
            return
        # Creates a network profile in the local database
        try:
            network_profile_o = app.model.network_profile.create(name=form_values['create_network_profile_name'])
            # The networks are sent using a hidden input that is loaded before the request using javascript.
            # Each network is separated by a ';' character
            selected_networks = str(form_values['create_network_profile_dns']).split(';')
            for epg_dn in selected_networks:
                if len(epg_dn) > 0:
                    network_list = app.model.network.select().where(app.model.network.epg_dn == epg_dn)
                    if len(network_list) > 0:
                        app.model.network_profilexnetwork.create(network=network_list[0],
                                                                 network_profile=network_profile_o)
                    else:
                        obj_response.script(
                            "create_notification('VLAN " + epg_dn + " not added to profile',"
                                                                    "'Not founded in local database',"
                                                                    "'warning', 0)")
            # Load the table
            table = render_template('network/network_profile_table_partial.html', item_table=[])
            obj_response.html("#table_create_network_profile", table)
            obj_response.html("#sel_create_network_profile_network", '')
            # Executes javascript functions (only after the response is received by the browser)
            obj_response.script('get_network_profiles();get_network_profile_list();')
            obj_response.script('$("#sel_create_network_profile_group").val("")')
            obj_response.script("create_notification('Created', '', 'success', 5000)")
        except Exception as e:
            print traceback.print_exc()
            obj_response.script(
                "create_notification('Can not create VLAN profile', '" + str(e).replace("'", "").replace('"', '').
                replace("\n", "")[0:100] + "', 'danger', 0)")
        finally:
            g.db.close()
            obj_response.html("#create_network_profile_response", '')

    def get_network_profiles(self, obj_response):
        # Check if there has been connection errors
        if self.exception is not None:
            obj_response.script("create_notification('Connection problem', '" + str(self.exception).replace("'", "").
                                    replace('"', '').replace("\n", "")[0:100] + "', 'danger', 0)")
            return
        # Load the network profile selects with the available network/vlan profiles saved in the local database
        try:
            network_profiles = app.model.network_profile.select()
            item_list = []
            for network_p in network_profiles:
                # Creates a dynamic object
                networkp_do = type('networkp_do', (object,), {})
                networkp_do.key = str(network_p.id)
                networkp_do.text = network_p.name
                item_list.append(networkp_do)
            html_response = render_template('select_partial.html', item_list=item_list)
            obj_response.html(".sel-net-profile", html_response)
            obj_response.html("#div_create_vpc_access_response", '')
        except Exception as e:
            print traceback.print_exc()
            obj_response.script(
                "create_notification('Can not retrieve VLAN profile', '" + str(e).replace("'", "").replace('"', '').
                replace("\n", "")[0:100] + "', 'danger', 0)")
        finally:
            g.db.close()
            obj_response.html("#div_create_vpc_access_response", '')

    def get_delete_network_profile_networks(self, obj_response, form_values):
        # Check if there has been connection errors
        if self.exception is not None:
            obj_response.script("create_notification('Connection problem', '" + str(self.exception).replace("'", "").
                                    replace('"', '').replace("\n", "")[0:100] + "', 'danger', 0)")
            return
        # Load the table_delete_network_profile table with the network that are associated with the
        # network/vlan profile
        try:
            network_profile_o = app.model.network_profile.select().where(
                app.model.network_profile.id == int(form_values['sel_delete_network_profile']))[0]

            network_profilexnetwork_list = app.model.network_profilexnetwork.select().where(
                app.model.network_profilexnetwork.network_profile == network_profile_o)
            item_table = []
            for network_profilexnetwork in network_profilexnetwork_list:
                group_mo = self.cobra_apic_object.moDir.lookupByDn(network_profilexnetwork.network.group)
                # Creates a dynamic object
                item = type('network_profile_table_item', (object,), {})
                item.group_name = group_mo.name
                item.network_profile_name = network_profilexnetwork.network.name
                item_table.append(item)
            html_response = render_template('network/network_profile_table_partial.html',
                                            item_table=item_table)
            obj_response.html("#table_delete_network_profile", html_response)
        except Exception as e:
            print traceback.print_exc()
            obj_response.script(
                "create_notification('Can not retrieve networks', '" + str(e).replace("'", "").replace('"', '').
                replace("\n", "")[0:100] + "', 'danger', 0)")
        finally:
            g.db.close()
            obj_response.html("#delete_network_profile_response", '')

    def delete_network_profile(self, obj_response, form_values):
        # Check if there has been connection errors
        if self.exception is not None:
            obj_response.script("create_notification('Connection problem', '" + str(self.exception).replace("'", "").
                                    replace('"', '').replace("\n", "")[0:100] + "', 'danger', 0)")
            return
        # Removes a network/vlan profile from the local database
        try:
            network_profile_o = app.model.network_profile.select().where(
                app.model.network_profile.id == int(form_values['sel_delete_network_profile']))[0]
            app.model.network_profilexnetwork.delete().where(
                app.model.network_profilexnetwork.network_profile == network_profile_o).execute()
            app.model.network_profile.delete().where(
                app.model.network_profile.id == int(form_values['sel_delete_network_profile'])).execute()
            html_response = render_template('network/network_profile_table_partial.html', item_table=[])
            obj_response.html("#table_delete_network_profile", html_response)
            obj_response.script("create_notification('Deleted', '', 'success', 5000)")
        except Exception as e:
            print traceback.print_exc()
            obj_response.script(
                "create_notification('Can not delete VLAN profile', '" + str(e).replace("'", "").replace('"', '').
                replace("\n", "")[0:100] + "', 'danger', 0)")
        finally:
            g.db.close()
            obj_response.html("#delete_network_profile_response", '')
            obj_response.html("#sel_create_network_profile_network", '')
            # Executes javascript functions (only after the response is received by the browser)
            obj_response.script('get_network_profiles();get_network_profile_list();')
            obj_response.script('$("#sel_delete_network_profile").val("")')

    def get_network_list(self, obj_response):
        # Check if there has been connection errors
        if self.exception is not None:
            obj_response.script("create_notification('Connection problem', '" + str(self.exception).replace("'", "").
                                    replace('"', '').replace("\n", "")[0:100] + "', 'danger', 0)")
            return
        # Load the network_list table with the networks that have been created grouped by tenant
        try:
            item_list = []
            for tenant in self.cobra_apic_object.get_all_tenants():
                if tenant.name not in REMOVED_TENANTS:
                    network_aps = self.cobra_apic_object.get_ap_by_tenant(str(tenant.dn))
                    if len(network_aps) > 0:
                        networks = self.cobra_apic_object.get_epg_by_ap(str(network_aps[0].dn))
                        # Creates a dynamic object
                        item = type('item', (object,), {})
                        item.name = tenant.name
                        item.sub_item_list = []
                        for network in networks:
                            # Creates a dynamic object
                            sub_item = type('item', (object,), {})
                            sub_item.name = network.name
                            item.sub_item_list.append(sub_item)
                        item_list.append(item)
            html_response = render_template('collapse_list_partial.html', item_list=item_list)
            obj_response.html("#network_list", html_response)
        except Exception as e:
            print traceback.print_exc()
            obj_response.script("create_notification('Can not retrieve networks', '" + str(e).replace("'", "").
                                replace('"', '').replace("\n", "")[0:100] + "', 'danger', 0)")
        finally:
            g.db.close()
            obj_response.html("#delete_network_response", '')

    def get_network_profile_list(self, obj_response):
        # Check if there has been connection errors
        if self.exception is not None:
            obj_response.script("create_notification('Connection problem', '" + str(self.exception).replace("'", "").
                                    replace('"', '').replace("\n", "")[0:100] + "', 'danger', 0)")
            return
        # Load the network_profile_list with the available network profiles in the local database
        try:
            network_profiles = app.model.network_profile.select()
            item_list = []
            for network_p in network_profiles:
                # Creates a dynamic object
                item = type('item', (object,), {})
                item.name = network_p.name
                item.sub_item_list = []
                network_profilexnetwork_list = app.model.network_profilexnetwork.select().where(
                    app.model.network_profilexnetwork.network_profile == network_p)
                for network_profilexnetwork in network_profilexnetwork_list:
                    # Creates a dynamic object
                    group_mo = self.cobra_apic_object.moDir.lookupByDn(network_profilexnetwork.network.group)
                    sub_item = type('item', (object,), {})
                    sub_item.name = group_mo.name + ' - ' + str(network_profilexnetwork.network.name)
                    item.sub_item_list.append(sub_item)
                item_list.append(item)
            html_response = render_template('collapse_list_partial.html', item_list=item_list)
            obj_response.html("#network_profile_list", html_response)
            obj_response.html("#div_create_vpc_access_response", '')
        except Exception as e:
            print traceback.print_exc()
            obj_response.script(
                "create_notification('Can not retrieve VLAN profile', '" + str(e).replace("'", "").replace('"', '').
                replace("\n", "")[0:100] + "', 'danger', 0)")
        finally:
            g.db.close()
            obj_response.html("#div_create_vpc_access_response", '')

