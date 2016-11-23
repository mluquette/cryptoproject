from flask import Flask, request
import json
app = Flask(__name__)


registered_voter_ids = ["1521","4333","6667"]

candidates = ["Alice","Bob","Carol"]

@app.route("/check_registration", methods=["POST"])
def check_registration():
    if request.form["id"] in registered_voter_ids:
        return "true"
    else:
        return "false"


@app.route("/get_candidates", methods=["POST"])
def get_candidates():
    return json.dumps(candidates)

if __name__ == "__main__":
    app.run()
