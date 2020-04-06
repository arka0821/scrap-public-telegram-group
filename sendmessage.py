from telethon.sync import TelegramClient
from telethon.tl.types import InputPeerUser
from telethon.errors.rpcerrorlist import PeerFloodError
import sys
import csv
import time
import logging
import yaml
import pandas as pd

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logging.getLogger('telethon').setLevel(level=logging.WARNING)
logger = logging.getLogger(__name__)


def start(config):
    print("Initiating message sending process.\n")
    try:
        try:
            api_id = config['api_id']
            session_name = config["session_name"]
            api_hash = config["api_hash"]
            phone_number = config['phone_number']
            SLEEP_TIME = int(config['sleep_time'])
            client = TelegramClient(session_name, api_id, api_hash)
        except KeyError:
            print("Unable to get Telegram developer id.\nPlease register for telegram developer.")
            sys.exit(1)
            
        client.connect()
        client.start()
        
        if not client.is_user_authorized():
            client.send_code_request(phone_number)
            client.sign_in(phone_number, input('Enter the code: '))
        
        input_file = 'members.csv'
        users = []
        with open(input_file, encoding='UTF-8') as f:
            rows = csv.reader(f,delimiter=",",lineterminator="\n")
            next(rows, None)
            for row in rows:
                user = {}
                user['username'] = row[0]
                user['user_id'] = int(row[1])
                user['access_hash'] = int(row[2])
                user['name'] = row[3]
                if row[6] == 'N':
                    users.append(user)
                    
        df = pd.read_csv("members.csv")
        
        message = config['message']
        for user in users:
            receiver = InputPeerUser(user['user_id'],user['access_hash'])
            try:
                print("Sending Message to:", user['name'])
                client.send_message(receiver, message)
                print("Waiting {} seconds".format(SLEEP_TIME))
                df.loc[df["user_id"] == user['user_id'], "status"] = 'Y'
                time.sleep(SLEEP_TIME)
            except PeerFloodError:
                print("Getting Flood Error from telegram. Script is stopping now. Please try again after some time.")
                client.disconnect()
                sys.exit()
            except Exception as e:
                print("Error:", e)
                print("Trying to continue...")
                continue
    except:
        print("Failed to execute script. Please check logs.")
    finally:
        df.to_csv("members.csv", index=False)
        print("Done. Message sent to all users.")
        client.disconnect()


if __name__ == "__main__":
    with open('config.yml', 'rb') as f:
        config = yaml.load(f)
    start(config)