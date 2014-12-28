#!/usr/bin/env python2.7

import os
import random
import re
import sys
import time
import traceback

from bottle import route, run, template, static_file, abort, Bottle, request, redirect

clients = {}
current_message = ""

#####################################################################
#
# Bottle Routing
#
#####################################################################
app = Bottle()

@app.route('/')
@app.route('/create')
def main():
    # generate uniq id, then redirect to that page
    uid = '%030x' % random.randrange(16**30)
    while uid in clients.keys():
        uid = '%030x' % random.randrange(16**30)
    return redirect("/roller/%s" % uid)

@app.route('/static/<path:path>')
def static(path):
    return static_file(path, root="./static")

@app.route('/roller/<uid>')
def roller(uid):
    return template("dorolls")


@app.route('/viewer/<uid>')
def roller(uid):
    return template("viewrolls")


@app.route('/test/roll/<msg>')
def testroll(msg):
    return parse_roll(msg)

@app.route('/ws/roller/<uid>')
@app.route('/ws/viewer/<uid>')
def ws(uid):
    """
    websocket code
    """
    print >>sys.stderr, "websocket called"
    wsock = request.environ.get('wsgi.websocket')
    if not wsock:
        print >>sys.stderr, "no websock environ"
        print >>sys.stderr, request.environ
        abort(400, 'Expected WebSocket request.')

    if uid not in clients.keys():
        clients[uid] = []
    clients[uid].append(wsock)

    while True:
        try:
            print >>sys.stderr, "waiting for msg"
            message = wsock.receive()
            print >>sys.stderr, "msg received"
            if message != None:
                handle_ws(uid, message, wsock)
            else:
                clients[uid].remove(wsock)
                if len(clients[uid]) == 0:
                    del(clients[uid])
        except WebSocketError:
            clients[uid].remove(wsock)
            if len(clients[uid]) == 0:
                del(clients[uid])
            break
    print >>sys.stderr, "websock destroyed"

    
#####################################################################
#
# Bottle helpers
#
#####################################################################

def handle_ws(uid, message, ws):
    """
    fall through opcodes do do work
    """
    global current_message

    if "," in message:
        op, message = message.split(",", 1)
        op = int(op)
    elif message.strip().isdigit():
        op = int(message)
        message = ""
    else:
        print >> sys.stderr,"WTF is '%s'" % str(message)

    if op == 0:
        pass
    elif op == 1:
        retmsg = parse_roll(message)
        retmsg = "1,%s" % str(retmsg)
        send_to_all_ws(uid, retmsg)
        

def send_to_all_ws(uid, message):
    for s in clients[uid][:]:
        try:
            s.send(message)
            print "sent 1"
        except WebSocketError:
            traceback.print_exc()
            clients.remove(s)

def parse_roll(msg):
    dice = []

    try:
        if "," in msg:
            for msg_part in msg.split(","):
                dice.append(parse_dice_msg(msg_part))
        else:
            dice.append(parse_dice_msg(msg))
    except Exception:
        return None

    return perform_and_format_roll(msg, dice)


def perform_and_format_roll(msg, dice):
    results = []
    total = 0
    for rolls in dice:
        die = int(rolls['die'])
        midresult = []

        if rolls['modifier']:
            midresult.append("((")

        dierolls = []
        for i in xrange(int(rolls['quantity'])):
            dierolls.append(random.randint(1, die))
        total += sum(dierolls)
        dierolls = map(str, dierolls)
        midresult.append(" + ".join(dierolls))

        if rolls['modifier']:
            midresult.append(")")
            midresult.append(rolls['modifier'])
            midresult.append(")")
            total += int(rolls['modifier'])
        results.append(" ".join(midresult))

     
    return "%s: %s = %d" % (msg, " + ".join(results), total)


def parse_dice_msg(msg):
    """ msg format here should be [0-9]+d[0-9]+([+-][0-9]+)? """

    msg = msg.strip().lower()
    result = re.match("(?P<quantity>[0-9]+)d(?P<die>[0-9]+)(?P<modifier>[+-][0-9]+)?", msg)
    if result:
        return result.groupdict()
    else:
        raise Exception("ugh, not valid dice roll")

    if quantity.isdigit() and value.isdigit():
        return [ int(value) ] * int(quantity)
    else:
        raise Exception("ugh, not valid dice roll")



#####################################################################
#
# Initialization Code
#
#####################################################################

#run(host='0.0.0.0', port=8080, server="paste")
#run(host='0.0.0.0', port=8080)



from gevent.pywsgi import WSGIServer
from geventwebsocket import WebSocketError
from geventwebsocket.handler import WebSocketHandler
server = WSGIServer(("127.0.0.1", 8080), app,
                    handler_class=WebSocketHandler)
server.serve_forever()
