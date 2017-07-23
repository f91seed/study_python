import smtplib
from email.mime.text import MIMEText

class sendGmail:
    username, password = 'f91seed@gmail.com', 'XXXXX'

    def __init__(self, to, sub, body):
        host, port = 'smtp.gmail.com', 465
        msg = MIMEText(body)
        msg['Subject'] = sub
        msg['From'] = self.username
        msg['To'] = to

        smtp = smtplib.SMTP_SSL(host, port)
        smtp.ehlo()
        smtp.login(self.username, self.password)
        smtp.mail(self.username)
        smtp.rcpt(to)
        smtp.data(msg.as_string())
        smtp.quit()

if __name__ == '__main__':
    to = 'f91seed@yahoo.co.jp'
    sub = 'Python smtplib'
    body = 'Hello, Python'
    sendGmail(to, sub, body)