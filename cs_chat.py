"""
Timothy Queva
CS3130 Lab3
Feb. 10, 2021

This program simulates a chat client-server program using UDP
"""

import argparse, socket, sys, select

def read():
    rfds,wfds,efds = select.select([sys.stdin],[],[],5)
    if rfds:
        return sys.stdin.readline()
    else:
        return ""

#sends help information to requester
def send_help(sock,address):
    reply = ("Available commands:\n" +
             "help    --displays help information\n" +
             "signin  --allows user to signon (eg. signin Franco)\n" +
             "send    --send a message to a user (eg. send Franco hi)\n" +
             "whoison --checks who is currently signed in.\n" +
             "signoff --signs user off chat service\n" +
             "exit    --closes client program.\n")
    reply = reply.encode('utf-8')
    sock.sendto(reply,address)

#signs user in
def signin(msg,sock,address,mailbox,on_users,userlist):
    msg = msg.split()
    #try-except block ensures username was provided
    try:
        sender = str(msg[1]).strip()
        
        #prevents multi-user signin's from same client
        for user in on_users:
            if address == on_users[user]:
                reply = ("Sorry! User " + str(user) + " is already signed " +
                         "in from this client. Please open a new client in " +
                         "order to sign in.")
                sock.sendto(reply.encode('utf-8'),address)
                return
        
        #checks sender against valid users
        if sender in userlist:
            #records sender who just signed in
            on_users[sender]=address
            
            #Sends contents of mailbox to sender who just signed in
            if(len(mailbox[sender]) == 1):
                reply = ("Welcome " + str(sender) + "! There is " +
                         str(len(mailbox[sender])) + " message for you:")
            else:
                reply = ("Welcome " + str(sender) + "! There are " +
                         str(len(mailbox[sender])) + " messages for you:")
            sock.sendto(reply.encode('utf-8'),address)
            for message in mailbox[sender]:
                sock.sendto(message.encode('utf-8'),address)
                
            #delete messages in mailbox
            mailbox[sender] = []
        else:
            reply = ("Username " + str(user) + " is not recognized. Please " +
                     "note that username is case-sensitive.")
            sock.sendto(reply.encode('utf-8'),address)
    except IndexError:
        reply = ("Sorry! The signon command must be accompanied by a " +
                 "username. Please provide a valid username.")
        sock.sendto(reply.encode('utf-8'),address)

#sends messages to specified recipient
def send(msg,sock,address,mailbox,on_users,userlist):
    msg=msg.strip().split()
    #try-except block ensures recipient and message was provided
    recipient = ""
    try:
        recipient = str(msg[1])
        msg[2]
    except IndexError:
        reply = ("Sorry. Please specify a recipient and message alongside " +
                 "the send command")
        sock.sendto(reply.encode('utf-8'),address)
        return
    
    #processes split list into string message
    sender = ""
    for user in on_users:
        if address == on_users[user]:
            sender=user
    msg = str(sender) + " says: " + " ".join(msg[2:])
    
    #checks recipient against list of valid users
    if recipient in userlist:
        #Sends msg to recipient if online or their mailbox
        if recipient in on_users:
            raddress = on_users[recipient]
            try:
                sock.sendto(msg.encode('utf-8'),raddress)
            
                '''
                This exception handler below was intended to deal with the
                situation where a user terminated the client without signing
                off. However, this handler is never used. It is currently
                unknown why this is the case.
                
                The only way to deal with such a situation is to have the
                server periodically send "silent" messages to the client
                to see if the client is still reachable/running. If not, sign
                the user out. On the client side, there can be (not required)
                a way for the client remember its signed in state and
                accordingly sign the user back in if it was abruptly
                terminated.
                
                Additionally, in terms of the windows X to exit a window,
                There could be some code to sign the user out before
                terminating the program. However, this code would be useless
                in situations where the program abnormally terimated
                (eg. system exception, sigkill signal, etc.)
                '''
            except ConnectionRefusedError:
                reply = ("Huh! " + str(recipient) + " appears to have " +
                         "closed the client window without signing off.\n" +
                         "Your message will be stored in his mailbox for " +
                         "the next time he/she logs in.")
                sock.sendto(reply.encode('utf-8'),address)
                mailbox[recipient].append(msg)
                del on_users[recipient]
        else:
            reply = (str(recipient) + " is currently offline. Your msg " +
                     "will be stored in his mailbox for the next time " +
                     "he/she logs in.")
            sock.sendto(reply.encode('utf-8'),address)
            mailbox[recipient].append(msg)
    else:
        reply = ("Sorry. User " + str(recipient) + " could not be found. " +
                 "Please check to make sure he/she uses this chat service.\n"+
                 "Note: usernames are case-sensitive.")
        sock.sendto(reply.encode('utf-8'),address)

