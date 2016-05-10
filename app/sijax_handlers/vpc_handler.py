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

class vpc_handler(base_handler):

    @staticmethod
    def vpc_handler(obj_response, formvalues):
        try:
            apic_object, values = vpc_handler.init_connections(formvalues)
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
                        if_policy_group_mo = apic_object.create_vpc_if_policy_group(values['create_vpc_name'], 'migration-tool')
                        if_profile = apic_object.create_vpc_interface_profile(
                            port_dn, if_policy_group_mo.dn, values['create_vpc_name']
                        )
                        apic_object.create_vpc_switch_profile(
                            str(switch_mo.dn), str(if_profile.dn), values['create_vpc_name']
                        )

                vpc_list = app.model.vpc.select()
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
                obj_response.script('get_vpcs();get_vpc_list();')
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
                obj_response.script('get_vpcs();get_vpc_list();')
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
                obj_response.script("get_vpcs();get_vpc_group_list();get_vpc_list();")
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
                obj_response.script("get_vpc_groups();get_vpc_group_list();get_vpc_list();")
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

        elif values['operation'] == 'get_vpc_group_list':
            try:
                vpc_group_list_str = ''
                vpc_groups = apic_object.get_vpc_explicit_groups()
                for group in vpc_groups:
                    vpc_group_list_str += '<h5>' + str(group.name) + '</h5><hr style="margin:0px 0px 0px 0px"/>'
                vpc_group_list_str += "</div>"
                obj_response.html("#vpc_group_list", vpc_group_list_str)
            except Exception as e:
                print traceback.print_exc()
                obj_response.script("create_notification('Can not retrieve VPC groups', '" + str(e).replace("'", "").
                                    replace('"', '').replace("\n", "")[0:100] + "', 'danger', 0)")
            finally:
                g.db.close()

        elif values['operation'] == 'get_vpc_list':
            try:
                vpc_list = apic_object.get_vpcs()
                vpc_list_str = ''
                for vpc in vpc_list:
                    vpc_list_str += '<label data-toggle="collapse" data-target="#vpc_' + vpc.name + '" style="cursor:pointer">'
                    vpc_list_str += vpc.name + ' </label>'
                    vpc_list_str += '<div id="vpc_' + vpc.name + '" class="collapse">'
                    port_list = apic_object.get_vpc_ports(str(vpc.dn))
                    for vpc_port_mo in port_list:
                        switch_mo = apic_object.get_switch_by_vpc_port(str(vpc_port_mo.dn))
                        vpc_list_str += '<p>' + str(switch_mo.rn) + ' - ' + str(vpc_port_mo.tSKey) + '</p>'
                    vpc_list_str += '</div>'
                    vpc_list_str += '<hr style="margin:0px 0px 0px 0px"/>'
                obj_response.html("#vpc_list", vpc_list_str)
            except Exception as e:
                print traceback.print_exc()
                obj_response.script("create_notification('Can not retrieve VPCs', '" + str(e).replace("'", "").
                                    replace('"', '').replace("\n", "")[0:100] + "', 'danger', 0)")
            finally:
                g.db.close()