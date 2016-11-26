#!/usr/bin/python3

from urllib.parse import urlencode
from urllib.request import Request, urlopen
import json
from tkinter import *
from paillier.paillier import *

'''

voting process:
1) receive list of candidates from server
2) cast vote with voter ID
3) blind sign and send to server for counting
4) verify with ZKP


'''

server_url = "http://127.0.0.1:5000/"

def message_server(url,data={}):
    post_data = urlencode(data)
    req = Request(server_url + url, post_data.encode())
    data = urlopen(req).read().decode()
    return data



root = Tk()
root.geometry('{}x{}'.format(300,300))

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


def send_vote(candidates, vote):

    pub = PublicKey.from_n(int(message_server("get_public_key")))

    #convert the vote to one-hot
    v = [0]*len(candidates)
    v[vote] = 1

    #encrypt the votes
    e_v = [encrypt(pub, vx) for vx in v]

    #send encrypted votes to server
    data = {"vote%d"%i:x for i,x in enumerate(e_v)}
    data["voter_id"] = voter_id
    message_server("vote",data)
    
def present_choices(candidates):
    separator = Frame(height=2, bd=1, relief=SUNKEN)
    separator.pack(fill=X, padx=5, pady=5)

    Label(separator, text="Select a candidate").grid(row=0, column=0, sticky=W)
    
    v = IntVar()

    def onclick():
        send_vote(candidates, v.get())

    for i,c in enumerate(candidates):
        Radiobutton(separator, text=c, variable=v, value=i).grid(row=i+1, sticky=W)

    Button(separator, text='Submit', command=onclick).grid(row=4, sticky=W, pady=4)



    
    

check_registration()
mainloop()
