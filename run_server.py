# Create a file called run_server.py
from app import app

if __name__ == "__main__":
    print("Starting server on http://127.0.0.1:5000")
    print("Your AI Resume Analyzer is now running with all security features!")
    app.run(host='127.0.0.1', port=5000, debug=False)