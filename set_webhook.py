# set up telegram-bot webhook

import sys
import telegram
from flask import Flask, request, send_file
from transitions import State
from transitions.extensions import GraphMachine as Machine
from io import BytesIO
from fsm import RisMachine
from pygraphviz import *
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db


ngrok_hex_name = 'ngrok url'; # # # modify here # # #

app = Flask(__name__)
bot = telegram.Bot(token='m_bot_token')

machine = RisMachine(
	states = [
		'init',
		'intro',
		'help',
		'view',
		'result',
		'post_video',
		'post_comment',
		'post_username',
		'shuffle'
	],
	transitions = [
		{
			'trigger':'done',
			'source':'*',
			'dest':'init'
		},
		{
			'trigger':'get_instruc',
			'source':'init',
			'dest':'intro',
			'conditions':'c_intro'
		},
		{
			'trigger':'get_instruc',
			'source':'init',
			'dest':'help',
			'conditions':'c_help'
		},
		{
			'trigger':'get_instruc',
			'source':'init',
			'dest':'view',
			'conditions':'c_view'
		},
		{
			'trigger':'get_instruc',
			'source':'init',
			'dest':'shuffle',
			'conditions':'c_shuffle'
		},
		{
			'trigger':'advance_view',
			'source':'view',
			'dest':'view',
			'conditions':'c_view'
		},
		{
			'trigger':'advance_view',
			'source':'view',
			'dest':'result',
			'conditions':'c_result'
		},
		{
			'trigger':'get_instruc',
			'source':'init',
			'dest':'post_video',
			'conditions':'c_post'
		},
		{
			'trigger':'advance_post',
			'source':'post_video',
			'dest':'post_comment',
			'conditions':'c_post'
		},
		{
			'trigger':'advance_post',
			'source':'post_comment',
			'dest':'post_username',
			'conditions':'c_post'
		},
		{
			'trigger':'advance_post',
			'source':'post_username',
			'dest':'init',
			'conditions':'c_post'
		}
	],
	initial = 'init',
	auto_transitions = False,
	show_conditions = True
)

# set bot and web hook
def _set_webhook():
	status = bot.set_webhook(ngrok_hex_name+'/hook')
	if not status:
		print('web hook setup failed')
		sys.exit(1)

# set function when receiving messages		
@app.route('/hook', methods = ['POST'])
def webhook_handler():
	if request.method == "POST":
		update = telegram.Update.de_json(request.get_json(force=True), bot)
		if update.message != None:
			text = update.message.text
		elif update.callback_query != None:
			text = update.callback_query.data
		else:
			print('got message None')
			return
		print('got message:'+text)
		if text.lower() == '/start':
			machine.done(update)
		if machine.state == 'init':
			machine.get_instruc(update)
		elif machine.state == 'view':
			machine.advance_view(update)
		elif (machine.state == 'post_video' or \
				machine.state == 'post_comment' or \
				machine.state == 'post_username'):
			machine.advance_post(update)
		else :
			machine.get_instruc(update)
	return 'ok'
	
if __name__ == '__main__':
	machine.graph.draw('state.png', prog='dot')
	_set_webhook()
	app.run()
