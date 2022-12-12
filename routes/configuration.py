from flask import Blueprint, render_template, current_app

import logging

configuration = Blueprint('configuration', __name__, template_folder='templates')

@current_app.errorhandler(404)
def page_not_found(e):
    logging.error(e)
    return render_template("404.html"), 404

@current_app.errorhandler(500)
def internal_server_error(e):
    logging.error(e)
    return render_template("500.html"), 500

@current_app.after_request
def security_headers(response):
    #response.headers['Content-Security-Policy'] = "default-src 'self' style-src https://cdn.jsdelivr.net/npm/bootstrap@4.3.1/dist/css/bootstrap.min.css"
    # response.headers['Strict-Transport-Security'] = 'max-age=63072000; includeSubDomains; preload'
    # response.headers['X-Frame-Options'] = 'SAMEORIGIN'
    # response.headers['X-Content-Type-Options'] = 'nosniff'
    return response