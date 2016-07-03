"""

L2 integration tool methods
"""

from cobra_apic_base import cobra_apic_base
from cobra.model.fv import Tenant, BD, Subnet, AEPg, Ap, RsProv, RsCons, RsDomAtt, RsPathAtt, RsCtx, RsPathAtt
from cobra.mit.request import ClassQuery
from cobra.modelimpl.fabric.protpol import ProtPol
from cobra.modelimpl.fvns.encapblk import EncapBlk
from cobra.modelimpl.infra.accportp import AccPortP
from cobra.modelimpl.infra.hports import HPortS
from cobra.modelimpl.infra.rsaccbasegrp import RsAccBaseGrp
from cobra.modelimpl.infra.rsaccportp import RsAccPortP
from cobra.modelimpl.infra.portblk import PortBlk
from cobra.modelimpl.infra.nodep import NodeP
from cobra.modelimpl.infra.leafs import LeafS
from cobra.modelimpl.infra.nodeblk import NodeBlk
from cobra.modelimpl.infra.accbndlgrp import AccBndlGrp
from cobra.modelimpl.infra.rsattentp import RsAttEntP
from cobra.modelimpl.infra.rshifpol import RsHIfPol
from cobra.modelimpl.infra.rsl2ifpol import RsL2IfPol
from cobra.modelimpl.infra.rslacppol import RsLacpPol
from cobra.modelimpl.infra.rslldpifpol import RsLldpIfPol
from cobra.modelimpl.infra.rsmcpifpol import RsMcpIfPol
from cobra.modelimpl.infra.rsmonifinfrapol import RsMonIfInfraPol
from cobra.modelimpl.infra.rsstormctrlifpol import RsStormctrlIfPol
from cobra.modelimpl.infra.rsstpifpol import RsStpIfPol
from cobra.modelimpl.infra.rscdpifpol import RsCdpIfPol
from cobra.modelimpl.fvns.vlaninstp import VlanInstP
from cobra.modelimpl.infra.rsvlanns import RsVlanNs
from cobra.modelimpl.phys.domp import DomP
from cobra.modelimpl.infra.attentityp import AttEntityP
from cobra.modelimpl.infra.rsdomp import RsDomP
from cobra.modelimpl.fabric.explicitgep import ExplicitGEp
from cobra.modelimpl.fabric.nodepep import NodePEp
from cobra.modelimpl.fabric.hifpol import HIfPol
from cobra.modelimpl.lacp.lagpol import LagPol
from cobra.modelimpl.cdp.ifpol import IfPol
from cobra.modelimpl.fv.ctx import Ctx
from cobra.modelimpl.infra.accportgrp import AccPortGrp
from cobra.mit.request import DnQuery
from cobra.modelimpl.fv.subnet import Subnet
from constant import *
import re

__author__ = 'Santiago Flores Kanter (sfloresk@cisco.com)'

""" Helpers """
def natural_keys(text):
    '''
    list.sort(key=natural_keys) sorts in human order
    '''
    return [atoi(c) for c in re.split('(\d+)', text)]


def atoi(text):
    return int(text) if text.isdigit() else text

""" All calls to APIC are done using the following class """


