SESSION = {}


def set(user_id, key, value):

    if user_id not in SESSION:
        SESSION[user_id] = {}

    SESSION[user_id][key] = value


def value(user_id, key):

    if user_id not in SESSION:
        return None

    return SESSION[user_id].get(key)


def clear(user_id):

    SESSION.pop(user_id, None)
