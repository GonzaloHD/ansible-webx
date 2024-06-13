from ansible_webx import config
from ansible_webx.app import create_app

if __name__ == '__main__':
    app, socketio = create_app()
    socketio.run(app,
                 host=config['flask'].get('host', '0.0.0.0'),
                 port=int(config['flask'].get('port', 5005)),
                 debug=config['flask'].get('debug', False))
