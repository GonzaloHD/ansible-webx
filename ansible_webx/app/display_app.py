import datetime
import json
import traceback
from ansible_webx import config
from flask import Blueprint, g, jsonify, render_template, request, redirect, session, url_for

from ansible_webx.app.ansible_run_command import run_ansible
from ansible_webx.app.data_utils import get_input_command, get_last_form
from ansible_webx.prepare_data.get_data import find_servers, find_tags, find_keys_extra_vars_sites, find_values_extra_vars_sites

client_app = Blueprint('client', __name__)
last_inputs_empty = dict()
empty_form = {
    'limit': '',
    'tags': [''],
    'extra_vars': None,
    'extra_vars_sites': {
        '': '',
    },
    'executed': False
}

last_inputs_empty.update({0: empty_form})


# Function to load cookie before each request
@client_app.before_request
def load_cookies():
    global last_inputs_empty
    cookie_data = request.cookies.get('data_form')
    if cookie_data:
        g.last_inputs = json.loads(cookie_data)
        # Get the last key
        last_key = max(g.last_inputs.keys())
        # Access the last entry using the last key
        g.last_form = g.last_inputs[last_key]

    else:
        g.last_inputs = last_inputs_empty


# Function to save cookies after each request
@client_app.after_request
def save_cookies(response):
    # Save only the last 5 elements
    max_commands_to_show = -int(config['flask'].get('max_commands_to_show', 5))
    keys_to_keep = list(g.last_inputs.keys())[max_commands_to_show:]
    g.last_inputs = {k: g.last_inputs[k] for k in keys_to_keep}
    data = json.dumps(g.last_inputs)
    # Set cookie to expire
    expiration_date = datetime.datetime.now() + datetime.timedelta(days=365)
    # Set SameSite=None and Secure flag
    response.set_cookie('data_form',
                        data,
                        expires=expiration_date,
                        samesite='None',
                        secure=True)
    return response


@client_app.route('/execute_ansible', methods=['POST'])
def execute_ansible():
    sid = session.get('sid', None)
    # Retrieve form inputs from the post request: server, tags, extra_vars for single_site or selected_sites and other extra_vars if any
    server = request.form.get('limit') if request.form.get('limit') else None
    tags_list = request.form.getlist('tags') if request.form.getlist(
        'tags') else None
    extra_vars_list_form = request.form.getlist(
        'extra_vars') if request.form.getlist('extra_vars') else None
    extra_vars_sites_key_form = request.form.get(
        'extra_vars_sites_key') if request.form.get(
            'extra_vars_sites_key') else None
    extra_vars_sites_value_form = request.form.getlist(
        'extra_vars_sites_value') if request.form.getlist(
            'extra_vars_sites_value') else None

    id_input = int(list(g.last_inputs.keys())[-1]) + 1

    # Prepare last form dictionary with the inputs to display back the form as it was submitted:
    g.last_form = get_last_form(server, tags_list, extra_vars_list_form,
                                extra_vars_sites_key_form,
                                extra_vars_sites_value_form)
    # Check if last_input was not executed, if so pop it out as no need of it any more.
    last_key_inputs = list(g.last_inputs)[-1]
    removed = g.last_inputs.pop(
        last_key_inputs
    ) if g.last_inputs[last_key_inputs]['executed'] == False else None
    g.last_inputs.update({id_input: g.last_form})

    # Prepare input command from the inputs to run ansible, it captures any error or warning returned
    input_data, warning_message, error_message = get_input_command(
        **g.last_form)

    session['warning_message'] = warning_message
    if error_message:
        session['error_message'] = error_message
        return redirect(url_for('client.display_app'))

    else:
        print("INPUT DATA: \n", input_data)
        # Launch prepared data to the run_ansible function
        try:
            # Call the run_ansible function with the extracted parameters. It returns warnings, errors from the output.
            play_recap, warning_output, error_output, command_error = run_ansible(
                **input_data, sid=sid)

            # Reder json and save the ouput to display. If command_error then there was an exception so the output is the exception itself.
            if command_error:
                session['error_message'] = command_error
            else:
                session['play_recap'] = play_recap
                session['error_output'] = error_output
                session['warning_output'] = warning_output
                g.last_form['executed'] = True

            return redirect(url_for('client.display_app'))
        except Exception as e:
            session['error_message'] = f'Unexpected error: {e}'
            return redirect(url_for('client.display_app'))


# Output section to stream data output. Remain fix.
@client_app.route('/constant_section')
def constant_section():
    return render_template('constant.html')


