from use_bd import *
from email.message import EmailMessage
import smtplib

nm = os.environ['EMAIL']
pwd = os.environ['EMAIL_KEY']

def send_mail(to,text,title = ""):
    server = smtplib.SMTP("smtp.gmail.com", 587)
    server.ehlo()
    server.starttls()
    server.login(nm, pwd)
    for t in to:
        em = EmailMessage()
        em.set_content(text)
        em["To"] = t
        em["From"] = nm
        em["Subject"] = title
       # print(t,nm,text)
        server.send_message(em)
    server.quit()
