from ma import ma


class AuthSchema(ma.Schema):
    class Meta:
        fields = ("username", "password",)
