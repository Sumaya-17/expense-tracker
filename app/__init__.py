from flask import Flask, render_template
from config import config
from .extensions import csrf, db, login_manager, migrate


def create_app(config_name="development"):
    app = Flask(__name__)
    app.config.from_object(config[config_name])

    db.init_app(app)
    migrate.init_app(app, db)
    csrf.init_app(app)

    @app.template_filter("inr")
    def inr(value):
        return "₹{:,.2f}".format(value or 0)
    login_manager.init_app(app)
    login_manager.login_view = "auth.login"
    login_manager.login_message = "Please sign in to access your finances."
    login_manager.login_message_category = "warning"

    from .auth.routes import auth_bp
    from .budgets.routes import budgets_bp
    from .main.routes import main_bp
    from .profile.routes import profile_bp
    from .reports.routes import reports_bp
    from .transactions.routes import transactions_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp, url_prefix="/auth")
    app.register_blueprint(transactions_bp, url_prefix="/transactions")
    app.register_blueprint(budgets_bp, url_prefix="/budgets")
    app.register_blueprint(reports_bp, url_prefix="/reports")
    app.register_blueprint(profile_bp, url_prefix="/profile")

    @app.errorhandler(403)
    def forbidden(_error):
        return render_template("errors/403.html"), 403

    @app.errorhandler(404)
    def not_found(_error):
        return render_template("errors/404.html"), 404

    @app.errorhandler(500)
    def server_error(_error):
        db.session.rollback()
        return render_template("errors/500.html"), 500

    with app.app_context():
        from . import models  # noqa: F401
        db.create_all()
    return app
