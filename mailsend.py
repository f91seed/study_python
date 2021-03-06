import smtplib
from email.mime.text import MIMEText
from email.utils import formatdate
import configparser

# コンフィグファイルのロード
inifile = configparser.ConfigParser()
inifile.read('./config.ini')

def create_message(from_addr, to_addr, subject, body):
    msg = MIMEText(body)
    msg['Subject'] = subject
    msg['From'] = from_addr
    msg['To'] = to_addr
    msg['Date'] = formatdate()
    return msg

def send(from_addr, to_addr, msg):
    # localhost 25
    s = smtplib.SMTP()
    s.connect()
    s.sendmail(from_addr, to_addr, msg.as_string())
    print('mail send OK')
    print(msg)
    s.close()

if __name__ == '__main__':
    # メイン処理(メール送るときに内部処理としてこれを書く)
    from_addr = inifile.get('mail', 'from_addr')
    to_addr = inifile.get('mail', 'to_addr')
    msg = create_message(from_addr, to_addr, 'test subject', 'test body')
    send(from_addr, to_addr, msg)