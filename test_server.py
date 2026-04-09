from flask import Flask
import os

app = Flask(__name__)

@app.route('/')
def hello():
    return "AI Resume Analyzer is running!"

if __name__ == "__main__":
    port = int(os.getenv('PORT', 5000))
    print(f"Starting server on http://127.0.0.1:{port}")
    app.run(host='127.0.0.1', port=port, debug=False)