from datetime import datetime
import os
from app import app, db





if __name__ == '__main__':
    # Create database tables
    with app.app_context():
        db.create_all()
    
    # Check for required environment variables
    if not os.environ.get('ccpa_google_client_id'):
        print("Warning: ccpa_google_client_id environment variable not set")
    if not os.environ.get('ccpa_google_client_secret'):
        print("Warning: ccpa_google_client_secret environment variable not set")
    
    #app.run(debug=True)
    app.run(debug="True",use_reloader=True, ssl_context=('cert.pem', 'key.pem'),port=8080)