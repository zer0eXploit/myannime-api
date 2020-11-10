from typing import Dict

from flask_restful import Resource


MESSAGE = "What ya doin' here, dear? :)"


class Root(Resource):
    @classmethod
    def get(cls) -> Dict:
        return {"greetings": MESSAGE}, 200
