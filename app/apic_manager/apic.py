"""

Sets connections with APIC controller for creation and deletion of object such as Tenants, VMMs and switch profiles

"""

from constant import *
from cobra.mit.access import MoDirectory
from cobra.mit.session import LoginSession
from cobra.mit.request import ConfigRequest, CommitError
from cobra.model.fv import Tenant, BD, Subnet, AEPg, Ap, RsProv, RsCons
from cobra.model.vmm import ProvP, DomP, UsrAccP, CtrlrP, RsAcc
# from cobra.modelimpl.infra.nodep import NodeP
from cobra.mit.request import DnQuery, ClassQuery
from cobra.model.vz import Filter, BrCP, Subj, RsSubjFiltAtt


__author__ = 'Santiago Flores Kanter (sfloresk@cisco.com)'


class Apic:

    def __init__(self):
        self.session = None
        self.moDir = None
        self.configReq = None
        self.uniMo = None
    # Commits object changes to controller

    def commit(self, commit_object):
        self.configReq = ConfigRequest()
        self.configReq.addMo(commit_object)
        self.moDir.commit(self.configReq)

    # Creates a tenant and commit changes to controller
    def create_tenant(self, tenant_name):
        fv_tenant_mo = Tenant(self.uniMo, tenant_name)
        self.commit(fv_tenant_mo)

    # Deletes a tenant and commit changes to controller
    def delete_tenant(self, tenant_dn):
        fv_tenant_mo = self.moDir.lookupByDn(tenant_dn)
        if fv_tenant_mo is not None:
            fv_tenant_mo.delete()
            self.commit(fv_tenant_mo)

    # Searches all tenants within apic
    def get_all_tenants(self):
        class_query = ClassQuery('fvTenant')
        tn_list = self.moDir.query(class_query)
        return tn_list

    """
    # Creates an access policy switch profile
    def create_switch_profile(self, switch_profile_name):
        infra = self.moDir.lookupByDn('uni/infra')
        node = NodeP(infra, switch_profile_name)
        self.commit(node)
    """
    # Deletes an access policy switch profile
    def delete_switch_profile(self, switch_profile_name):
        switch_profile = self.moDir.lookupByDn('uni/infra/nprof-' + switch_profile_name)
        if switch_profile is not None:
            switch_profile.delete()
            self.commit(switch_profile)

    # Creates a virtual machine manager profile
    def create_vmmp(self, provider_name, vmmp_name):
        vmmp_provider = self.moDir.lookupByDn('uni/vmmp-' + provider_name)
        vmmp = DomP(vmmp_provider, vmmp_name)
        self.commit(vmmp)

    # Creates a virtual machine manager profile
    def delete_vmmp(self, provider_name, vmmp_name):
        vmmp_provider = self.moDir.lookupByDn('uni/vmmp-' + provider_name)
        vmmp = DomP(vmmp_provider, vmmp_name)
        self.commit(vmmp)

    def query_child_objects(self, dn_query_name):
        dn_query = DnQuery(dn_query_name)
        dn_query.queryTarget = QUERY_TARGET_CHILDREN
        child_mos = self.moDir.query(dn_query)
        return child_mos

    def delete_dn_by_pattern(self, dn_object_list, dn_pattern, recursive):
        for dn_object in dn_object_list:
            if dn_pattern in str(dn_object.dn):
                try:
                    # if '[' not in str(dn_object.dn):
                    self.delete_by_dn(str(dn_object.dn))
                except CommitError as e:
                    print 'Could not delete ' + str(dn_object.dn) + ' -> ' + str(e)
            elif recursive:
                children = self.query_child_objects(dn_object.dn)
                if children is not None:
                    self.delete_dn_by_pattern(children, dn_pattern, recursive)

    def delete_by_dn(self, dn_name):
        dn_object = self.moDir.lookupByDn(dn_name)
        if dn_object is not None:
            dn_object.delete()
            self.commit(dn_object)
            print 'Deleted ---> ' + dn_name

