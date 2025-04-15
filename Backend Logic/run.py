from flask import Flask
from app import create_app

app = create_app()

if __name__ == '__main__':
    # Optimize for local development
    # app.config['PROPAGATE_EXCEPTIONS'] = True
    # app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0
    app.run(
        host='localhost',
        port=5000,
        debug=True,  # Disable debug mode for speed
        threaded=True,
    )
