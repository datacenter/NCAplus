"""
*************************************************************************
 Copyright (c) 2016 Cisco Systems, Inc.  All rights reserved.
*************************************************************************
Helper for views.py

"""
from base_handler import base_handler, REMOVED_TENANTS
import traceback
import app.model
from flask import g

class network_handler(base_handler):

    @staticmethod
    def network_handler(obj_response, formvalues):
        try:
            apic_object, values = network_handler.init_connections(formvalues)
        except Exception as e:
            print traceback.print_exc()
            obj_response.script("create_notification('Connection problem', '" + str(e).replace("'", "").
                                    replace('"', '').replace("\n", "")[0:100] + "', 'danger', 0)")
            return
        if values['operation'] == 'create_network':
            try:
                network_object = app.model.network.create(name=values['create_network_name'],
                                                          encapsulation=int(values['create_network_encapsulation']),
                                                          group=values['sel_create_network_group'],
                                                          epg_dn='')
                apic_object.add_vlan(network_object.encapsulation, 'migration-tool')
                epg = apic_object.create_network(network_object)
                apic_object.associate_epg_physical_domain(str(epg.dn), 'migration-tool')
                network_object.update(epg_dn=str(epg.dn)).where(
                    app.model.network.id == network_object.id).execute()

                obj_response.script("create_notification('Created', '', 'success', 5000);")
                obj_response.script("get_sel_delete_networks();get_network_list();")
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
                network_list = app.model.network.select().where(
                    app.model.network.epg_dn == values['sel_delete_network_name'])
                if len(network_list) > 0:
                    apic_object.remove_vlan(network_list[0].encapsulation, 'migration-tool')
                    apic_object.delete_network(network_list[0])
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
                network_profile_o = app.model.network_profile.create(name=values['create_network_profile_name'])
                selected_networks = str(values['create_network_profile_dns']).split(';')
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

        elif values['operation'] == 'get_network_profiles':
            try:
                network_profiles = app.model.network_profile.select()
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
                network_profile_o = app.model.network_profile.select().where(
                    app.model.network_profile.id == int(values['sel_delete_network_profile']))[0]

                network_profilexnetwork_list = app.model.network_profilexnetwork.select().where(
                    app.model.network_profilexnetwork.network_profile == network_profile_o)
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
                network_profile_o = app.model.network_profile.select().where(
                    app.model.network_profile.id == int(values['sel_delete_network_profile']))[0]
                app.model.network_profilexnetwork.delete().where(
                    app.model.network_profilexnetwork.network_profile == network_profile_o).execute()
                app.model.network_profile.delete().where(
                    app.model.network_profile.id == int(values['sel_delete_network_profile'])).execute()
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
                obj_response.script('get_network_profiles();get_network_profile_list();')
                obj_response.script('$("#sel_delete_network_profile").val("")')

        elif values['operation'] == 'get_network_list':
            try:
                network_list = ''
                for tenant in apic_object.get_all_tenants():
                    network_aps = apic_object.get_ap_by_tenant(str(tenant.dn))
                    if len(network_aps) > 0:
                        if tenant.name not in REMOVED_TENANTS:
                            networks = apic_object.get_epg_by_ap(str(network_aps[0].dn))
                            network_list += '<ul style="padding-left:10px;font-size:.9em;">'
                            network_list += '<label data-toggle="collapse" data-target="#' + tenant.name + '" style="float:left;cursor:pointer">'
                            network_list += '<i class="fa fa-chevron-circle-down" aria-hidden="true"></i></label>&nbsp;' + tenant.name
                            network_list += '<div id="' + tenant.name + '" class="collapse">'
                            for network in networks:
                                network_list += '<div style="clear:both; padding-left:10px;font-size:.8em;">' + str(network.name) + '</div>'
                            network_list += '</div>'
                            network_list += '</ul>'
                obj_response.html("#network_list", network_list)
            except Exception as e:
                print traceback.print_exc()
                obj_response.script("create_notification('Can not retrieve networks', '" + str(e).replace("'", "").
                                    replace('"', '').replace("\n", "")[0:100] + "', 'danger', 0)")
            finally:
                g.db.close()
                obj_response.html("#delete_network_response", '')

        elif values['operation'] == 'get_network_profile_list':
            try:
                network_profiles = app.model.network_profile.select()
                vlan_profile_list_str = ''
                for network_p in network_profiles:
                    vlan_profile_list_str += '<label data-toggle="collapse" data-target="#profile_' + str(network_p.id)\
                                             + '" style="cursor:pointer">'
                    vlan_profile_list_str += network_p.name + ' </label>'
                    vlan_profile_list_str += '<div id="profile_' + str(network_p.id) + '" class="collapse">'
                    network_profilexnetwork_list = app.model.network_profilexnetwork.select().where(
                        app.model.network_profilexnetwork.network_profile == network_p)
                    for network_profilexnetwork in network_profilexnetwork_list:
                        group_mo = apic_object.moDir.lookupByDn(network_profilexnetwork.network.group)
                        vlan_profile_list_str += '<p>' + group_mo.name + ' - ' + str(network_profilexnetwork.network.name) + '</p>'
                    vlan_profile_list_str += '</div>'
                    vlan_profile_list_str += '<hr style="margin:0px 0px 0px 0px"/>'
                obj_response.html("#network_profile_list", vlan_profile_list_str)
                obj_response.html("#div_create_vpc_access_response", '')
            except Exception as e:
                print traceback.print_exc()
                obj_response.script(
                    "create_notification('Can not retrieve VLAN profile', '" + str(e).replace("'", "").replace('"', '').
                    replace("\n", "")[0:100] + "', 'danger', 0)")
            finally:
                g.db.close()
                obj_response.html("#div_create_vpc_access_response", '')

