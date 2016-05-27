"""
*************************************************************************
 Copyright (c) 2016 Cisco Systems, Inc.  All rights reserved.
*************************************************************************
Sijax Handler for the access switches operations

"""
from base_handler import base_handler2
import traceback
import app.model
from flask import g
from app.access_switch_manager import switch_controller


class access_switch_handler(base_handler2):

    def __init__(self):
        """
        Manages all the operations related access switches that are
        outside the fabric
        :param obj_response:
        :param formvalues:
        :return:
        """
        try:
            self.cobra_apic_object = access_switch_handler.init_connections()
            self.exception = None
        except Exception as e:
            self.exception = e
            print traceback.print_exc()

    def configure_access_switches(self, obj_response, form_values):
        """ Send commands to the switches. All the selected switches are sent using a hidden (called
        hd_configure_access_switches) input in the HTML that is set using javascript before the request. Each
        switch is separated by a ';' character"""
        if self.exception is not None:
            obj_response.script("create_notification('Connection problem', '" + str(self.exception).replace("'", "").
                                    replace('"', '').replace("\n", "")[0:100] + "', 'danger', 0)")
            return
        try:
            # Get the switches
            switch_list = form_values['hd_configure_access_switches'].split(';')
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
                        form_values['access_switch_login_password'],
                        form_values['access_switch_enable_password'],
                        switch_model.hostname,
                        form_values['access_switch_commands'].split(
                            '\n'))  # Each command is separated by a '\n' character
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

    def create_access_switch(self, obj_response, form_values):
        """ Creates an access switch into the local database """
        if self.exception is not None:
            obj_response.script("create_notification('Connection problem', '" + str(self.exception).replace("'", "").
                                    replace('"', '').replace("\n", "")[0:100] + "', 'danger', 0)")
            return
        try:
            app.model.access_switch.create(ip=form_values['access_switch_ip'],
                                           user=form_values['access_switch_user'],
                                           hostname=form_values['access_switch_hostname'])
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

    def delete_access_switch(self, obj_response, form_values):
        if self.exception is not None:
            obj_response.script("create_notification('Connection problem', '" + str(self.exception).replace("'", "").
                                    replace('"', '').replace("\n", "")[0:100] + "', 'danger', 0)")
            return
        try:
            app.model.access_switch.delete().where(
                app.model.access_switch.ip == form_values['sel_delete_access_switch']).execute()
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

    def get_access_switches(self, obj_response):
        """Load the selects that will show the access switches saved in the local database"""
        if self.exception is not None:
            obj_response.script("create_notification('Connection problem', '" + str(self.exception).replace("'", "").
                                    replace('"', '').replace("\n", "")[0:100] + "', 'danger', 0)")
            return
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

    def get_access_switch_list(self, obj_response):
        """ Load the list that contains all the switches that are in the local database"""
        if self.exception is not None:
            obj_response.script("create_notification('Connection problem', '" + str(self.exception).replace("'", "").
                                    replace('"', '').replace("\n", "")[0:100] + "', 'danger', 0)")
            return
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
