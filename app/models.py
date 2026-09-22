from datetime import datetime
from decimal import Decimal
from flask_login import UserMixin
from werkzeug.security import check_password_hash, generate_password_hash
from .extensions import db, login_manager


@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))


class TimestampMixin:
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)


class User(UserMixin, TimestampMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    username = db.Column(db.String(30), nullable=False, unique=True, index=True)
    email = db.Column(db.String(120), nullable=False, unique=True, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    currency_code = db.Column(db.String(3), nullable=False, default="INR")
    transactions = db.relationship("Transaction", backref="user", lazy="dynamic", cascade="all, delete-orphan")
    categories = db.relationship("Category", backref="user", lazy="dynamic", cascade="all, delete-orphan")
    budgets = db.relationship("Budget", backref="user", lazy="dynamic", cascade="all, delete-orphan")

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class Category(TimestampMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=True, index=True)
    name = db.Column(db.String(50), nullable=False)
    transaction_type = db.Column(db.String(10), nullable=False, index=True)
    is_default = db.Column(db.Boolean, nullable=False, default=False)
    transactions = db.relationship("Transaction", backref="category", lazy="dynamic")
    budgets = db.relationship("Budget", backref="category", lazy="dynamic", cascade="all, delete-orphan")
    __table_args__ = (db.UniqueConstraint("user_id", "name", "transaction_type", name="uq_category_owner_name_type"),)


class Transaction(TimestampMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False, index=True)
    category_id = db.Column(db.Integer, db.ForeignKey("category.id"), nullable=False, index=True)
    transaction_type = db.Column(db.String(10), nullable=False, index=True)
    title = db.Column(db.String(120), nullable=False)
    amount = db.Column(db.Numeric(12, 2), nullable=False)
    description = db.Column(db.Text)
    payment_method = db.Column(db.String(40))
    transaction_date = db.Column(db.Date, nullable=False, index=True)


class Budget(TimestampMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False, index=True)
    category_id = db.Column(db.Integer, db.ForeignKey("category.id"), nullable=False, index=True)
    amount = db.Column(db.Numeric(12, 2), nullable=False, default=Decimal("0"))
    period_start = db.Column(db.Date, nullable=False, index=True)
    __table_args__ = (db.UniqueConstraint("user_id", "category_id", "period_start", name="uq_budget_period"),)
