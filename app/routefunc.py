

def base_section_files():
    """
    Each member of the list is a section. Inside is a dictionary that contains the information for the chapters.
    These three separate sections are split in the template to separate columns to fit the many sections on tje
    menu as needed.
    """

    data = {
        "integration":
            {
                "head": {"line":"head", "pos": 0, "weburl": "head",
                         "file": None, "title": "Integration"},
                "createnetwork": {"line":"data", "pos": 1, "weburl": "create_network",
                               "file": "create-network.html", "title": "Create Network"},
                "createaccess": {"line":"data", "pos": 1, "weburl": "create_access",
                               "file": "create-access.html", "title": "Create access vlan"},
            },
    }
    return data


def ordered_menu_list(data):
    """
    The purpose of this function is to take the menu dictionary and return a dictionary that is indexed by the
    section and then that section would contain a list based on the sorted value of the POS column. If not the
    MENU would end up with a different order as dictionaries in Python don't have order. This function is called
    when the menu data is passed to the template that then processes it. Since we can't have the lambda function
    inside of the template, we have to pass it ordered to the template.
    """
    mylist={}
    for topkey, menudict in data.iteritems():
        mylist[topkey]=[]

    for topkey, menudict in data.iteritems():
        for key, value in sorted(menudict.iteritems(), key=lambda (k, v): (v["pos"], k)):
            mylist[topkey].append(value)

    return mylist


def xml_files():
    data = {
        "inbinfra": {
            1: "intVlanPool.xml",
            2: "l3VlanPool.xml",
            3: "intPhyDom.xml",
        }
    }
    return data


def readxmlfile(section, ident):
    import re
    files = xml_files()
    filename = files[section][ident]
    filename = "app/xml/" + filename

    with open(filename, "r") as xmlfile:
        xmlstring = xmlfile.read()

    xmlstring = re.sub(r'<', "&lt;", xmlstring)
    xmlstring = "<pre><code>" + xmlstring + "</code></pre>"
    return xmlstring


def growljs(growltext):
    return '$.bootstrapGrowl("' + growltext + '",{type:"info",delay:"2000",offset: {from: "top", amount: 45}});'


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
"""
Code Snipet saves:

Button for sijax request
<button class='btn btn-info' onclick="Sijax.request('insTenant', ['{{ data.PN }}' , '{{ data.password }}'] );">Execute</button><div id="result1"></div>


"""