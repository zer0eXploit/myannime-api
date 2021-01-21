import os
import requests


class SendInBlueError(Exception):
    def __init__(self, message):
        self.message = message
        super().__init__(self.message)

    def __str__(self):
        return self.message


class SendInBlue:
    SEND_EMAIL_ENDPOINT = "https://api.sendinblue.com/v3/smtp/email"
    API_KEY = os.environ.get("SENDINBLUE_API_KEY")
    MAIL_NOT_SENT_ERROR = "SendInBlue response status is not 201. Email not sent."
    REQUEST_ERROR = "Error occurred during SendInBlue API request."

    @classmethod
    def send_activation_email(cls, **kwargs) -> None:
        payload = {
            "sender": {
                "name": "MyanNime",
                "email": "noreply@myannime.com"
            },
            "to": [
                {
                    "email": kwargs["email"],
                    "name": kwargs["name"]
                }
            ],
            "params": {
                "NAME": kwargs["name"],
                "ACTIVATION_LINK": kwargs["activation_link"]
            },
            "templateId": 1
        }
        headers = {
            "accept": "application/json",
            "content-type": "application/json",
            "api-key": cls.API_KEY
        }

        try:
            response = requests.request(
                "POST",
                cls.SEND_EMAIL_ENDPOINT,
                json=payload,
                headers=headers
            )

            print(response.status_code)
            if response.status_code != 201:
                raise SendInBlueError(cls.MAIL_NOT_SENT_ERROR)

            print(response.text)

        except Exception as ex:
            print(ex)
            raise SendInBlueError(cls.REQUEST_ERROR)

    @classmethod
    def send_pw_reset_email(cls, **kwargs) -> None:
        # The code is not dry! Re UPDATE IT!!
        payload = {
            "sender": {
                "name": "MyanNime",
                "email": "noreply@myannime.com"
            },
            "to": [
                {
                    "email": kwargs["email"],
                    "name": kwargs["name"]
                }
            ],
            "params": {
                "NAME": kwargs["name"],
                "PW_RESET_LINK": kwargs["pw_reset_link"]
            },
            "templateId": 2
        }
        headers = {
            "accept": "application/json",
            "content-type": "application/json",
            "api-key": cls.API_KEY
        }

        try:
            response = requests.request(
                "POST",
                cls.SEND_EMAIL_ENDPOINT,
                json=payload,
                headers=headers
            )

            print(response.status_code)
            if response.status_code != 201:
                raise SendInBlueError(cls.MAIL_NOT_SENT_ERROR)

            print(response.text)

        except Exception as ex:
            print(ex)
            raise SendInBlueError(cls.REQUEST_ERROR)
