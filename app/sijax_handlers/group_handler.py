"""
*************************************************************************
 Copyright (c) 2016 Cisco Systems, Inc.  All rights reserved.
*************************************************************************
Helper for views.py

"""
from base_handler import base_handler,REMOVED_TENANTS
import traceback
from flask import g

class group_handler(base_handler):


    @staticmethod
    def group_handler(obj_response, formvalues):
        """
        Manages all operations related to groups or tenants
        :param obj_response:
        :param formvalues:
        :return:
        """
        try:
            apic_object, values = group_handler.init_connections(formvalues)
        except Exception as e:
            print traceback.print_exc()
            obj_response.script("create_notification('Connection problem', '" + str(e).replace("'", "").
                                    replace('"', '').replace("\n", "")[0:100] + "', 'danger', 0)")
            return
        if values['operation'] == 'get_groups':
            # Load the selects that show the groups
            try:
                tenants = apic_object.get_all_tenants()
                option_list = '<option value="">Select</option>'
                # for tenant in tenants:
                for tenant in [elem for elem in tenants if elem.name not in REMOVED_TENANTS]:
                # if tenant.name not in REMOVED_TENANTS:
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
            # Load the list that shows all the tenants that have been created, avoids the defaults
            # (common, mgmt and fabric)
            try:
                tenants = apic_object.get_all_tenants()
                all_tenants_list = '<ul style="padding-left:10px;">'
                for tenant in [elem for elem in tenants if elem.name not in REMOVED_TENANTS]:
                    all_tenants_list += '<li><div style="font-size:.9em;">' + str(tenant.name) + '</div></li>'
                all_tenants_list += '</ul>'
                obj_response.html("#tenant_list", all_tenants_list)
            except Exception as e:
                print traceback.print_exc()
                obj_response.script("create_notification('Can not retrieve group list', '" + str(e).replace("'", "").
                                    replace('"', '').replace("\n", "")[0:100] + "', 'danger', 0)")
            finally:
                g.db.close()

        elif values['operation'] == 'create_group':
            # Creates a tenant in ACI
            try:
                apic_object.create_group(values['create_group_name'])
                obj_response.script("create_notification('Created', '', 'success', 5000)")
                # Executes javascript function (only after the response is received by the browser)
                obj_response.script('get_groups();get_tenants();')
            except Exception as e:
                print traceback.print_exc()
                obj_response.script("create_notification('Can not create group', '" + str(e).replace("'", "").
                                    replace('"', '').replace("\n", "")[0:100] + "', 'danger', 0)")
            finally:
                g.db.close()
                obj_response.html("#create_group_response", '')

        elif values['operation'] == 'delete_group':
            # Removes a tenant from ACI
            try:
                apic_object.delete_tenant(values['sel_delete_group_name'])
                # Executes javascript function (only after the response is received by the browser)
                obj_response.script("get_groups();get_tenants();")
                obj_response.script("create_notification('Deleted', '', 'success', 5000)")
            except Exception as e:
                print traceback.print_exc()
                obj_response.script("create_notification('Can not delete group', '" + str(e).replace("'", "").
                                    replace('"', '').replace("\n", "")[0:100] + "', 'danger', 0)")
            finally:
                g.db.close()
                obj_response.html("#delete_group_response", '')

