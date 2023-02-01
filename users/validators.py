import re


def password_validator(password):
    password_validation = (r"^(?=.*[a-z])(?=.*\d)(?=.*[$@$!%*?&])[A-Za-z\d$@$!%*?&]{8,16}")

    if not re.search(password_validation, str(password)):
        return True
    return False


def nickname_validator(nickname):
    nickname_validation = (r"^[A-Za-z가-힣0-9]{3,10}$")

    if not re.search(nickname_validation, str(nickname)):
        return True
    return False
