"""
*************************************************************************
 Copyright (c) 2016 Cisco Systems, Inc.  All rights reserved.
*************************************************************************
Helper for views.py

"""

__author__ = 'Santiago Flores Kanter (sfloresk@cisco.com)'

def get_values(form):
    """
    :param form: html form to be mapped
    :return dictionary with field as keys and field values as the dictionary value
    """
    result = {}
    for field, fieldvalue in form.items():
        result[field] = fieldvalue
    return result


def get_tenant_options(apic_object):
    option_list = '<option value="">Select</option>'
    for tenant in apic_object.get_all_tenants():
        option_list += '<option value="' + str(tenant.dn) + '">' + tenant.name + '</option>'
    return option_list


def get_bd_options(apic_object, tenant_dn):
    option_list = '<option value="">Select</option>'
    for bd in apic_object.get_bds_by_tenant(tenant_dn):
        option_list += '<option value="' + str(bd.dn) + '">' + bd.name + '</option>'
    return option_list


def get_filter_options(apic_object, tenant_dn):
    option_list = '<option value="">Select</option>'
    for filter_mo in apic_object.get_filters_by_tenant(tenant_dn):
        option_list += '<option value="' + str(filter_mo.dn) + '">' + filter_mo.name + '</option>'
    return option_list


def get_contract_options(apic_object, tenant_dn):
    option_list = '<option value="">Select</option>'
    for contract in apic_object.get_contracts_by_tenant(tenant_dn):
        option_list += '<option value="' + str(contract.dn) + '">' + contract.name + '</option>'
    return option_list

def get_ap_options(apic_object, tenant_dn):
    option_list = '<option value="">Select</option>'
    for ap in apic_object.get_ap_by_tenant(tenant_dn):
        option_list += '<option value="' + str(ap.dn) + '">' + ap.name + '</option>'
    return option_list

def get_epg_options(apic_object, ap_dn):
    option_list = '<option value="">Select</option>'
    for epg in apic_object.get_epg_by_ap(ap_dn):
        option_list += '<option value="' + str(epg.dn) + '">' + epg.name + '</option>'
    return option_list

def get_subject_options(apic_object, contract_dn):
    option_list = '<option value="">Select</option>'
    for contract in apic_object.get_subjects_by_contract(contract_dn):
        option_list += '<option value="' + str(contract.dn) + '">' + contract.name + '</option>'
    return option_list
