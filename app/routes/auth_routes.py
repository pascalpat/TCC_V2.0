# app/routes/auth_routes.py

from flask import Blueprint, render_template, request, session, redirect, url_for, current_app

auth = Blueprint(
    'auth_bp', 
    __name__, 
    url_prefix='/auth_bp', 
    template_folder='templates'
)

@auth.route('/login', methods=['GET', 'POST'])
def login():
    """Handles user login. On POST, stores user & clears any previous project/date."""
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        if not username:
            return render_template('login.html', error="Please provide a username.")

        # In a real app you'd validate credentials here...
        session.clear()  
        session['username']   = username
        session['user_id']    = 101      # example
        session['project_id'] = None
        session['report_date'] = None

        current_app.logger.info(f"User {username!r} logged in as ID {session['user_id']}")
        # Redirect into your calendar selection page
        return redirect(url_for('calendar.show_calendar'))

    # GET → show the login form
    return render_template('login.html')


@auth.route('/logout')
def logout():
    """Clears session and sends the user back to login."""
    session.clear()
    return redirect(url_for('auth.login'))
