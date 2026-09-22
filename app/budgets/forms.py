from datetime import date
from flask_wtf import FlaskForm
from wtforms import DateField, DecimalField, SelectField, SubmitField
from wtforms.validators import DataRequired, NumberRange


class BudgetForm(FlaskForm):
    category_id = SelectField("Expense category", coerce=int, validators=[DataRequired()])
    amount = DecimalField("Monthly budget", places=2, validators=[DataRequired(), NumberRange(min=0.01)])
    period_start = DateField("Budget month", default=lambda: date.today().replace(day=1), validators=[DataRequired()])
    submit = SubmitField("Save budget")
