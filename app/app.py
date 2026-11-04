from flask import Flask, jsonify, render_template
import logging

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)

products = [
    {"id": 1, "name": "Laptop", "price": 55000, "status": "In Stock"},
    {"id": 2, "name": "Headphones", "price": 2500, "status": "In Stock"},
    {"id": 3, "name": "Mobile", "price": 30000, "status": "In Stock"}
]

@app.route("/")
def home():
    app.logger.info("Home page accessed")
    return jsonify({
        "message": "Welcome to CloudCart!",
        "status": "Running",
        "application": "Cloud-Native E-Commerce Deployment",
        "products": products
    })

@app.route("/health")
def health():
    return jsonify({
        "status": "healthy",
        "application": "E-Commerce Cloud App"
    }), 200

@app.route("/api/products")
def get_products():
    app.logger.info("Products API accessed")
    return jsonify(products)

@app.route("/test-error")
def test_error():
    app.logger.error("Test error generated for CloudWatch / Prometheus alerting")
    return jsonify({"error": "Test error simulated for monitoring verification"}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
