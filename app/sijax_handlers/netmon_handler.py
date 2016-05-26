"""
*************************************************************************
 Copyright (c) 2016 Cisco Systems, Inc.  All rights reserved.
*************************************************************************
Helper for views.py

"""
from base_handler import base_handler2, REMOVED_TENANTS
import traceback
import app.model
from flask import g


class netmon_handler(base_handler2):

    def __init__(obj_response):
        """
        Manages all the operations related with VLANs/Networks or VLAN profiles
        :param obj_response:
        :param formvalues:
        :return:
        """
        try:
            netmon_handler.apic_object = netmon_handler.init_connections()
        except Exception as e:
            print traceback.print_exc()
            obj_response.script("create_notification('Connection problem', '" + str(e).replace("'", "").
                                    replace('"', '').replace("\n", "")[0:100] + "', 'danger', 0)")
            return

    def network_list(self, obj_response):
        try:
            network_list = ''
            for tenant in netmon_handler.apic_object.get_all_tenants():
                network_aps = netmon_handler.apic_object.get_ap_by_tenant(str(tenant.dn))
                if len(network_aps) > 0:
                    if tenant.name not in REMOVED_TENANTS:
                        networks = netmon_handler.apic_object.get_epg_by_ap(str(network_aps[0].dn))
                        network_list += '<ul style="padding-left:10px;font-size:.9em;">'
                        network_list += '<label data-toggle="collapse" data-target="#' + tenant.name + '" style="float:left;cursor:pointer">'
                        network_list += '<i class="fa fa-chevron-circle-down" aria-hidden="true"></i></label>&nbsp;' + tenant.name
                        network_list += '<div id="' + tenant.name + '" class="collapse">'
                        for network in networks:
                            network_list += '<div style="clear:both; padding-left:10px;font-size:.8em;">' + str(
                                network.name) + '</div>'
                        network_list += '</div>'
                        network_list += '</ul>'
            obj_response.html("#network_list", network_list)
            obj_response.script('$("#busy_indicator").hide()')
        except Exception as e:
            print traceback.print_exc()
            obj_response.script("create_notification('Can not retrieve networks', '" + str(e).replace("'", "").
                                replace('"', '').replace("\n", "")[0:100] + "', 'danger', 0)")
        finally:
            g.db.close()
            obj_response.html("#delete_network_response", '')
