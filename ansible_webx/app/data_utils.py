import json
import re
from ansible_webx import config


# Defaults to see empty form
def get_last_form(server='',
                  tags_list=[''],
                  extra_vars_list_form=None,
                  extra_vars_sites_key_form='',
                  extra_vars_sites_value_form=[''],
                  executed=False) -> dict:
    form_dictionary = dict()

    # Set last form inputs to display back the form as it was submitted:
    # Extra vars for single_site and selected_sites for displaying the last form inputs back accordingly.
    extra_vars_sites_form = {
        extra_vars_sites_key_form: extra_vars_sites_value_form
    } if extra_vars_sites_key_form and extra_vars_sites_value_form else {
        extra_vars_sites_key_form: ['']
    } if extra_vars_sites_key_form else {
        '': extra_vars_sites_value_form
    } if extra_vars_sites_value_form else {
        '': ['']
    }
    form_dictionary['limit'] = server if server else ''
    form_dictionary['tags'] = tags_list if tags_list else ['']
    form_dictionary['extra_vars'] = extra_vars_list_form
    form_dictionary[
        'extra_vars_sites'] = extra_vars_sites_form if extra_vars_sites_form else {
            '': ''
        }
    form_dictionary['executed'] = executed
    return form_dictionary


# extra_vars_list = form_dictionary['extra_vars']
def get_input_command(limit=None,
                      tags=None,
                      extra_vars=None,
                      extra_vars_sites=None,
                      **kwargs) -> dict:

    playbook_directory = f"{config['app'].get('root_directory')}"
    playbook = config['app'].get('playbook', 'playbook.yml')
    command_data = dict()
    warning_message = ''
    error_message = ''

    limit = limit if limit != '' else None

    # tags are expected as a list for run_ansible function, they are presented as strings, possibly separated by coma, in a list
    tags = [
        sub_tag.strip() for tag in tags for sub_tag in tag.split(',')
        if sub_tag.strip()
    ] if tags else None

    # Prepare the data to be sent to the run_ansible function:
    # Extra vars for single_site and selected_sites is expected as a single string or multiple separate by coma by run_ansible function and ansible roles behind.
    for key, value in extra_vars_sites.items():
        extra_vars_sites_value = value[
            0] if key == 'single_site' and value else ','.join(
                value) if value else None
        extra_vars_sites = {
            key: extra_vars_sites_value
        } if key and value else None

        # Send warning if more than one variable is selected for single_site
        warning_message = f"Warning: More than one var has been selected for single_site, only '{value[0]}' has been considered" if key == 'single_site' and len(
            value) > 1 else ''

    # Prepare a unify dictionary with all the vars to be sent.
    # extra_vars_list_input extracted from extra_vars in the form and extra_vars_sites for the single_site or selected_site.
    # https://docs.ansible.com/ansible/latest/playbook_guide/playbooks_variables.html
    if extra_vars or extra_vars_sites:
        # Prepare dictionary with all the vars
        extra_vars_result = extra_vars_sites.copy() if extra_vars_sites else {}
        vars_list = []
        if extra_vars:
            for extra_var in extra_vars:
                try:
                    if re.match(r'^\s*$', extra_var): continue
                    elif '=' in extra_var:
                        extra_var = extra_var.replace(',', ' ')
                        vars_list.extend(
                            re.sub(r'\s*=\s*', '=', extra_var).strip().split())
                    else:
                        vars_list.append(json.loads(extra_var))
                except json.JSONDecodeError as e:
                    error_message = 'Check format for variables, they should be key = value key2=value2 separate by space or json format: {"variable":"value","other_variable":"foo"}'
                except Exception as ex:
                    error_message = f'Unexpected error: {ex}. Check format for variables, they should be key = value key2=value2 separate by space or coma, or json format: {"variable":"value","other_variable":"foo"}'

        for var in vars_list:
            try:
                if '=' in var:
                    key, value = var.split('=', 1)
                    extra_vars_result[key.strip()] = value.strip()
                elif isinstance(var, dict):
                    extra_vars_result.update(var)
                else:
                    error_message = 'Check format for variables, they should be key = value key2=value2 separate by space or json format: {"variable":"value","other_variable":"foo"}'
            except Exception as ex:
                error_message = f'Unexpected error: {ex}. Check format for variables, they should be key = value key2=value2 separate by space or json format: {"variable":"value","other_variable":"foo"}'
        extra_vars_result = None if len(
            extra_vars_result) == 0 else extra_vars_result
    else:
        extra_vars_result = None

    command_data = {
        'playbook_directory': playbook_directory,
        'playbook': playbook,
        'limit': limit,
        'tags': tags,
        'extra_vars': extra_vars_result
    }

    return command_data, warning_message, error_message
