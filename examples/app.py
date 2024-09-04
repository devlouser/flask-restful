from flask import Flask, jsonify, request
from flask_mysqldb import MySQL
from calculations import calculate_discount  # Importing from calculations.py
from db import get_users  # Importing from db.py

app = Flask(__name__)
mysql = None


def init_app(app, test_config=None):
    global mysql
    if test_config:
        app.config.update(test_config)
    else:
        # Load your production config
        pass
    try:
        mysql = MySQL(app)
    except Exception as e:
        raise Exception("Database connection failed") from e


@app.route("/")
def users():
    users_data = get_users(mysql)  # Using function from db.py
    return str(users_data)


@app.route("/")
def products():
    products = get_products(mysql)  # Using function from db.py
    return str(products)


@app.route("/discount")
def discount():
    price = request.args.get("price", type=float)
    discount_percentage = request.args.get("discount", type=float)

    if price is None or discount_percentage is None:
        return jsonify({"error": "Missing price or discount parameter"}), 400

    try:
        discounted_price = calculate_discount(price, discount_percentage)
        return jsonify({"original_price": price, "discounted_price": discounted_price})
    except ValueError as e:
        return jsonify({"error": str(e)}), 400


if __name__ == "__main__":
    init_app(app)  # Initialize MySQL only when running the actual app
    app.run(debug=True)
