import configparser

config = configparser.ConfigParser()
config.read("test.ini")

# Import smtplib for the actual sending function
import smtplib

# Import the email modules we'll need
from email.message import EmailMessage

textfile = "mail.txt"
me = "123@gmail.com"
you = "w.bochenski.05@proton.me"

# Open the plain text file whose name is in textfile for reading.
with open(textfile) as fp:
    # Create a text/plain message
    msg = EmailMessage()
    msg.set_content(fp.read())

# me == the sender's email address
# you == the recipient's email address
msg['Subject'] = f'The contents of {textfile}'
msg['From'] = me
msg['To'] = you

# Send the message via our own SMTP server.
with smtplib.SMTP("localhost", 1025) as server:
    server.send_message(msg)