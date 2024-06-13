<div style="text-align: center;">
    <img src="ansible_webx/app/static/AnsibleWebX_logo_v1.svg" alt="AnsibleWebX Logo" width="200"/>
    <h1 style="font-weight: bold; margin-top: 10px;">AnsibleWebX</h1>
</div>

Flask web application that allows users to execute Ansible commands via a user-friendly web interface. It also provides an optional REST API.

## Features

- Execute Ansible commands through a web interface.
- Supports specifying tags, extra variables, and limit.
- Real-time streaming of command output.
- Error handling for invalid input and command execution failures.
- Utilize an optional REST API for accessing various functionalities.

## Installation

1. **Clone the repository:**

   ```
   git clone <repository_url>
   ```

2. **Install dependencies:**

    ```
    pip install -r requirements.txt
    ```

3. **Configure the application by editing the `config.ini` file.**

   The `config.ini` file contains configuration variables for the application. Here are the variables you can configure:

   ```ini
   [app]
   root_directory = /path/to/your/playbooks/directory
   ; The directory path where your Ansible playbooks are located.

   playbook = your_playbook.yml
   ; The name of the main playbook file to be executed.

   emit = 'client'
    ; Emitting to 'all' ensures that stdout is emitted, but could not give desirable experience when working with multiple sessions.
    ; The 'client' approach has been tested and works with gevent and Flask's built-in web servers,
    ; allowing for emitting to a specific client, which is the preferred method in such cases.

   [flask]
   app_key = your_secret_key
   ; Secret key for Flask application session management.

   host = 0.0.0.0
   ; Host address to run the Flask application.

   port = 5005
   ; Port number to run the Flask application.

   protocol = http
   ; Protocol to use for the Flask application.

   debug = True
   ; Enable/disable Flask application debugging mode.

   server_name = 127.0.0.1
   ; Server name or IP address for the Flask application.

4. **Run the Flask application:**
    ```
    cd ansible_cli_app
    ```
    ```
    python3 -m ansible_webx.app.run
    ```

5. **Access the application in your web browser at [http://127.0.0.1:5005].**

## Usage

### Web Interface

1. Open your web browser and navigate to the application URL.
2. Fill in the form with the desired options:
   - **Server:** Select the server to execute the playbook on.
   - **Tags:** Specify the tags to include in the execution, it will narrow the roles.
   - **Extra Vars Sites:** Choose the between 'single_site' and 'selected_sites' as key and the domains or domains for the 'selected_sites' case.
   - **Other Extra Vars:** Provide any extra variables needed for the execution.
3. Click the "Execute" button to run the Ansible command.
4. View the real-time output of the command execution.
5. The previous commands executed will display above, you can load its values for executing them again or modifiyin them before.


### REST API (Optional)

The application provides the following endpoints, allowing you to interact with it programmatically or by sending requests:

- **GET /api/servers:** Get available server options.
- **GET /api/tags:** Get available tag options.
- **GET /api/extra_vars_sites_keys:** Get available extra variables site keys.
- **GET /api/extra_vars_sites_values:** Get available extra variables site values based on tags and servers.
- **POST /api/running_ansible:** Execute an Ansible command. Provide JSON data with the following parameters:
  - `playbook_directory`: Directory path of the playbook.
  - `playbook`: Name of the playbook file.
  - `tags`: List of tags to include in the execution.
  - `extra_vars`: Extra variables as a dictionary.
  - `limit`: Limit the execution to specific hosts.
- **POST /api/set_cookie:** Set a cookie with JSON data.
- **GET /api/get_cookie:** Retrieve the JSON data stored in the cookie.

Note: Useful if you desire to develop another front-end using the API.

## Dependencies

- Flask: Web framework for Python.
- PyYAML: YAML parser and emitter for Python.
- ansible: Configuration management and application deployment tool.
- ansible-runner: Library for running Ansible in Python.
- ansi2html: Library for converting ANSI escape sequences to HTML.
- Flask-SocketIO: Flask extension for Socket.IO integration.
- Flask-Session: Flask extension for session management with filesystem storage, allowing better session sharing between HTTP and SocketIO.
- Flask-Cors: Flask extension for handling Cross-Origin Resource Sharing (CORS).
- requests: HTTP library for Python.
- jmespath: JSON Matching Expressions (JMESPath) implementation for Python.