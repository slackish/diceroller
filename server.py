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

@app.route('/roller/<uid>/ws')
def ws(uid):
    """
    websocket code
    """
    print >>sys.stderr, "websocket called"
    wsock = request.environ.get('wsgi.websocket')
    if not wsock:
        abort(400, 'Expected WebSocket request.')

    if uid not in clients.keys():
        clients[uid] = []
    clients[uid].append(wsock)

    while True:
        try:
            message = wsock.receive()
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
                dice.extend(parse_dice_msg(msg_part))
        else:
            dice.extend(parse_dice_msg(msg))
    except Exception:
        return None

    results = perform_roll(dice)
    return format_roll(msg, results)


def format_roll(msg, results):
    retstr = [msg, ": "]

    if len(results) == 1:
        retstr.append("%d" % results[0])
    else:
        total = sum(results)
        results = map(str, results)
        retstr.append("%s = %d" % (" + ".join(results), total))

    return "".join(retstr)


def perform_roll(dice):
    results = []
    for die in dice:
        results.append(random.randint(1, die))
    return results


def parse_dice_msg(msg):
    """ msg format here should be [0-9]+d[0-9]+ """

    msg = msg.strip().lower()
    if re.match("[0-9]+d[0-9]+", msg):
        quantity, value = msg.split("d", 1)
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
server = WSGIServer(("0.0.0.0", 8080), app,
                    handler_class=WebSocketHandler)
server.serve_forever()
