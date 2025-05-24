
# ─── Blueprint imports ──────────────────────────────────────────────────────────
# Import each blueprint directly to avoid circular imports
from app.routes.auth_routes                import auth_bp
from app.routes.calendar_routes            import calendar_bp
from app.routes.data_entry_routes          import data_entry_bp
from app.routes.entries_daily_notes_routes import entries_daily_notes_bp
from app.routes.main_routes                import main_bp
from app.routes.workers_routes             import workers_bp
from app.routes.equipment_routes           import equipment_bp
from app.routes.activity_codes_routes      import activity_codes_bp
from app.routes.cwp_routes                 import cwp_bp
from app.routes.purchase_orders_routes     import purchase_orders_bp
from app.routes.projects_routes            import projects_bp
from app.routes.update_progress_routes     import update_progress_bp
from app.routes.validation_routes          import validation_bp
from app.routes.payment_items_routes       import payment_items_bp
from app.routes.materials_routes           import materials_bp
from app.routes.pictures_routes            import pictures_bp
from app.routes.subcontractors_routes      import subcontractors_bp
from app.routes.work_orders_routes         import work_orders_bp
from app.routes.data_persistence           import data_persistence_bp
from app.routes.labor_equipment_routes     import labor_equipment_bp
from app.routes.media_routes               import media_bp
from app.routes.documents_routes           import documents_bp
from app.routes.admin_routes               import admin_bp

