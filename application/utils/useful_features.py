from flask import abort


# =====================SOME USEFUL FUNCTION WITHOUT CATEGORY=============================================
def check_on_space(arguments: dict) -> bool:
    """
    checking some spacing in parametrs of request
    :param arguments:
    :return: bool answer
    """
    data = arguments

    if type(data) == dict:
        for word in data.values():
            check = str(word).split(' ')
            if len(check) != 1:
                return False
        return True
    else:
        for word in data:
            check = str(word).split(' ')
            if len(check) != 1:
                return False
        return True


def check_id(user_id: str) -> int:
    """
    Get string ID from user serialize from int and check them
    :param user_id:
    :return: user_id -> int
    """
    if len(user_id) <= 0:
        abort(400)

    if user_id.lower() == 'null' or user_id == 'none' or user_id == '':
        abort(400)
    try:
        user_id = int(user_id)
    except:
        abort(400)

    if user_id <= 0:
        abort(400)

    return user_id


def serialize_to_task_user(user: dict) -> dict:
    return {
        'id': user['id'],
        'firstName': user['firstName'],
        'lastName': user['lastName'],
        'email': user['email']
    }


def check_on_null(**kwargs: dict) -> bool:
    """CHECK OBJECT ON NULL"""

    for value in kwargs.values():

        if len(value) <= 0 or value == '' or value is None:
            return True

    return False
# .