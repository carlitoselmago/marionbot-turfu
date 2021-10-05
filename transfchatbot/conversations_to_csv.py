import argparse
from pathlib import Path
import re
from bs4 import BeautifulSoup
from functools import reduce
import csv
from tqdm import tqdm

def messageFileKey(file):
    match = re.search(r'message_(\d+).html', str(file))
    return int(match.group(1))

def parseMessage(block):
    children = block.div.find_all(recursive=False)
    message = children[1].find(text=True, recursive=False)
    if message != None:
        message = ' '.join(message.split())
    return message

def parseMessageBlock(block):
    author = block.select('div._3-96._2pio._2lek._2lel')[0].getText()
    message = parseMessage(block.select('div._3-96._2let')[0])
    return (author, message)


def parseFile(file):
    with open(file, 'r', encoding='utf-8') as f:
        soup = BeautifulSoup(f.read(), 'lxml')
        blocks = soup.select('html body._5vb_._2yq._4yic div.clearfix._ikh div._4bl9 div._li div._3a_u div._4t5n div.pam._3-95._2pi0._2lej.uiBoxWhite.noborder')
        messages = []
        for block in blocks[::-1]:
            messages.append(parseMessageBlock(block))
        return messages

def filterMessages(messages):
    return filter(lambda message: message[1] != None, messages)

def mergeMessages(messages):
    def reducer(acc, message):
        if len(acc) == 0:
            return [message]

        (lastAuthor, lastMessage) = acc[-1]
        (currentAuthor, currentMessage) = message
        if lastAuthor != currentAuthor:
            return acc + [message]
        else:
            newMessage = ' '.join([lastMessage, currentMessage])
            return acc[:-1] + [(currentAuthor, newMessage)]

    return reduce(reducer, messages, [])

def saveMessages(messages):
    with open('conversations.csv', 'w', encoding='utf-8') as f:
        writer = csv.writer(f, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
        writer.writerow([f'Input', f'Target'])
        for msg1, msg2 in zip(messages[::2], messages[1::2]):
            author1, message1 = msg1
            author2, message2 = msg2

            if author1 == INPUT:
                writer.writerow([message1, message2])
            else:
                writer.writerow([message2, message1])

INPUT = input("Please enter input person fullname: ")
TARGET = input("Please enter target person fullname (for chatbot): ")

argparser = argparse.ArgumentParser(description='Converts Facebook messages to CSV')
argparser.add_argument('Path', metavar='path', type=str, help='Message path')
args = argparser.parse_args()

print("Find messenger files...")
messagePath = args.Path
messageFiles = Path(messagePath).rglob('message*.html')
messageFiles = sorted(messageFiles, key=messageFileKey, reverse=True)
print("Parse files...")
messages = []
for messageFile in tqdm(messageFiles):
    messages = messages + parseFile(messageFile)
print("Filter and merge files...")
messages = filterMessages(messages)
messages = mergeMessages(messages)
saveMessages(messages)
print("Conversations saved!")