class cobra_apic_l2_tool(cobra_apic_base):
    def __init__(self):
        cobra_apic_base.__init__(self)

    def create_network(self, network_o):
        """
        Creates a network within the fabric.
        To create a network or VLAN, it is necessary to create an EPG and a bridge domain associated to a vrf or context
        :param network_o:
        :return:
        """
        # Retrieve the tenant or group from the network object
        tenant_mo = self.moDir.lookupByDn(network_o.group)
        # Query the children bellow the tenant
        tenant_children = self.query_child_objects(network_o.group)
        # Filters the children in memory looking for the ones that belongs to the Ap class and with an specific name.
        ap_list = filter(lambda x: type(x).__name__ == 'Ap' and x.name == AP_NAME,
                         tenant_children)
        # Check if Application profile exists, if not creates one.
        if len(ap_list) == 0:
            network_ap = self.create_ap(str(tenant_mo.dn), AP_NAME)
        else:
            network_ap = ap_list[0]

        # Creates bridge domain
        bd_mo = self.create_bd('vlan' + str(network_o.encapsulation), tenant_mo, None)

        if not network_o.is_l3:
            # Set BD parameters. This one are needed so that the bridge domain floods the VLAN packets across the fabric
            bd_mo.arpFlood = YES
            bd_mo.multiDstPktAct = BD_FLOOD
            bd_mo.unicastRoute = NO
            bd_mo.unkMacUcastAct = FLOOD
            bd_mo.unkMcastAct = FLOOD
        else:
            Subnet(bd_mo, network_o.l3_default_gateway)
        self.commit(bd_mo)

        # Filters the tenant children in memory looking for the ones that belongs to the Ctx
        # class and with an specific name.
        tenant_ctxs = filter(lambda x: type(x).__name__ == 'Ctx' and x.name == VRF_NAME,
                             self.query_child_objects(str(tenant_mo.dn)))

        # check if vrf exists, if not creates one
        if len(tenant_ctxs) == 0:
            bd_ctx = self.create_vrf(tenant_mo.dn, VRF_NAME)
        else:
            bd_ctx = tenant_ctxs[0]

        # Filters the bridge domain children in memory looking for the ones that belongs to the RsCtx class
        bd_cxts = filter(lambda x: type(x).__name__ == 'RsCtx',
                             self.query_child_objects(str(bd_mo.dn)))
        # Selects the first RsCtx object and assign the tnFvCtxName to the context/vrf name to create the relashionship
        if len(bd_cxts) > 0:
            bd_cxts[0].tnFvCtxName = bd_ctx.name
            self.commit(bd_cxts[0])

        # Creates and return an EPG
        return self.create_epg(str(network_ap.dn), str(bd_mo.dn), network_o.name + VLAN_SUFIX +
                               str(network_o.encapsulation))

    def delete_network(self, network_o):
        """
        Removes the network from the fabric.
        Removes EPG and bridge domain associated to the network
        :param network_o:
        :return:
        """
        tenant_mo = self.moDir.lookupByDn(network_o.group)

        # Filters the tenant children in memory looking for the ones that belongs to the Ap class with an specific name
        ap_list = filter(lambda x: type(x).__name__ == 'Ap' and x.name == AP_NAME,
                         self.query_child_objects(str(tenant_mo.dn)))
        if len(ap_list) > 0:
            network_ap = ap_list[0]
            # Filters the tenant children in memory looking for the ones that belongs to the AEPg
            # class with an specific name
            network_epgs = filter(lambda x: type(x).__name__ == 'AEPg' and x.name == network_o.name + VLAN_SUFIX +
                                  str(network_o.encapsulation),
                                  self.query_child_objects(str(network_ap.dn)))
            # Removes EPG
            if len(network_epgs) > 0:
                network_epgs[0].delete()
                self.commit(network_epgs[0])

        # Filters the tenant children in memory looking for the ones that belongs to the BD class and with an specific
        # name
        bd_list = filter(lambda x: type(x).__name__ == 'BD' and x.name == VLAN + str(network_o.encapsulation),
                         self.query_child_objects(str(tenant_mo.dn)))
        if len(bd_list) > 0:
            # Removes bridge domain
            bd_list[0].delete()
            self.commit(bd_list[0])


    def create_group(self, group_name):
        """
        Creates a group/tenant
        :param group_name:
        :return:
        """
        tenant_mo = self.create_tenant(group_name)

    def delete_group(self, group_o):
        """
        Removes a group/tenant from the fabric
        :param group_o:
        :return:
        """
        class_query = ClassQuery('fvTenant')
        class_query.propFilter = 'eq(fvTenant.name, "' + group_o.name + '")'
        tenant_list = self.moDir.query(class_query)
        if len(tenant_list) > 0:
            tenant_list[0].delete()
            self.commit(tenant_list[0])

    def get_leafs(self):
        """
        Returns the leafs that are registered in the APIC
        :return:
        """
        # Query leafs from the fabric
        class_query = ClassQuery('fabricNode')
        class_query.propFilter = 'eq(fabricNode.role, "leaf")'
        leafs = self.moDir.query(class_query)
        # creates two lists that will include the distinguished names and the relative names
        result = []
        dns = []
        rns = []
        for leaf in leafs:
            dns.append(str(leaf.dn))
            rns.append(str(leaf.rn))
        # The following lines human sort the lists (e.g. 1,2,3,11 and not 1,11,2,3)
        dns.sort(key=natural_keys)
        rns.sort(key=natural_keys)
        result.append(dns)
        result.append(rns)
        # The result is a list with two lists inside. One list has distinguished names and the other the relative names
        return result

    def get_ports(self, leaf_dn):
        """
        Return a list of ports within a leaf
        :param leaf_dn:
        :return:
        """
        # Filters the leaf/sys children in memory looking for the ones that belongs to the PhysIf class
        leaf_ports = filter(lambda x: type(x).__name__ == 'PhysIf', self.query_child_objects(leaf_dn + '/sys'))
        # creates two lists that will include the distinguished names and the port identifiers
        result = []
        dns = []
        port_ids = []
        for port in leaf_ports:
            dns.append(str(port.dn))
            port_ids.append(port.id)
        # The following lines human sort the lists (e.g. 1,2,3,11 and not 1,11,2,3)
        dns.sort(key=natural_keys)
        port_ids.sort(key=natural_keys)
        # The result is a list with two lists inside. One list has distinguished names and the other the port
        # identifiers
        result.append(dns)
        result.append(port_ids)
        return result

    def get_switch_by_port(self, port_dn):
        """
        returns the switch that the port belongs
        :param port_dn:
        :return:
        """
        port_mo = self.moDir.lookupByDn(port_dn)
        switch_sys_mo = self.moDir.lookupByDn(port_mo.parentDn)
        switch_mo = self.moDir.lookupByDn(switch_sys_mo.parentDn)
        return switch_mo

    def get_vpcs(self):
        """
        returns all virtual port channel within the fabric
        :return:
        """
        class_query = ClassQuery('fabricProtPathEpCont')
        vpc_containers = self.moDir.query(class_query)
        vpc_list = []
        for container in vpc_containers:
            for vdc in self.query_child_objects(str(container.dn)):
                vpc_list.append(vdc)
        return vpc_list

    def associate_epg_vpc(self, epg_dn, vpc_dn, vlan_number):
        """
        Creates an static binding between a virtual port channel and an end point group
        :param epg_dn:
        :param vpc_dn:
        :param vlan_number:
        :return:
        """
        rspath = RsPathAtt(epg_dn, vpc_dn, encap=VLAN_PREFIX + str(vlan_number))
        self.commit(rspath)

    def associate_epg_physical_domain(self, epg_dn, physical_domain_name):
        """
        Associate a physical domain to an end point group
        :param epg_dn:
        :param physical_domain_name:
        :return:
        """
        # Query the physical domain according to an specific name
        class_query = ClassQuery('physDomP')
        class_query.propFilter = 'eq(physDomP.name, "' + PD_PREFIX + physical_domain_name + '")'
        pd_list = self.moDir.query(class_query)
        # If the physical domain does not exists, create it with the vlan pool and the attachable entity profile
        if len(pd_list) == 0:
            vlan_pool_mo = self.create_vlan_pool(VLAN_POOL_PREFIX + physical_domain_name, 'static')
            DomP_mo = self.create_physical_domain(PD_PREFIX + physical_domain_name, str(vlan_pool_mo.dn))
            self.create_attachable_entity_profile(AEP_PREFIX + physical_domain_name, str(DomP_mo.dn))
        else:
            DomP_mo = pd_list[0]
        # Creates and commits the association
        rsdom = RsDomAtt(epg_dn, str(DomP_mo.dn))
        self.commit(rsdom)

    def get_vpc_assignments_by_epg(self, epg_dn):
        """
        Returns all virtual port channel that are assigned to an specific end point group
        :param epg_dn:
        :return:
        """
        # Filters the EPG children in memory looking for the ones that belongs to the RsPathAtt class and are
        # virtual port channels
        return filter(lambda x: type(x).__name__ == 'RsPathAtt' and 'topology/pod-1/protpaths' in str(x.tDn),
                      self.query_child_objects(epg_dn))

    def delete_vpc_assignment(self, rspathattr_dn):
        """
        Removes the assignment of a vpc within and end point group
        :param rspathattr_dn:
        :return:
        """
        fv_rspathattr_mo = self.moDir.lookupByDn(rspathattr_dn)
        if fv_rspathattr_mo is not None:
            fv_rspathattr_mo.delete()
            self.commit(fv_rspathattr_mo)

    def create_single_access(self, epg_dn, switch_dn, port_dn, vlan_number, aep_name,
                             if_policy_group_name, switch_p_name):
        """
        Creates the switch profile, policy group and the interface profile needed to assign a specific port
        to a end point group via static binding. Creates the relationship between the EPG and the port as wll
        :param epg_dn:
        :param switch_dn:
        :param port_dn:
        :param vlan_number:
        :param aep_name:
        :param if_policy_group_name:
        :param switch_p_name:
        :return:
        """
        # Creates interface policy group
        if_policy_group = self.create_if_policy_group(if_policy_group_name, aep_name)
        # Creates interface profile
        if_profile = self.create_interface_profile(port_dn,if_policy_group.dn)
        # Creates switch profile
        self.create_single_access_switch_profile(switch_dn, if_profile.dn, switch_p_name)
        # Creates static binding
        fabric_path_dn = port_dn.replace('node', 'paths').replace('sys/phys', 'pathep')
        rspathatt_mo = RsPathAtt(epg_dn, fabric_path_dn, encap=VLAN_PREFIX + str(vlan_number))
        self.commit(rspathatt_mo)

    def create_single_access_switch_profile(self, switch_dn, if_profile_dn, switch_p_name):
        """
        Creates a switch profile for a specific interface profile and switch
        :param switch_dn:
        :param if_profile_dn:
        :param switch_p_name:
        :return:
        """
        # Create switch profile
        switch_mo = self.moDir.lookupByDn(switch_dn)
        switch_p_mo = NodeP('uni/infra/', switch_p_name)
        self.commit(switch_p_mo)
        # Add switch selector
        switch_selector_mo = LeafS(str(switch_p_mo.dn), str(switch_mo.rn), 'range')
        self.commit(switch_selector_mo)
        node_block_mo = NodeBlk(switch_selector_mo.dn, str(switch_mo.rn) + NB_SUFIX, from_=switch_mo.id, to_=switch_mo.id)
        self.commit(node_block_mo)
        # Add interface profile
        rs_acc_port_p_mo = RsAccPortP(switch_p_mo.dn, if_profile_dn)
        self.commit(rs_acc_port_p_mo)

    def create_interface_profile(self, port_dn, if_group_profile_dn):
        """
        Creates the interface profile for an specific port and group profile
        :param port_dn:
        :param if_group_profile_dn:
        :return:
        """
        # Create interface profile
        port_mo = self.moDir.lookupByDn(port_dn)
        interface_p = AccPortP('uni/infra/', 'single_access_' + str(port_mo.id).split('/')[1])
        self.commit(interface_p)
        # Create interface selector
        if_sel_mo = HPortS(interface_p.dn, PORT_PREFIX + str(port_mo.id).split('/')[1], 'range')
        self.commit(if_sel_mo)
        # Assign interface selector to interface policy group
        rs_access_base_group_mo = RsAccBaseGrp(if_sel_mo.dn, tDn=str(if_group_profile_dn))
        self.commit(rs_access_base_group_mo)
        # Create port block
        port_blk_mo = PortBlk(if_sel_mo.dn, str(port_mo.id).replace('/', '-'),
                              fromCard=str(port_mo.id).split('/')[0].replace('eth', ''),
                              fromPort=str(port_mo.id).split('/')[1],
                              toCard=str(port_mo.id).split('/')[0].replace('eth', ''),
                              toPort=str(port_mo.id).split('/')[1])
        self.commit(port_blk_mo)
        return interface_p

    def create_if_policy_group(self, name, aep_name):
        """
        Creates an interface policy group and associates it to an attachable entity profile
        :param name: interface policy group name
        :param aep_name: attachable entity profile. If does not exist the system will create it
        :return:
        """
        # Creates policy group
        if_policy_group_mo = AccPortGrp('uni/infra/funcprof/', name)
        self.commit(if_policy_group_mo)
        # Query the AEP
        class_query = ClassQuery('infraAttEntityP')
        class_query.propFilter = 'eq(infraAttEntityP.name, "' + AEP_PREFIX + aep_name + '")'
        pd_list = self.moDir.query(class_query)
        if len(pd_list) == 0:
            # if attachable entity profile does not exists, creates a new one
            vlan_pool_mo = self.create_vlan_pool('vlan-pool-' + aep_name, 'static')
            DomP_mo = self.create_physical_domain('pd-' + aep_name, str(vlan_pool_mo.dn))
            AttEntityP_mo = self.create_attachable_entity_profile('aep-' + aep_name, str(DomP_mo.dn))
        else:
            AttEntityP_mo = pd_list[0]
        # Assign attached entity profile to the policy group
        self.commit(
            RsAttEntP(if_policy_group_mo.dn, tDn=str(AttEntityP_mo.dn))
        )
        # Assign interface policies. For non-defaults, check if is already created. If not, the system will create them
        IfPolmo = self.moDir.lookupByDn('uni/infra/cdpIfP-CDP-ON')
        if not IfPolmo:
            IfPolmo = IfPol('uni/infra','CDP-ON',adminSt='enabled')
            self.commit(IfPolmo)
        self.commit(
            RsCdpIfPol(if_policy_group_mo.dn, tnCdpIfPolName=IfPolmo.name)
        )
        HIfPolmo = self.moDir.lookupByDn('uni/infra/hintfpol-1GB')
        if not HIfPolmo:
            HIfPolmo = HIfPol('uni/infra', '1GB', speed='1G')
            self.commit(HIfPolmo)
        self.commit(
            RsHIfPol(if_policy_group_mo.dn, tnFabricHIfPolName=HIfPolmo.name)
        )
        self.commit(
            RsL2IfPol(if_policy_group_mo.dn, tnL2IfPolName='default')
        )
        self.commit(
            RsLldpIfPol(if_policy_group_mo.dn, tnLldpIfPolName='default')
        )
        self.commit(
            RsMcpIfPol(if_policy_group_mo.dn, tnMcpIfPolName='default')
        )
        self.commit(
            RsMonIfInfraPol(if_policy_group_mo.dn, tnMonInfraPolName='default')
        )
        self.commit(
            RsStormctrlIfPol(if_policy_group_mo.dn, tnStormctrlIfPolName='default')
        )
        self.commit(
            RsStpIfPol(if_policy_group_mo.dn, tnStpIfPolName='default')
        )
        return if_policy_group_mo

    def delete_single_access(self, epg_dn, port_dn, if_policy_group_name, switch_p_name):
        """
        Removes the static binding between a port and an end point group. If no other EPGs are using this port the
        system will remove the switch profiles, interface profiles and interface policy groups associated to the port
        :param epg_dn:
        :param port_dn:
        :param if_policy_group_name:
        :param switch_p_name:
        :return:
        """
        fabric_path_dn = port_dn.replace('node', 'paths').replace('sys/phys', 'pathep')
        # Filters the EPG children in memory looking for the ones that belongs to the RsPathAtt class
        # and with an specific tDn
        rspathatt_list = filter(lambda x: type(x).__name__ == 'RsPathAtt' and str(x.tDn) == fabric_path_dn,
                                self.query_child_objects(epg_dn))
        if len(rspathatt_list) > 0:
            # Removes the static binding
            rspathatt_list[0].delete()
            self.commit(rspathatt_list[0])

        # If there is not other assignment to this port, the switch profiles and policy groups are removed
        fabric_path_dn = port_dn.replace('node', 'paths').replace('sys/phys', 'pathep')
        class_query = ClassQuery('fvRsPathAtt')
        # Filters the all the fvRsPathAtt in memory looking for the ones that are using the port
        RsPathAtt_list = filter(lambda x: str(fabric_path_dn) in str(x.tDn),
                      self.moDir.query(class_query))
        if len(RsPathAtt_list) == 0:

            # Remove Policy group
            class_query = ClassQuery('infraAccPortGrp')
            class_query.propFilter = 'eq(infraAccPortGrp.name, "' + if_policy_group_name + '")'
            policy_groups = self.moDir.query(class_query)
            if len(policy_groups) > 0:
                policy_groups[0].delete()
                self.commit(policy_groups[0])

            # Remove Interface profile
            port_mo = self.moDir.lookupByDn(port_dn)
            class_query = ClassQuery('infraAccPortP')
            class_query.propFilter = 'eq(infraAccPortP.name, "single_access_' + str(port_mo.id).split('/')[1] + '")'
            interface_profiles = self.moDir.query(class_query)
            if len(interface_profiles) > 0:
                interface_profiles[0].delete()
                self.commit(interface_profiles[0])

            # RemoveSwitch profile
            class_query = ClassQuery('infraNodeP')
            class_query.propFilter = 'eq(infraNodeP.name, "' + switch_p_name + '")'
            switch_profiles = self.moDir.query(class_query)
            if len(switch_profiles) > 0:
                switch_profiles[0].delete()
                self.commit(switch_profiles[0])

    def add_vlan(self, vlan_number, vlan_pool_name):
        """
        Add a vlan to a vlan pool.
        :param vlan_number:
        :param vlan_pool_name: Vlan pool name. If it does not exist the system will create one.
        :return:
        """
        class_query = ClassQuery('fvnsVlanInstP')
        class_query.propFilter = 'eq(fvnsVlanInstP.name, "' + VLAN_POOL_PREFIX + vlan_pool_name + '")'
        vp_list = self.moDir.query(class_query)
        # If the vlan pool does not exists, create it with the physical domain and the attachable entity profile
        if len(vp_list) == 0:
            VlanInstP_mo = self.create_vlan_pool(VLAN_POOL_PREFIX + vlan_pool_name, 'static')
            DomP_mo = self.create_physical_domain(PD_PREFIX + vlan_pool_name, str(VlanInstP_mo.dn))
            self.create_attachable_entity_profile(AEP_PREFIX + vlan_pool_name, str(DomP_mo.dn))
        else:
            VlanInstP_mo = vp_list[0]
        encap_mo = EncapBlk(str(VlanInstP_mo.dn), VLAN_PREFIX + str(vlan_number),
                            VLAN_PREFIX + str(vlan_number), allocMode='static')
        self.commit(encap_mo)

    def remove_vlan(self, vlan_number, vlan_pool_name):
        """
        Removes a VLAN from a vlan pool
        :param vlan_number:
        :param vlan_pool_name:
        :return:
        """
        class_query = ClassQuery('fvnsVlanInstP')
        class_query.propFilter = 'eq(fvnsVlanInstP.name, "' + VLAN_POOL_PREFIX + vlan_pool_name + '")'
        vp_list = self.moDir.query(class_query)
        # Check if vlan pool exists
        if len(vp_list) == 0:
            vlan_pool_children = self.query_child_objects(str(vp_list[0].dn))
            for vlan in vlan_pool_children:
                if vlan.to == 'vlan-' + str(vlan_number):
                    vlan.delete()
                    self.commit(vlan)
                    break

    def create_vpc_interface_profile(self, port_dn, if_group_profile_dn, name):
        """
        Creates an interface profile to be used for a virtual port channel
        :param port_dn:
        :param if_group_profile_dn:
        :param name:
        :return:
        """
        # Create interface profile
        port_mo = self.moDir.lookupByDn(port_dn)
        interface_p = AccPortP('uni/infra/', name + VPC_PORT_PREFIX + str(port_mo.id).split('/')[1])
        self.commit(interface_p)
        # Create interface selector
        if_sel_mo = HPortS(interface_p.dn, PORT_PREFIX + str(port_mo.id).split('/')[1], 'range')
        self.commit(if_sel_mo)
        # Assign interface selector to interface policy group
        rs_access_base_group_mo = RsAccBaseGrp(if_sel_mo.dn, tDn=str(if_group_profile_dn))
        self.commit(rs_access_base_group_mo)
        # Create port block
        port_blk_mo = PortBlk(if_sel_mo.dn, str(port_mo.id).replace('/', '-'),
                              fromCard=str(port_mo.id).split('/')[0].replace('eth', ''),
                              fromPort=str(port_mo.id).split('/')[1],
                              toCard=str(port_mo.id).split('/')[0].replace('eth', ''),
                              toPort=str(port_mo.id).split('/')[1])
        self.commit(port_blk_mo)
        return interface_p

    def create_vpc_if_policy_group(self, name, aep_name):
        """
        Creates the virtual port channel interface policy groups
        :param name:
        :param aep_name: attachable entity profile name. If it does not exists the system will create a new one
        :return:
        """
        policy_group_mo = AccBndlGrp('uni/infra/funcprof/', name, lagT='node')
        self.commit(policy_group_mo)
        # if attachable entity profile does not exists, creates a new one
        class_query = ClassQuery('infraAttEntityP')
        class_query.propFilter = 'eq(infraAttEntityP.name, "' + AEP_PREFIX + aep_name + '")'
        pd_list = self.moDir.query(class_query)
        if len(pd_list) == 0:
            vlan_pool_mo = self.create_vlan_pool(VLAN_POOL_PREFIX + aep_name, 'static')
            DomP_mo = self.create_physical_domain(PD_PREFIX + aep_name, str(vlan_pool_mo.dn))
            AttEntityP_mo = self.create_attachable_entity_profile(AEP_PREFIX + aep_name, str(DomP_mo.dn))
        else:
            AttEntityP_mo = pd_list[0]
        # Assign attached entity profile
        self.commit(
            RsAttEntP(policy_group_mo.dn, tDn=str(AttEntityP_mo.dn))
        )
        # Assign interface policies. For non-defaults, check if is already created. If not, the system will create them
        IfPolmo = self.moDir.lookupByDn('uni/infra/cdpIfP-CDP-ON')
        if not IfPolmo:
            IfPolmo = IfPol('uni/infra','CDP-ON',adminSt='enabled')
            self.commit(IfPolmo)
        self.commit(
            RsCdpIfPol(policy_group_mo.dn, tnCdpIfPolName=IfPolmo.name)
        )
        HIfPolmo = self.moDir.lookupByDn('uni/infra/hintfpol-1GB')
        if not HIfPolmo:
            HIfPolmo = HIfPol('uni/infra', '1GB', speed='1G')
            self.commit(HIfPolmo)
        self.commit(
            RsHIfPol(policy_group_mo.dn, tnFabricHIfPolName=HIfPolmo.name)
        )
        self.commit(
            RsL2IfPol(policy_group_mo.dn, tnL2IfPolName='default')
        )
        LagPolmo = self.moDir.lookupByDn('uni/infra/lacplagp-LACP')
        if not LagPolmo:
            LagPolmo = LagPol('uni/infra', 'LACP', mode='active')
            self.commit(LagPolmo)
        self.commit(
            RsLacpPol(policy_group_mo.dn, tnLacpLagPolName=LagPolmo.name)
        )
        self.commit(
            RsLldpIfPol(policy_group_mo.dn, tnLldpIfPolName='default')
        )
        self.commit(
            RsMcpIfPol(policy_group_mo.dn, tnMcpIfPolName='default')
        )
        self.commit(
            RsMonIfInfraPol(policy_group_mo.dn, tnMonInfraPolName='default')
        )
        self.commit(
            RsStormctrlIfPol(policy_group_mo.dn, tnStormctrlIfPolName='default')
        )
        self.commit(
            RsStpIfPol(policy_group_mo.dn, tnStpIfPolName='default')
        )
        return policy_group_mo

    def create_vpc_switch_profile(self, switch_dn, if_profile_dn, switch_p_name):
        """
        Creates a virtual port channel switch profile
        :param switch_dn:
        :param if_profile_dn:
        :param switch_p_name:
        :return:
        """
        # Create switch profile
        switch_mo = self.moDir.lookupByDn(switch_dn)
        switch_p_mo = NodeP('uni/infra/', switch_p_name + VPC_MIDDLE_STR + str(switch_mo.rn))
        self.commit(switch_p_mo)

        # Add switch selector
        switch_selector_mo = LeafS(str(switch_p_mo.dn), str(switch_mo.rn), 'range')
        self.commit(switch_selector_mo)
        node_block_mo = NodeBlk(switch_selector_mo.dn, str(switch_mo.rn) + NB_SUFIX, from_=switch_mo.id, to_=switch_mo.id)
        self.commit(node_block_mo)

        # Add interface profile
        rs_acc_port_p_mo = RsAccPortP(switch_p_mo.dn, if_profile_dn)
        self.commit(rs_acc_port_p_mo)

    def get_vpc_assignments(self):
        """
        Returns a dictionary: keys are VPC names and values are the list of EPGs that are associated to the it
        """
        result = {}
        class_query = ClassQuery('fvRsPathAtt')
        # Filters the all the fvRsPathAtt in memory looking for the ones that are using a VPC
        RsPathAtt_list = filter(lambda x: 'topology/pod-1/protpaths' in str(x.tDn),
                      self.moDir.query(class_query))
        for RsPathAtt_mo in RsPathAtt_list:
            vpc_name = str(RsPathAtt_mo.tDn).split('[')[1][:-1]
            epg_mo = self.moDir.lookupByDn(RsPathAtt_mo.parentDn)
            if vpc_name not in result.keys():
                result[vpc_name] = []
            result[vpc_name].append(epg_mo.name)
        return result

    def get_vpc_ports(self, vpc_dn):
        """
        Returns all the ports that are part of an specific virtual port channel
        :param vpc_dn:
        :return:
        """
        result = []
        fabric_path_ep_mo = self.moDir.lookupByDn(vpc_dn)
        # Filters the all the pcAggrIf objects in memory looking for the one that has the vpc name
        pc_aggr_vpc_mo_list = filter(
            lambda x: x.name == fabric_path_ep_mo.name, self.moDir.query(ClassQuery('pcAggrIf'))
        )
        for pc_aggr_vpc_mo in pc_aggr_vpc_mo_list:
            # Filters all the children of the pc_aggr_vpc_mo in memory looking for the ones
            # that are from the RsMbrIfs class
            RsMbrIfs_mo_list = filter(
                lambda x: type(x).__name__ == 'RsMbrIfs', self.query_child_objects(str(pc_aggr_vpc_mo.dn))
            )
            for RsMbrIfs_mo in RsMbrIfs_mo_list:
                result.append(RsMbrIfs_mo)
        return result

    def get_switch_by_vpc_port(self, rsmbrifs_dn):
        """
        Return the switch that an specific virtual port channel port is part of
        :param rsmbrifs_dn:
        :return:
        """
        vpc_port_mo = self.moDir.lookupByDn(rsmbrifs_dn)
        switch_vpc_mo = self.moDir.lookupByDn(vpc_port_mo.parentDn)
        switch_sys_mo = self.moDir.lookupByDn(switch_vpc_mo.parentDn)
        switch_mo = self.moDir.lookupByDn(switch_sys_mo.parentDn)
        return switch_mo

    def delete_vpc(self, vpc_dn):
        """
        Removes the virtual port channel interface profiles, policy groups and switch profiles
        :param vpc_dn:
        :return:
        """
        vpc_mo = self.moDir.lookupByDn(vpc_dn)
        # Filters all infraAccBndlGrp objectsin memory looking for the ones that
        # has the vpc name and then select the first in the list
        AccBndlGrp_mo = filter(lambda x: x.name == vpc_mo.name, self.moDir.query(ClassQuery('infraAccBndlGrp')))[0]
        # Delete policy group
        AccBndlGrp_mo.delete()
        self.commit(AccBndlGrp_mo)
        # Filters all infraAccPortP objects in memory looking for the ones that
        # has the vpc name
        AccPortP_mo_list = filter(
            lambda x: vpc_mo.name + VPC in x.name, self.moDir.query(ClassQuery('infraAccPortP'))
        )
        for AccPortP_mo in AccPortP_mo_list:
            # Delete interface profiles
            AccPortP_mo.delete()
            self.commit(AccPortP_mo)

        # Filters all infraNodeP objects in memory looking for the ones that
        # has the vpc name
        NodeP_mo_list = filter(
            lambda x: vpc_mo.name in x.name + VPC, self.moDir.query(ClassQuery('infraNodeP'))
        )
        for NodeP_mo in NodeP_mo_list:
            # Delete switch profile
            NodeP_mo.delete()
            self.commit(NodeP_mo)

    def get_available_ports(self, switch_dn):
        """
        Search ports that are not VPC bundled
        :return:
        """
        # Get switch
        switch_mo = self.moDir.lookupByDn(switch_dn)
        # Get all switch ports
        switch_port_list = self.get_ports(switch_dn)
        # Get all VPCs
        vpc_list = self.get_vpcs()
        # Traverse the VPCs searching matches in VPCs' ports and switch's ports.
        for vpc_mo in vpc_list:
            vpc_port_list = self.get_vpc_ports(str(vpc_mo.dn))
            for vpc_port_mo in vpc_port_list:
                vpc_switch_mo = self.get_switch_by_vpc_port(str(vpc_port_mo.dn))
                if str(vpc_switch_mo.rn) == str(switch_mo.rn):
                    for i in range(0, len(switch_port_list[1]) - 1):
                        if switch_port_list[1][i] == vpc_port_mo.tSKey:
                            # removes the item from the two lists. See get_ports method
                            del switch_port_list[1][i]
                            del switch_port_list[0][i]
        return switch_port_list

    def create_vlan_pool(self, vlan_pool_name, allocation_mode):
        """
        Creates a vlan pool within the fabric
        :param vlan_pool_name:
        :param allocation_mode:
        :return:
        """
        VlanInstP_mo = VlanInstP('uni/infra/', vlan_pool_name, allocation_mode)
        self.commit(VlanInstP_mo)
        return VlanInstP_mo

    def create_physical_domain(self, physical_domain_name, vlan_pool_dn):
        """
        Creates a physical domain within the fabric
        :param physical_domain_name:
        :param vlan_pool_dn:
        :return:
        """
        DomP_mo = DomP('uni/', physical_domain_name)
        self.commit(DomP_mo)
        if vlan_pool_dn is not None:
            RsVlanNs_mo = RsVlanNs(DomP_mo.dn)
            RsVlanNs_mo.tDn = vlan_pool_dn
            self.commit(RsVlanNs_mo)
        return DomP_mo

    def create_attachable_entity_profile(self, name, physical_domain_dn):
        """
        Creates an attachable entity profile
        :param name:
        :param physical_domain_dn: if it is not None, will assign it to the AEP
        :return:
        """
        AttEntityP_mo = AttEntityP('uni/infra/', name)
        self.commit(AttEntityP_mo)
        if physical_domain_dn is not None:
            RsDomP_mo = RsDomP(AttEntityP_mo.dn, physical_domain_dn)
            self.commit(RsDomP_mo)
        return AttEntityP_mo

    def create_explicit_vpc_pgroup(self, pgroup_name, leaf_1_dn, leaf_2_dn):
        """
        Creates an explicit virtual port channel group. This is a prerequisite to create a port channel
        :param pgroup_name:
        :param leaf_1_dn:
        :param leaf_2_dn:
        :return:
        """
        fabric = self.moDir.lookupByDn('uni/fabric')
        fabricProtPol = ProtPol(fabric, pairT='explicit')
        fabricExplicitGEp = ExplicitGEp(fabricProtPol, name=pgroup_name, id=1)
        NodePEp(fabricExplicitGEp, id=self.moDir.lookupByDn(leaf_1_dn).id)
        NodePEp(fabricExplicitGEp, id=self.moDir.lookupByDn(leaf_2_dn).id)
        self.commit(fabricProtPol)
        # Filters all children of fabricExplicitGEp in memory looking for the ones that
        # are from the RsVpcInstPol class and select the first one
        RsVpcInstPol_mo = filter(
            lambda x: type(x).__name__ == 'RsVpcInstPol',
            self.query_child_objects(str(fabricExplicitGEp.dn))
        )[0]
        # Set variables to None and default that removes the relationship
        RsVpcInstPol_mo.stateQual = None
        RsVpcInstPol_mo.tnVpcInstPolName = 'default'
        self.commit(RsVpcInstPol_mo)
        return fabricProtPol

    def get_vpc_explicit_groups(self):
        """
        Returns explicit groups created in the fabric
        :return:
        """
        class_query = ClassQuery('fabricExplicitGEp')
        return self.moDir.query(class_query)

    def get_leaf_by_explicit_group(self, fabricExplicitGEp_dn):
        """
        Return the leaf switches that are part of an explicit group
        :param fabricExplicitGEp_dn:
        :return:
        """
        # Three lists are created: one for the result, one for the distinguished names and other one for the
        # relative names
        result = []
        dns = []
        rns = []
        leafs = self.get_leafs()
        # Filters all children of the explicit group in memory looking for the ones that
        # are from the NodePEp class
        NodePEp_list = filter(lambda x: type(x).__name__ == 'NodePEp', self.query_child_objects(fabricExplicitGEp_dn))
        for NodePEp_mo in NodePEp_list:
            for i in range(0, len(leafs[0])):
                if leafs[1][i].split('-')[1] == NodePEp_mo.id:
                    dns.append(leafs[0][i])
                    rns.append(leafs[1][i])
        result.append(dns)
        result.append(rns)
        return result

    def remove_vpc_group(self, fabricExplicitGEp_dn):
        """
        Removes a explicit protection group
        :param fabricExplicitGEp_dn:
        :return:
        """
        fabricExplicitGEp_mo = self.moDir.lookupByDn(fabricExplicitGEp_dn)
        fabricExplicitGEp_mo.delete()
        self.commit(fabricExplicitGEp_mo)

    def create_vrf(self, parent_dn, vrf_name):
        """
        Creates a virtual routing forwarding context
        :param parent_dn:
        :param vrf_name:
        :return:
        """
        Ctx_mo = Ctx(parent_dn, vrf_name)
        self.commit(Ctx_mo)
        return Ctx_mo

    def get_fabric_switches(self):
        """
        Returns all switches within the fabric
        :return:
        """
        # Leafs
        class_query = ClassQuery('fabricNode')
        class_query.propFilter = 'eq(fabricNode.role, "leaf")'
        leafs = self.moDir.query(class_query)
        # Two lists are created, one for the distinguished names and other for the relative names
        dns = []
        rns = []
        for leaf in leafs:
            dns.append(str(leaf.dn))
            rns.append(str(leaf.rn))
        # Spines
        class_query = ClassQuery('fabricNode')
        class_query.propFilter = 'eq(fabricNode.role, "spine")'
        spines = self.moDir.query(class_query)
        for spine in spines:
            dns.append(str(spine.dn))
            rns.append(str(spine.rn))
        # Need to be human sorted (e.g 1,2,3,11 and not 1,11,2,3)
        dns.sort(key=natural_keys)
        rns.sort(key=natural_keys)
        return dns, rns

    def get_health_dashboard(self):
        """
        Returns the switches health information
        :return: A dictionary that contains dictionaries. Each key is a switch
        """
        result = {}
        fabric_switches_dns, fabric_switches_rns = self.get_fabric_switches()
        for fabric_switch in fabric_switches_rns:
            result[fabric_switch] = {}
            # Switch health
            Health_Inst_mo = self.moDir.lookupByDn('topology/pod-1/' + fabric_switch + '/sys/health')
            result[fabric_switch]['Health'] = Health_Inst_mo.cur

            # Switch Policy CAM table
            cam_usage_mo = self.moDir.lookupByDn('topology/pod-1/' + str(fabric_switch) +
                                                  '/sys/eqptcapacity/CDeqptcapacityPolUsage5min')
            result[fabric_switch]['Policy CAM table'] = cam_usage_mo.polUsageCum + ' of ' + cam_usage_mo.polUsageCapCum

            # Switch MAC table
            multicast_usage_mo = self.moDir.lookupByDn('topology/pod-1/' + str(fabric_switch) +
                                                  '/sys/eqptcapacity/CDeqptcapacityMcastUsage5min')
            result[fabric_switch]['Multicast'] = multicast_usage_mo.localEpCum + ' of ' + multicast_usage_mo.localEpCapCum

            # VLAN
            vlan_usage_mo = self.moDir.lookupByDn('topology/pod-1/' + str(fabric_switch) +
                                                  '/sys/eqptcapacity/CDeqptcapacityVlanUsage5min')
            result[fabric_switch]['VLAN'] = vlan_usage_mo.totalCum + ' of ' + vlan_usage_mo.totalCapCum
        return result

    def get_system_health(self):
        """
        Returns the system health
        :return:
        """
        HealthTotal_mo = self.moDir.lookupByDn('topology/health')
        return HealthTotal_mo.cur

    def get_endpoints(self, epg_dn):
        """
        Returns an end point list
        :return:
        """
        result = []
        for item in filter(lambda x: type(x).__name__ == 'CEp', self.query_child_objects(epg_dn)):
            # Creates a dynamic object type.
            endpoint = type('endpoint', (object,), {})

            # Filter the endpoint in memory looking for the object that contains the interface where the endpoint is
            # attached
            endpoint_connection_mo = filter(lambda x: type(x).__name__ == 'RsCEpToPathEp',
                                            self.query_child_objects(item.dn))[0]

            # Format the string to be human readable
            endpoint_connection_interface = str(endpoint_connection_mo.tDn).replace('topology/pod-1/paths','node').\
                replace('pathep-[', '').replace(']','')

            # Add attributes to the object
            endpoint.ip = item.ip
            endpoint.mac = item.mac
            endpoint.name = item.name
            endpoint.interface = endpoint_connection_interface

            # Append it to the list
            result.append(endpoint)
        return result

    def get_epg_health_score(self, epg_dn):
        return self.moDir.lookupByDn(epg_dn + '/health').cur

    def get_epg(self, tenant_name, ap_name, epg_name):
        """
        Retrieves the epg
        :param tenant_name:
        :param ap_name:
        :param epg_name:
        :return:
        """
        ap_list = filter(lambda x: type(x).__name__ == 'Ap' and x.name == ap_name,
                          self.query_child_objects('uni/tn-%s' % tenant_name))
        if len(ap_list) > 0:
            epg_list = filter(lambda x: type(x).__name__ == 'AEPg' and x.name == epg_name,
                              self.query_child_objects(str(ap_list[0].dn)))
            if len(epg_list) > 0:
                return epg_list[0]

    def get_faults_history(self, epg_dn):
        """
        Retrieves a historic list of all faults associated to an EPG
        :param epg_dn:
        :return:
        """
        class_query = ClassQuery('faultRecord')
        class_query.propFilter = 'eq(faultRecord.affected, "' + epg_dn + '")'
        return self.moDir.query(class_query)

    def get_stats(self, epg_dn):
        """
        Get all traffic statistics of an EPG
        :param epg_dn:
        :return:
        """
        # Apic saves up to 95 different objects with statistic information
        traffic_list = []
        for i in range(10, -1, -1):
            traffic = self.moDir.lookupByDn(epg_dn + '/HDl2IngrBytesAg15min-%s' % str(i))
            if traffic is not None:
                traffic_list.append(traffic)
        return traffic_list

    def get_faults(self, epg_dn):
        class_query = DnQuery(epg_dn)
        class_query.subtree = 'full'
        class_query.subtreeInclude = 'faults'
        epg_list = self.moDir.query(class_query)
        fault_list = self.get_faults_from_tree(epg_list[0], [])
        return fault_list

    def get_faults_from_tree(self, mo, faults):
        if type(mo).__name__ == 'Inst':
            faults.append(mo)
        for child in mo.children:
                self.get_faults_from_tree(child, faults)
        return faults

    def get_nca_ap(self, tenant_dn):
        aps = self.get_ap_by_tenant(tenant_dn)
        for ap in aps:
            if ap.name == AP_NAME:
                return ap

    def assign_any_to_any_contract(self, network_o):
        contract_mo = self.create_contract(network_o.group, ANY_TO_ANY_CONTRACT_NAME)
        filter_mo = self.create_filter(network_o.group,ANY_TO_ANY_FILTER_NAME)
        self.create_entry(filter_mo.dn, ANY_TO_ANY_ENTRY_NAME, 'ip')
        self.create_subject(filter_mo.dn, contract_mo.dn, ANY_TO_ANY_SUBJ_NAME)
        self.assign_contract(network_o.epg_dn, contract_mo.dn, contract_mo.dn)

