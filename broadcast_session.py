SESSION = {}


def create(user_id):

    SESSION[user_id] = {
        "message_id": None
    }


def set_message(user_id, message_id):

    if user_id not in SESSION:
        create(user_id)

    SESSION[user_id]["message_id"] = message_id


def message(user_id):

    if user_id not in SESSION:
        return None

    return SESSION[user_id]["message_id"]


def clear(user_id):

    SESSION.pop(user_id, None)

