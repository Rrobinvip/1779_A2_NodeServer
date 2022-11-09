from backend import app as Node_app

Node_app.run(
    '0.0.0.0',
    debug=True,
    port=5000
)