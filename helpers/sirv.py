import os
import requests
import json
import datetime


class Sirv():
    def __init__(self, client_id, client_secret):
        self.client_id = client_id
        self.client_secret = client_secret

    @property
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
            print("Auth token attained...")
            return r.json()['token']

        return None

    def upload(self, file_name, file_path, sirv_folder_name):
        URI = 'https://api.sirv.com/v2/files/upload'

        auth_token = self.get_auth_token
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

        auth_token = self.get_auth_token
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
