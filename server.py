from flask import Flask, request
import json
from database import db_session
from models import Voter, Candidate, Vote
from paillier.paillier import *

app = Flask(__name__)

priv = None
pub = None

@app.teardown_appcontext
def shutdown_session(exception=None):
    db_session.remove()

@app.route("/check_registration", methods=["POST"])
def check_registration():
    voter = Voter.query.filter_by(voter_id=int(request.form["voter_id"])).first()
    if voter != None:
        return "true"
    else:
        return "false"

@app.route("/get_public_key", methods=["POST"])
def get_public_key():
    return str(pub.n)

@app.route("/get_candidates", methods=["GET", "POST"])
def get_candidates():
    return json.dumps([c.name for c in Candidate.query.all()])

@app.route("/vote", methods=["POST"])
def vote():
    print(request.form)
    voter = Voter.query.filter_by(voter_id=int(request.form["voter_id"])).first()
    if voter == None:
        return "Invalid Voter ID"
    vote = Vote.query.filter_by(voter=int(request.form["voter_id"])).first()
    print(vote, voter)
    if vote == None:
        v = Vote()
        v.voter = voter.voter_id
        for i in range(len(Candidate.query.all())):
            try:
                k = "vote%d"%i
                setattr(v, k, request.form[k])
            except AttributeError:
                return "Invalid vote format"
        db_session.add(v)
        db_session.commit()
        return "Vote successful"
    else:
        return "Voter %s already voted"%voter.voter_id


@app.route("/display_results", methods=["GET", "POST"])
def tally_votes():
    #get all votes
    all_votes = Vote.query.all()
    total_votes = len(all_votes)
    candidates = [c.name for c in Candidate.query.all()]
    candidate_votes = {i:[] for i in range(len(candidates))}

    for v in all_votes:
        for i in range(len(candidates)):
            candidate_votes[i].append(int(getattr(v,"vote%d"%i)))

    candidate_totals = {}
    
    for i in range(len(candidates)):
        total = None
        for v in candidate_votes[i]:
            if total == None:
                total = v
            else:
                total = e_add(pub, total, v)
        print(total)
        print(type(total))
        candidate_totals[i] = decrypt(priv, pub, total)

    ret = "Candidate\tVotes\tPercent\n"
    for i,candidate in enumerate(candidates):
        ret += "{0}:\t{1}\t{2}\n".format(candidate, candidate_totals[i], "%.2f%%"%(candidate_totals[i]/total_votes*100))

    return ret

if __name__ == "__main__":
    from database import init_db
    init_db()
    #generate paillier keys
    priv, pub = generate_keypair(512)
    app.run()
