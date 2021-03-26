from typing import Dict

from flask_restful import Resource

from helpers.strings import get_text


class Root(Resource):
    @classmethod
    def get(cls) -> Dict:
        return {
            "greetings": get_text('home_welcome'),
            "frontend_uri": get_text('frontend_uri'),
            "api_docs_uri": get_text('api_docs_uri')
        }, 200
