"""
Main point of entry for the web application

"""

import flask_sijax
from flask import render_template, g, session, request, redirect

import model
from apic_manager import cobra_apic_l2_tool
from app import app
from sijax_handlers.group_handler import group_handler
from sijax_handlers.network_handler import network_handler
from sijax_handlers.fabric_handler import fabric_handler
from sijax_handlers.vpc_handler import vpc_handler
from sijax_handlers.vpc_access_handler import vpc_access_handler
from sijax_handlers.single_access_handler import single_access_handler
from sijax_handlers.access_switch_handler import access_switch_handler
from sijax_handlers.netmon_handler import netmon_handler

__author__ = 'Santiago Flores Kanter (sfloresk@cisco.com)'


""" Prerequisites """
@app.before_request
def before_request():
    if not model.network.table_exists():
        model.create_tables()

""" Error management """
@app.errorhandler(404)
def page_not_found(e):
    return redirect('/')

""" Account Log in and Log out """
@flask_sijax.route(app, '/login')
def login():
    if not session.get('login_apic_url'):
        if request.method == 'POST':
            values = request.form
            try:
                if len(values['login_username']) == 0:
                    ex = Exception()
                    ex.message = 'Username is required'
                    raise ex
                elif len(values['login_password']) == 0:
                    ex = Exception()
                    ex.message = 'Password is required'
                    raise ex
                elif len(values['login_apic_url']) == 0:
                    ex = Exception()
                    ex.message = 'Apic URL is required'
                    raise ex
                elif not values['login_apic_url'].startswith('http'):
                    ex = Exception()
                    ex.message = 'Please specify protocol (http/https)'
                    raise ex
                else:
                    apic_object = cobra_apic_l2_tool.cobra_apic_l2_tool()
                    apic_object.login(values['login_apic_url'], values['login_username'], values['login_password'])
                    session['login_apic_url'] = values['login_apic_url']
                    session['username'] = values['login_username']
                    session['password'] = values['login_password']
                    return redirect('/')
            except Exception as e:
                return render_template('login.html',
                                       error=e.message.replace("'", "").replace('"', '').replace("\n", "")[0:200],
                                       login_apic_url=values['login_apic_url'],
                                       login_username=values['login_username'])
        return render_template('login.html')
    else:
        return redirect('/')


@flask_sijax.route(app, '/logout')
def logout():
    session['login_apic_url'] = None
    session['username'] = None
    session['password'] = None
    return redirect('/login')


@flask_sijax.route(app, '/')
def main():
    if not session.get('login_apic_url'):
        return redirect('/login')

    return render_template('index.html')

@flask_sijax.route(app, '/groups')
def groups():
    if not session.get('login_apic_url'):
        return redirect('/login')

    if g.sijax.is_sijax_request:
        g.sijax.register_object(group_handler())

        g.sijax.register_object(fabric_handler())

        return g.sijax.process_request()

    return render_template('groups.html')

@flask_sijax.route(app, '/networks')
def networks():
    if not session.get('login_apic_url'):
        return redirect('/login')

    if g.sijax.is_sijax_request:
        g.sijax.register_object(network_handler())

        g.sijax.register_object(group_handler())

        g.sijax.register_object(fabric_handler())

        return g.sijax.process_request()

    return render_template('network/networks.html')

@flask_sijax.route(app, '/vpcs')
def vpcs():
    if not session.get('login_apic_url'):
        return redirect('/login')

    if g.sijax.is_sijax_request:
        g.sijax.register_object(fabric_handler())

        g.sijax.register_object(vpc_handler())

        g.sijax.register_object(group_handler())

        return g.sijax.process_request()

    return render_template('vpcs.html')

@flask_sijax.route(app, '/vpc_access')
def vpc_access():
    if not session.get('login_apic_url'):
        return redirect('/login')

    if g.sijax.is_sijax_request:
        g.sijax.register_object(network_handler())

        g.sijax.register_object(fabric_handler())

        g.sijax.register_object(vpc_handler())

        g.sijax.register_object(group_handler())

        g.sijax.register_object(vpc_access_handler())

        return g.sijax.process_request()

    return render_template('vpc_access.html')

@flask_sijax.route(app, '/single_access')
def single_access():
    if not session.get('login_apic_url'):
        return redirect('/login')

    if g.sijax.is_sijax_request:
        g.sijax.register_object(network_handler())

        g.sijax.register_object(fabric_handler())

        g.sijax.register_object(vpc_handler())

        g.sijax.register_object(group_handler())

        g.sijax.register_object(single_access_handler())

        return g.sijax.process_request()

    return render_template('single_access.html')

@flask_sijax.route(app, '/access_switches')
def access_switches():
    if not session.get('login_apic_url'):
        return redirect('/login')

    if g.sijax.is_sijax_request:
        g.sijax.register_object(access_switch_handler())
        return g.sijax.process_request()

    return render_template('access_switches.html')


@flask_sijax.route(app, '/netmon')
def netmon():
    if not session.get('login_apic_url'):
        return redirect('/login')

    if g.sijax.is_sijax_request:
        g.sijax.register_object(netmon_handler())
        g.sijax.register_object(fabric_handler())
        return g.sijax.process_request()

    return render_template('netmon/netmon.html')


@flask_sijax.route(app, '/netmon/<tenant_name>/<ap_name>/<network_name>')
def network_dashboard(tenant_name, ap_name, network_name):
    if not session.get('login_apic_url'):
        return redirect('/login')

    if g.sijax.is_sijax_request:
        g.sijax.register_object(netmon_handler())
        g.sijax.register_object(fabric_handler())
        return g.sijax.process_request()

    return render_template('netmon/network_dashboard.html', tenant=tenant_name, ap=ap_name, network=network_name)


@flask_sijax.route(app, '/netmon/<tenant_name>/<ap_name>/<network_name>/<endpoint_mac>')
def endpoint_track(tenant_name, ap_name, network_name, endpoint_mac):
    if not session.get('login_apic_url'):
        return redirect('/login')

    if g.sijax.is_sijax_request:
        g.sijax.register_object(netmon_handler())
        g.sijax.register_object(fabric_handler())
        return g.sijax.process_request()

    return render_template('netmon/endpoint_track.html', tenant=tenant_name, network=network_name, ap=ap_name,
                           endpoint_mac=endpoint_mac)
