from flask import session, redirect, url_for, abort


def login_required():
    """Redirect to login page if the user is not logged in."""
    if 'user_id' not in session:
        return redirect(url_for('auth_bp.login'))


def roles_required(*roles):
    """Return a before-request function enforcing the given roles."""
    def checker():
        if 'user_id' not in session:
            return redirect(url_for('auth_bp.login'))
        if session.get('role') not in roles:
            abort(403)
    return checker