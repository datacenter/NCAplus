"""
Helper for views.py

"""
from base_handler import base_handler, REMOVED_TENANTS
import traceback
from flask import g, render_template
import datetime
import json

class netmon_handler(base_handler):

    def __init__(self):
        """
        Manages all the operations related with network monitoring
        :return:
        """
        try:
            self.cobra_apic_object = netmon_handler.init_connections()
            self.exception = None
        except Exception as e:
            self.exception = e
            print traceback.print_exc()

    def network_list(self, obj_response):
        """
        Returns a list of networks grouped by tenant
        :param obj_response:
        :return:
        """
        if self.exception is not None:
            obj_response.script("create_notification('Connection problem', '" + str(self.exception).replace("'", "").
                                    replace('"', '').replace("\n", "")[0:100] + "', 'danger', 0)")
            return
        try:
            network_tree = []
            for tenant in self.cobra_apic_object.get_all_tenants():
                if tenant.name not in REMOVED_TENANTS:
                    network_tree.append({
                        "text": tenant.name,
                        "selectable": False,
                        "color": "#FFFFFF",
                        "backColor": "#245580"
                    })
                    network_aps = self.cobra_apic_object.get_ap_by_tenant(str(tenant.dn))
                    if len(network_aps) > 0:
                        network_tree[len(network_tree) - 1]["nodes"] = []
                        for network_ap in network_aps:
                            network_tree[len(network_tree) - 1]["nodes"].append({
                                "text": network_ap.name,
                                "selectable": False,
                                "color": "#000000",
                                "backColor": "#FFFFFF"
                            })
                            networks = self.cobra_apic_object.get_epg_by_ap(str(network_ap.dn))
                            if len(networks) > 0:
                                network_tree[len(network_tree) - 1]["nodes"][len(network_tree[len(network_tree) - 1]["nodes"]) - 1]["nodes"] = []
                                for network in networks:
                                    network_tree[len(network_tree) - 1]["nodes"][len(network_tree[len(network_tree) - 1]["nodes"]) - 1]["nodes"].append({
                                        "text": network.name,
                                    })
            obj_response.script('$("#busy_indicator").hide()')


            data = json.dumps(network_tree, ensure_ascii=False)
            obj_response.script('set_network_tree(' + data + ')')
        except Exception as e:
            print traceback.print_exc()
            obj_response.script("create_notification('Can not retrieve networks', '" + str(e).replace("'", "").
                                replace('"', '').replace("\n", "")[0:100] + "', 'danger', 0)")
        finally:
            g.db.close()
            obj_response.html("#delete_network_response", '')

    def get_endpoints(self, obj_response, form_values):
        """
        Return a list of end points associated to an end point group
        :param obj_response:
        :param form_values:
        :return:
        """
        if self.exception is not None:
            obj_response.script("create_notification('Connection problem', '" + str(self.exception).replace("'", "").
                                    replace('"', '').replace("\n", "")[0:100] + "', 'danger', 0)")
            return
        try:
            epg_dn = 'uni/tn-%s/ap-%s/epg-%s' % (form_values['tenant'], form_values['ap'], form_values['network'])
            html_response = render_template('netmon/endpoint_list.html',
                                            endpoints=self.cobra_apic_object.get_endpoints(epg_dn),
                                            tenant=form_values['tenant'],
                                            ap=form_values['ap'],
                                            network=form_values['network'])
            obj_response.html("#endpoints", html_response)
            obj_response.script('$("#endpoints_busy_indicator").hide()')
        except Exception as e:
            print traceback.print_exc()
            obj_response.script("create_notification('Can not retrieve end points', '" + str(e).replace("'", "").
                                replace('"', '').replace("\n", "")[0:100] + "', 'danger', 0)")
        finally:
            g.db.close()

    def get_epg_health_score(self, obj_response, form_values):
        """
        Returns the health score of a specific end point group
        :param obj_response:
        :param form_values:
        :return:
        """
        if self.exception is not None:
            obj_response.script("create_notification('Connection problem', '" + str(self.exception).replace("'", "").
                                    replace('"', '').replace("\n", "")[0:100] + "', 'danger', 0)")
            return
        try:
            epg = self.cobra_apic_object.get_epg(form_values['tenant'], form_values['ap'], form_values['network'])
            score = self.cobra_apic_object.get_epg_health_score(str(epg.dn))
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
        """
        Get the history of faults within an end point group
        :param obj_response:
        :param form_values:
        :return:
        """
        if self.exception is not None:
            obj_response.script("create_notification('Connection problem', '" + str(self.exception).replace("'", "").
                                    replace('"', '').replace("\n", "")[0:100] + "', 'danger', 0)")
            return
        try:
            epg = self.cobra_apic_object.get_epg(form_values['tenant'], form_values['ap'], form_values['network'])
            fault_list = self.cobra_apic_object.get_faults_history(str(epg.dn))
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
        """
        returns traffic statistics
        :param obj_response:
        :param form_values:
        :return:
        """
        if self.exception is not None:
            obj_response.script("create_notification('Connection problem', '" + str(self.exception).replace("'", "").
                                    replace('"', '').replace("\n", "")[0:100] + "', 'danger', 0)")
            return
        try:
            epg = self.cobra_apic_object.get_epg(form_values['tenant'], form_values['ap'], form_values['network'])
            traffic_list = self.cobra_apic_object.get_stats(str(epg.dn))
            labels = []
            data = []
            for traffic in traffic_list:
                date = datetime.datetime.strptime(traffic.repIntvEnd[:-13], "%Y-%m-%dT%H:%M")
                labels.append(date.strftime('%H:%M'))
                data.append(traffic.unicastPer)
            obj_response.script("load_traffic_chart(%s, %s)" % (labels, data))
        except Exception as e:
            print traceback.print_exc()
            obj_response.script("create_notification('Can not retrieve score', '" + str(e).replace("'", "").
                                replace('"', '').replace("\n", "")[0:100] + "', 'danger', 0)")
        finally:
            g.db.close()

    def get_faults(self, obj_response, form_values):
        """
        Return the active faults within the epg
        :param obj_response:
        :param form_values:
        :return:
        """
        if self.exception is not None:
            obj_response.script("create_notification('Connection problem', '" + str(self.exception).replace("'", "").
                                    replace('"', '').replace("\n", "")[0:100] + "', 'danger', 0)")
            return
        try:
            epg = self.cobra_apic_object.get_epg(form_values['tenant'], form_values['ap'], form_values['network'])
            fault_list = self.cobra_apic_object.get_faults(str(epg.dn))
            html_response = render_template('netmon/fault_list.html',
                                            faults=fault_list)
            obj_response.html("#faults", html_response)
        except Exception as e:
            print traceback.print_exc()
            obj_response.script("create_notification('Can not retrieve score', '" + str(e).replace("'", "").
                                replace('"', '').replace("\n", "")[0:100] + "', 'danger', 0)")
        finally:
            g.db.close()

    def get_endpoint_track(self, obj_response, form_values):
        """
        Shows the endpoint track
        This operation is not supported in cobra, we are using direct api calls
        :param obj_response:
        :param form_values:
        :return:
        """
        if self.exception is not None:
            obj_response.script("create_notification('Connection problem', '" + str(self.exception).replace("'", "").
                                    replace('"', '').replace("\n", "")[0:100] + "', 'danger', 0)")
            return
        try:
            epg = self.cobra_apic_object.get_epg(form_values['tenant'], form_values['ap'], form_values['network'])
            api_apic = self.create_api_apic()
            end_point_track_list = api_apic.get_endpoint_track(str(epg.dn) + '/cep-' + form_values['endpoint_mac'])
            html_response = render_template('netmon/endpoint_track_list.html',
                                            end_point_track_list=end_point_track_list)
            obj_response.html("#network_track", html_response)
        except Exception as e:
            print traceback.print_exc()
            obj_response.script("create_notification('Can not retrieve score', '" + str(e).replace("'", "").
                                replace('"', '').replace("\n", "")[0:100] + "', 'danger', 0)")
        finally:
            g.db.close()


