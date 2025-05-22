# app/routes/__init__.py

from flask import Blueprint, session, jsonify

from .main_routes           import main_bp
from .workers_routes        import workers_bp
from .activity_codes_routes import activity_codes_bp

# -- debug session endpoint ---
debug_bp = Blueprint("debug", __name__)

@debug_bp.route("/debug/session", methods=["GET"])
def debug_session():
    return jsonify(dict(session))


def register_blueprints(app):
    # 1) Debug first
    app.register_blueprint(debug_bp)

    # 2) Core flow: Auth → Calendar → Data-Entry → Daily-Notes
    from .auth_routes                import auth             # defines auth = Blueprint('auth', …)
    from .calendar_routes            import calendar_bp      # defines calendar_bp = Blueprint('calendar_bp', …)
    from .data_entry_routes          import data_entry_bp    # defines data_entry_bp = Blueprint('data_entry_bp', url_prefix='/data-entry')
    from .entries_daily_notes_routes import entries_daily_notes_bp
                                                    # defines entries_daily_notes_bp = Blueprint('entries_daily_notes_bp', url_prefix='/entries_daily_notes')

    app.register_blueprint(auth)                             # auth has its own url_prefix='/auth'
    app.register_blueprint(calendar_bp, url_prefix='/calendar')
    app.register_blueprint(data_entry_bp)                     # data_entry_bp already has url_prefix
    app.register_blueprint(entries_daily_notes_bp)            # ditto for entries_daily_notes_bp

    # 3) Everything else
    app.register_blueprint(main_bp)
    app.register_blueprint(workers_bp,        url_prefix='/workers')
    app.register_blueprint(activity_codes_bp, url_prefix='/activity-codes')

    from .equipment_routes       import equipment_bp
    from .projects_routes        import projects_bp
    from .update_progress_routes import update_progress_bp
    from .validation_routes      import validation_bp
    from .materials_routes       import materials_bp
    from .pictures_routes        import pictures_bp
    from .subcontractors_routes  import subcontractors_bp
    from .work_orders_routes     import work_orders_bp
    from .data_persistence       import data_persistence_bp
    from .labor_equipment_routes import labor_equipment_bp
    from .media_routes           import media_bp
    from .documents_routes       import documents_bp


    app.register_blueprint(equipment_bp,        url_prefix='/equipment')
    app.register_blueprint(projects_bp,         url_prefix='/projects')
    app.register_blueprint(update_progress_bp,  url_prefix='/update-progress')
    app.register_blueprint(validation_bp,       url_prefix='/validation')
    app.register_blueprint(materials_bp,        url_prefix='/materials')
    app.register_blueprint(pictures_bp,         url_prefix='/pictures')
    app.register_blueprint(subcontractors_bp,   url_prefix='/subcontractors')
    app.register_blueprint(work_orders_bp,      url_prefix='/work-orders')
    app.register_blueprint(data_persistence_bp)             # if that blueprint has its own prefix
    app.register_blueprint(labor_equipment_bp,  url_prefix='/labor-equipment')
    app.register_blueprint(media_bp,            url_prefix='/media')
    app.register_blueprint(documents_bp,        url_prefix='/documents')
