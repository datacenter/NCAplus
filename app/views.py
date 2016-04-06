"""
*************************************************************************
 Copyright (c) 2016 Cisco Systems, Inc.  All rights reserved.
*************************************************************************
Main point of entry for the web application

"""

from app import app
from flask import render_template, g, session, request, redirect
import flask_sijax
import model
import sijax_handler
from routefunc import get_values
from apic_manager import apic

__author__ = 'Santiago Flores Kanter (sfloresk@cisco.com)'


@app.before_request
def before_request():
    if not model.network.table_exists():
        model.create_tables()

@app.errorhandler(404)
def page_not_found(e):
    return redirect('/')

@flask_sijax.route(app, '/')
def main():
    if not session.get('login_apic_url'):
        return redirect('/login')

    if g.sijax.is_sijax_request:
        g.sijax.register_object(sijax_handler.handler)
        sijax_handler.handler_app = app
        return g.sijax.process_request()

    return render_template('main.html')


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

