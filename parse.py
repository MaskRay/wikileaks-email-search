#!/usr/bin/env python3
import chardet, email, os

mail_dir = '/home/user/mail/cur'
text_dir = '/home/user/text'

os.makedirs(text_dir, exist_ok=True)

for filename in os.listdir(mail_dir):
    path = os.path.join(mail_dir, filename)
    if os.path.isfile(path):
        try:
            with open(path, 'rb') as fp:
                buf = fp.read()
                detect = chardet.detect(buf)
                message = email.message_from_string(buf.decode(detect['encoding']))
                #headers = message.items()
                #from_ = headers['From']
                #to_ = headers['To']
                for part in message.walk():
                    if part.get_content_type() == 'text/plain':
                        with open(os.path.join(text_dir, filename), 'w') as fp2:
                            t = part.get_payload(decode=True).decode(part.get_content_charset() or 'utf-8', 'ignore')
                            lines = t.split('\r\n')
                            while len(lines) and (len(lines[-1]) == 0 or lines[-1].startswith('>')):
                                lines.pop()
                            fp2.write('\n'.join(lines))
                        break
                print(filename)
        except Exception as e:
            print(filename, e)
