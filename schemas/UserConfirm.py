from ma import ma
from models.UserConfirmation import ConfirmationModel


class ConfirmationSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = ConfirmationModel
        load_only = ('user',)
        dump_only = ('confirmation_id', 'expires_at', 'confirmed')
        include_fk = True
