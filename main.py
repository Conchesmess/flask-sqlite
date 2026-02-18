
# This is the main file that starts the app.
# It sets up the database and runs the web server.

from datetime import datetime  # Used for dates and times
import os  # Used to access environment variables
from app import app, db  # Import the app and database from the app folder

if __name__ == '__main__':
    # Create database tables if they don't exist
    with app.app_context():
        db.create_all()
    
    # Check if Google client ID and secret are set in environment variables
    if not os.environ.get('ccpa_google_client_id'):
        print("Warning: ccpa_google_client_id environment variable not set")
    if not os.environ.get('ccpa_google_client_secret'):
        print("Warning: ccpa_google_client_secret environment variable not set")
    
    # Start the web server with SSL (secure connection)
    app.run(debug=True, use_reloader=True, ssl_context=('cert.pem', 'key.pem'), port=8080)