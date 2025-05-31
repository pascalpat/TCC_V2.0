# app/routes/auth_routes.py

from flask import Blueprint, render_template, request, session, redirect, url_for, current_app
from werkzeug.security import check_password_hash
from app.models.workforce_models import Worker
from sqlalchemy.orm import load_only

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
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '').strip()

        if not email or not password:
            return render_template('login.html', error="Please provide an email and password.")

        worker = Worker.query.options(
            load_only(Worker.id, Worker.name, Worker.password_hash, Worker.role)
        ).filter_by(courriel=email).first()

        if worker and worker.password_hash and check_password_hash(worker.password_hash, password):
            session.clear()
            session.permanent = False  # expire on browser close

            session['role'] = worker.role
            session['user_id'] = worker.id
            session['username'] = worker.name
            session['project_id'] = None
            session['report_date'] = None

            current_app.logger.info(
                f"User {worker.name!r} logged in with role {worker.role!r} and ID {worker.id}"
            )

            role = session['role']
            if role in ("foreman", "superintendent"):
                return redirect(url_for('data_entry_bp.submit_data_entry'))
            if role == 'manager':
                return redirect(url_for('projects_bp.get_project_numbers'))
            if role == 'admin':
                return redirect(url_for('admin_bp.index'))
            return redirect(url_for('calendar_bp.calendar_page'))

        return render_template('login.html', error="Invalid email or password.")


    # GET → show the login form
    return render_template('login.html')

@auth_bp.route('/logout')
def logout():
    """Clears session and sends the user back to login."""
    session.clear()
    return redirect(url_for('auth_bp.login'))