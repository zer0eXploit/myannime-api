import os
import requests
import json
import datetime


class Sirv():
    def __init__(self, client_id, client_secret):
        self.client_id = client_id
        self.client_secret = client_secret
        self.sirv_token = None
        self.sirv_token_expiry = None

    def get_auth_token(self):
        print("Getting auth token...")
        AUTH_URI = 'https://api.sirv.com/v2/token'
        headers = {
            'content-type': 'application/json',
        }
        data = {
            'clientId': self.client_id,
            'clientSecret': self.client_secret
        }
        r = requests.post(AUTH_URI, headers=headers, data=json.dumps(data))

        if r.status_code == 200:
            now = datetime.datetime.now()
            time_expires = now + datetime.timedelta(seconds=1200)
            time_expires = int(time_expires.timestamp())
            self.sirv_token = r.json()['token']
            self.sirv_token_expiry = f'{time_expires}'
            print("Auth token attained...")

    def token_expiry_check(self):
        time_expires = int(self.sirv_token_expiry)
        now = datetime.datetime.now().timestamp()

        if time_expires < now:
            self.sirv_token = None
            self.sirv_token_expiry = None

    def setup(self):
        '''
        Make necessary preperations to upload file to sirv.
        Check token existence and validity.
        '''
        sirv_token = self.sirv_token

        if sirv_token is not None:
            print("Checking Sirv token expiry...")
            self.token_expiry_check()

        if sirv_token is None:
            print("Sirv token not found.")
            self.get_auth_token()

    def upload(self, file_name, file_path, sirv_folder_name):
        URI = 'https://api.sirv.com/v2/files/upload'

        self.setup()

        auth_token = self.sirv_token
        querystring = {'filename': f"/{sirv_folder_name}/{file_name}"}
        file_location = f'{file_path}/{file_name}'
        payload = open(file_location, 'rb')
        headers = {
            'content-type': 'application/json',
            'authorization': f'Bearer {auth_token}'
        }

        r = requests.post(
            URI, data=payload, headers=headers, params=querystring)

        if r.status_code == 200:
            print("Upload to sirv done. Removing local file...")
            os.remove(file_location)

        return {
            "image_path": f"https://veherthb.sirv.com/{sirv_folder_name}/{file_name}",
        }

    def delete(self, file_name, sirv_folder_name):
        URI = 'https://api.sirv.com/v2/files/delete'

        self.setup()

        auth_token = self.sirv_token
        querystring = {'filename': f"/{sirv_folder_name}/{file_name}"}
        headers = {
            'content-type': 'application/json',
            'authorization': f'Bearer {auth_token}'
        }

        r = requests.post(URI, headers=headers, params=querystring)

        if r.status_code == 200:
            print("Image from Sirv has been deleted...")
        else:
            print("Error removing file...")
