from datetime import date
from app.extensions import db
from app.models import Category, Transaction, User


def register(client, username="alex", email="alex@example.com"):
    return client.post("/auth/register", data={"name":"Alex Kumar", "username":username, "email":email, "password":"safe-password-1", "confirm_password":"safe-password-1"}, follow_redirects=True)


def login(client, username="alex"):
    return client.post("/auth/login", data={"username":username, "password":"safe-password-1"}, follow_redirects=True)


def test_registration_hashes_password_and_login_logout(client, app):
    response = register(client)
    assert response.status_code == 200
    with app.app_context():
        user = User.query.filter_by(username="alex").one()
        assert user.password_hash != "safe-password-1"
        assert user.check_password("safe-password-1")
    assert client.post("/auth/logout", follow_redirects=True).status_code == 200
    assert login(client).status_code == 200


def test_private_dashboard_requires_login(client):
    assert client.get("/dashboard").status_code == 302
    assert client.get("/transactions/").status_code == 302


def test_transaction_crud_and_dashboard_totals(client, app):
    register(client)
    with app.app_context():
        salary = Category.query.filter_by(name="Salary", transaction_type="income").first()
        food = Category.query.filter_by(name="Food", transaction_type="expense").first()
        salary_id, food_id = salary.id, food.id
    for kind, category_id, title, amount in [("income", salary_id, "Salary", "50000"), ("expense", food_id, "Groceries", "1250.50")]:
        response = client.post("/transactions/", data={"transaction_type":kind,"title":title,"amount":amount,"category_id":category_id,"transaction_date":date.today().isoformat(),"payment_method":"UPI","description":""}, follow_redirects=True)
        assert response.status_code == 200
    summary = client.get("/api/dashboard/summary").get_json()["data"]
    assert summary == {"income": 50000.0, "expenses": 1250.5, "balance": 48749.5}
    with app.app_context(): tx_id = Transaction.query.filter_by(title="Groceries").one().id
    assert client.post(f"/transactions/{tx_id}/delete", data={}, follow_redirects=True).status_code == 200
    with app.app_context(): assert Transaction.query.filter_by(id=tx_id).first() is None


def test_user_cannot_access_another_users_transaction(client, app):
    register(client, "one", "one@example.com")
    with app.app_context():
        food = Category.query.filter_by(name="Food", transaction_type="expense").first()
        user = User.query.filter_by(username="one").one()
        tx = Transaction(user_id=user.id, category_id=food.id, transaction_type="expense", title="Private", amount=10, transaction_date=date.today())
        db.session.add(tx); db.session.commit(); tx_id = tx.id
    client.post("/auth/logout")
    register(client, "two", "two@example.com")
    assert client.get(f"/transactions/{tx_id}/edit").status_code == 404
    assert client.post(f"/transactions/{tx_id}/delete", data={}).status_code == 404
