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

class vpc_access_handler(base_handler):

    @staticmethod
    def vpc_access_handler(obj_response, formvalues):
        try:
            apic_object, values = vpc_access_handler.init_connections(formvalues)
        except Exception as e:
            print traceback.print_exc()
            obj_response.script("create_notification('Connection problem', '" + str(e).replace("'", "").
                                    replace('"', '').replace("\n", "")[0:100] + "', 'danger', 0)")
            return
        if values['operation'] == 'create_vpc_access':
            try:
                if values['create_vpc_access_type'] == 'single_vlan':
                    network_o = app.model.network.select().where(app.model.network.epg_dn ==
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
                    network_profilexnetworks = app.model.network_profilexnetwork.select().where(
                        app.model.network_profilexnetwork.network_profile == int(values['sel_profile_create_vpc_access']))
                    for network_profile in network_profilexnetworks:
                        network_o = app.model.network.select().where(app.model.network.id == network_profile.network.id)
                        if len(network_o) > 0:
                            apic_object.associate_epg_vpc(network_o[0].epg_dn,
                                                          values['sel_vpc_create_vpc_access'],
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
                vpc_assignments = apic_object.get_vpc_assignments_by_epg(values['sel_network_delete_vpc_access'])
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
                    network_profile_o = app.model.network_profile.select().where(
                        app.model.network_profile.id == int(values['sel_profile_delete_vpc_access'])
                    )[0]
                    network_profilexnetwork_list = app.model.network_profilexnetwork.select().where(
                        app.model.network_profilexnetwork.network_profile == network_profile_o)

                    for network_profilexnetwork in network_profilexnetwork_list:
                        vpc_assignments = apic_object.get_vpc_assignments_by_epg(network_profilexnetwork.network.epg_dn)
                        for vpc_assignment in vpc_assignments:
                            if str(vpc_assignment.tDn) == values['sel_vpc_delete_vpc_access_profile']:
                                apic_object.delete_vpc_assignment(str(vpc_assignment.dn))
                    obj_response.script("create_notification('Removed', '', 'success', 5000)")
                obj_response.script("get_vpc_assignment_list();")
            except Exception as e:
                print traceback.print_exc()
                obj_response.script("create_notification('Can not delete VPC access', '" + str(e).replace("'", "").
                                    replace('"', '').replace("\n", "")[0:100] + "', 'danger', 0)")
            finally:
                g.db.close()
                obj_response.html("#div_delete_vpc_access_response", '')

        elif values['operation'] == 'get_vpc_assignment_list':
            try:
                vpc_list = apic_object.get_vpcs()
                vpc_assignments = apic_object.get_vpc_assignments()
                vpc_assignment_list_str = ''
                for vpc in vpc_list:
                    vpc_assignment_list_str += '<label data-toggle="collapse" data-target="#vpc_assign_' + vpc.name + '" style="cursor:pointer">'
                    vpc_assignment_list_str += vpc.name + ' </label>'
                    vpc_assignment_list_str += '<div id="vpc_assign_' + vpc.name + '" class="collapse">'
                    if vpc.name in vpc_assignments.keys():
                        for epg_name in vpc_assignments[vpc.name]:
                            vpc_assignment_list_str += '<p>' + epg_name + '</p>'
                    vpc_assignment_list_str += '</div>'
                    vpc_assignment_list_str += '<hr style="margin:0px 0px 0px 0px"/>'
                obj_response.html("#vpc_assignment_list", vpc_assignment_list_str)
            except Exception as e:
                print traceback.print_exc()
                obj_response.script("create_notification('Can not retrieve VPC assignments', '" + str(e).replace("'", "").
                                    replace('"', '').replace("\n", "")[0:100] + "', 'danger', 0)")
            finally:
                g.db.close()
