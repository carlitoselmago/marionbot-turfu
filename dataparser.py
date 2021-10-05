# -*- coding: utf-8 -*-
import os
import json
import sys
from emoji import UNICODE_EMOJI
import re
from pyquery import PyQuery as pq
import shutil

class dataParser():

    maxprint=20
    minchars=1
    sources=["telegram","whatsapp"]

    def __init__(self):
        pass

    def parse_telegram(self):

        for root, dirs, files in os.walk("data/telegram"):
            for file in files:
                if file.endswith('.json'):
                    cleaned=[]
                    fileuri=os.path.join(root, file)

                    savefilename='telegram_'+fileuri.replace(".","_").replace("/","_").replace('\\',"_")
                    if os.path.exists('data/ready/'+savefilename+'.txt'):
                        print("skipping ",fileuri,":: already parsed")
                        print("")
                        break

                    print("parsing: ",fileuri,":::")
                    print("")
                    with open(fileuri, encoding='utf-8') as fh:
                        data = json.load(fh)
                        for i,chat in enumerate(data["chats"]["list"]):
                            if i<self.maxprint:
                                for msg in chat["messages"]:
                                    if msg["type"]=="message" and msg["text"]!="":
                                        if not isinstance(msg["text"], list):
                                            clean_text=self.cleanup_text(msg["text"])
                                            if clean_text:
                                                cleaned.append(clean_text)
                    print("Parsed ",len(cleaned),"messages")

                    #save
                    self.saveMessages(savefilename,cleaned)

    def parse_whatsapp(self):
        for root, dirs, files in os.walk("data/whatsapp"):
            for file in files:
                if file.endswith('.txt'):
                    cleaned=[]
                    fileuri=os.path.join(root, file)

                    savefilename='whatsapp_'+fileuri.replace(".","_").replace("/","_").replace('\\',"_")
                    if os.path.exists('data/ready/'+savefilename+'.txt'):
                        print("skipping ",fileuri,":: already parsed")
                        break

                    print("parsing: ",fileuri,":::")
                    print("")
                    with open(fileuri, encoding='utf-8') as fh:
                        lines=fh.read().split('\n')[:-1]
                        for l in lines:
                            if " - " in l:
                                msg=l.split(" - ")[1]
                                if ": " in msg:
                                    msg=msg.split(": ")[1]
                                    clean_text=self.cleanup_text(msg)
                                    if clean_text:
                                        blacklist=["<Media omitted>"]
                                        for b in blacklist:
                                            if b not in clean_text:
                                                cleaned.append(clean_text)
                    print("Parsed ",len(cleaned),"messages")

                    #save
                    self.saveMessages(savefilename,cleaned)

    def parse_instagram(self):

        minimum_messages=10

        def parseIGmsg(node):
            print(node)

        for root, dirs, files in os.walk("data/instagram"):
            for file in files:
                if file=='message_1.html':
                    cleaned=[]
                    fileuri=os.path.join(root, file)

                    savefilename='instagram_'+fileuri.replace(".","_").replace("/","_").replace('\\',"_")
                    if os.path.exists('data/ready/'+savefilename+'.txt'):
                        print("skipping ",fileuri,":: already parsed")
                        break

                    print("parsing: ",fileuri,":::")
                    print("")



                    with open(fileuri, encoding='utf-8') as fh:
                        html=pq(fh.read())

                        dom=html.children("body")
                        messages=html("._4bl9 ._li ._3a_u ._4t5n").find(".pam")
                        for i in range(len(messages)):
                            msg=messages.eq(i).find("._3-95 div div").eq(1).text()
                            clean_text=self.cleanup_text(msg)
                            if clean_text:
                                cleaned.append(clean_text)

                    if len(cleaned)>minimum_messages:
                        print("Parsed ",len(cleaned),"messages")

                        #save
                        self.saveMessages(savefilename,cleaned)


    def saveMessages(self,filename,msgs):
        with open('data/ready/'+filename+'.txt', 'w',encoding="utf-8") as f:
            f.writelines( "%s\n" % item for item in msgs )

    def parse(self):
        self.parse_instagram()
        self.parse_telegram()
        self.parse_whatsapp()


    def cleanup_text(self,s):
        cleaned=str(s)
        if len(s)>self.minchars:
            if (self.is_emoji(s)):
                cleaned= False
            else:
                #remove urls
                cleaned=re.sub(r"http\S+", "", cleaned)
        else:
            cleaned=False

        return cleaned

    def is_emoji(self,s):
        count = 0
        for emoji in UNICODE_EMOJI:
            count += s.count(emoji)
            if count > 1:
                return False
        return bool(count)

if __name__ == "__main__":
    if len(sys.argv)>1:
        if sys.argv[1]=="clean":
            for root, dirs, files in os.walk('data/ready/'):
                for f in files:
                    os.unlink(os.path.join(root, f))
                for d in dirs:
                    shutil.rmtree(os.path.join(root, d))


    dp=dataParser()
    dp.parse()
