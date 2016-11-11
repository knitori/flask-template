
from flask import request, session, abort
import random
import string


def csrf_protect():
    if request.method == "POST":
        token = session.pop('csrf_token', None)
        if not token or token != request.form.get('csrf_token'):
            abort(403)


def generate_csrf_token():
    if 'csrf_token' not in session:
        sysrand = random.SystemRandom()
        s = string.ascii_letters + string.digits
        parts = [
            ''.join(sysrand.choice(s) for _ in range(8)),
            ''.join(sysrand.choice(s) for _ in range(8)),
            ''.join(sysrand.choice(s) for _ in range(24)),
            ''.join(sysrand.choice(s) for _ in range(12)),
        ]
        session['csrf_token'] = '-'.join(parts)
    return session['csrf_token']
