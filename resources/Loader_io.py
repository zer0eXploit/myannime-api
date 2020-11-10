from flask import send_file
from flask_restful import Resource


class Loader(Resource):
    def get(self):
        response = send_file('loaderio-b8a35b9227646ad0cb661aa0a227f084.txt')

        return response
