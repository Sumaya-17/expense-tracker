from datetime import date
from decimal import Decimal, InvalidOperation
from flask import Blueprint, abort, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required
from sqlalchemy import or_
from .forms import DeleteForm, TransactionForm
from ..extensions import db
from ..models import Category, Transaction

transactions_bp = Blueprint("transactions", __name__)
DEFAULT_CATEGORIES = {
    "income": ["Salary", "Freelance", "Business", "Investment", "Gift", "Other"],
    "expense": ["Food", "Transport", "Shopping", "Bills", "Entertainment", "Healthcare", "Education", "Travel", "Rent", "Subscriptions", "Other"],
}


def available_categories(kind=None):
    defaults = Category.query.filter_by(is_default=True)
    personal = Category.query.filter_by(user_id=current_user.id)
    if kind:
        defaults = defaults.filter_by(transaction_type=kind)
        personal = personal.filter_by(transaction_type=kind)
    return defaults.union(personal).order_by(Category.name).all()


def set_category_choices(form, kind=None):
    form.category_id.choices = [(c.id, c.name) for c in available_categories(kind)]


@transactions_bp.before_app_request
def ensure_default_categories():
    # Defaults are shared rows; this safely seeds them on first request.
    if not Category.query.filter_by(is_default=True).first():
        for kind, names in DEFAULT_CATEGORIES.items():
            db.session.add_all([Category(name=name, transaction_type=kind, is_default=True) for name in names])
        db.session.commit()


@transactions_bp.route("/", methods=["GET", "POST"])
@login_required
def list_transactions():
    form = TransactionForm()
    selected_type = request.args.get("type", "expense")
    if selected_type not in {"income", "expense"}:
        selected_type = "expense"
    # Both sets are available because the type control can be changed client-side;
    # the ownership/type check below remains the source of truth.
    set_category_choices(form)
    if form.validate_on_submit():
        category = db.session.get(Category, form.category_id.data)
        if not category or category.transaction_type != form.transaction_type.data or (category.user_id and category.user_id != current_user.id):
            abort(403)
        transaction = Transaction(user_id=current_user.id, category_id=category.id, transaction_type=form.transaction_type.data,
                                  title=form.title.data.strip(), amount=form.amount.data, description=(form.description.data or "").strip(),
                                  payment_method=form.payment_method.data or None, transaction_date=form.transaction_date.data)
        db.session.add(transaction)
        db.session.commit()
        flash(f"{form.transaction_type.data.title()} added successfully.", "success")
        return redirect(url_for("transactions.list_transactions"))

    query = Transaction.query.filter_by(user_id=current_user.id)
    kind = request.args.get("type")
    if kind in {"income", "expense"}: query = query.filter_by(transaction_type=kind)
    search = request.args.get("q", "").strip()
    if search: query = query.join(Category).filter(or_(Transaction.title.ilike(f"%{search}%"), Transaction.description.ilike(f"%{search}%"), Category.name.ilike(f"%{search}%")))
    category_id = request.args.get("category", type=int)
    if category_id:
        query = query.filter(Transaction.category_id == category_id)
    for arg, operator in (("from", Transaction.transaction_date.__ge__), ("to", Transaction.transaction_date.__le__)):
        value = request.args.get(arg)
        if value:
            try: query = query.filter(operator(date.fromisoformat(value)))
            except ValueError: pass
    for arg, operator in (("min_amount", Transaction.amount.__ge__), ("max_amount", Transaction.amount.__le__)):
        value = request.args.get(arg)
        if value:
            try: query = query.filter(operator(Decimal(value)))
            except (InvalidOperation, ValueError): pass
    ordering = request.args.get("sort", "newest")
    orderings = {"oldest": (Transaction.transaction_date.asc(), Transaction.id.asc()), "highest": (Transaction.amount.desc(),), "lowest": (Transaction.amount.asc(),), "newest": (Transaction.transaction_date.desc(), Transaction.id.desc())}
    page = request.args.get("page", 1, type=int)
    transactions = query.order_by(*orderings.get(ordering, orderings["newest"])).paginate(page=page, per_page=10, error_out=False)
    return render_template("transactions/list.html", form=form, transactions=transactions, delete_form=DeleteForm(), selected_type=selected_type, filter_categories=available_categories())


@transactions_bp.route("/<int:transaction_id>/edit", methods=["GET", "POST"])
@login_required
def edit_transaction(transaction_id):
    transaction = Transaction.query.filter_by(id=transaction_id, user_id=current_user.id).first_or_404()
    form = TransactionForm(obj=transaction)
    set_category_choices(form)
    if form.validate_on_submit():
        category = db.session.get(Category, form.category_id.data)
        if not category or category.transaction_type != form.transaction_type.data or (category.user_id and category.user_id != current_user.id): abort(403)
        for field in ("transaction_type", "title", "amount", "category_id", "transaction_date", "payment_method", "description"):
            setattr(transaction, field, getattr(form, field).data)
        transaction.title = transaction.title.strip()
        transaction.description = (transaction.description or "").strip()
        db.session.commit()
        flash("Transaction updated.", "success")
        return redirect(url_for("transactions.list_transactions"))
    return render_template("transactions/edit.html", form=form, transaction=transaction)


@transactions_bp.post("/<int:transaction_id>/delete")
@login_required
def delete_transaction(transaction_id):
    form = DeleteForm()
    transaction = Transaction.query.filter_by(id=transaction_id, user_id=current_user.id).first_or_404()
    if form.validate_on_submit():
        db.session.delete(transaction); db.session.commit(); flash("Transaction deleted.", "info")
    return redirect(url_for("transactions.list_transactions"))
