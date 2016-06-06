"""

Sets connections with APIC controller for creation and deletion of object
"""

from cobra.model.vz import Filter, BrCP, Subj, RsSubjFiltAtt
from cobra.mit.access import MoDirectory
from cobra.mit.session import LoginSession
from cobra.mit.request import ConfigRequest, CommitError
from constant import *
from cobra.mit.request import DnQuery
from cobra.model.fv import Tenant, BD, Subnet, AEPg, Ap, RsProv, RsCons, RsDomAtt, RsPathAtt, RsCtx, RsPathAtt
from cobra.mit.request import ClassQuery

__author__ = 'Santiago Flores Kanter (sfloresk@cisco.com)'


class cobra_apic_base:
    def __init__(self):
        self.session = None
        self.moDir = None
        self.configReq = None
        self.uniMo = None

    """ Authentication """
    def login(self, url, user, password):
        """
        Login to the APIC
        :param url:
        :param user:
        :param password:
        :return:
        """
        self.apic_url = url
        self.apic_user = user
        self.session = LoginSession(url, user, password)
        self.moDir = MoDirectory(self.session)
        self.moDir.login()
        self.configReq = ConfigRequest()
        self.uniMo = self.moDir.lookupByDn('uni')

    def logout(self):
        """
        Logout from the APIC
        :return:
        """
        self.moDir.logout()

    """ Commits """
    def commit(self, commit_object):
        """
        Commits object changes to controller
        :param commit_object:
        :return:
        """

        self.configReq = ConfigRequest()
        self.configReq.addMo(commit_object)
        self.moDir.commit(self.configReq)

    """ Queries """
    def query_child_objects(self, dn_query_name):
        """
        Retrieve the object using the dn and return all the children under it
        :param dn_query_name: dn of the management object
        :return:
        """
        dn_query = DnQuery(dn_query_name)
        dn_query.queryTarget = QUERY_TARGET_CHILDREN
        child_mos = self.moDir.query(dn_query)
        return child_mos

    """ Generic Deletes """
    def delete_dn_by_pattern(self, dn_object_list, dn_pattern, recursive):
        """
        Travers a dn list and compare each member with a pattern. If there is a match that object will be removed.
        If recursive is true, the algorithm will also do a recursive look for the children of each object looking
        for the pattern: will stop only when there is no more children to look for.
        :param dn_object_list:
        :param dn_pattern:
        :param recursive:
        :return:
        """
        for dn_object in dn_object_list:
            if dn_pattern in str(dn_object.dn):
                try:
                    self.delete_by_dn(str(dn_object.dn))
                except CommitError as e:
                    print 'Could not delete ' + str(dn_object.dn) + ' -> ' + str(e)
            elif recursive:
                children = self.query_child_objects(dn_object.dn)
                if children is not None:
                    self.delete_dn_by_pattern(children, dn_pattern, recursive)

    def delete_by_dn(self, dn_name):
        """
        Retrieve a mo and it removes it from the APIC
        :param dn_name:
        :return:
        """
        dn_object = self.moDir.lookupByDn(dn_name)
        if dn_object is not None:
            dn_object.delete()
            self.commit(dn_object)

    """ Tenants """
    def create_tenant(self, tenant_name):
        """
        Creates a tenant and commit changes to controller
        :param tenant_name:
        :return:
        """
        fv_tenant_mo = Tenant(self.uniMo, tenant_name)
        self.commit(fv_tenant_mo)
        return fv_tenant_mo

    def delete_tenant(self, tenant_dn):
        """
        Deletes a tenant and commit changes to controller
        :param tenant_dn:
        :return:
        """
        self.delete_by_dn(tenant_dn)

    def get_all_tenants(self):
        """
        Searches all tenants within apic
        :return:
        """
        class_query = ClassQuery('fvTenant')
        tn_list = self.moDir.query(class_query)
        return tn_list

    """ Switch Profiles """
    def delete_switch_profile(self, switch_profile_name):
        """
        Deletes an access policy switch profile
        :param switch_profile_name:
        :return:
        """
        self.delete_by_dn('uni/infra/nprof-' + switch_profile_name)

    """ Bridge domains """
    def create_bd(self, bd_name, tenant_dn, default_gw, **creation_props):
        """
        Creates a BD object. Creates a subnet for the default gateway if it is not None
        :param bd_name:
        :param tenant_dn:
        :param default_gw:
        :param creation_props:
        :return:
        """
        fv_bd_mo = BD(tenant_dn, bd_name, creation_props)
        self.commit(fv_bd_mo)
        if default_gw is not None and len(default_gw) > 0:
            fv_subnet_mo = Subnet(fv_bd_mo, default_gw)
            self.commit(fv_subnet_mo)
        return fv_bd_mo

    def delete_bd(self, bd_dn):
        """
        Removes a bridge domain
        :param bd_dn:
        :return:
        """
        self.delete_by_dn(bd_dn)

    def get_bds_by_tenant(self, tenant_dn):
        """
        Retrieve a list with all bridge domains under a tenant
        :param tenant_dn:
        :return:
        """
        # Queries all the children and then filter them in memory looking for the ones that belongs to the BD class
        tn_children = self.query_child_objects(tenant_dn)
        return filter(lambda x: type(x).__name__ == 'BD', tn_children)

    def get_all_bds(self):
        """
        Returns a list of all bridge domains in the fabric
        :return:
        """
        class_query = ClassQuery('fvBD')
        bd_list = self.moDir.query(class_query)
        return bd_list

    """ Filters """
    def create_filter(self, tenant_dn, filter_name):
        """
        Creates a filter under a tenant
        :param tenant_dn:
        :param filter_name:
        :return:
        """
        vz_filter_mo = Filter(tenant_dn, filter_name)
        self.commit(vz_filter_mo)

    def delete_filter(self, filter_dn):
        """
        Removes a filter from the APIC
        :param filter_dn:
        :return:
        """
        self.delete_by_dn(filter_dn)

    def get_filters_by_tenant(self, tenant_dn):
        """
        Query the filters that are children of a tenant
        :param tenant_dn:
        :return:
        """
        tn_children = self.query_child_objects(tenant_dn)
        # Queries all the children and then filter them in memory looking for the ones that belongs to the Filter class
        return filter(lambda x: type(x).__name__ == 'Filter', tn_children)

    """ Contracts """
    def create_contract(self, tenant_dn, contract_name):
        """
        Creates a contract under a tenant
        :param tenant_dn:
        :param contract_name:
        :return:
        """
        vz_contract = BrCP(tenant_dn, contract_name)
        self.commit(vz_contract)

    def delete_contract(self, contract_dn):
        """
        Removes a contract from the APIC
        :param contract_dn:
        :return:
        """
        self.delete_by_dn(contract_dn)

    def get_contracts_by_tenant(self, tenant_dn):
        """
        Return a list with all the contracts under a tenant
        :param tenant_dn:
        :return:
        """
        tn_children = self.query_child_objects(tenant_dn)
        # Queries all the children and then filter them in memory looking for the ones that belongs to the BrCP class
        return filter(lambda x: type(x).__name__ == 'BrCP', tn_children)

    def assign_contract(self, epg_dn, provider_dn, consumer_dn):
        """
        Assign contracts to an end point group
        :param epg_dn:
        :param provider_dn: Provider contract
        :param consumer_dn: Consumer contract
        :return:
        """
        epg_mo = self.moDir.lookupByDn(epg_dn)
        if len(provider_dn) > 0:
            # Retrieve the provider contract
            provider_mo = self.moDir.lookupByDn(provider_dn)
            # Create the provider relationship with EPG
            rsprov_mo = RsProv(epg_mo, provider_mo.name)
            self.commit(rsprov_mo)
        if len(consumer_dn) > 0:
            # Retrieve the consumer contract
            consumer_mo = self.moDir.lookupByDn(consumer_dn)
            # Creates the consumer relationship with EPG
            rscons_mo = RsCons(epg_mo, consumer_mo.name)
            self.commit(rscons_mo)

    def delete_assign_contract(self, epg_dn):
        """
        Removes the EPG's assigned contracts
        :param epg_dn:
        :return:
        """
        # Queries all the EPG children and then filter them in memory looking for the ones that belongs to the
        # RsProv class
        epg_providers = filter(lambda x: type(x).__name__ == 'RsProv', self.query_child_objects(epg_dn))
        # Queries all the EPG children and then filter them in memory looking for the ones that belongs to the
        # RsCons class
        epg_consumers = filter(lambda x: type(x).__name__ == 'RsCons', self.query_child_objects(epg_dn))
        # For each consumer and provider contract removes the relationship
        for provider in epg_providers:
            provider.delete()
            self.commit(provider)
        for consumer in epg_consumers:
            consumer.delete()
            self.commit(consumer)

    """ Subjects """
    def create_subject(self, filter_dn, contract_dn, subject_name):
        """
        Creates a subject between a contract and a filter
        :param filter_dn:
        :param contract_dn:
        :param subject_name:
        :return:
        """
        subject_dn = Subj(contract_dn, subject_name)
        self.commit(subject_dn)
        filter_mo = self.moDir.lookupByDn(filter_dn)
        rs_filter_subject = RsSubjFiltAtt(subject_dn, filter_mo.name)
        self.commit(rs_filter_subject)

    def get_subjects_by_contract(self, contract_dn):
        """
        Returns all subject under a given contract
        :param contract_dn:
        :return:
        """
        contract_children = self.query_child_objects(contract_dn)
        # Queries all the children and then filter them in memory looking for the ones that belongs to the Subj class
        return filter(lambda x: type(x).__name__ == 'Subj', contract_children)

    def delete_subject(self, subject_dn):
        """
        Removes a subject from the APIC
        :param subject_dn:
        :return:
        """
        self.delete_by_dn(subject_dn)

    """ End Point Groups """
    def create_epg(self, ap_dn, bd_dn, epg_name):
        """
        Creates a EPG and, if the bd_dn parameter is not None, will associate that bridge domain to the EPG
        :param ap_dn: application profile to be used as parent
        :param bd_dn: bridge domain to be associated with the EPG
        :param epg_name:
        :return:
        """
        epg_mo = AEPg(ap_dn, epg_name)
        self.commit(epg_mo)
        if bd_dn is not None and len(bd_dn) > 0:
            # Queries all the children and then filter them in memory looking for the ones that belongs to the RsBd
            #  class. Choose the first one and assign it to the rsbd_mo variable
            rsbd_mo = filter(lambda x: type(x).__name__ == 'RsBd', self.query_child_objects(str(epg_mo.dn)))[0]
            # The tnFvBDName is the attribute that sets the relationship between the bridge domain and the EPG.
            # Looks for the bd_dn object and then assign its name to the tnFvBDName attribute of the rsdb_mo object
            rsbd_mo.tnFvBDName = self.moDir.lookupByDn(bd_dn).name
            self.commit(rsbd_mo)
        return epg_mo

    def delete_epg(self, epg_dn):
        """
        Removes an EPG from the APIC
        :param epg_dn:
        :return:
        """
        self.delete_by_dn(epg_dn)

    def get_epg_by_ap(self, ap_dn):
        """
        Returns a list of end point groups under an application profile
        :param ap_dn:
        :return:
        """
        ap_children = self.query_child_objects(ap_dn)
        # Queries all the children and then filters them in memory looking for the ones that belongs to the AEPg class.
        return filter(lambda x: type(x).__name__ == 'AEPg', ap_children)

    """ Application Profiles """
    def create_ap(self, tenant_dn, ap_name):
        """
        Creates an application profile
        :param tenant_dn:
        :param ap_name:
        :return:
        """
        ap_mo = Ap(tenant_dn, ap_name)
        self.commit(ap_mo)
        return ap_mo

    def delete_ap(self, ap_dn):
        """
        Removes an application profile
        :param ap_dn:
        :return:
        """
        self.delete_by_dn(ap_dn)

    def get_ap_by_tenant(self, tenant_dn):
        """
        Returns a list of application profiles under a tenant
        :param tenant_dn:
        :return:
        """
        tn_children = self.query_child_objects(tenant_dn)
        # Queries all the children and then filters them in memory looking for the ones that belongs to the Ap class.
        return filter(lambda x: type(x).__name__ == 'Ap', tn_children)

    def __repr__(self):
        return 'Connected to %s with userid: %s' % (self.apic_url, self.apic_user)