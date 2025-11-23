import threading
import time
import webbrowser
import os
import sys

# Import the Flask app
from app import app


def run_server(host='127.0.0.1', port=5000, debug=False):
    # When running under PyInstaller, avoid the reloader
    app.run(host=host, port=port, debug=debug, use_reloader=False)


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    host = os.environ.get('FLASK_HOST', '127.0.0.1')
    debug = os.environ.get('FLASK_DEBUG', 'false').lower() in ('1', 'true', 'yes')

    t = threading.Thread(target=run_server, args=(host, port, debug), daemon=True)
    t.start()

    # Wait briefly for server to start
    time.sleep(1)
    url = f'http://{host}:{port}'
    try:
        webbrowser.open(url)
    except Exception:
        pass

    print(f"Server running at {url}. Press Ctrl+C to stop.")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print('Stopping')
