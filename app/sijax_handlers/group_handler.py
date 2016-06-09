"""

Helper for views.py

"""
from base_handler import base_handler, REMOVED_TENANTS
import traceback
from flask import g, render_template

class group_handler(base_handler):

    def __init__(self):
        """
        Manages all operations related to groups or tenants
        :return:
        """
        try:
            self.cobra_apic_object = group_handler.init_connections()
            self.exception = None
        except Exception as e:
            self.exception = e
            print traceback.print_exc()

    def get_groups(self, obj_response):
        # Check if there has been connection errors
        if self.exception is not None:
            obj_response.script("create_notification('Connection problem', '" + str(self.exception).replace("'", "").
                                    replace('"', '').replace("\n", "")[0:100] + "', 'danger', 0)")
            return
        # Load the selects that show the groups
        try:
            # Creates dynamic object list to use it in select_template.html
            tenant_do_list = []
            tenants = self.cobra_apic_object.get_all_tenants()
            for tenant in [elem for elem in tenants if elem.name not in REMOVED_TENANTS]:
                # Creates a dynamic object
                tenant_do = type('tenant_do', (object,), {})
                tenant_do.key = str(tenant.dn)
                tenant_do.text = tenant.name
                tenant_do_list.append(tenant_do)
            option_list = render_template('select_partial.html', item_list=tenant_do_list)
            obj_response.html(".sel-group", option_list)
        except Exception as e:
            print traceback.print_exc()
            obj_response.script("create_notification('Can not retrieve groups', '" + str(e).replace("'", "").
                                replace('"', '').replace("\n", "")[0:100] + "', 'danger', 0)")
        finally:
            g.db.close()
            obj_response.html("#create_network_response", '')

    def tenant_list(self, obj_response):
        # Check if there has been connection errors
        if self.exception is not None:
            obj_response.script("create_notification('Connection problem', '" + str(self.exception).replace("'", "").
                                    replace('"', '').replace("\n", "")[0:100] + "', 'danger', 0)")
            return
        # Load the list that shows all the tenants that have been created, avoids the defaults
        # (common, mgmt and fabric)
        try:
            tenants = self.cobra_apic_object.get_all_tenants()
            tenant_list = []
            for tenant in [elem for elem in tenants if elem.name not in REMOVED_TENANTS]:
                # Creates a dynamic object
                tenant_do = type('tenant_do', (object,), {})
                tenant_do.name = tenant.name
                tenant_list.append(tenant_do)
            html_response = render_template('list_partial.html', item_list=tenant_list)
            obj_response.html("#tenant_list", html_response)
        except Exception as e:
            print traceback.print_exc()
            obj_response.script("create_notification('Can not retrieve group list', '" + str(e).replace("'", "").
                                replace('"', '').replace("\n", "")[0:100] + "', 'danger', 0)")
        finally:
            g.db.close()

    def create_group(self, obj_response, form_values):
        # Check if there has been connection errors
        if self.exception is not None:
            obj_response.script("create_notification('Connection problem', '" + str(self.exception).replace("'", "").
                                    replace('"', '').replace("\n", "")[0:100] + "', 'danger', 0)")
            return
        # Creates a tenant in ACI
        try:
            self.cobra_apic_object.create_group(form_values['create_group_name'])
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

    def delete_group(self, obj_response, form_values):
        # Check if there has been connection errors
        if self.exception is not None:
            obj_response.script("create_notification('Connection problem', '" + str(self.exception).replace("'", "").
                                    replace('"', '').replace("\n", "")[0:100] + "', 'danger', 0)")
            return
        # Removes a tenant from ACI
        try:
            self.cobra_apic_object.delete_tenant(form_values['sel_delete_group_name'])
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