import subprocess
import yaml


def decrypter(vault_file, yaml_file):

    # Decrypt and load database data
    decrypt_cmd = [
        "ansible-vault", "view", "--vault-password-file", vault_file, yaml_file
    ]
    try:
        process = subprocess.Popen(decrypt_cmd,
                                   stdout=subprocess.PIPE,
                                   stderr=subprocess.PIPE,
                                   universal_newlines=True)
        stdout, stderr = process.communicate()
        vars_data = yaml.safe_load(stdout)

        if process.returncode != 0:
            return False

    except Exception as e:
        print(f"Exception occurred: {e}")
        return False
    return vars_data


if __name__ == '__main__':
    from ansible_webx import config
    import os
    root_dir = config['app'].get('root_directory')
    vault_file = os.path.join(root_dir, '.vault')
    vars_yaml_file = "roles/databases/vars/databases.yml"
    print(decrypter(vault_file, os.path.join(root_dir, vars_yaml_file)))
