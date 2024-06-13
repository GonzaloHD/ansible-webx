import os
import re
from ansible_webx import config
import yaml

from ansible_webx.prepare_data.decrypter import decrypter

root_dir = config['app'].get('root_directory')


def load_yaml_file(file_path):
    with open(file_path, 'r') as file:
        try:
            data = yaml.safe_load(file)
            if data is None:
                return []
            else:
                return data
        except yaml.YAMLError as exc:
            print(exc)


def get_yml_files() -> set:
    yml_files = set()

    for _, _, files in os.walk(root_dir):
        for file in files:
            if ".yml" in file:
                yml_files.add(file)
        break

    return yml_files


def find_tags() -> list:
    tags_list = []
    for dir, roles, _ in os.walk(os.path.join(root_dir, 'roles')):
        for role in roles:
            for tasks_folder, _, tasks in os.walk(
                    os.path.join(dir, role, 'tasks')):

                for task in tasks:
                    data = load_yaml_file(os.path.join(tasks_folder, task))
                    task_dictionary_list = data if isinstance(
                        data, list) else [data]
                    for single_task_dict in task_dictionary_list:
                        try:
                            tags = single_task_dict['tags']
                            if isinstance(tags, list):
                                tags_list.extend(tags)
                            elif isinstance(tags, str):
                                tags_list.append(tags)
                        except KeyError as ke:
                            continue
                break
        break
    return list(set(tags_list))


def find_servers() -> list:
    servers = []

    with open(os.path.join(root_dir, 'hosts'), 'r') as hosts:
        match_host = re.compile(r'^\s*#|^\s*\n')
        match_group = re.compile(r'^\s*\[[^\s]+\]\s*\n')
        for line in hosts:
            if match_host.match(line):
                continue
            else:
                if match_group.match(line):
                    continue
                    # servers.append(line.strip().replace('[',
                    #                                     '').replace(']', ''))
                else:
                    line = line.strip()
                    index_space = line.find(' ')
                    if index_space != -1:
                        servers.append(line[:index_space])
                    else:
                        servers.append(line)
    return servers


def find_keys_extra_vars_sites() -> list:
    keys = []
    keys.append('one_site')
    keys.append('multiple_sites')
    return keys


# Get the domains or host from the file vars in the managed-websites and managed-databases.
# By default loads all found on those roles, if set a server and/or tag/s then the search will focus on it or them.
def find_values_extra_vars_sites(tags=None, server=None) -> list:
    values_extra_vars_sites = set()
    var_dict = dict()
    server = '' if not server else server
    # Filter empty string from the list and if the result list is empty or None set to get all by default: ['database', 'website']
    tags = [tag for tag in tags
            if tag != ''] or ['database', 'website'] if tags is not None else [
                'database', 'website'
            ]
    # Extract domains for 'server_name' withing 'sites'
    if 'website' in ','.join(tags):
        for root, _, vars in os.walk(
                os.path.join(root_dir, 'roles', 'websites', 'vars')):
            for var in vars:
                if server in var:
                    var_dict = load_yaml_file(os.path.join(root, var))
                    try:
                        for site in var_dict['sites']:
                            values_extra_vars_sites.add(site['server_name'])
                    except KeyError as ke:
                        pass
    # Extract domains for 'domain' withing 'databases'
    if 'database' in ','.join(tags):
        for root, _, vars in os.walk(
                os.path.join(root_dir, 'roles', 'databases', 'vars')):
            for var in vars:
                if server in var:
                    extracted_var = decrypter(os.path.join(root_dir, '.vault'),
                                              os.path.join(root, var))
                    if not extracted_var:
                        extracted_var = load_yaml_file(os.path.join(root, var))
                    if isinstance(extracted_var, dict):
                        try:
                            for database in extracted_var['databases']:
                                values_extra_vars_sites.add(database['domain'])
                        except KeyError as ke:
                            pass
    return list(values_extra_vars_sites)


if __name__ == '__main__':
    print(get_yml_files())
    print(find_tags())
    print(find_keys_extra_vars_sites())
    print(find_values_extra_vars_sites())
