from flask import Blueprint, render_template, current_app
import json
import os
import glob

admin_bp = Blueprint("admin_bp", __name__, url_prefix="/admin")

@admin_bp.route("/")
def index():
    """Render the admin panel with hashed asset paths if available."""
    
    static_admin = os.path.join(current_app.static_folder, "admin")
    manifest_path = os.path.join(static_admin, "manifest.json")

    admin_js = None
    admin_css = None

    if os.path.exists(manifest_path):
        with open(manifest_path, "r", encoding="utf-8") as f:
            manifest = json.load(f)

        entry = manifest.get("index.html") or next(iter(manifest.values()), {})
        file_path = entry.get("file")
        if file_path:
            admin_js = f"admin/{file_path}"

        css_files = entry.get("css") or []
        if css_files:
            admin_css = f"admin/{css_files[0]}"
    else:
        assets_dir = os.path.join(static_admin, "assets")
        js_matches = glob.glob(os.path.join(assets_dir, "index-*.js"))
        if not js_matches:
            plain_js = os.path.join(assets_dir, "index.js")
            if os.path.exists(plain_js):
                js_matches = [plain_js]
        if js_matches:
            js_path = js_matches[0]
            admin_js = f"admin/assets/{os.path.basename(js_path)}"

            css_candidate = os.path.splitext(js_path)[0] + ".css"
            if os.path.exists(css_candidate):
                admin_css = f"admin/assets/{os.path.basename(css_candidate)}"

    return render_template("admin/index.html", admin_js=admin_js, admin_css=admin_css)