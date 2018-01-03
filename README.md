# YouShare-telegram-chatbot
Video-sharing telegram chatbot

## About YouShare Chatbot
#### < Welcome to YouShare ><br/>
This is a video-comment-sharing platform!<br/>
You can leave a comment about the YouTube video which you're greatly moved or simply just want to share with!<br/>
And you can see those videos other people are being inspired and impressed!<br/>
You can only discover a new vibe depends on others' comments!<br/>
So be sure to leave your comment precisely if you really hope others would see the video you share!<br/>
<br/>
[Visit YouShare chatbot on Telegram](https://web.telegram.org/#/im?p=@ris_ys_bot)

## How to Run Chatbot Server
### Prerequisite
1.<br/>
`ngrok http 5000`<br/>
ngrok would generate a temporary http url, copy the url to `'ngrok url'` in `set_webhook.py`<br/>
2. get your telegram bot token, and copy to `'m_bot_token'` in `set_webhook.py`<br/>
3. get your google api key, and copy to `'M_API_KEY_HERE'` in `fsm.py`<br/>
4. get your firebase credential json file, and copy the file path to `'youtube_api_key_filepath'` in `fsm.py`<br/>
5. copy your firebase database url to `'firebase_database_url'` in `fsm.py` (should prepare a node in database: `"info:{latest_index:0}"`)<br/>
6.<br/>
`python3 set_webhook.py`
    
### python modules required
- python-telegram-bot(9.0.0)
- flask(0.12.2)
- transitions
- graphviz(0.8.2)
- pygraphviz(1.3.1)
- firebase_admin(2.7.0)
- json
- urllib3(1.22)
- random

## How to interact with YouShare chatbot
### commands
**/start** - get back to the `'init'` state from anywhere<br/>
**/intro** - introduction of YouShare robot<br/>
**/post** - share a new comment and post it<br/>
**/browse** - browse the comments list, chatbot will list the first 10 comments<br/>
**/shuffle** - get a random video with comment<br/>
<br/>
in `'view'` state(after typing command '/browse'), you could type the commands below to browse other parts of the comment list:<br/>
**/view_NUM** - view the specific page of the comment list, e.g. /view_2 would go to page 2 of the comment list<br/>
**/get_NUM** - get the video by the number, e.g. /get_15 chatbot would send you the video url of the 15th comment<br/>
or click the inline button:<br/>
**"<< prev page"** - view the previous 10 comments<br/>
**"next page >>"** - view the next 10 comments<br/>
<br/>

## Finite State Machine implemented in chatbot
![fsm image](https://i.imgur.com/BI2uQ6d.png)

## Code Description
### set_webhook.py
Setting states and transitions of the chatbot finite state machine, webhook of the chatbot. Generate the fsm image 'state.png' in the directory. Dealing with the first hand messages received(Decide what to trigger based on the current machine state).

### fsm.py
Define the database reference(with Google Firebase), the page of the comment list the user last browsed/ browsing, the index of the comment the user chose and the index of the comment the user is posting. It also defines what to do after the triggers are on, the transition conditions, and what to do after entering a new state.

#### State Description
Every state has a transition to `'init'` state, and that means users can type the command `/start` anywhere to get back to `'init'` state where the chatbot would give the basic hint of instructions the users can do.<br/>
There are five main routes of transition: `'intro'`, `'help'`, `'post'`, `'view'`, `'shuffle'`. Each route will lead to `'init'`state after they properly reach the end of the route.<br/>
- **POST**: Users would advance through every state in `post` route while entering the data required by the chatbot. If users leaving while in `'post'` route, the data would be uploaded to database, but the incomplete data would be overwritten next time when other users successfully making a comment post.<br/>
- **VIEW**: While still browsing the comment list, users would be in the same state. Users only leave the `view` state after choosing a comment or simply going back to `init` state by typing `/start`.<br/>
The other 3 routes would automatically guide the users back to `init` state after each work in the state is done.<br/>

## Author
Iris Wu

