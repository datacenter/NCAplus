from routefunc import base_section_files, ordered_menu_list, get_values
from apic_manager import apic
from app import app
from flask import render_template, g
import flask_sijax
import model
import traceback
import sys

@app.route('/')
@app.route('/index')
def index():
    section_info = base_section_files()
    return render_template('index.html', title='Index', data=ordered_menu_list(section_info))


@flask_sijax.route(app, '/integration/create_access')
def create_access_vlan():
    
    def access_vlan_form_handler(obj_response, formvalues):
        values = get_values(formvalues)
        apic_object = apic.Apic()
        apic_object.login(app.apic_url, app.apic_user, app.apic_password)
        g.db = model.database
        g.db.connect()

        if values['operation'] == 'create_access_vlan':
            pass
        
    if g.sijax.is_sijax_request:
        g.sijax.register_callback('access_vlan_form_handler', access_vlan_form_handler)
        return g.sijax.process_request()

    section_info = base_section_files()
    return render_template('create-access.html', title='Create access VLAN', data=ordered_menu_list(section_info))



@flask_sijax.route(app, '/integration/create_network')
def create_network():
    def network_form_handler(obj_response, formvalues):
        values = get_values(formvalues)
        apic_object = apic.Apic()
        apic_object.login(app.apic_url, app.apic_user, app.apic_password)
        g.db = model.database
        g.db.connect()

        if values['operation'] == 'get_groups':
            try:
                groups = model.group.select()
                option_list = '<option value="">Select</option>'
                for group in groups:
                    option_list += '<option value="' + str(group.id) + '">' + group.name + '</option>'
                obj_response.html("#sel_create_network_group", option_list)
                obj_response.html("#create_network_response", '')
            except Exception as e:
                print traceback.print_exc()
                obj_response.html("#create_network_response", '<label class="label label-danger" > '
                                                              '<i class="fa fa-times-circle"></i> '
                                                              'Can not create network: ' + e.message + '</label>')
            finally:
                g.db.close()

        elif values['operation'] == 'create_group':
            try:
                group = model.group.create(name=values['create_group_name'])
                apic_object.create_tenant(group.name)
                obj_response.html("#create_group_response", '<label class="label label-success" > '
                                                            '<i class="fa fa-check-circle"></i> Created </label>')

                groups = model.group.select()
                option_list = '<option value="">Select</option>'
                for group in groups:
                    option_list += '<option value="' + str(group.id) + '">' + group.name + '</option>'
                obj_response.html("#sel_create_network_group", option_list)
            except Exception as e:
                print traceback.print_exc()
                obj_response.html("#create_network_response", '<label class="label label-danger" > '
                                                              '<i class="fa fa-times-circle">'
                                                              '</i> Can not create network: ' + e.message + '</label>')
            finally:
                g.db.close()

        elif values['operation'] == 'create_network':
            try:
                network_object = model.network.create(name=values['create_network_name'],
                                                      encapsulation=int(values['create_network_encapsulation']),
                                                      group=int(values['sel_create_network_group']))
                apic_object.create_network(network_object)
                obj_response.html("#create_network_response", '<label class="label label-success" > '
                                                              '<i class="fa fa-check-circle"></i> Created </label>')
            except Exception as e:
                print traceback.print_exc()
                obj_response.html("#create_network_response", '<label class="label label-danger" > '
                                                              '<i class="fa fa-times-circle"></i> '
                                                              'Can not create network: ' + e.message + '</label>')
            finally:
                g.db.close()

    if g.sijax.is_sijax_request:
        g.sijax.register_callback('network_form_handler', network_form_handler)
        return g.sijax.process_request()

    section_info = base_section_files()
    return render_template('create-network.html', title='Create network', data=ordered_menu_list(section_info))

@app.before_request
def before_request():
    if not model.group.table_exists():
        model.create_tables()
