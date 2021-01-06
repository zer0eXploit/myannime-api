from marshmallow import Schema, fields
from werkzeug.datastructures import FileStorage


class FileStorageField(fields.Field):
    default_error_message = {
        'invalid': 'Not a valid field.'
    }

    def _deserialize(self, value, attr, data, partial) -> FileStorage:
        if value is None:
            return None

        if not isinstance(value, FileStorage):
            self.fail('invalid')

        return value


class ImageSchema(Schema):
    image = FileStorageField(required=True)
