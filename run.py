from backend import app as Node_app

Node_app.run(
    '0.0.0.0',
    debug=True,
    port=5000,
    use_debugger = True,
    use_reloader = True,
    threaded = True
)