# app/routes/__init__.py
from .main_routes import main_bp
from .workers_routes import workers_bp
from .activity_codes_routes import activity_codes_bp
from flask import Blueprint, session, jsonify

debug_bp = Blueprint("debug", __name__)

@debug_bp.route("/debug/session", methods=["GET"])
def debug_session():
    """Returns the current session data as JSON."""
    return jsonify(dict(session))



def register_blueprints(app):
        # Register Blueprints (deferred to avoid circular imports)
        
        app.register_blueprint(debug_bp)
        app.register_blueprint(main_bp)
        app.register_blueprint(workers_bp, url_prefix='/workers')
        app.register_blueprint(activity_codes_bp, url_prefix='/activity-codes')
        from .equipment_routes import equipment_bp
        app.register_blueprint(equipment_bp, url_prefix='/equipment')
        from .data_entry_routes import data_entry_bp
        app.register_blueprint(data_entry_bp, url_prefix='/data-entry')
        from .projects_routes import projects_bp
        app.register_blueprint(projects_bp, url_prefix='/projects')
        from .update_progress_routes import update_progress_bp
        app.register_blueprint(update_progress_bp, url_prefix='/update-progress')
        from .validation_routes import validation_bp
        app.register_blueprint(validation_bp, url_prefix='/validation')
        from .dailynotes_routes import dailynotes_bp
        app.register_blueprint(dailynotes_bp, url_prefix='/dailynotes')
        from .materials_routes import materials_bp
        app.register_blueprint(materials_bp, url_prefix='/materials')
        from .pictures_routes import pictures_bp
        app.register_blueprint(pictures_bp, url_prefix='/pictures')
        from .subcontractors_routes import subcontractors_bp
        app.register_blueprint(subcontractors_bp, url_prefix='/subcontractors')
        from .work_orders_routes import work_orders_bp
        app.register_blueprint(work_orders_bp, url_prefix='/work-orders')
        from .data_persistence import data_persistence_bp
        app.register_blueprint(data_persistence_bp)
        from .calendar_routes import calendar_bp
        app.register_blueprint(calendar_bp, url_prefix='/calendar')
        from .auth_routes import auth_bp
        app.register_blueprint(auth_bp, url_prefix='/auth')
        from .labor_equipment_routes import labor_equipment_bp
        app.register_blueprint(labor_equipment_bp, url_prefix="/labor-equipment")
      