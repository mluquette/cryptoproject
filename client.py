#!/usr/bin/python3

from urllib.parse import urlencode
from urllib.request import Request, urlopen
import json
from tkinter import *
from paillier.paillier import *
import rsa
from fractions import gcd

ZKP_ITERATIONS = 9


'''

voting process:
1) receive list of candidates from server
2) cast vote with voter ID
3) blind sign and send to server for counting
4) verify with ZKP


'''

server_url = "http://127.0.0.1:5000/"

#def message_server(url,data={}):
#    post_data = urlencode(data)
#    req = Request(server_url + url, post_data.encode())
#    data = urlopen(req).read().decode()
#    return data

def message_server(url,data={}):
    req = Request(server_url + url)
    req.add_header('Content-Type', 'application/json; charset=utf-8')
    jsondata = json.dumps(data).encode()
    req.add_header('Content-Length', len(jsondata))
    response = urlopen(req, jsondata).read().decode()
    return response

root = Tk()
root.geometry('{}x{}'.format(300,300))
root.wm_title("Secure Voting Client")

voter_id = None

def check_registration():
    separator = Frame(height=2, bd=1, relief=SUNKEN)
    separator.pack(fill=X, padx=5, pady=5)
    Label(separator, text="Voter ID: ").grid(row=1, column=0, sticky=W)
    e = Entry(separator)
    e.grid(row=1, column=1, sticky=W)
    def callback():
        global voter_id
        voter_id = e.get()
        x = json.loads(message_server("check_registration", {"voter_id":voter_id}))
        if x:
            separator.pack_forget()
            candidates = json.loads(message_server("get_candidates"))
            present_choices(candidates)
        else:
            Label(separator, text="Invalid voter ID.", fg="red").grid(row=2, column=1, sticky=W)
    Button(separator, text='Submit', command=callback).grid(row=2, sticky=W)


def send_vote(candidates, vote, separator): 

    pub = PublicKey.from_n(int(message_server("get_public_key")))

    #convert the vote to one-hot
    m = [0]*len(candidates)
    m[vote] = 1

    #encrypt the votes
    e_v = []
    xs = []

    for mx in m:
        a,b = encrypt(pub, mx)
        e_v.append(a)
        xs.append(b)
    
    #get blind signature on encrypted vote
    signature = blind_sign(e_v)

    #send encrypted votes to server
    data = {"ballot":e_v, "voter_id":voter_id, "signature":signature}
    ret = message_server("vote",data)
    Label(separator, text=ret, fg="red").grid(row=2, column=1, sticky=W)

    for i in range(ZKP_ITERATIONS):
        r = []
        u = []
        ss = []
        for i in range(len(candidates)):
            r.append(rsa.randnum.randint(pub.n))
            a,b = encrypt(pub, r[i])
            u.append(a)
            ss.append(b)

        data = {"u":[str(x) for x in u], "voter_id":voter_id}
            
        es = json.loads(message_server("zkp_witness",data))

        #create v,w for every e

        v = []
        w = []

        for i,e in enumerate(es):
            v.append((r[i] - e * m[i]) % pub.n_sq)
            w.append((ss[i] * invmod(xs[i]**e,pub.n_sq)) % pub.n_sq)
 
        data = {"v":v,"w":w,"voter_id":voter_id}

        message_server("zkp_check",data)


def display_results():
    separator = Frame(height=2, bd=1, relief=SUNKEN)
    separator.pack(fill=X, padx=5, pady=5)


    
    
    l = Label(separator, text="")
    l.grid(row=1, column=0, sticky=W)

    def refresh():
        res = message_server("display_results")
        print(res)
        l.config(text = res)

    def xuit():
        separator.pack_forget()
        check_registration()

    refresh()
    
    Button(separator, text='reload', command=refresh).grid(row=2, sticky=W)
    Button(separator, text='quit', command=xuit).grid(row=2, sticky=E)
    
    
def present_choices(candidates):
    separator = Frame(height=2, bd=1, relief=SUNKEN)
    separator.pack(fill=X, padx=5, pady=5)

    Label(separator, text="Select a candidate").grid(row=0, column=0, sticky=W)
    
    v = IntVar()

    def onclick():
        send_vote(candidates, v.get(), separator)
        separator.pack_forget()
        #check_registration()
        display_results()

    for i,c in enumerate(candidates):
        Radiobutton(separator, text=c, variable=v, value=i).grid(row=i+1, sticky=W)

    Button(separator, text='Submit', command=onclick).grid(row=4, sticky=W, pady=4)

#blind sign the vote with RSA

def blind_sign(vote):

    data = json.loads(message_server("get_public_rsa_key"))

    e = int(data["e"])
    n = int(data["n"])

    #get random mask r that is coprime to n
    while True:
        r = rsa.randnum.randint(n)
        if gcd(r,n) == 1:
            break

    #mask the vote
    ctxt = [str(v*modpow(r,e,n)) for v in vote]

    #divide by r in mod n
    raw_signature = json.loads(message_server("get_blind_signature",ctxt))
    signature = [(int(k) * invmod(r,n)) % n for k in raw_signature]
    return signature



    
    

check_registration()
mainloop()
