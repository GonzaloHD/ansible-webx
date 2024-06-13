# socketio_instance.py
# Module to place the socketio instance to avoid circular imports between app main module and ansible_run_command module

from flask_socketio import SocketIO

socketio = SocketIO(manage_session=False, logger=True, engineio_logger=True)
