from telegram import Update
from telegram.ext import ContextTypes

INPUT = {}


def start_input(user_id, name):
    INPUT[user_id] = name


def stop_input(user_id):
    INPUT.pop(user_id, None)


def current_input(user_id):
    return INPUT.get(user_id)