#signs user off
def signoff(sock,address,on_users):
    sender = ""
    for user in on_users:
        if address == on_users[user]:
            sender=user
    reply = ("User " + str(sender) + " successfully signed " +
             "out. Byeee!!")
    del on_users[sender]             
    sock.sendto(reply.encode('utf-8'),address)

#checks server list to see who is signed in
def whoison(sock,on_users,address):
    if(len(on_users) < 2):
        reply = ("There is " + str(len(on_users)) + " user " +
                 "signed in:\n")
    else:
        reply = ("There are " + str(len(on_users)) + " users " +
                 "signed in:\n")
    
    for user in list(on_users.keys()):
        reply = reply + str(user) + "\n"
    
    #removes the last "\n" from "list" of users online
    reply = reply.strip()
    
    sock.sendto(reply.encode('utf-8'),address)


MAX_BYTES = 65535
def server(interface, port):
    #stores list of authorized chat users
    userlist = []
    with open("AuthorizedUsers.txt") as v_users:
        for name in v_users:
            userlist.append(name.strip())
    
    #setups the authorized user's mailboxes
    mailbox = {}
    for user in userlist:
        mailbox[user] = []
    
    #this dictionary hold the records of who is online
    on_users = {}
    
    #setups server interface
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((interface, port))
    print('Listening at', sock.getsockname())
    while True:
        data, address = sock.recvfrom(MAX_BYTES)
        msg = data.decode('utf-8')
        
        #displays help information
        if(msg[:4].lower()=="help"):
            send_help(sock,address)
            
        #signs user into IRC server
        elif(msg[:6].lower()=="signin"):
            signin(msg,sock,address,mailbox,on_users,userlist)
        
        #Only executes chat functions if user authenticated
        elif address in on_users.values():
            #sends messages to specified recipient
            if(msg[:4].lower()=="send"):
                send(msg,sock,address,mailbox,on_users,userlist)
            
            #signs user off
            elif(msg[:7].lower()=="signoff"):
                signoff(sock,address,on_users)
            
            #checks server list to see who is signed in
            elif(msg[:7].lower()=="whoison"):
                whoison(sock,on_users,address)
            else:
                reply = "Sorry. Please enter a valid command."
                sock.sendto(reply.encode('utf-8'),address)
        elif msg[:4].lower()!="help" or msg[:6].lower()=="signin":
            reply = "Sorry. Please enter a valid command."
            sock.sendto(reply.encode('utf-8'),address)
        else:
            reply = "Sorry. Please signin before using chat services."
            sock.sendto(reply.encode('utf-8'),address)
        

def client(hostname, port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.connect((hostname, port))
    #print('Client socket name is {}'.format(sock.getsockname()))
    
    print("Welcome to CS chat--an IRC program.")
    print()
    print("Important information:")
    print("1. Please note that if program advances to next line " +
          "while you are still typing,\n" +
          "   your whole message will still be sent.")
    print("2. Also, please signoff before closing or exiting program to " +
          "ensure that messages\n"
          "   to you are saved in your mailbox while you are offline.")
    
    while True:
        #This part handles sending to the server
        while True:
            print()
            sys.stdout.write("-->: ")
            sys.stdout.flush()
            data = read()   #non-blocking read
            
            #allows user to exit program without reliance on ctrl + c
            if data.lower() == "exit\n":
                sock.send("signoff".encode('utf-8'))
                print()
                print("Thank you for using CS chat. Goodbye!")
                exit()
            
            #sends msg to server if user hits ENTER key
            if data.find("\n") != -1:
                data = data.strip()
                data = data + "\r\n\r\n"
                data = data.encode('utf-8')
                sock.send(data)
                break
            
            #breaks loop to check if any message was received from server
            if data =="":
               break
        
        #receives messages from server     
        delay = 0.1  # seconds
        while True:
            sock.settimeout(delay)
            try:
                data = sock.recv(MAX_BYTES)
                data = data.decode('utf-8')
                #data.strip()
                print(str(data))
            except socket.timeout:
                delay *= 2  # wait even longer for the next request
                if delay > 1.0:
                    break
            except ConnectionRefusedError:
                print()
                print("Sorry, the command/message was refused.")
                print("There doesn't appear to be a server " +
                      "at that interface (" + str(hostname) +
                      ", " + str(port) + ").")
                exit()

if __name__ == '__main__':
    choices = {'client': client, 'server': server}
    parser = argparse.ArgumentParser(description='Computer Science chat'+
                                     'program')
    parser.add_argument('role', choices=choices, help='which role to take')
    parser.add_argument('host', help='interface the server listens at;'
                        ' host the client sends to')
    parser.add_argument('-p', metavar='PORT', type=int, default=1123,
                        help='UDP port (default 1123)')
    args = parser.parse_args()
    function = choices[args.role]
    function(args.host, args.p)