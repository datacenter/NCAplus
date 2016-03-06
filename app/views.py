"""
*************************************************************************
 Copyright (c) 2016 Cisco Systems, Inc.  All rights reserved.
*************************************************************************
Main point of entry for the web application

"""

from app import app
from flask import render_template, g
import flask_sijax
import model
import sijax_handler

__author__ = 'Santiago Flores Kanter (sfloresk@cisco.com)'


@flask_sijax.route(app, '/')
def main():
    if g.sijax.is_sijax_request:
        g.sijax.register_object(sijax_handler.handler)
        sijax_handler.handler_app = app
        return g.sijax.process_request()

    return render_template('main.html')


@app.before_request
def before_request():
    if not model.network.table_exists():
        model.create_tables()
