"""

Helper for views.py

"""
from base_handler import base_handler
import traceback
import app.model
from flask import g, render_template

class vpc_handler(base_handler):

    def __init__(self):
        """
        Handles all operations related to virtual port channels association with EPGs (for single port associations
        single_access_handler is used)
        """
        try:
            self.cobra_apic_object = vpc_handler.init_connections()
            self.exception = None
        except Exception as e:
            self.exception = e
            print traceback.print_exc()

    def create_vpc(self, obj_response, form_values):
        try:
            # Creates a switch profile, interface profiles and policy groups
            # check if vpc has a unique name
            vpc_list = self.cobra_apic_object.get_vpcs()
            for vpc in vpc_list:
                if vpc.name.lower() == form_values['create_vpc_name'].lower():
                    ex = Exception()
                    ex.message = 'That name has been used before'
                    raise ex
            selected_ports = str(form_values['port_dns']).split(';')
            switch_mo_list = []
            for port_dn in selected_ports:
                if len(port_dn) > 0:
                    switch_mo = self.cobra_apic_object.get_switch_by_port(port_dn)
                    switch_mo_list.append(switch_mo)
                    if_policy_group_mo = self.cobra_apic_object.create_vpc_if_policy_group(form_values['create_vpc_name'], 'migration-tool')
                    if_profile = self.cobra_apic_object.create_vpc_interface_profile(
                        port_dn, if_policy_group_mo.dn, form_values['create_vpc_name']
                    )
                    self.cobra_apic_object.create_vpc_switch_profile(
                        str(switch_mo.dn), str(if_profile.dn), form_values['create_vpc_name']
                    )

            vpc_list = app.model.vpc.select()
            option_list = '<option value="">Select</option>'
            for vpc in vpc_list:
               option_list += '<option value="' + str(vpc.id) + '">' + vpc.name + '</option>'
            obj_response.html(".sel-vpc", option_list)
            html_response = render_template('vpc/vpc_port_table_partial.html', item_table=[])
            obj_response.html("#vpc_ports", html_response)
            obj_response.html("#sel_port_create_vpc", '')
            # Executes javascript function (only after the response is received by the browser)
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

    def get_delete_vpc_assigned_ports(self, obj_response, form_values):
        # load the list delete_vpc_ports with the ports assigned to a virtual port channel
        try:
            port_list = self.cobra_apic_object.get_vpc_ports(form_values['sel_delete_vpc_name'])
            item_table = []
            for vpc_port_mo in port_list:
                switch_mo = self.cobra_apic_object.get_switch_by_vpc_port(str(vpc_port_mo.dn))
                item = type('vpc_port_table_item', (object,), {})
                item.rn = str(switch_mo.rn)
                item.tSKey = str(vpc_port_mo.tSKey)
                item_table.append(item)
            html_response = render_template('vpc/vpc_port_table_partial.html', item_table=item_table)
            obj_response.html("#delete_vpc_ports", html_response)
        except Exception as e:
            print traceback.print_exc()
            obj_response.script("create_notification('Can not retrieve ports', '" + str(e).replace("'", "").
                                replace('"', '').replace("\n", "")[0:100] + "', 'danger', 0)")
        finally:
            g.db.close()
            obj_response.html("#delete_vpc_response", '')

    def get_vpcs(self, obj_response):
        # Load the selects that show all the virtual port channels
        try:
            vpc_list = self.cobra_apic_object.get_vpcs()
            item_list = []
            for vpc in vpc_list:
                # Creates a dynamic object
                vpc_do = type('vpc_do', (object,), {})
                vpc_do.key = str(vpc.dn)
                vpc_do.text = vpc.name
                item_list.append(vpc_do)
            html_response = render_template('select_partial.html', item_list=item_list)
            obj_response.html(".sel-vpc", html_response)
        except Exception as e:
            print traceback.print_exc()
            obj_response.script("create_notification('Can not retrieve VPCs', '" + str(e).replace("'", "").
                                replace('"', '').replace("\n", "")[0:100] + "', 'danger', 0)")
        finally:
            g.db.close()
            obj_response.html("#delete_vpc_response", '')

    def delete_vpc(self, obj_response, form_values):
        # Removes switch profiles, interface policies and policy groups associated to the selected
        # virtual port channel
        try:
            self.cobra_apic_object.delete_vpc(form_values['sel_delete_vpc_name'])
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

    def get_leafs_by_vpc_group(self, obj_response, form_values):
        # Load the sel_leaf_create_vpc with the leafs that are port of the selected vpc explicit group
        try:
            leafs = self.cobra_apic_object.get_leaf_by_explicit_group(form_values['sel_vpc_group_create_vpc'])
            item_list = []
            for i in range(0, len(leafs[0])):
                # Creates a dynamic object
                leaf_do = type('leaf_do', (object,), {})
                leaf_do.key = leafs[0][i]
                leaf_do.text = leafs[1][i]
                item_list.append(leaf_do)
            html_response = render_template('select_partial.html', item_list=item_list)
            obj_response.html("#sel_leaf_create_vpc", html_response)
            obj_response.html("#delete_vpc_group_response", '')
        except Exception as e:
            print traceback.print_exc()
            obj_response.script("create_notification('Can not retrieve leafs', '" + str(e).replace("'", "").
                                replace('"', '').replace("\n", "")[0:100] + "', 'danger', 0)")
        finally:
            g.db.close()
            obj_response.html("#create_vpc_response", '')

    def delete_vpc_group(self, obj_response, form_values):
        # Delete an explicit protection group
        try:
            self.cobra_apic_object.remove_vpc_group(form_values['sel_delete_vpc_group_name'])
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

    def create_vpc_group(self, obj_response, form_values):
        # Creates an explicit protection group
        try:
            switch_mo_1 = self.cobra_apic_object.moDir.lookupByDn(form_values['sel_create_vpc_group_leaf_1'])
            switch_mo_2 = self.cobra_apic_object.moDir.lookupByDn(form_values['sel_create_vpc_group_leaf_2'])
            self.cobra_apic_object.create_explicit_vpc_pgroup(
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

    def get_vpc_groups(self, obj_response):
        # Load the selects that shows all the vpc explicit groups
        try:
            vpc_groups = self.cobra_apic_object.get_vpc_explicit_groups()
            item_list = []
            for group in vpc_groups:
                # Creates a dynamic object
                leaf_do = type('leaf_do', (object,), {})
                leaf_do.key = str(group.dn)
                leaf_do.text = group.name
                item_list.append(leaf_do)
            html_response = render_template('select_partial.html', item_list=item_list)
            obj_response.html(".sel-vpc-group", html_response)
        except Exception as e:
            print traceback.print_exc()
            obj_response.script("create_notification('Can not retrieve VPC groups', '" + str(e).replace("'", "").
                                replace('"', '').replace("\n", "")[0:100] + "', 'danger', 0)")
        finally:
            g.db.close()
            obj_response.html("#create_vpc_response", '')

    def get_vpc_group_list(self, obj_response):
        # Load the vpc_group_list with all the explicit groups created in ACI
        try:
            vpc_group_list = []
            vpc_groups = self.cobra_apic_object.get_vpc_explicit_groups()
            for group in vpc_groups:
                # Creates a dynamic object
                vpc_group_do = type('vpc_group_do', (object,), {})
                vpc_group_do.name = str(group.name)
                vpc_group_list.append(vpc_group_do)
            html_response = render_template('list_partial.html', item_list=vpc_group_list)
            obj_response.html("#vpc_group_list", html_response)
        except Exception as e:
            print traceback.print_exc()
            obj_response.script("create_notification('Can not retrieve VPC groups', '" + str(e).replace("'", "").
                                replace('"', '').replace("\n", "")[0:100] + "', 'danger', 0)")
        finally:
            g.db.close()

    def get_vpc_list(self, obj_response):
        # Load the vpc_list with all the virtual port channels created in ACI
        try:
            vpc_list = self.cobra_apic_object.get_vpcs()
            item_list = []
            for vpc in vpc_list:
                # Creates a dynamic object
                item = type('item', (object,), {})
                item.name = vpc.name
                item.sub_item_list = []
                port_list = self.cobra_apic_object.get_vpc_ports(str(vpc.dn))
                for vpc_port_mo in port_list:
                    switch_mo = self.cobra_apic_object.get_switch_by_vpc_port(str(vpc_port_mo.dn))
                    # Creates a dynamic object
                    sub_item = type('item', (object,), {})
                    sub_item.name = str(switch_mo.rn) + ' - ' + str(vpc_port_mo.tSKey)
                    item.sub_item_list.append(sub_item)
                item_list.append(item)
            html_response = render_template('collapse_list_partial.html', item_list=item_list)
            obj_response.html("#vpc_list", html_response)
        except Exception as e:
            print traceback.print_exc()
            obj_response.script("create_notification('Can not retrieve VPCs', '" + str(e).replace("'", "").
                                replace('"', '').replace("\n", "")[0:100] + "', 'danger', 0)")
        finally:
            g.db.close()