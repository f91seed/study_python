import smtplib
from email.mime.text import MIMEText
from email.utils import formatdate
import configparser

class sendGmail:
    username, password = 'sample@yahoo.co.jp', 'XXXXX'

    def __init__(self, to, sub, body):
        host, port = 'smtp.mail.yahoo.co.jp', 465
        msg = MIMEText(body)
        msg['Subject'] = sub
        msg['From'] = self.username
        msg['To'] = to
        msg['Date'] = formatdate()
        # コンフリクト検証

        smtp = smtplib.SMTP_SSL(host, port)
        smtp.ehlo()
        smtp.login(self.username, self.password)
        smtp.mail(self.username)
        smtp.rcpt(to)
        smtp.data(msg.as_string())
        smtp.quit()

if __name__ == '__main__':
    to = 'example@gmail.com'
    sub = 'Python smtplib'
    body = 'Hello, Python'
    sendGmail(to, sub, body)
