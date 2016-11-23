#!/usr/bin/python3

from urllib.parse import urlencode
from urllib.request import Request, urlopen
import json
from tkinter import *

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

def check_registration():
    separator = Frame(height=2, bd=1, relief=SUNKEN)
    separator.pack(fill=X, padx=5, pady=5)
    Label(separator, text="Voter ID: ").grid(row=1, column=0, sticky=W)
    e = Entry(separator)
    e.grid(row=1, column=1, sticky=W)
    def callback():
        x = json.loads(message_server("check_registration", {"id":e.get()}))
        if x:
            separator.pack_forget()
            candidates = json.loads(message_server("get_candidates"))
            present_choices(candidates)
        else:
            Label(separator, text="Invalid voter ID.", fg="red").grid(row=2, column=1, sticky=W)
    Button(separator, text='Submit', command=callback).grid(row=2, sticky=W)

def present_choices(candidates):
    separator = Frame(height=2, bd=1, relief=SUNKEN)
    separator.pack(fill=X, padx=5, pady=5)

    Label(separator, text="Select a candidate").grid(row=0, column=0, sticky=W)
    
    v = IntVar()

    for i,c in enumerate(candidates):
        Radiobutton(separator, text=c, variable=v, value=i).grid(row=i+1, sticky=W)

    def var_states():
       print(v.get())

    Button(separator, text='Submit', command=var_states).grid(row=4, sticky=W, pady=4)

check_registration()
mainloop()
