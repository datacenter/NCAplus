"""
*************************************************************************
 Copyright (c) 2016 Cisco Systems, Inc.  All rights reserved.
*************************************************************************
Sets connections with APIC controller using the API. This class is for operations
that are not supported in the Cobra SDK
"""
from constant import *
import requests
import json
import datetime

class api_apic_base:
    def __init__(self, url, user, password):
        """
        Login into the APIC when the object is created
        :param url:
        :param user:
        :param password:
        :return:
        """
        self.url = url
        self.user = user
        self.auth_token = ''
        self.cookies = {}
        credentials = {'aaaUser': {'attributes': {'name': user, 'pwd': password}}}
        json_credentials = json.dumps(credentials)
        login_url = url + API_URL + 'aaaLogin.json'
        try:
            post_response = requests.post(login_url, data=json_credentials)
            auth = json.loads(post_response.text)
            login_attributes = auth['imdata'][0]['aaaLogin']['attributes']
            self.auth_token = login_attributes['token']

            self.cookies['APIC-Cookie'] = login_attributes['token']
            self.connected = True

        except Exception, e:
            print "Exception on APIC pull: %s ", e
            self.connected = False

    def __repr__(self):
        return 'Connected to %s with userid: %s' % (self.url, self.user)

    def get_endpoint_track(self, endpoint_dn):
        """
        Returns the track for an specific endpoint using a list of generic objects
        :param endpoint_dn:
        :return:
        """
        call_url = self.url + MQ_API2_URL + 'troubleshoot.eptracker.json?ep=' + endpoint_dn
        get_response = requests.get(call_url, cookies=self.cookies, verify=False)
        inbounddata = get_response.json()
        end_point_track_list = []
        for item in inbounddata['imdata']:
            end_point_track = type('event', (object,), {})
            # Format date
            date = datetime.datetime.strptime(item['troubleshootEpTransition']['attributes']['date'][:-6],
                                              "%Y-%m-%dT%H:%M:%S.%f")
            end_point_track.date = date.strftime('%m-%d-%Y %H:%M:%S.%f')
            # Format leaf info
            end_point_track.path = item['troubleshootEpTransition']['attributes']['path']\
                .replace('topology/pod-1/paths','node').replace('pathep-[', '').replace(']','')
            end_point_track.action = item['troubleshootEpTransition']['attributes']['action']
            end_point_track_list.append(end_point_track)
        return end_point_track_list

