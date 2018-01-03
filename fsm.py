import telegram
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from transitions import State
from transitions.extensions import GraphMachine
import json
import urllib.request
#import urllib2 # should import urllib.request if with python3
import firebase_admin
from firebase_admin import credentials, db
import random

class RisMachine(GraphMachine):
	cred = credentials.Certificate('youtube_api_key_filepath')
	firebase_admin.initialize_app(cred, {'databaseURL':'firebase_database_url'})
	current_index = 0
	current_page = 1
	chosen_index = 0
	def __init__(self, **machine_configs):
		self.machine = GraphMachine(
			model = self,
			**machine_configs
		)
		self.ref = db.reference()
	
	def c_intro(self, update):
		text = update.message.text
		return text.lower() == '/intro'

	def c_help(self, update):
		text = update.message.text
		return text.lower() == '/help'

	def c_shuffle(self, update):
		text = update.message.text
		return text.lower() == '/shuffle'

	def c_view(self, update):
		if update.message != None:
			text = update.message.text
		elif update.callback_query != None:
			text = update.callback_query.data
		else:
			print('got message None')
			return False
		if self.state == 'init':
			return text.lower() == '/browse'
		elif self.state == 'view':
			m_ref = db.reference('info/latest_index')
			g_latest_index = str(m_ref.get())
			g_latest_index_int = int(g_latest_index)
			g_latest_index_int = g_latest_index_int / 10 + 1
			if text.lower() == 'next>>':
				if self.current_page+1 <= g_latest_index_int:
					self.current_page = self.current_page + 1
					return True
				else:
					return False
			elif text.lower() == '<<prev':
				if self.current_page-1 > 0:
					self.current_page = self.current_page - 1
					return True
				else:
					return False
			text_list = text.split('_')
			if text_list[0].lower() == '/view':
				if int(text_list[1]) > 0 and int(text_list[1]) <= g_latest_index_int:
					self.current_page = int(text_list[1])
					return True
				else:
					return False
			else:
				return False
		else:
			return False

	def c_result(self, update):
		if update.message != None:
			text = update.message.text
		elif update.callback_query != None:
			text = update.callback_query.data
		else:
			print('got message None')
			return False
		text_list = text.split('_')
		if text_list[0].lower() == '/get':
			m_ref = db.reference('info/latest_index')
			g_latest_index = str(m_ref.get())
			g_latest_index_int = int(g_latest_index)
			if text_list[1] == None:
				return False
			i_ref = db.reference(str(text_list[1]))
			if i_ref == None:
				return False
			self.chosen_index = int(text_list[1])
			return True
		else:
			return False
		
	def c_post(self, update):
		text = update.message.text
		if self.state == 'init':
			return text.lower() == '/post'
		elif self.state == 'post_video':
			# get video url
			m_ref = db.reference('info/latest_index')
			g_latest_index = str(m_ref.get())
			g_latest_index_int = int(g_latest_index)
			g_latest_index_int = g_latest_index_int + 1
			self.current_index = g_latest_index_int
			self.ref.child(str(self.current_index)).child('video').set(update.message.text)
			# get video title by url with youtube api
			vid_index_s = text.find('v=') + 2
			vid = text[vid_index_s : vid_index_s + 11]
			get_video_info = urllib.request.urlopen('https://www.googleapis.com/youtube/v3/videos?id='+vid+'&key='+'M_API_KEY_HERE'+'%20&fields=items(id%2Csnippet(title%2CcategoryId))&part=snippet').read().decode('utf-8')
			get_video_dict = json.loads(get_video_info)
			get_video_title = get_video_dict['items'][0]['snippet']['title']
			self.ref.child(str(self.current_index)).child('video_title').set(get_video_title)
			return True
		elif self.state == 'post_comment':
			self.ref.child(str(self.current_index)).child('comment').set(update.message.text)
			return True
		elif self.state == 'post_username':
			return True
		else:
			return False

	def on_enter_intro(self, update):
		update.message.reply_text('< Welcome to YouShare >\nI am the chatbot of YouShare!\nThis is a video-comment-sharing platform!\nYou can leave a comment about the YouTube video which you\'re greatly moved or simply just want to share with!\nAnd you can see those videos other people are being inspired and impressed!\nYou can only discover a new vibe depends on others\' comments!\nSo be sure to leave your comment precisely if you really hope others would see the video you share!\n(If you really just want to get a video without reading any text, just type /shuffle ! ;) )')
		self.done(update)
		return
		
	def on_enter_help(self, update):
		update.message.reply_text('< Commands Tutorial >\ntype /post to start sharing a new video\ntype /browse to see others\' comments\ntype /shuffle to get a random video with comment!\ntype /intro to see the introduction of YouShare robot!\ntype /start anywhere to get back to the initial state!')
		self.done(update)
		return

	def on_enter_init(self, update):
		update.message.reply_text('< Hello! >\nHello! I am YouShare chatbot!\nYou can type /intro to see the introduction of YouShare robot!\n Or type /help to see the commands available in YouShare bot!')
		return

	def on_enter_shuffle(self, update):
		i_ref = db.reference('info/latest_index')
		g_latest_index = str(i_ref.get())
		g_latest_index_int = int(g_latest_index)
		get_random_index = random.randint(1, g_latest_index_int)
		m_ref = db.reference(str(get_random_index))
		if m_ref != None:
			to_reply = '< Shuffle! >\n'
			to_reply += '[' + str(get_random_index) + ']'
			to_reply += str(m_ref.child('video_title').get())
			to_reply += '\n'
			to_reply += str(m_ref.child('video').get())
			to_reply += '\n\"'
			to_reply += str(m_ref.child('comment').get())
			to_reply += '\"\nby '
			to_reply += str(m_ref.child('username').get())
			update.message.reply_text(to_reply)
		self.done(update)
		return

	def on_enter_view(self, update):
		#print('now request page:'+str(self.current_page))
		if update.message != None:
			update.message.reply_text('I\'m loading data for you... please hold on!')
		elif update.callback_query != None:
			update.callback_query.message.reply_text('I\'m loading data for you... please hold on!')
		i_ref = db.reference('info/latest_index')
		g_latest_index = str(i_ref.get())
		g_latest_index_int = int(g_latest_index)
		start_index = self.current_page * 10 - 9
		to_reply = '< Video List - page ' + str(self.current_page) + ' >\n'
		for num in range(1,11):
			if start_index > g_latest_index_int:
				break
			to_reply = to_reply + '[' + str(start_index) + '] '
			m_ref = db.reference(str(start_index))
			if m_ref != None:
				to_reply += str(m_ref.child('comment').get())
				to_reply += '\t('
				to_reply += str(m_ref.child('username').get())
				to_reply += ')\n'
			start_index += 1
		kb = [[InlineKeyboardButton('<< prev page', callback_data = '<<prev'), InlineKeyboardButton('next page >>', callback_data = 'next>>')]]
		if update.message != None:
			update.message.reply_text(to_reply)
			update.message.reply_text('please type /get_NUM to get the video you want by index number,\ntype /view_NUM to jump to the specific page of the video list!', reply_markup=telegram.InlineKeyboardMarkup(inline_keyboard = kb, resize_keyboard = True, one_time_keyboard = True))
		elif update.callback_query != None:
			update.callback_query.message.reply_text(to_reply)
			update.callback_query.message.reply_text('please type /get_NUM to get the video you want by index number,\ntype /view_NUM to jump to the specific page of the video list!', reply_markup=telegram.InlineKeyboardMarkup(inline_keyboard = kb, resize_keyboard = True, one_time_keyboard = True))
		else:
			return
		return

	def on_enter_result(self, update):
		to_reply = 'Here is the video you choose by comment!\n'
		m_ref = db.reference(str(self.chosen_index))
		to_reply = to_reply + '[' + str(self.chosen_index) + ']\n'
		to_reply += str(m_ref.child('video_title').get())
		to_reply += '\n'
		to_reply += str(m_ref.child('video').get())
		to_reply += '\n\"'
		to_reply += str(m_ref.child('comment').get())
		to_reply += '\"\nby '
		to_reply += str(m_ref.child('username').get())
		if update.message != None:
			update.message.reply_text(to_reply)
		elif update.callback_query != None:
			update.callback_query.message.reply_text(to_reply)
		else:
			return
		self.done(update)
		return

	def on_enter_post_video(self, update):
		update.message.reply_text('please give me the video url you want to share!')
		return

	def on_enter_post_comment(self, update):
		update.message.reply_text('please tell me your comment on this video')
		return
	def on_enter_post_username(self, update):
		m_ref = db.reference('info/latest_index')
		temp_ind = int(m_ref.get())
		temp_ind += 1
		m_ref.set(str(temp_ind))
		temp_string = str(update.message.from_user.username)
		if temp_string == 'None':
			if str(update.message.from_user.last_name) == 'None':
				temp_string = update.message.from_user.first_name
			else:
				temp_string = update.message.from_user.first_name + " " + update.message.from_user.last_name
		self.ref.child(str(self.current_index)).child('username').set(temp_string)
		update.message.reply_text('I\'ve added your comment by your id: ' + temp_string)
		update.message.reply_text('Your comment is listed as No. '+str(temp_ind))
		self.done(update)
		return

