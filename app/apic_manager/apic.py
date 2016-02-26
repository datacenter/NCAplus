"""

Sets connections with APIC controller for creation and deletion of object such as Tenants, VMMs and switch profiles

"""

from constant import *
from cobra.mit.access import MoDirectory
from cobra.mit.session import LoginSession
from cobra.mit.request import ConfigRequest, CommitError
from cobra.model.fv import Tenant, BD, Subnet, AEPg, Ap, RsProv, RsCons, RsDomAtt, RsPathAtt, RsCtx, RsPathAtt
from cobra.model.vmm import ProvP, DomP, UsrAccP, CtrlrP, RsAcc
# from cobra.modelimpl.infra.nodep import NodeP
from cobra.mit.request import DnQuery, ClassQuery
from cobra.model.vz import Filter, BrCP, Subj, RsSubjFiltAtt
from cobra.modelimpl.fvns.vlaninstp import VlanInstP
from cobra.modelimpl.fvns.encapblk import EncapBlk
import re


__author__ = 'Santiago Flores Kanter (sfloresk@cisco.com)'

def natural_keys(text):
    '''
    alist.sort(key=natural_keys) sorts in human order
    '''
    return [atoi(c) for c in re.split('(\d+)', text)]


def atoi(text):
    return int(text) if text.isdigit() else text

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
        return fv_tenant_mo

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

    def create_bd(self, bd_name, tenant_dn, default_gw, **creation_props):
        fv_bd_mo = BD(tenant_dn, bd_name, creation_props)
        self.commit(fv_bd_mo)
        if default_gw is not None and len(default_gw) > 0:
            fv_subnet_mo = Subnet(fv_bd_mo, default_gw)
            self.commit(fv_subnet_mo)
        return fv_bd_mo

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
        return epg_mo

    def delete_epg(self, epg_dn):
        epg_mo = self.moDir.lookupByDn(epg_dn)
        epg_mo.delete()
        self.commit(epg_mo)

    def create_ap(self, tenant_dn, ap_name):
        ap_mo = Ap(tenant_dn, ap_name)
        self.commit(ap_mo)
        return ap_mo

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

    def create_vlan_abstraction(self, vlan_o):
        tn_list = filter(lambda x: x.name == vlan_o.tenant_name, self.get_all_tenants())
        if len(tn_list) == 0:
            vlan_tenant = self.create_tenant(vlan_o.tenant_name)
        else:
            vlan_tenant = tn_list[0]

        ap_list = filter(lambda x: type(x).__name__ == 'Ap' and x.name == vlan_o.ap_name,
                         self.query_child_objects(str(vlan_tenant.dn)))
        if len(ap_list) == 0:
            vlan_ap = self.create_ap(str(vlan_tenant.dn), vlan_o.ap_name)
        else:
            vlan_ap = ap_list[0]

        epg_list = filter(lambda x: type(x).__name__ == 'AEPg' and x.name == vlan_o.epg_name,
                          self.query_child_objects(str(vlan_ap.dn)))
        if len(epg_list) == 0:
            vlan_epg = self.create_epg(str(vlan_ap.dn), None, vlan_o.epg_name)
        else:
            vlan_epg = epg_list[0]

    def create_network(self, network_o):
            tenant_mo = self.moDir.lookupByDn(network_o.group)
            tenant_children = self.query_child_objects(network_o.group)
            ap_list = filter(lambda x: type(x).__name__ == 'Ap' and x.name == tenant_mo.name + "-ap",
                             tenant_children)
            if len(ap_list) == 0:
                network_ap = self.create_ap(str(tenant_mo.dn), tenant_mo.name + "-ap")
            else:
                network_ap = ap_list[0]
            bd_list = filter(lambda x: type(x).__name__ == 'BD',
                             tenant_children)
            if len(bd_list) > 0:
                bd_cxts = filter(lambda x: type(x).__name__ == 'RsCtx',
                                     self.query_child_objects(str(bd_list[0].dn)))
                if len(bd_cxts) > 0:
                    if bd_cxts[0].tnFvCtxName == '':
                        bd_cxts[0].tnFvCtxName = 'default'
                        self.commit(bd_cxts[0])
                return self.create_epg(str(network_ap.dn), str(bd_list[0].dn), network_o.name + '-vlan' +
                                       str(network_o.encapsulation))
            else:
                return self.create_epg(str(network_ap.dn), None, network_o.name + '-vlan' +
                                       str(network_o.encapsulation))

    def delete_network(self, network_o):
        class_query = ClassQuery('fvTenant')
        class_query.propFilter = 'eq(fvTenant.name, "' + network_o.group.name + '")'
        tenant_list = self.moDir.query(class_query)
        if len(tenant_list) > 0:
            tenant_mo = tenant_list[0]
            ap_list = filter(lambda x: type(x).__name__ == 'Ap' and x.name == tenant_mo.name + "-ap",
                             self.query_child_objects(str(tenant_mo.dn)))
            if len(ap_list) > 0:
                network_ap = ap_list[0]
                network_epgs = filter(lambda x: type(x).__name__ == 'AEPg' and x.name == network_o.name,
                                      self.query_child_objects(str(network_ap.dn)))
                if len(network_epgs) > 0:
                    network_epgs[0].delete()
                    self.commit(network_epgs[0])

    def create_group(self, group_name):
        tenant_mo = self.create_tenant(group_name)
        bd_mo = self.create_bd(group_name + '-BD', tenant_mo, None)
        bd_mo.arpFlood = 'yes'
        bd_mo.multiDstPktAct = 'bd-flood'
        bd_mo.unicastRoute = 'no'
        bd_mo.unkMacUcastAct = 'flood'
        bd_mo.unkMcastAct = 'flood'
        self.commit(bd_mo)

    def delete_group(self, group_o):
        class_query = ClassQuery('fvTenant')
        class_query.propFilter = 'eq(fvTenant.name, "' + group_o.name + '")'
        tenant_list = self.moDir.query(class_query)
        if len(tenant_list) > 0:
            tenant_list[0].delete()
            self.commit(tenant_list[0])

    def get_leafs(self):
        class_query = ClassQuery('fabricNode')
        class_query.propFilter = 'eq(fabricNode.role, "leaf")'
        leafs = self.moDir.query(class_query)
        result = []
        dns = []
        rns = []
        for leaf in leafs:
            dns.append(str(leaf.dn))
            rns.append(str(leaf.rn))
        # Need to be human sorted
        dns.sort(key=natural_keys)
        rns.sort(key=natural_keys)
        result.append(dns)
        result.append(rns)
        return result

    def get_ports(self, leaf_dn):
        leaf_ports = filter(lambda x: type(x).__name__ == 'PhysIf', self.query_child_objects(leaf_dn + '/sys'))
        result = []
        dns = []
        port_ids = []
        for port in leaf_ports:
            dns.append(str(port.dn))
            port_ids.append(port.id)
        # Need to be human sorted
        dns.sort(key=natural_keys)
        port_ids.sort(key=natural_keys)
        result.append(dns)
        result.append(port_ids)
        return result

    def get_switch_by_port(self, port_o):
        port_mo = self.moDir.lookupByDn(port_o.port_dn)
        switch_sys_mo = self.moDir.lookupByDn(port_mo.parentDn)
        switch_mo = self.moDir.lookupByDn(switch_sys_mo.parentDn)
        return switch_mo

    def get_vpcs(self):
        class_query = ClassQuery('fabricProtPathEpCont')
        vpc_containers = self.moDir.query(class_query)
        vpc_list = []
        for container in vpc_containers:
            for vdc in self.query_child_objects(str(container.dn)):
                vpc_list.append(vdc)
        return vpc_list

    def associate_epg_vpc(self,epg_dn, vpc_dn, vlan_number):
        rspath = RsPathAtt(epg_dn, vpc_dn, encap='vlan-' + str(vlan_number))
        self.commit(rspath)

    def associate_epg_physical_domain(self, epg_dn, physicaldom_dn='uni/phys-FEDEX_PhysicalDomain'):
        rsdom = RsDomAtt(epg_dn, physicaldom_dn)
        self.commit(rsdom)

    def get_vpc_assignments(self, epg_dn):
        return filter(lambda x: type(x).__name__ == 'RsPathAtt', self.query_child_objects(epg_dn))

    def delete_vpc_assignment(self, rspathattr_dn):
        fv_rspathattr_mo = self.moDir.lookupByDn(rspathattr_dn)
        if fv_rspathattr_mo is not None:
            fv_rspathattr_mo.delete()
            self.commit(fv_rspathattr_mo)

    def create_single_access(self, epg_dn, port_dn, vlan_number):
        fabric_path_dn = port_dn.replace('node', 'paths').replace('sys/phys','pathep')
        rspathatt_mo = RsPathAtt(epg_dn, fabric_path_dn, encap='vlan-' + str(vlan_number))
        self.commit(rspathatt_mo)

    def delete_single_access(self, epg_dn, port_dn):
        fabric_path_dn = port_dn.replace('node', 'paths').replace('sys/phys', 'pathep')
        rspathatt_list = filter(lambda x: type(x).__name__ == 'RsPathAtt' and str(x.tDn) == fabric_path_dn,
                                self.query_child_objects(epg_dn))
        if len(rspathatt_list) > 0:
            rspathatt_list[0].delete()
            self.commit(rspathatt_list[0])

    def add_vlan(self, vlan_number, vlan_pool_dn='uni/infra/vlanns-[FEDEX_VLANPOOL]-static'):
        encap_mo = EncapBlk(vlan_pool_dn, 'vlan-' + str(vlan_number),'vlan-' + str(vlan_number), allocMode='static')
        self.commit(encap_mo)
        pass

    def remove_vlan(self, vlan_number, vlan_pool_dn='uni/infra/vlanns-[FEDEX_VLANPOOL]-static'):
        vlan_pool_children = self.query_child_objects(vlan_pool_dn)
        for vlan in vlan_pool_children:
            if vlan.to == 'vlan-' + str(vlan_number):
                vlan.delete()
                self.commit(vlan)
                break

