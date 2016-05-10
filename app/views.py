"""
*************************************************************************
 Copyright (c) 2016 Cisco Systems, Inc.  All rights reserved.
*************************************************************************
Main point of entry for the web application

"""

import flask_sijax
from flask import render_template, g, session, request, redirect

import model
from apic_manager import apic
from app import app
from sijax_handlers.group_handler import group_handler
from sijax_handlers.network_handler import network_handler
from sijax_handlers.fabric_handler import fabric_handler
from sijax_handlers.vpc_handler import vpc_handler
from sijax_handlers.vpc_access_handler import vpc_access_handler
from sijax_handlers.single_access_handler import single_access_handler
from sijax_handlers.access_switch_handler import access_switch_handler
from routefunc import get_values

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
            values = get_values(request.form)
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
                else:
                    apic_object = apic.Apic()
                    apic_object.login(values['login_apic_url'],values['login_username'],values['login_password'])
                    session['login_apic_url'] = values['login_apic_url']
                    session['username'] = values['login_username']
                    session['password'] = values['login_password']
                    return redirect('/')
            except Exception as e:
                return render_template('login.html',
                                       error=str(e).replace("'", "").replace('"', '').replace("\n", "")[0:100],
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
        g.sijax.register_object(group_handler)
        group_handler.handler_app = app
        return g.sijax.process_request()

    return render_template('groups.html')

@flask_sijax.route(app, '/networks')
def networks():
    if not session.get('login_apic_url'):
        return redirect('/login')

    if g.sijax.is_sijax_request:
        g.sijax.register_object(network_handler)
        network_handler.handler_app = app
        g.sijax.register_object(group_handler)
        group_handler.handler_app = app
        return g.sijax.process_request()

    return render_template('networks.html')

@flask_sijax.route(app, '/vpcs')
def vpcs():
    if not session.get('login_apic_url'):
        return redirect('/login')

    if g.sijax.is_sijax_request:
        g.sijax.register_object(fabric_handler)
        fabric_handler.handler_app = app
        g.sijax.register_object(vpc_handler)
        vpc_handler.handler_app = app
        g.sijax.register_object(group_handler)
        group_handler.handler_app = app

        return g.sijax.process_request()

    return render_template('vpcs.html')

@flask_sijax.route(app, '/vpc_access')
def vpc_access():
    if not session.get('login_apic_url'):
        return redirect('/login')

    if g.sijax.is_sijax_request:
        g.sijax.register_object(network_handler)
        network_handler.handler_app = app
        g.sijax.register_object(fabric_handler)
        fabric_handler.handler_app = app
        g.sijax.register_object(vpc_handler)
        vpc_handler.handler_app = app
        g.sijax.register_object(group_handler)
        group_handler.handler_app = app
        g.sijax.register_object(vpc_access_handler)
        vpc_access_handler.handler_app = app
        return g.sijax.process_request()

    return render_template('vpc_access.html')

@flask_sijax.route(app, '/single_access')
def single_access():
    if not session.get('login_apic_url'):
        return redirect('/login')

    if g.sijax.is_sijax_request:
        g.sijax.register_object(network_handler)
        network_handler.handler_app = app
        g.sijax.register_object(fabric_handler)
        fabric_handler.handler_app = app
        g.sijax.register_object(vpc_handler)
        vpc_handler.handler_app = app
        g.sijax.register_object(group_handler)
        group_handler.handler_app = app
        g.sijax.register_object(single_access_handler)
        single_access_handler.handler_app = app
        return g.sijax.process_request()

    return render_template('single_access.html')

@flask_sijax.route(app, '/access_switches')
def access_switches():
    if not session.get('login_apic_url'):
        return redirect('/login')

    if g.sijax.is_sijax_request:
        g.sijax.register_object(access_switch_handler)
        access_switch_handler.handler_app = app
        return g.sijax.process_request()

    return render_template('access_switches.html')

@flask_sijax.route(app, '/monitor')
def monitor():
    if not session.get('login_apic_url'):
        return redirect('/login')

    if g.sijax.is_sijax_request:
        g.sijax.register_object(fabric_handler)
        fabric_handler.handler_app = app
        return g.sijax.process_request()

    return render_template('monitor.html')