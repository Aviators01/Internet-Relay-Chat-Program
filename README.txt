Timothy Queva
CS3130 Lab3
March 10, 2021

Description: This program is a IRC program or an internet relay chat program. Necessary functions required for
both server and client operation are included within the same file.

Limitations:
1. Only works over the local area network due to NAT (Network Address Translation) preventing
communication beyond a subnet.
2. If user closes client via other means except by typing "exit", any messages sent to the user
are not stored in the mailbox.

Security issues:
1. communication is unencrypted.
2. If username is known, third party can sign in under that username.
3. If username is known, third party can sign in under that username even if said username was already signed in.
   Technically, this would result in the third party being able to hijack the conversation and pretend to be the
   the username that was already signed in.

Instructions:
	1. Navigate to the correct folder:
	2. Start the server by typing: python3 cs_chat.py server 127.0.0.1
	3. (In a different window) start client by typing: python3 cs_chat.py client 127.0.0.1
	4. For help in how to use client once program is running, type: help

Additional tips:
-for help in typing arguments with which to start program, type: python3 cs_chat.py -h
-127.0.0.1 is just the loopback address. It can be replaced with any valid-according-to-subnet-rules ip address
-to stop the server, press ctrl + c