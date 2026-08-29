import time

SESSION = {}


def create(user_id):

    SESSION[user_id] = {
        "step": "method",
        "message_id": None,
        "method": None,
        "number": None,
        "amount": None,
        "trx": None,
        "photo": None,
        "time": time.time()
    }

def exists(user_id):

    return user_id in SESSION


def get(user_id):

    return SESSION.get(user_id)


def set(user_id, key, value):

    if user_id not in SESSION:

        create(user_id)

    SESSION[user_id][key] = value


def value(user_id, key):

    if user_id not in SESSION:

        return None

    return SESSION[user_id].get(key)


def clear(user_id):

    SESSION.pop(user_id, None)

def expired(user):

    if user not in SESSION:
        return True

    return time.time() - SESSION[user]["time"] > 600

def set_message(user_id, message_id):

    if user_id not in SESSION:
        create(user_id)

    SESSION[user_id]["message_id"] = message_id


def message(user_id):

    if user_id not in SESSION:
        return None

    return SESSION[user_id]["message_id"]
