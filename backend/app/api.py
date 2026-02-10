from flask import Flask, jsonify
import os

app = Flask(__name__)

@app.route("/")
def home():
    return jsonify({
        "status": "Backend is running",
        "message": "Render deployment successful"
    })

@app.route("/health")
def health():
    return jsonify({"health": "OK"})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
