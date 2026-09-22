from datetime import date
from flask_wtf import FlaskForm
from wtforms import DateField, DecimalField, SelectField, StringField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, Length, NumberRange, Optional


class TransactionForm(FlaskForm):
    transaction_type = SelectField("Type", choices=[("expense", "Expense"), ("income", "Income")], validators=[DataRequired()])
    title = StringField("Title", validators=[DataRequired(), Length(max=120)])
    amount = DecimalField("Amount", places=2, validators=[DataRequired(), NumberRange(min=0.01, max=999999999)])
    category_id = SelectField("Category", coerce=int, validators=[DataRequired()])
    transaction_date = DateField("Date", default=date.today, validators=[DataRequired()])
    payment_method = SelectField("Payment method", choices=[("", "Select method"), ("Cash", "Cash"), ("UPI", "UPI"), ("Credit card", "Credit card"), ("Debit card", "Debit card"), ("Bank transfer", "Bank transfer"), ("Other", "Other")], validators=[Optional()])
    description = TextAreaField("Notes", validators=[Optional(), Length(max=1000)])
    submit = SubmitField("Save transaction")


class DeleteForm(FlaskForm):
    submit = SubmitField("Delete")
