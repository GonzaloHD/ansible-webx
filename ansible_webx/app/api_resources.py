# Optional RestAPI end points

import datetime
import json
from flask import Blueprint, g, jsonify, request
from ansible_webx.app.ansible_run_command import run_ansible
from ansible_webx.prepare_data.get_data import find_servers, find_tags, find_values_extra_vars_sites, find_keys_extra_vars_sites

api_app = Blueprint('api', __name__)


@api_app.route('/servers', methods=['GET'])
def get_tags():
    response = {'servers': find_servers()}
    return jsonify(response)


@api_app.route('/tags', methods=['GET'])
def get_servers():
    response = {'tags': find_tags()}
    return jsonify(response)


@api_app.route('/extra_vars_sites_keys', methods=['GET'])
def get_keys_extra_vars_sites():
    response = {'extra_vars_sites_keys': find_keys_extra_vars_sites()}
    return jsonify(response)


@api_app.route('/extra_vars_sites_values', methods=['GET'])
def get_values_extra_vars_sites(tags=None, server=None):
    tags = request.args.getlist('tags')
    server = request.args.get('server')
    response = {
        'extra_vars_sites_values': find_values_extra_vars_sites(tags, server)
    }
    return jsonify(response)


@api_app.route('/running_ansible', methods=['POST'])
def running_ansible():
    # Get JSON data from the request
    request_data = request.get_json()

    # Extract required parameters from JSON data
    data = {
        'playbook_directory': request_data.get('playbook_directory'),
        'playbook': request_data.get('playbook'),
        'limit': request_data.get('limit'),
        'tags': request_data.get('tags'),
        'extra_vars': request_data.get('extra_vars')
    }

    # Call the run_ansible function with the extracted parameters
    response = run_ansible(**data)

    # Return the response as JSON
    return jsonify(response), 200


@api_app.route('/set_cookie', methods=['POST'])
def set_cookie():
    # Get JSON data from the request body
    data = request.json

    # Check if JSON data is provided
    if not data:
        return jsonify({'error': 'No JSON data provided'}), 400

    response = jsonify(data)

    # Set cookie to expire
    expiration_date = datetime.datetime.now() + datetime.timedelta(days=365)
    response.set_cookie('data_form',
                        json.dumps(data),
                        expires=expiration_date,
                        samesite='None',
                        secure=True)
    return response


@api_app.route('/get_cookie', methods=['GET'])
def get_cookie():
    # Retrieve cookie data
    cookie_data = request.cookies.get('data_form')
    return jsonify(cookie_data)
