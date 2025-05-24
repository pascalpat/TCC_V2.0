# app/routes/auth_routes.py

from flask import Blueprint, render_template, request, session, redirect, url_for, current_app

# Define the Blueprint with matching variable name and URL prefix
# Blueprint variable name must match the import in app/__init__.py (auth_bp)
auth_bp = Blueprint(
    'auth_bp',               # endpoint name used in url_for()
    __name__,                # module name
    url_prefix='/auth',      # serves routes under /auth/...
    template_folder='templates'
)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Handles user login. On POST, stores user & clears any previous project/date."""
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        if not username:
            return render_template('login.html', error="Please provide a username.")

        # In a real app you'd validate credentials here...
        session.clear()
        session.permanent = False  # expire on browser close
        session['username']   = username
        session['user_id']    = 101      # example ID
        session['project_id'] = None
        session['report_date'] = None

        current_app.logger.info(f"User {username!r} logged in as ID {session['user_id']}")
        # Redirect to your calendar selection page (ensure calendar_bp is registered)
        return redirect(url_for('calendar_bp.calendar_page'))

    # GET → show the login form
    return render_template('login.html')

@auth_bp.route('/logout')
def logout():
    """Clears session and sends the user back to login."""
    session.clear()
    return redirect(url_for('auth_bp.login'))