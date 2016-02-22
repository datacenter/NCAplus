from routefunc import base_section_files, ordered_menu_list, get_values
from apic_manager import apic
from app import app
from flask import render_template, g
import flask_sijax


@app.route('/')
@app.route('/index')
def index():
    section_info = base_section_files()
    return render_template('index.html', title='Index', data=ordered_menu_list(section_info))


@flask_sijax.route(app, '/integration/create_vlan')
def create_vlan():
    def vlan_form_handler(obj_response, formvalues):
        values = get_values(formvalues)
        apic_object = apic.Apic()

        if values['operation'] == 'test_submit':
            obj_response.alert("submited!")

    if g.sijax.is_sijax_request:
        g.sijax.register_callback('vlan_form_handler', vlan_form_handler)
        return g.sijax.process_request()

    section_info = base_section_files()
    return render_template('create-vlan.html', title='Create VLAN', data=ordered_menu_list(section_info))
