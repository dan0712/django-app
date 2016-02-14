
def validate_email(email):
    from django.core.validators import validate_email
    from django.core.exceptions import ValidationError

    try:
        validate_email(email)
        return True
    except ValidationError:
        return False
