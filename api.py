#!/usr/bin/env python3
from flask import Flask, request
import chardet, email, os, re, subprocess

app = Flask(__name__)
email_dir = '/home/user/mail'


def extract_text(path):
    with open(path, 'rb') as fp:
        buf = fp.read()
        detect = chardet.detect(buf)
        message = email.message_from_string(buf.decode(detect['encoding']))
        for part in message.walk():
            if part.get_content_type() == 'text/plain':
                return part.get_payload(decode=True).decode(part.get_content_charset() or 'utf-8', 'ignore')
        return ''


@app.route('/api/query')
def api_query():
    args = request.args
    try:
        argv = ['notmuch', 'search', '--output=files', '--']
        for i in ['from', 'to', 'subject', 'id', 'attachment', 'mimetype', 'thread', 'date']:
            if i in args:
                argv.append(i+':'+args[i])
        if 'term' in args:
            argv.append(args['term'])
        output = subprocess.check_output(argv).decode()
        return '\n'.join(re.sub('.*/', '', filename) for filename in output.split('\n'))
    except subprocess.CalledProcessError:
        raise


@app.route('/api/email/<id>')
def api_email_show(id):
    return extract_text(os.path.join(email_dir, 'cur', id))


if __name__ == '__main__':
    app.run(debug=True)
