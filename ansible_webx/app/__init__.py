from datetime import datetime
import logging
from flask import Flask, jsonify, request, session
from flask_session import Session
from flask_cors import CORS
from ansible_webx.app.display_app import client_app
from ansible_webx.app.api_resources import api_app
from ansible_webx import config

connected_clients = {}


def create_app():

    app = Flask(__name__)

    app.register_blueprint(api_app)
    app.register_blueprint(client_app)
    CORS(app)

    @app.errorhandler(405)
    def method_not_allowed(e):
        return jsonify({'message': 'method not allowed'}), 405

    @app.errorhandler(404)
    def not_found(e):
        return jsonify({'message': 'not found'}), 404

    # Set secret key
    app.config['SECRET_KEY'] = config['flask'].get('app_key', 'secret')

    # Configure session cookie to use SameSite=None attribute
    app.config['SESSION_COOKIE_SAMESITE'] = 'None'

    # Ensure that Flask app uses a secure session cookie
    app.config['SESSION_COOKIE_SECURE'] = True

    app.config['SESSION_COOKIE_NAME'] = 'FLASK_ANSIBLE_APP'

    app.config[
        'SESSION_TYPE'] = 'filesystem'  # Consider a more persistent type

    # Get the socketio instance and init it with the app
    from ansible_webx.app.socketio_instance import socketio
    socketio.init_app(app)

    # Set logging level to ERROR for Flask-SocketIO
    logging.getLogger('socketio').setLevel(logging.ERROR)
    logging.getLogger('engineio').setLevel(logging.ERROR)

    @socketio.on_error_default  # handles all namespaces without an explicit error handler
    def default_error_handler(e):
        pass

    @socketio.on('connect')
    def handle_connect():
        client_id = request.sid  # Get the socket ID of the connected client
        connected_clients[client_id] = {
            'ip_address': request.remote_addr,  # Get client's IP address
            'connection_time': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }  # Store client information
        print(f"Client {client_id} connected...")
        session['sid'] = client_id

    @socketio.on('disconnect')
    def handle_disconnect():
        client_id = request.sid
        if client_id in connected_clients:
            del connected_clients[
                client_id]  # Remove client information upon disconnection
            session.pop('sid')
        print(f"Client {client_id} disconnected...")

    Session(app)
    return app, socketio
