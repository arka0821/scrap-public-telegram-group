from telethon.sync import TelegramClient
from telethon.tl.functions.messages import GetDialogsRequest
from telethon.tl.types import InputPeerEmpty
import logging
import csv
import time
import yaml
import sys

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logging.getLogger('telethon').setLevel(level=logging.WARNING)
logger = logging.getLogger(__name__)


def start(config):
    try:
        api_id = config['api_id']
        session_name = config["session_name"]
        api_hash = config["api_hash"]
        phone_number = config['phone_number']
    
        client = TelegramClient(session_name, api_id, api_hash)
    except KeyError:
        print("Unable to get Telegram developer id.\nPlease register for telegram developer.")
        sys.exit(1)    
    client.connect()
    client.start()
    if not client.is_user_authorized():
        client.send_code_request(phone_number)
        client.sign_in(phone_number, input('Enter the code: '))

    chats = []
    last_date = None
    chunk_size = 200
    groups=[]
 
    result = client(GetDialogsRequest(
             offset_date=last_date,
             offset_id=0,
             offset_peer=InputPeerEmpty(),
             limit=chunk_size,
             hash = 0
         ))
    chats.extend(result.chats)
    for chat in chats:
        try:
            if chat.megagroup== True:
                groups.append(chat)
        except:
            continue
    print('Choose a group to scrape members :')
    i=0
    for g in groups:
        print('['+str(i)+']'+' - '+ g.title)
        i+=1
 
    print('')
    g_index = input("Enter a Number : ")
    target_group=groups[int(g_index)]
 
    print('Fetching Members...')
    time.sleep(1)
    all_participants = []
    all_participants = client.get_participants(target_group, aggressive=True)
 
    print('Saving In file...')
    time.sleep(1)
    with open("members.csv","w",encoding='UTF-8') as f:
        writer = csv.writer(f,delimiter=",",lineterminator="\n")
        writer.writerow(['username','user_id', 'access_hash','name','group', 'group_id','status'])
        for user in all_participants:
            if user.username:
                username= user.username
            else:
                username= ""
            if user.first_name:
                first_name= user.first_name
            else:
                first_name= ""
            if user.last_name:
                last_name= user.last_name
            else:
                last_name= ""
            name= (first_name + ' ' + last_name).strip()
            writer.writerow([username,user.id,user.access_hash,name,target_group.title, target_group.id, 'N'])      
    print('Members scraped successfully.')

if __name__ == "__main__":
    with open('config.yml', 'rb') as f:
        config = yaml.load(f)
    start(config)