# Input part of the document, will be loaded after each submission or data retrieval
@client_app.route('/dynamic_section', methods=['GET'])
def dynamic_section():
    global empty_form
    # Retrieve errors, warnings and play_recap from the session
    error_message = session.pop('error_message', None)
    warning_message = session.pop('warning_message', None)
    play_recap = session.pop('play_recap', None)
    warning_output = session.pop('warning_output', None)
    error_output = session.pop('error_output', None)

    # Check data to see the request
    id_input = request.args.get('id_input') if request.args.get(
        'id_input') else None

    tag_options = find_tags()
    server_options = find_servers()
    command_inputs = {}

    # If id_input the request come from loading values of previous input list.
    if id_input:
        id_input = id_input
        g.last_form = g.last_inputs[id_input]
    try:
        # Get vars for single_site and selected_sites according to the server and tags
        extra_vars_sites_key_options = find_keys_extra_vars_sites()
        extra_vars_sites_value_options = find_values_extra_vars_sites(
            tags=g.last_form['tags'], server=g.last_form['limit'])

        for key, value in g.last_inputs.items():
            val_dict, _, _ = get_input_command(**value)
            command = {key: val_dict}
            command_inputs.update(
                command) if value['executed'] == True else None

    except Exception as e:
        tag_options = []
        server_options = []
        extra_vars_sites_key_options = []
        extra_vars_sites_value_options = []
        g.last_form = empty_form
        print(f'Check Ansible file system: {e}')
        print(traceback.print_exc())

    # Render the dynamic section template with the obtained variables
    dynamic_section_content = render_template('dynamic.html',
                                              last_form=g.last_form,
                                              inputs=command_inputs,
                                              error_message=error_message,
                                              warning_message=warning_message,
                                              play_recap=play_recap,
                                              warning_output=warning_output,
                                              error_output=error_output,
                                              tag_options=tag_options,
                                              server_options=server_options)
    # Render the Extra Vars Sites Section template with the obtained variables
    extra_vars_section_content = render_template(
        'extra_vars_sites.html',
        last_form=g.last_form,
        extra_vars_sites_key_options=extra_vars_sites_key_options,
        extra_vars_sites_value_options=extra_vars_sites_value_options)

    # Return both contents as JSON response
    return jsonify(dynamic_section_content=dynamic_section_content,
                   extra_vars_section_content=extra_vars_section_content)


# Extra vars sites section that will be loaded each time tags or server is changed
@client_app.route('/extra_vars_sites_section', methods=['GET'])
def extra_vars_sites_section():
    # If load_vars, the request comes from selecting tags or server to load Extra Vars Sites, then convinient to load the values to the last form
    load_vars = request.args.get('loadVars') if request.args.get(
        'loadVars') else None
    if (load_vars):
        tags_selected = request.args.getlist(
            'tagsSelected[]'
        ) if request.args.getlist('tagsSelected[]') and request.args.getlist(
            'tagsSelected[]') != [''] else None
        server_selected = request.args.get(
            'serverSelected') if request.args.get('serverSelected') else None
        extra_vars_list_input = request.args.getlist(
            'extraVarsSelected[]') if request.args.getlist(
                'extraVarsSelected[]') else None
        extra_vars_sites_key_selected = request.args.get(
            'extraVarKeySelected') if request.args.get(
                'extraVarKeySelected') else None
        extra_vars_sites_value_selected = request.args.getlist(
            'extraVarValueSelected[]') if request.args.getlist(
                'extraVarValueSelected[]') else None

        id_input = int(list(g.last_inputs.keys())[-1]) + 1
        g.last_form = get_last_form(server_selected, tags_selected,
                                    extra_vars_list_input,
                                    extra_vars_sites_key_selected,
                                    extra_vars_sites_value_selected)
        last_key_inputs = list(g.last_inputs)[-1]
        removed = g.last_inputs.pop(
            last_key_inputs
        ) if g.last_inputs[last_key_inputs]['executed'] == False else None
        g.last_inputs.update({id_input: g.last_form})

    try:
        # Get vars for single_site and selected_sites according to the server and tags
        extra_vars_sites_key_options = find_keys_extra_vars_sites()
        extra_vars_sites_value_options = find_values_extra_vars_sites(
            tags=g.last_form['tags'], server=g.last_form['limit'])

    except Exception as e:
        extra_vars_sites_key_options = []
        extra_vars_sites_value_options = []
        g.last_form = empty_form
        print(f'Check Ansible file system: {e}')
        print(traceback.print_exc())

    return render_template(
        'extra_vars_sites.html',
        last_form=g.last_form,
        extra_vars_sites_key_options=extra_vars_sites_key_options,
        extra_vars_sites_value_options=extra_vars_sites_value_options)


# Display app start end point
@client_app.route('/')
def display_app():
    session['Set Session'] = 'HTTP Started'
    return render_template('ansible_cli.html')
