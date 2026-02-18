
# This file stores important credentials for the app.
# Credentials are like keys that let the app connect to other services.

import os

# Twilio credentials (for sending texts)
twilio_account_sid = os.environ['twilio_account_sid']
twilio_auth_token = os.environ['twilio_auth_token']

# Google login info
GOOGLE_CLIENT_CONFIG = {
    "web": {
        "client_id": "1009101443632-fjnpa5cs3u2kl0m5uasglvjmvm7751vk.apps.googleusercontent.com",
        "client_secret": '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',
        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
        "token_uri": "https://oauth2.googleapis.com/token",
        "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
        "redirect_uris": [
            "https://127.0.0.1:5000/oauth2callback"
        ]
    }
}