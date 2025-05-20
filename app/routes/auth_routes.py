from flask import Blueprint, render_template, request, session, redirect, url_for

auth_bp = Blueprint('auth_bp', __name__, template_folder='templates')

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Handles user login."""
    if request.method == 'POST':
        username = request.form.get('username')
        if not username:
            return render_template('login.html', error="Please provide a username.")
        
        # Store user in session
        session['username'] = username
        session['user_id'] = 101
        session['project_id'] = None
        session ['report_date'] = None
        print(f"User {username} logged in with user id 101.")
        return redirect(url_for('calendar_bp.calendar_page'))

    return render_template('login.html')

@auth_bp.route('/logout', methods=['GET'])
def logout():
    """Clear the session and redirect to the login page."""
    session.clear()
    return redirect(url_for('auth_bp.login'))
