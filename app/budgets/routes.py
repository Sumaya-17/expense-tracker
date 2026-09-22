from datetime import date
from decimal import Decimal
from flask import Blueprint, flash, redirect, render_template, url_for
from flask_login import current_user, login_required
from sqlalchemy import func
from .forms import BudgetForm
from ..extensions import db
from ..models import Budget, Category, Transaction

budgets_bp = Blueprint("budgets", __name__)


def expense_categories():
    return Category.query.filter(Category.transaction_type == "expense", (Category.is_default.is_(True)) | (Category.user_id == current_user.id)).order_by(Category.name).all()


@budgets_bp.route("/", methods=["GET", "POST"])
@login_required
def list_budgets():
    form = BudgetForm()
    form.category_id.choices = [(c.id, c.name) for c in expense_categories()]
    if form.validate_on_submit():
        category = db.session.get(Category, form.category_id.data)
        if not category or category.transaction_type != "expense" or (category.user_id and category.user_id != current_user.id):
            flash("Please choose a valid expense category.", "danger")
        else:
            period = form.period_start.data.replace(day=1)
            budget = Budget.query.filter_by(user_id=current_user.id, category_id=category.id, period_start=period).first()
            if budget: budget.amount = form.amount.data
            else: db.session.add(Budget(user_id=current_user.id, category_id=category.id, amount=form.amount.data, period_start=period))
            db.session.commit(); flash("Budget saved.", "success")
            return redirect(url_for("budgets.list_budgets"))
    month = date.today().replace(day=1)
    next_month = date(month.year + (month.month == 12), (month.month % 12) + 1, 1)
    budgets = Budget.query.filter_by(user_id=current_user.id, period_start=month).all()
    cards = []
    for budget in budgets:
        spent = db.session.query(func.coalesce(func.sum(Transaction.amount), 0)).filter_by(user_id=current_user.id, category_id=budget.category_id, transaction_type="expense").filter(Transaction.transaction_date >= month, Transaction.transaction_date < next_month).scalar()
        percent = float((spent / budget.amount * 100) if budget.amount else 0)
        cards.append({"budget": budget, "spent": spent, "remaining": budget.amount-spent, "percent": percent})
    return render_template("budgets/list.html", form=form, cards=cards)
