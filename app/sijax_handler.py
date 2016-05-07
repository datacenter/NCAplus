"""
*************************************************************************
 Copyright (c) 2016 Cisco Systems, Inc.  All rights reserved.
*************************************************************************
Helper for views.py

"""
import traceback
import model

from apic_manager import apic
from routefunc import get_values
from flask import g, session
from access_switch_manager import switch_controller

__author__ = 'Santiago Flores Kanter (sfloresk@cisco.com)'
COMMAND_WAIT_TIME = 1
handler_app = None


class handler:

    @staticmethod
    def init_connections(formvalues):
        values = get_values(formvalues)
        apic_object = apic.Apic()
        apic_object.login(
            session['login_apic_url'],
            session['username'],
            session['password'],
        )
        g.db = model.database
        g.db.connect()
        return apic_object, values

    @staticmethod
    def group_handler(obj_response, formvalues):
        try:
            apic_object, values = handler.init_connections(formvalues)
        except Exception as e:
            print traceback.print_exc()
            obj_response.script("create_notification('Connection problem', '" + str(e).replace("'", "").
                                    replace('"', '').replace("\n", "")[0:100] + "', 'danger', 0)")
            return
        if values['operation'] == 'get_groups':
            try:
                tenants = apic_object.get_all_tenants()
                option_list = '<option value="">Select</option>'
                for tenant in tenants:
                    option_list += '<option value="' + str(tenant.dn) + '">' + tenant.name + '</option>'
                obj_response.html(".sel-group", option_list)
            except Exception as e:
                print traceback.print_exc()
                obj_response.script("create_notification('Can not retrieve groups', '" + str(e).replace("'", "").
                                    replace('"', '').replace("\n", "")[0:100] + "', 'danger', 0)")
            finally:
                g.db.close()
                obj_response.html("#create_network_response", '')

        elif values['operation'] == 'tenant_list':
            try:
                tenants = apic_object.get_all_tenants()
                all_tenants_list = '<div style="font-size:.8em;">'
                for tenant in tenants:
                    all_tenants_list += str(tenant.name) + '</br>'
                obj_response.html("#tenant_list", all_tenants_list)
                all_tenants_list += "</div>"
            except Exception as e:
                print traceback.print_exc()
                obj_response.script("create_notification('Can not retrieve group list', '" + str(e).replace("'", "").
                                    replace('"', '').replace("\n", "")[0:100] + "', 'danger', 0)")
            finally:
                g.db.close()
                #obj_response.html("#get_group_list", '')

        elif values['operation'] == 'create_group':
            try:
                apic_object.create_group(values['create_group_name'])
                obj_response.script("create_notification('Created', '', 'success', 5000)")
                obj_response.script('get_groups();')
            except Exception as e:
                print traceback.print_exc()
                obj_response.script("create_notification('Can not create group', '" + str(e).replace("'", "").
                                    replace('"', '').replace("\n", "")[0:100] + "', 'danger', 0)")
            finally:
                g.db.close()
                obj_response.html("#create_group_response", '')

        elif values['operation'] == 'delete_group':
            try:
                apic_object.delete_tenant(values['sel_delete_group_name'])
                obj_response.script("get_groups();")
                obj_response.script("create_notification('Deleted', '', 'success', 5000)")
            except Exception as e:
                print traceback.print_exc()
                obj_response.script("create_notification('Can not delete group', '" + str(e).replace("'", "").
                                    replace('"', '').replace("\n", "")[0:100] + "', 'danger', 0)")
            finally:
                g.db.close()
                obj_response.html("#delete_group_response", '')

    @staticmethod
    def network_handler(obj_response, formvalues):
        try:
            apic_object, values = handler.init_connections(formvalues)
        except Exception as e:
            print traceback.print_exc()
            obj_response.script("create_notification('Connection problem', '" + str(e).replace("'", "").
                                    replace('"', '').replace("\n", "")[0:100] + "', 'danger', 0)")
            return
        if values['operation'] == 'create_network':
            try:
                network_object = model.network.create(name=values['create_network_name'],
                                                      encapsulation=int(values['create_network_encapsulation']),
                                                      group=values['sel_create_network_group'],
                                                      epg_dn='')
                apic_object.add_vlan(network_object.encapsulation, 'migration-tool')
                epg = apic_object.create_network(network_object)
                apic_object.associate_epg_physical_domain(str(epg.dn), 'migration-tool')
                network_object.update(epg_dn=str(epg.dn)).where(
                    model.network.id == network_object.id).execute()

                obj_response.script("create_notification('Created', '', 'success', 5000)")
            except Exception as e:
                print traceback.print_exc()
                obj_response.script("create_notification('Can not create network', '" + str(e).replace("'", "").
                                    replace('"', '').replace("\n", "")[0:100] + "', 'danger', 0)")
            finally:
                g.db.close()
                obj_response.html("#create_network_response", '')

        elif values['operation'] == 'get_sel_delete_networks':
            try:
                network_aps = apic_object.get_ap_by_tenant(values['sel_delete_network_group'])
                if len(network_aps) > 0:
                    networks = apic_object.get_epg_by_ap(str(network_aps[0].dn))
                    option_list = '<option value="">Select</option>'
                    for network in networks:
                        option_list += '<option value="' + str(network.dn) + '">' + network.name + '</option>'
                    obj_response.html("#sel_delete_network_name", option_list)
            except Exception as e:
                print traceback.print_exc()
                obj_response.script("create_notification('Can not retrieve networks', '" + str(e).replace("'", "").
                                    replace('"', '').replace("\n", "")[0:100] + "', 'danger', 0)")
            finally:
                g.db.close()
                obj_response.html("#delete_network_response", '')

        elif values['operation'] == 'delete_network':
            try:
                # Get the network from local database
                network_list = model.network.select().where(model.network.epg_dn == values['sel_delete_network_name'])
                if len(network_list) > 0:
                    apic_object.remove_vlan(network_list[0].encapsulation, 'migration-tool')
                    apic_object.delete_network(network_list[0])
                    obj_response.script('get_sel_delete_networks()')
                    obj_response.script("create_notification('Deleted', '', 'success', 5000)")
                    # Delete the network from any network profile
                    model.network_profilexnetwork.delete().where(
                        model.network_profilexnetwork.network == network_list[0].id).execute()
                    # Delete network from database
                    model.network.delete().where(model.network.id == network_list[0].id).execute()
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

        elif values['operation'] == 'get_create_network_profile_networks':
            try:
                network_aps = apic_object.get_ap_by_tenant(values['sel_create_network_profile_group'])
                if len(network_aps) > 0:
                    networks = apic_object.get_epg_by_ap(str(network_aps[0].dn))
                    option_list = '<option value="">Select</option>'
                    for network in networks:
                        option_list += '<option value="' + str(network.dn) + '">' + network.name + '</option>'
                    obj_response.html("#sel_create_network_profile_network", option_list)
            except Exception as e:
                print traceback.print_exc()
                obj_response.script(
                    "create_notification('Can not retrieve networks', '" + str(e).replace("'", "").replace('"', '').
                    replace("\n", "")[0:100] + "', 'danger', 0)")
            finally:
                g.db.close()
                obj_response.html("#create_network_profile_response", '')

        elif values['operation'] == 'create_network_profile':
            try:
                network_profile_o = model.network_profile.create(name=values['create_network_profile_name'])
                selected_networks = str(values['create_network_profile_dns']).split(';')
                for epg_dn in selected_networks:
                    if len(epg_dn) > 0:
                        network_list = model.network.select().where(model.network.epg_dn == epg_dn)
                        if len(network_list) > 0:
                            model.network_profilexnetwork.create(network=network_list[0],
                                                                 network_profile=network_profile_o)
                        else:
                            obj_response.script(
                                "create_notification('VLAN " + epg_dn + " not added to profile',"
                                                                        "'Not founded in local database',"
                                                                        "'warning', 0)")

                table = '<thead>' \
                            '<tr>' \
                                '<th>Group</th>' \
                                '<th>Network</th>' \
                            '</tr>' \
                        '</thead>' \
                        '<tbody>' \
                        '<tr></tr>' \
                        '</tbody>'
                obj_response.html("#table_create_network_profile", table)
                obj_response.html("#sel_create_network_profile_network", '')
                obj_response.script('get_network_profiles()')
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

        elif values['operation'] == 'get_network_profiles':
            try:
                network_profiles = model.network_profile.select()
                option_list = '<option value="">Select</option>'
                for network_p in network_profiles:
                    option_list += '<option value="' + str(network_p.id) + '">' + network_p.name + '</option>'
                obj_response.html(".sel-net-profile", option_list)
                obj_response.html("#div_create_vpc_access_response", '')
            except Exception as e:
                print traceback.print_exc()
                obj_response.script(
                    "create_notification('Can not retrieve VLAN profile', '" + str(e).replace("'", "").replace('"', '').
                    replace("\n", "")[0:100] + "', 'danger', 0)")
            finally:
                g.db.close()
                obj_response.html("#div_create_vpc_access_response", '')

        elif values['operation'] == 'get_delete_network_profile_networks':
            try:
                network_profile_o = model.network_profile.select().where(
                model.network_profile.id == int(values['sel_delete_network_profile']))[0]

                network_profilexnetwork_list = model.network_profilexnetwork.select().where(
                    model.network_profilexnetwork.network_profile == network_profile_o)
                table = '<thead>' \
                            '<tr>' \
                                '<th>Group</th>' \
                                '<th>Network</th>' \
                            '</tr>' \
                        '</thead>' \
                        '<tbody>'
                for network_profilexnetwork in network_profilexnetwork_list:
                    group_mo = apic_object.moDir.lookupByDn(network_profilexnetwork.network.group)
                    table += '<tr><td>' \
                                 + group_mo.name + \
                             '</td><td>' \
                                 + network_profilexnetwork.network.name + \
                             '</td></tr>'
                table +='</tbody>'
                obj_response.html("#table_delete_network_profile", table)
            except Exception as e:
                print traceback.print_exc()
                obj_response.script(
                    "create_notification('Can not retrieve networks', '" + str(e).replace("'", "").replace('"', '').
                    replace("\n", "")[0:100] + "', 'danger', 0)")
            finally:
                g.db.close()
                obj_response.html("#delete_network_profile_response", '')

        elif values['operation'] == 'delete_network_profile':
            try:
                network_profile_o = model.network_profile.select().where(
                model.network_profile.id == int(values['sel_delete_network_profile']))[0]
                model.network_profilexnetwork.delete().where(
                    model.network_profilexnetwork.network_profile == network_profile_o).execute()
                model.network_profile.delete().where(
                    model.network_profile.id == int(values['sel_delete_network_profile'])).execute()
                table = '<thead>' \
                            '<tr>' \
                                '<th>Group</th>' \
                                '<th>Network</th>' \
                            '</tr>' \
                        '</thead>' \
                        '<tbody>'
                table += '<tr><td>' \
                             '</td><td>' \
                             '</td></tr>'
                table += '</tbody>'
                obj_response.html("#table_delete_network_profile", table)
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
                obj_response.script('get_network_profiles()')
                obj_response.script('$("#sel_delete_network_profile").val("")')

    @staticmethod
    def fabric_handler(obj_response, formvalues):
        try:
            apic_object, values = handler.init_connections(formvalues)
        except Exception as e:
            print traceback.print_exc()
            obj_response.script("create_notification('Connection problem', '" + str(e).replace("'", "").
                                    replace('"', '').replace("\n", "")[0:100] + "', 'danger', 0)")
            return
        if values['operation'] == 'get_leafs':
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
            # """ Returns only available ports """
            try:
                option_list = '<option value="">Select</option>'
                ports = apic_object.get_available_ports(values['sel_leaf_create_vpc'])
                for i in range(0, len(ports[0])):
                    port_list = model.port.select().where(model.port.port_dn == ports[0][i])
                    if len(port_list) > 0:
                        # Port already exists in database.. checking availability
                        port_o = port_list[0]
                        portxnetwork_list = model.portxnetwork.select().where(
                            model.portxnetwork.switch_port == port_o.id)
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
            # """ Returns only available ports """
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

    @staticmethod
    def vpc_handler(obj_response, formvalues):
        try:
            apic_object, values = handler.init_connections(formvalues)
        except Exception as e:
            print traceback.print_exc()
            obj_response.script("create_notification('Connection problem', '" + str(e).replace("'", "").
                                    replace('"', '').replace("\n", "")[0:100] + "', 'danger', 0)")
            return
        if values['operation'] == 'create_vpc':
            try:
                # check if vpc has a unique name
                vpc_list = apic_object.get_vpcs()
                for vpc in vpc_list:
                    if vpc.name.lower() == values['create_vpc_name'].lower():
                        ex = Exception()
                        ex.message = 'That name has been used before'
                        raise ex
                selected_ports = str(values['port_dns']).split(';')
                switch_mo_list = []
                for port_dn in selected_ports:
                    if len(port_dn) > 0:
                        switch_mo = apic_object.get_switch_by_port(port_dn)
                        switch_mo_list.append(switch_mo)
                        if_policy_group_mo = apic_object.create_if_policy_group(values['create_vpc_name'], 'migration-tool')
                        if_profile = apic_object.create_vpc_interface_profile(
                            port_dn, if_policy_group_mo.dn, values['create_vpc_name']
                        )
                        apic_object.create_vpc_switch_profile(
                            str(switch_mo.dn), str(if_profile.dn), values['create_vpc_name']
                        )

                vpc_list = model.vpc.select()
                option_list = '<option value="">Select</option>'
                for vpc in vpc_list:
                   option_list += '<option value="' + str(vpc.id) + '">' + vpc.name + '</option>'
                obj_response.html(".sel-vpc", option_list)
                table = '<thead>' \
                            '<tr>' \
                                '<th>Switch</th>' \
                                '<th>Port</th>' \
                            '</tr>' \
                        '</thead>' \
                        '<tbody>' \
                        '<tr></tr>' \
                        '</tbody>'
                obj_response.html("#vpc_ports", table)
                obj_response.html("#sel_port_create_vpc", '')
                obj_response.script('$("#create_vpc_name").val("")')
                obj_response.script('$("#sel_leaf_create_vpc").val("")')
                obj_response.script('get_vpcs()')
                obj_response.script("create_notification('Created', '', 'success', 5000)")
            except Exception as e:
                print traceback.print_exc()
                obj_response.script("create_notification('Can not create VPC', '" + str(e).replace("'", "").
                                    replace('"', '').replace("\n", "")[0:100] + "', 'danger', 0)")
            finally:
                g.db.close()
                obj_response.html("#create_vpc_response", '')

        elif values['operation'] == 'get_delete_vpc_assigned_ports':
            try:
                port_list = apic_object.get_vpc_ports(values['sel_delete_vpc_name'])
                table = '<thead>' \
                            '<tr>' \
                                '<th>Switch</th>' \
                                '<th>Port</th>' \
                            '</tr>' \
                        '</thead>' \
                        '<tbody>'
                for vpc_port_mo in port_list:
                    switch_mo = apic_object.get_switch_by_vpc_port(str(vpc_port_mo.dn))
                    table += '<tr><td>' + str(switch_mo.rn) + '</td><td>' + str(vpc_port_mo.tSKey) + '</td></tr>'
                table += '</tbody>'
                obj_response.html("#delete_vpc_ports", table)
            except Exception as e:
                print traceback.print_exc()
                obj_response.script("create_notification('Can not retrieve ports', '" + str(e).replace("'", "").
                                    replace('"', '').replace("\n", "")[0:100] + "', 'danger', 0)")
            finally:
                g.db.close()
                obj_response.html("#delete_vpc_response", '')

        elif values['operation'] == 'get_vpcs':
            try:
                vpc_list = apic_object.get_vpcs()
                option_list = '<option value="">Select</option>'
                for vpc in vpc_list:
                   option_list += '<option value="' + str(vpc.dn) + '">' + vpc.name + '</option>'
                obj_response.html(".sel-vpc", option_list)
            except Exception as e:
                print traceback.print_exc()
                obj_response.script("create_notification('Can not retrieve VPCs', '" + str(e).replace("'", "").
                                    replace('"', '').replace("\n", "")[0:100] + "', 'danger', 0)")
            finally:
                g.db.close()
                obj_response.html("#delete_vpc_response", '')

        elif values['operation'] == 'delete_vpc':
            try:
                apic_object.delete_vpc(values['sel_delete_vpc_name'])
                obj_response.script('get_vpcs();')
                obj_response.html("#delete_vpc_ports", "")
                obj_response.script("create_notification('Deleted', '', 'success', 5000)")
            except Exception as e:
                print traceback.print_exc()
                obj_response.script("create_notification('Can not delete VPC', '" + str(e).replace("'", "").
                                    replace('"', '').replace("\n", "")[0:100] + "', 'danger', 0)")
            finally:
                g.db.close()
                obj_response.html("#delete_vpc_response", '')

        elif values['operation'] == 'get_leafs_by_vpc_group':
            try:
                option_list = '<option value="">Select</option>'
                leafs = apic_object.get_leaf_by_explicit_group(values['sel_vpc_group_create_vpc'])
                for i in range(0, len(leafs[0])):
                    option_list += '<option value="' + leafs[0][i] + '">' + leafs[1][i] + '</option>'
                obj_response.html("#sel_leaf_create_vpc", option_list)
                obj_response.html("#delete_vpc_group_response", '')
            except Exception as e:
                print traceback.print_exc()
                obj_response.script("create_notification('Can not retrieve leafs', '" + str(e).replace("'", "").
                                    replace('"', '').replace("\n", "")[0:100] + "', 'danger', 0)")
            finally:
                g.db.close()
                obj_response.html("#create_vpc_response", '')

        elif values['operation'] == 'delete_vpc_group':
            try:
                apic_object.remove_vpc_group(values['sel_delete_vpc_group_name'])
                obj_response.script("get_vpc_groups()")
                obj_response.script("get_vpcs()")
                obj_response.script("create_notification('Deleted', '', 'success', 5000)")
            except Exception as e:
                print traceback.print_exc()
                obj_response.script("create_notification('Can not delete VPC group', '" + str(e).replace("'", "").
                                    replace('"', '').replace("\n", "")[0:100] + "', 'danger', 0)")
            finally:
                g.db.close()
                obj_response.html("#delete_vpc_group_response", '')

        elif values['operation'] == 'create_vpc_group':
            try:
                switch_mo_1 = apic_object.moDir.lookupByDn(values['sel_create_vpc_group_leaf_1'])
                switch_mo_2 = apic_object.moDir.lookupByDn(values['sel_create_vpc_group_leaf_2'])
                apic_object.create_explicit_vpc_pgroup(
                    str(switch_mo_1.id) + '_' + str(switch_mo_2.id),
                    str(switch_mo_1.dn),
                    str(switch_mo_2.dn)
                )
                obj_response.script("get_vpc_groups()")
                obj_response.script("create_notification('Created', '', 'success', 5000)")
            except Exception as e:
                print traceback.print_exc()
                obj_response.script("create_notification('Can not create vpc group', '" + str(e).replace("'", "").
                                    replace('"', '').replace("\n", "")[0:100] + "', 'danger', 0)")
            finally:
                g.db.close()
                obj_response.html("#div_create_vpc_group_response", '')

        elif values['operation'] == 'get_vpc_groups':
            try:
                option_list = '<option value="">Select</option>'
                vpc_groups = apic_object.get_vpc_explicit_groups()
                for group in vpc_groups:
                    option_list += '<option value="' + str(group.dn) + '">' + group.name + '</option>'
                obj_response.html(".sel-vpc-group", option_list)
            except Exception as e:
                print traceback.print_exc()
                obj_response.script("create_notification('Can not retrieve VPC groups', '" + str(e).replace("'", "").
                                    replace('"', '').replace("\n", "")[0:100] + "', 'danger', 0)")
            finally:
                g.db.close()
                obj_response.html("#create_vpc_response", '')

    @staticmethod
    def vpc_access_handler(obj_response, formvalues):
        try:
            apic_object, values = handler.init_connections(formvalues)
        except Exception as e:
            print traceback.print_exc()
            obj_response.script("create_notification('Connection problem', '" + str(e).replace("'", "").
                                    replace('"', '').replace("\n", "")[0:100] + "', 'danger', 0)")
            return
        if values['operation'] == 'create_vpc_access':
            try:
                if values['create_vpc_access_type'] == 'single_vlan':
                    network_o = model.network.select().where(model.network.epg_dn ==
                                                             values['sel_network_create_vpc_access'])
                    if len(network_o) > 0:
                        apic_object.associate_epg_vpc(values['sel_network_create_vpc_access'],
                                                      values['sel_vpc_create_vpc_access'], network_o[0].encapsulation)
                        obj_response.script("create_notification('Assigned', '', 'success', 5000)")
                    else:
                        obj_response.script(
                                "create_notification('Can not create VPC access', "
                                "'Network not found in local database', 'danger', 0)"
                            )
                elif values['create_vpc_access_type'] == 'vlan_profile':
                    network_profilexnetworks = model.network_profilexnetwork.select().where(
                        model.network_profilexnetwork.network_profile == int(values['sel_profile_create_vpc_access']))
                    for network_profile in network_profilexnetworks:
                        network_o = model.network.select().where(model.network.id == network_profile.network.id)
                        if len(network_o) > 0:
                            apic_object.associate_epg_vpc(network_o[0].epg_dn,
                                                          values['sel_vpc_create_vpc_access'],
                                                          network_o[0].encapsulation)
                        else:
                            ex = Exception()
                            ex.message = 'Some networks where not assigned because they are not in the local database'
                            raise ex
                    obj_response.script("create_notification('Assigned', '', 'success', 5000)")
            except Exception as e:
                print traceback.print_exc()
                obj_response.script("create_notification('Can not create VPC access', '" + str(e).replace("'", "").
                                    replace('"', '').replace("\n", "")[0:100] + "', 'danger', 0)")
            finally:
                g.db.close()
                obj_response.html("#div_create_vpc_access_response", '')

        elif values['operation'] == 'get_create_vpc_access_networks':
            try:
                network_aps = apic_object.get_ap_by_tenant(values['sel_group_create_vpc_access'])
                if len(network_aps) > 0:
                    networks = apic_object.get_epg_by_ap(str(network_aps[0].dn))
                    option_list = '<option value="">Select</option>'
                    for network in networks:
                        option_list += '<option value="' + str(network.dn) + '">' + network.name + '</option>'
                    obj_response.html("#sel_network_create_vpc_access", option_list)
            except Exception as e:
                print traceback.print_exc()
                obj_response.script("create_notification('Can not retrieve networks', '" + str(e).replace("'", "").
                                    replace('"', '').replace("\n", "")[0:100] + "', 'danger', 0)")
            finally:
                g.db.close()
                obj_response.html("#div_create_vpc_access_response", '')

        elif values['operation'] == 'get_delete_vpc_access_networks':
            try:
                network_aps = apic_object.get_ap_by_tenant(values['sel_group_delete_vpc_access'])
                if len(network_aps) > 0:
                    networks = apic_object.get_epg_by_ap(str(network_aps[0].dn))
                    option_list = '<option value="">Select</option>'
                    for network in networks:
                        option_list += '<option value="' + str(network.dn) + '">' + network.name + '</option>'
                    obj_response.html("#sel_network_delete_vpc_access", option_list)
            except Exception as e:
                print traceback.print_exc()
                obj_response.script("create_notification('Can not retrieve networks', '" + str(e).replace("'", "").
                                    replace('"', '').replace("\n", "")[0:100] + "', 'danger', 0)")
            finally:
                g.db.close()
                obj_response.html("#div_delete_vpc_access_response", '')

        elif values['operation'] == 'get_delete_vpc_access_assignments':
            try:
                vpc_assignments = apic_object.get_vpc_assignments(values['sel_network_delete_vpc_access'])
                option_list = '<option value="">Select</option>'
                for vpc_assignment in vpc_assignments:

                    option_list += '<option value="' + str(vpc_assignment.dn) + '">' + \
                                   str(vpc_assignment.tDn).split('[')[1][:-1] + '</option>'
                obj_response.html("#sel_vpc_delete_vpc_access", option_list)
            except Exception as e:
                print traceback.print_exc()
                obj_response.script("create_notification('Can not retrieve networks', '" + str(e).replace("'", "").
                                    replace('"', '').replace("\n", "")[0:100] + "', 'danger', 0)")
            finally:
                g.db.close()
                obj_response.html("#div_delete_vpc_access_response", '')

        elif values['operation'] == 'delete_vpc_access':
            try:
                if values['delete_vpc_access_type'] == 'single_vlan':
                    apic_object.delete_vpc_assignment(values['sel_vpc_delete_vpc_access'])
                    obj_response.script("create_notification('Removed', '', 'success', 5000)")
                    obj_response.script('get_delete_vpc_access_assignments()')
                elif values['delete_vpc_access_type'] == 'vlan_profile':
                    network_profile_o = model.network_profile.select().where(
                        model.network_profile.id == int(values['sel_profile_delete_vpc_access'])
                    )[0]
                    network_profilexnetwork_list = model.network_profilexnetwork.select().where(
                        model.network_profilexnetwork.network_profile == network_profile_o)

                    for network_profilexnetwork in network_profilexnetwork_list:
                        vpc_assignments = apic_object.get_vpc_assignments(network_profilexnetwork.network.epg_dn)
                        for vpc_assignment in vpc_assignments:
                            if str(vpc_assignment.tDn) == values['sel_vpc_delete_vpc_access_profile']:
                                apic_object.delete_vpc_assignment(str(vpc_assignment.dn))
                    obj_response.script("create_notification('Removed', '', 'success', 5000)")
            except Exception as e:
                print traceback.print_exc()
                obj_response.script("create_notification('Can not delete VPC access', '" + str(e).replace("'", "").
                                    replace('"', '').replace("\n", "")[0:100] + "', 'danger', 0)")
            finally:
                g.db.close()
                obj_response.html("#div_delete_vpc_access_response", '')

    @staticmethod
    def single_access_handler(obj_response, formvalues):
        try:
            apic_object, values = handler.init_connections(formvalues)
        except Exception as e:
            print traceback.print_exc()
            obj_response.script("create_notification('Connection problem', '" + str(e).replace("'", "").
                                    replace('"', '').replace("\n", "")[0:100] + "', 'danger', 0)")
            return
        if values['operation'] == 'get_create_single_access_networks':
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
            try:
                if values['create_port_access_type'] == 'single_vlan':
                    network_o = model.network.select().where(model.network.epg_dn ==
                                                             values['sel_create_single_access_network'])
                    if len(network_o) > 0:
                        apic_object.create_single_access(values['sel_create_single_access_network'],
                                                         values['sel_create_single_access_port'],
                                                         network_o[0].encapsulation)
                        obj_response.script("create_notification('Assigned', '', 'success', 5000)")
                    else:
                        obj_response.script(
                                "create_notification('Network not found in local database', '', 'danger', 0)")
                elif values['create_port_access_type'] == 'vlan_profile':
                    network_profilexnetworks = model.network_profilexnetwork.select().where(
                        model.network_profilexnetwork.network_profile == int(values['sel_profile_create_port_access']))
                    for network_profile in network_profilexnetworks:
                        network_o = model.network.select().where(model.network.id == network_profile.network.id)
                        if len(network_o) > 0:
                            apic_object.create_single_access(network_o[0].epg_dn,
                                                             values['sel_create_single_access_port'],
                                                             network_o[0].encapsulation)
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
            try:
                if values['delete_port_access_type'] == 'single_vlan':
                    network_o = model.network.select().where(model.network.epg_dn ==
                                                             values['sel_delete_single_access_network'])
                    if len(network_o) > 0:
                        apic_object.delete_single_access(values['sel_delete_single_access_network'],
                                                         values['sel_delete_single_access_port'])
                        obj_response.script("create_notification('Removed', '', 'success', 5000)")
                    else:
                        obj_response.script(
                            "create_notification('Network not found in local database', '', 'danger', 0)")
                elif values['delete_port_access_type'] == 'vlan_profile':
                    network_profilexnetworks = model.network_profilexnetwork.select().where(
                        model.network_profilexnetwork.network_profile == int(values['sel_profile_delete_port_access']))
                    for network_profile in network_profilexnetworks:
                        network_o = model.network.select().where(model.network.id == network_profile.network.id)
                        if len(network_o) > 0:
                            apic_object.delete_single_access(network_o[0].epg_dn,
                                                             values['sel_delete_single_access_port'])
                    obj_response.script("create_notification('Removed', '', 'success', 5000)")
            except Exception as e:
                print traceback.print_exc()
                obj_response.script(
                    "create_notification('Can not delete single access', '" + str(e).replace("'", "").replace('"', '').
                    replace("\n", "")[0:100] + "', 'danger', 0)")
            finally:
                g.db.close()
                obj_response.html("#delete_single_access_response", '')

    @staticmethod
    def access_switch_handler(obj_response, formvalues):
        try:
            apic_object, values = handler.init_connections(formvalues)
        except Exception as e:
            print traceback.print_exc()
            obj_response.script("create_notification('Connection problem', '" + str(e).replace("'", "").
                                    replace('"', '').replace("\n", "")[0:100] + "', 'danger', 0)")
            return
        if values['operation'] == 'configure_access_switches':
            try:
                switch_list = values['hd_configure_access_switches'].split(';')
                sc = switch_controller.switch_controller()
                log_messages = ''
                for switch in switch_list:
                    if len(switch) > 0:
                        switch_ip = switch.split('(')[0].replace(' ', '')
                        switch_model = model.access_switch.select().where(model.access_switch.ip == switch_ip)[0]
                        log_messages += "\n*** " + switch + " ***\n\n"
                        log_messages += sc.send_commands(
                            switch_model.ip,
                            switch_model.user,
                            values['access_switch_login_password'],
                            values['access_switch_enable_password'],
                            switch_model.hostname,
                            values['access_switch_commands'].split('\n'))
                obj_response.script("create_notification('Commands sent!', '', 'success', 5000)")
                obj_response.html('#access_switch_result', str(log_messages))
                obj_response.script('$("#access_switch_result").val($("#access_switch_result").html())')
            except Exception as e:
                print traceback.print_exc()
                obj_response.script(
                    "create_notification('Cannot send the commands', '" + str(e).replace("'", "").
                    replace('"', '').replace("\n", "")[0:100] + "', 'danger', 0)")
            finally:
                g.db.close()
                obj_response.html("#access_switch_response", '')

        elif values['operation'] == 'create_access_switch':
            try:
                model.access_switch.create(ip=values['access_switch_ip'],
                                           user=values['access_switch_user'],
                                           hostname=values['access_switch_hostname'])
                obj_response.script("create_notification('Created', '', 'success', 5000)")
                obj_response.script("get_access_switches();")
            except Exception as e:
                print traceback.print_exc()
                obj_response.script(
                    "create_notification('Cannot not create access switch', '" + str(e).replace("'", "").
                    replace('"', '').replace("\n", "")[0:100] + "', 'danger', 0)")
            finally:
                g.db.close()
                obj_response.html("#access_switch_response", '')

        elif values['operation'] == 'delete_access_switch':
            try:
                model.access_switch.delete().where(
                    model.access_switch.ip == values['sel_delete_access_switch']).execute()
                obj_response.script("create_notification('Deleted', '', 'success', 5000)")
                obj_response.script("get_access_switches();")
            except Exception as e:
                print traceback.print_exc()
                obj_response.script(
                    "create_notification('Cannot create access switch', '" + str(e).replace("'", "").
                    replace('"', '').replace("\n", "")[0:100] + "', 'danger', 0)")
            finally:
                g.db.close()
                obj_response.html("#access_switch_response", '')

        elif values['operation'] == 'get_access_switches':
            try:
                access_switches = model.access_switch.select()
                option_list = '<option value="">Select</option>'
                for switch in access_switches:
                    option_list += '<option value="' + str(switch.ip) + '">' + switch.ip + \
                                   ' (' + switch.hostname + ')</option>'
                obj_response.html(".sel-access-switch", option_list)
            except Exception as e:
                print traceback.print_exc()
                obj_response.script(
                    "create_notification('Cannot retrieve access switches', '" + str(e).replace("'", "").
                    replace('"', '').replace("\n", "")[0:100] + "', 'danger', 0)")
            finally:
                g.db.close()
                obj_response.html("#access_switch_response", '')
