#!/usr/bin/env python3
from flask import Flask, request, Response
from flask.ext.cors import CORS
import chardet, email.utils, json, os, re, subprocess

app = Flask(__name__)
CORS(app)

email_dir = '/home/user/mail'


def show(path):
    ret = {}
    with open(path, 'rb') as fp:
        buf = fp.read()
        detect = chardet.detect(buf)
        message = email.message_from_string(buf.decode(detect['encoding']))
        for part in message.walk():
            if part.get_content_type() == 'text/plain':
                for k, v in message.items():
                    k = k.lower()
                    if k == 'date':
                        ret['date'] = email.utils.mktime_tz(email.utils.parsedate_tz(v))
                    elif k in ['from', 'to']:
                        name, address = email.utils.parseaddr(v)
                        ret[k] = name or address
                    elif k == 'subject':
                        ret['subject'] = v
                ret['body'] = part.get_payload(decode=True).decode(part.get_content_charset() or 'utf-8', 'ignore')
                return ret


@app.route('/api/query')
def api_query():
    args = request.args
    try:
        argv = ['notmuch', 'search', '--output=files']
        for i in ['offset', 'limit']:
            if i in args:
                argv.append('--{}={}'.format(i, args[i]))
            elif i == 'limit':
                argv.append('--{}=10'.format(i))
        argv.append('--')
        for i in ['from', 'to', 'subject', 'id', 'attachment', 'mimetype', 'thread', 'date']:
            if i in args:
                argv.append(i+':'+args[i])
        argv.append(args.get('term', '*') or '*')
        output = subprocess.check_output(argv).decode()
        ret = []
        for filename in output.split('\n'):
            if len(filename):
                item = show(filename)
                if item:
                    ret.append(item)
        return Response(json.dumps(ret), mimetype='application/json')
        #return '\n'.join(re.sub('.*/', '', filename) for filename in output.split('\n'))
    except subprocess.CalledProcessError:
        raise


@app.route('/api/email/<id>')
def api_email_show(id):
    return Response(json.dumps(show(os.path.join(email_dir, 'cur', id))),
                    mimetype='application/json')


if __name__ == '__main__':
    app.run(debug=True)
