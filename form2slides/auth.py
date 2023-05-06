import pickle
import json
import os
import sys
import google.auth
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

SCOPES = ["https://www.googleapis.com/auth/drive"]  # Replace with the scopes you need


def get_google_credentials():
    creds = None
    token_file = "token.pickle"
    client_secrets_file = "oauth_credentials.json"

    if os.path.exists(token_file):
        with open(token_file, "rb") as token:
            creds = pickle.load(token)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if os.path.exists(client_secrets_file):
                with open(client_secrets_file, "r") as json_file:
                    client_config = json.load(json_file)
            else:
                client_config = json.loads(sys.stdin.buffer.read())

            flow = InstalledAppFlow.from_client_config(
                client_config, SCOPES
            )
            creds = flow.run_local_server(port=0)

        with open(token_file, "wb") as token:
            pickle.dump(creds, token)

    return creds


if __name__ == "__main__":
    credentials = get_google_credentials()
    print("Access Token:", credentials.token)
    print("Refresh Token:", credentials.refresh_token)
