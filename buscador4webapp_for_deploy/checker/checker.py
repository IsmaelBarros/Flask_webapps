from flask import session
from functools import wraps

def check_logged_in(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if 'loggedin' in session:
            return func(*args, **kwargs)
        return 'Você NÃO está logado.'
    return wrapper