# Init the session, MoDirectory, ConfigRequest and uniMo objects.
    def login(self, url, user, password):
        self.session = LoginSession(url, user, password)
        self.moDir = MoDirectory(self.session)
        self.moDir.login()
        self.configReq = ConfigRequest()
        self.uniMo = self.moDir.lookupByDn('uni')

    def logout(self):
        self.moDir.logout()

    def create_bd(self, bd_name, tenant_dn, default_gw):
        fv_bd_mo = BD(tenant_dn, bd_name)
        self.commit(fv_bd_mo)
        if default_gw is not None and len(default_gw) > 0:
            fv_subnet_mo = Subnet(fv_bd_mo, default_gw)
            self.commit(fv_subnet_mo)

    def delete_bd(self, bd_dn):
        db_mo = self.moDir.lookupByDn(bd_dn)
        db_mo.delete()
        self.commit(db_mo)

    def get_bds_by_tenant(self, tenant_dn):
        tn_children = self.query_child_objects(tenant_dn)
        return filter(lambda x: type(x).__name__ == 'BD', tn_children)

    def get_all_bds(self):
        class_query = ClassQuery('fvBD')
        bd_list = self.moDir.query(class_query)
        return bd_list

    def create_filter(self,tenant_dn, filter_name):
        vz_filter_mo = Filter(tenant_dn, filter_name)
        self.commit(vz_filter_mo)

    def delete_filter(self, filter_dn):
        filter_mo = self.moDir.lookupByDn(filter_dn)
        filter_mo.delete()
        self.commit(filter_mo)

    def create_contract(self, tenant_dn, contract_name):
        vz_contract = BrCP(tenant_dn, contract_name)
        self.commit(vz_contract)

    def delete_contract(self, contract_dn):
        contract_mo = self.moDir.lookupByDn(contract_dn)
        contract_mo.delete()
        self.commit(contract_mo)

    def get_filters_by_tenant(self, tenant_dn):
        tn_children = self.query_child_objects(tenant_dn)
        return filter(lambda x: type(x).__name__ == 'Filter', tn_children)

    def get_contracts_by_tenant(self, tenant_dn):
        tn_children = self.query_child_objects(tenant_dn)
        return filter(lambda x: type(x).__name__ == 'BrCP', tn_children)

    def create_subject(self, filter_dn, contract_dn, subject_name):
        subject_dn = Subj(contract_dn, subject_name)
        self.commit(subject_dn)
        filter_mo = self.moDir.lookupByDn(filter_dn)
        rs_filter_subject = RsSubjFiltAtt(subject_dn, filter_mo.name)
        self.commit(rs_filter_subject)

    def get_subjects_by_contract(self, contract_dn):
        contract_children = self.query_child_objects(contract_dn)
        return filter(lambda x: type(x).__name__ == 'Subj', contract_children)

    def delete_subject(self, subject_dn):
        subject_mo = self.moDir.lookupByDn(subject_dn)
        subject_mo.delete()
        self.commit(subject_mo)

    def create_epg(self, ap_dn, bd_dn, epg_name):
        epg_mo = AEPg(ap_dn, epg_name)
        self.commit(epg_mo)
        if bd_dn is not None and len(bd_dn) > 0:
            rsbd_mo = filter(lambda x: type(x).__name__ == 'RsBd', self.query_child_objects(str(epg_mo.dn)))[0]
            rsbd_mo.tnFvBDName = self.moDir.lookupByDn(bd_dn).name
            self.commit(rsbd_mo)

    def delete_epg(self, epg_dn):
        epg_mo = self.moDir.lookupByDn(epg_dn)
        epg_mo.delete()
        self.commit(epg_mo)

    def create_ap(self, tenant_dn, ap_name):
        ap_mo = Ap(tenant_dn, ap_name)
        self.commit(ap_mo)

    def delete_ap(self, ap_dn):
        ap_mo = self.moDir.lookupByDn(ap_dn)
        ap_mo.delete()
        self.commit(ap_mo)

    def get_ap_by_tenant(self, tenant_dn):
        tn_children = self.query_child_objects(tenant_dn)
        return filter(lambda x: type(x).__name__ == 'Ap', tn_children)

    def get_epg_by_ap(self, ap_dn):
        ap_children = self.query_child_objects(ap_dn)
        return filter(lambda x: type(x).__name__ == 'AEPg', ap_children)

    def assign_contract(self, epg_dn, provider_dn, consumer_dn):
        epg_mo = self.moDir.lookupByDn(epg_dn)
        if len(provider_dn) > 0:
            provider_mo = self.moDir.lookupByDn(provider_dn)
            rsprov_mo = RsProv(epg_mo, provider_mo.name)
            self.commit(rsprov_mo)
        if len(consumer_dn) > 0:
            consumer_mo = self.moDir.lookupByDn(consumer_dn)
            rscons_mo = RsCons(epg_mo, consumer_mo.name)
            self.commit(rscons_mo)

    def delete_assign_contract(self, epg_dn):
        epg_providers = filter(lambda x: type(x).__name__ == 'RsProv', self.query_child_objects(epg_dn))
        epg_consumers = filter(lambda x: type(x).__name__ == 'RsCons', self.query_child_objects(epg_dn))
        for provider in epg_providers:
            provider.delete()
            self.commit(provider)
        for consumer in epg_consumers:
            consumer.delete()
            self.commit(consumer)
