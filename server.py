from flask import Flask, request
import json
from database import db_session
from models import Voter, Candidate, Vote
from paillier.paillier import *
import rsa

app = Flask(__name__)

#Paillier keys for voting
priv = None
pub = None

#RSA keys for blind signing
priv2 = None
pub2 = None

@app.teardown_appcontext
def shutdown_session(exception=None):
    db_session.remove()

@app.route("/check_registration", methods=["POST"])
def check_registration():
    voter = Voter.query.filter_by(voter_id=request.json["voter_id"]).first()
    if voter != None:
        return "true"
    else:
        return "false"

@app.route("/get_public_key", methods=["GET","POST"])
def get_public_key():
    return str(pub.n)

@app.route("/get_public_rsa_key", methods=["GET","POST"])
def get_public_rsa_key():
    return json.dumps({"e":str(pub2.e), "n":str(pub2.n)})

@app.route("/get_blind_signature", methods=["POST"])
def get_blind_signature():
    #blind sign the message (return m^d)
    return json.dumps([rsa.core.decrypt_int(int(x), priv2.d, priv2.n) for x in request.json])

@app.route("/get_candidates", methods=["GET", "POST"])
def get_candidates():
    return json.dumps([c.name for c in Candidate.query.all()])

@app.route("/vote", methods=["POST"])
def vote():
    #check if voter has valid voter id
    voter = Voter.query.filter_by(voter_id=request.json["voter_id"]).first()
    if voter == None:
        return "Invalid Voter ID"

    vote = Vote.query.filter_by(voter=request.json["voter_id"]).first()
    if vote == None:

        #check if ballot has correct number of votes
        ballot = request.json["ballot"]
        if len(ballot) != len(Candidate.query.all()):
            return "Invalid vote format1"

        #check blind signature
        #ensure signature matches message aka sig == m^e
        signature = request.json["signature"]
        for i,sig in enumerate(signature):

            a = rsa.core.encrypt_int(int(sig), pub2.e, pub2.n)

            print(a)
            print(ballot[i] % pub2.n)
            
            if a != (ballot[i] % pub2.n):
                return "Invalid vote format2"
            
        

        #malleability check: need to verify without decrypting
        #to preserve privacy. use ZKP

        '''

        ZKP GOES HERE

        '''

        #if all checks pass, process the vote

        vo = Vote() #make new vote entry
        vo.voter = voter.voter_id #set entry to voter id
        for i,v in enumerate(ballot): #assign vote values to vote entry 
            try:
                setattr(vo, "vote%d"%i, str(v))
            except AttributeError:
                return "Invalid vote format3"
        db_session.add(vo)
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
        candidate_totals[i] = decrypt(priv, pub, total)

    ret = "Candidate\tVotes\tPercent\n"
    for i,candidate in enumerate(candidates):
        ret += "{0}:\t{1}\t{2}\n".format(candidate, candidate_totals[i], "%.2f%%"%(candidate_totals[i]/total_votes*100))

    return ret

if __name__ == "__main__":
    from database import init_db
    init_db()
    #generate paillier keys
    priv, pub = generate_keypair(128)
    pub2, priv2 = rsa.newkeys(128, poolsize=2)
    app.run()
