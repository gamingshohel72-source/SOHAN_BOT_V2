from flask import Flask

app = Flask(__name__)

@app.route("/")
def home():
    return "GH PRIME STORE BOT is running!"

def run():
    app.run(host="0.0.0.0", port=8080)
