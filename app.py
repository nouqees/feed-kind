from flask import Flask, flash, redirect, render_template, request, url_for

from config import Config
from extensions import db


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)

    import models  # noqa: F401 registers models with SQLAlchemy before create_all()

    from routes.main import main_bp
    from routes.auth import auth_bp
    from routes.donor import donor_bp
    from routes.ngo import ngo_bp
    from routes.admin import admin_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(donor_bp)
    app.register_blueprint(ngo_bp)
    app.register_blueprint(admin_bp)

    register_cli(app)
    register_error_handlers(app)

    return app


def register_error_handlers(app):
    @app.errorhandler(413)
    def file_too_large(e):
        max_mb = app.config["MAX_CONTENT_LENGTH"] // (1024 * 1024)
        flash(f"The uploaded file is too large. Maximum size is {max_mb}MB.", "error")
        return redirect(request.referrer or url_for("main.home"))

    @app.errorhandler(404)
    def not_found(e):
        return render_template("errors/404.html"), 404

    @app.errorhandler(500)
    def server_error(e):
        db.session.rollback()
        return render_template("errors/500.html"), 500


def register_cli(app):
    @app.cli.command("init-db")
    def init_db():
        """Create all database tables."""
        db.create_all()
        print("Database tables created.")

    @app.cli.command("seed")
    def seed():
        """Seed default food categories and an admin account."""
        from werkzeug.security import generate_password_hash

        from models.category import FoodCategory
        from models.user import User

        for name in ("Vegetarian", "Non-Vegetarian"):
            if not FoodCategory.query.filter_by(category_name=name).first():
                db.session.add(FoodCategory(category_name=name))

        if not User.query.filter_by(email="admin@foodwaste.local").first():
            db.session.add(User(
                name="Platform Admin",
                email="admin@foodwaste.local",
                password_hash=generate_password_hash("Admin@123", method="pbkdf2:sha256"),
                role=User.ROLE_ADMIN,
            ))

        db.session.commit()
        print("Seed data created: categories + admin account (admin@foodwaste.local / Admin@123)")


app = create_app()

if __name__ == "__main__":
    app.run(debug=True)
