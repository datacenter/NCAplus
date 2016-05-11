"""
*************************************************************************
 Copyright (c) 2016 Cisco Systems, Inc.  All rights reserved.
*************************************************************************
Sijax Handler for the access switches operations

"""
from base_handler import base_handler
import traceback
import app.model
from flask import g
from app.access_switch_manager import switch_controller


class access_switch_handler(base_handler):

    @staticmethod
    def access_switch_handler(obj_response, formvalues):
        """
        Manages all the configuration to switches that are external to ACI
        There is hidden in the form that comes from the HTML request that tells which operation is going to be
        executed
        :param obj_response:
        :param formvalues:
        :return:
        """
        try:
            # Login to APIC and load the form's values
            apic_object, values = access_switch_handler.init_connections(formvalues)
        except Exception as e:
            print traceback.print_exc()
            obj_response.script("create_notification('Connection problem', '" + str(e).replace("'", "").
                                    replace('"', '').replace("\n", "")[0:100] + "', 'danger', 0)")
            return
        if values['operation'] == 'configure_access_switches':
            # Send commands to the switches. All the selected switches are sent using a hidden (called
            # hd_configure_access_switches) input in the HTML that is set using javascript before the request. Each
            # switch is separated by a ';' character
            try:
                # Get the switches
                switch_list = values['hd_configure_access_switches'].split(';')
                sc = switch_controller.switch_controller()
                log_messages = ''
                # Executes the commands per each switch
                for switch in switch_list:
                    if len(switch) > 0:
                        switch_ip = switch.split('(')[0].replace(' ', '')
                        switch_model = app.model.access_switch.select().where(
                            app.model.access_switch.ip == switch_ip)[0]
                        log_messages += "\n*** " + switch + " ***\n\n"
                        log_messages += sc.send_commands(
                            switch_model.ip,
                            switch_model.user,
                            values['access_switch_login_password'],
                            values['access_switch_enable_password'],
                            switch_model.hostname,
                            values['access_switch_commands'].split('\n')) # Each command is separated by a '\n' character
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
            # Creates an access switch into the local database
            try:
                app.model.access_switch.create(ip=values['access_switch_ip'],
                                               user=values['access_switch_user'],
                                               hostname=values['access_switch_hostname'])
                obj_response.script("create_notification('Created', '', 'success', 5000)")
                obj_response.script("get_access_switches();get_access_switch_list();")
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
                app.model.access_switch.delete().where(
                    app.model.access_switch.ip == values['sel_delete_access_switch']).execute()
                obj_response.script("create_notification('Deleted', '', 'success', 5000)")
                obj_response.script("get_access_switches();get_access_switch_list();")
            except Exception as e:
                print traceback.print_exc()
                obj_response.script(
                    "create_notification('Cannot create access switch', '" + str(e).replace("'", "").
                    replace('"', '').replace("\n", "")[0:100] + "', 'danger', 0)")
            finally:
                g.db.close()
                obj_response.html("#access_switch_response", '')

        elif values['operation'] == 'get_access_switches':
            # Load the selects that will show the access switches saved in the local database
            try:
                access_switches = app.model.access_switch.select()
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

        elif values['operation'] == 'get_access_switch_list':
            # Load the list that contains all the switches that are in the local database
            try:
                access_switches = app.model.access_switch.select()
                access_switch_list_str = ''
                for switch in access_switches:
                    access_switch_list_str += switch.hostname + ' - ' + switch.ip
                obj_response.html("#access_switch_list", access_switch_list_str)
            except Exception as e:
                print traceback.print_exc()
                obj_response.script(
                    "create_notification('Cannot retrieve access switches', '" + str(e).replace("'", "").
                    replace('"', '').replace("\n", "")[0:100] + "', 'danger', 0)")
            finally:
                g.db.close()
                obj_response.html("#access_switch_response", '')