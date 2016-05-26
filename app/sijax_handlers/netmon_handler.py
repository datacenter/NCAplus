"""
*************************************************************************
 Copyright (c) 2016 Cisco Systems, Inc.  All rights reserved.
*************************************************************************
Helper for views.py

"""
from base_handler import base_handler2, REMOVED_TENANTS
import traceback
import app.model
from flask import g, render_template
import datetime


class netmon_handler(base_handler2):

    def __init__(self):
        """
        Manages all the operations related with VLANs/Networks or VLAN profiles
        :param obj_response:
        :param formvalues:
        :return:
        """
        try:
            self.apic_object = netmon_handler.init_connections()
            self.exception = None
        except Exception as e:
            self.exception = e
            print traceback.print_exc()

    def network_list(self, obj_response):
        if self.exception is not None:
            obj_response.script("create_notification('Connection problem', '" + str(self.exception).replace("'", "").
                                    replace('"', '').replace("\n", "")[0:100] + "', 'danger', 0)")
            return
        try:
            html_response = ''
            for tenant in self.apic_object.get_all_tenants():
                network_aps = self.apic_object.get_ap_by_tenant(str(tenant.dn))
                if len(network_aps) > 0:
                    if tenant.name not in REMOVED_TENANTS:
                        networks = self.apic_object.get_epg_by_ap(str(network_aps[0].dn))
                        html_response += render_template('netmon/network_list.html', tenant=tenant, networks=networks)
            obj_response.html("#network_list", html_response)
            obj_response.script('$("#busy_indicator").hide()')
        except Exception as e:
            print traceback.print_exc()
            obj_response.script("create_notification('Can not retrieve networks', '" + str(e).replace("'", "").
                                replace('"', '').replace("\n", "")[0:100] + "', 'danger', 0)")
        finally:
            g.db.close()
            obj_response.html("#delete_network_response", '')

    def get_endpoints(self, obj_response, form_values):
        if self.exception is not None:
            obj_response.script("create_notification('Connection problem', '" + str(self.exception).replace("'", "").
                                    replace('"', '').replace("\n", "")[0:100] + "', 'danger', 0)")
            return
        try:
            epg_dn = 'uni/tn-%s/ap-%s/epg-%s' % (form_values['tenant'],form_values['tenant'],form_values['network'])
            html_response = render_template('netmon/endpoint_list.html',
                                            endpoints=self.apic_object.get_endpoints(epg_dn))
            obj_response.html("#endpoints", html_response)
            obj_response.script('$("#endpoints_busy_indicator").hide()')
        except Exception as e:
            print traceback.print_exc()
            obj_response.script("create_notification('Can not retrieve end points', '" + str(e).replace("'", "").
                                replace('"', '').replace("\n", "")[0:100] + "', 'danger', 0)")
        finally:
            g.db.close()

    def get_epg_health_score(self, obj_response, form_values):
        if self.exception is not None:
            obj_response.script("create_notification('Connection problem', '" + str(self.exception).replace("'", "").
                                    replace('"', '').replace("\n", "")[0:100] + "', 'danger', 0)")
            return
        try:
            epg = self.apic_object.get_epg(form_values['tenant'], form_values['network'])
            score = self.apic_object.get_epg_health_score(str(epg.dn))
            html_response = render_template('netmon/epg_score.html',
                                            score=int(score))
            obj_response.html("#epg_score", html_response)
        except Exception as e:
            print traceback.print_exc()
            obj_response.script("create_notification('Can not retrieve score', '" + str(e).replace("'", "").
                                replace('"', '').replace("\n", "")[0:100] + "', 'danger', 0)")
        finally:
            g.db.close()

    def get_faults_history(self, obj_response, form_values):
        if self.exception is not None:
            obj_response.script("create_notification('Connection problem', '" + str(self.exception).replace("'", "").
                                    replace('"', '').replace("\n", "")[0:100] + "', 'danger', 0)")
            return
        try:
            epg = self.apic_object.get_epg(form_values['tenant'], form_values['network'])
            fault_list = self.apic_object.get_faults_history(str(epg.dn))
            html_response = render_template('netmon/fault_list.html',
                                            faults=fault_list)
            obj_response.html("#history", html_response)
        except Exception as e:
            print traceback.print_exc()
            obj_response.script("create_notification('Can not retrieve score', '" + str(e).replace("'", "").
                                replace('"', '').replace("\n", "")[0:100] + "', 'danger', 0)")
        finally:
            g.db.close()

    def get_traffic_chart(self, obj_response, form_values):
        if self.exception is not None:
            obj_response.script("create_notification('Connection problem', '" + str(self.exception).replace("'", "").
                                    replace('"', '').replace("\n", "")[0:100] + "', 'danger', 0)")
            return
        try:

            epg = self.apic_object.get_epg(form_values['tenant'], form_values['network'])
            traffic_list = self.apic_object.get_stats(str(epg.dn))


            self.apic_object.get_faults(str(epg.dn))


            labels = []
            data = []

            for traffic in traffic_list:
                date = datetime.datetime.strptime(traffic.repIntvEnd[:-13], "%Y-%m-%dT%H:%M")
                labels.append(str(date.hour) + ':' + str(date.minute))
                data.append(traffic.unicastPer)
            obj_response.script("load_traffic_chart(%s, %s)" % (labels, data))
        except Exception as e:
            print traceback.print_exc()
            obj_response.script("create_notification('Can not retrieve score', '" + str(e).replace("'", "").
                                replace('"', '').replace("\n", "")[0:100] + "', 'danger', 0)")
        finally:
            g.db.close()