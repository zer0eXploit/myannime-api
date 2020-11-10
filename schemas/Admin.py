from ma import ma
from models.Admin import AdminModel


class AdminSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = AdminModel
