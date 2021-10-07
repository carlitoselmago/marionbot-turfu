# -*- coding: utf-8 -*-
import os
import json
import sys
from emoji import UNICODE_EMOJI
import re
from pyquery import PyQuery as pq
import shutil
import emoji

class dataParser():

    maxmessages=2000
    minmesages=20
    minchars=1
    sources=["telegram","whatsapp"]

    def __init__(self):
        pass

    def parse_telegram(self):
        total=0
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
                            if i<self.maxmessages:
                                for msg in chat["messages"]:
                                    if msg["type"]=="message" and msg["text"]!="":
                                        if not isinstance(msg["text"], list):
                                            clean_text=self.cleanup_text(msg["text"])
                                            if clean_text:
                                                cleaned.append(clean_text)
                    if len(cleaned)>self.minmesages:
                        print("Parsed ",len(cleaned),"messages")
                        total+=len(cleaned)
                        #save
                        self.saveMessages(savefilename,cleaned)
        return total

    def parse_whatsapp(self):
        total=0
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
                    if len(cleaned)>self.minmesages:
                        print("Parsed ",len(cleaned),"messages")
                        total+=len(cleaned)
                        #save
                        self.saveMessages(savefilename,cleaned)
        return total

    def parse_instagram(self):
        total=0

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

                    if len(cleaned)>self.minmesages:
                        print("Parsed ",len(cleaned),"messages")
                        total+=len(cleaned)
                        #save
                        self.saveMessages(savefilename,cleaned)
        return total

    def parse_facebook(self):
        total=0
        for root, dirs, files in os.walk("data/facebook"):
            for file in files:
                if file.endswith('.json'):
                    cleaned=[]
                    fileuri=os.path.join(root, file)

                    savefilename='facebook_'+fileuri.replace(".","_").replace("/","_").replace('\\',"_")
                    if os.path.exists('data/ready/'+savefilename+'.txt'):
                        print("skipping ",fileuri,":: already parsed")
                        print("")
                        break

                    print("parsing: ",fileuri,":::")
                    print("")
                    with open(fileuri, encoding='utf-8') as fh:
                        data = json.load(fh)
                        for i,msg in enumerate(data["messages"]):
                            if i<self.maxmessages:
                                if msg["type"]=="Generic":
                                    if "content" in msg:
                                        clean_text=self.cleanup_text(msg["content"])
                                        if clean_text:
                                            cleaned.append(clean_text)
                    if len(cleaned)>self.minmesages:
                        print("Parsed ",len(cleaned),"messages")
                        total+=len(cleaned)
                        #save
                        self.saveMessages(savefilename,cleaned)
        return total


    def saveMessages(self,filename,msgs):
        with open('data/ready/'+filename+'.txt', 'w',encoding="utf-8") as f:
            f.writelines( "%s\n" % item for item in msgs )

    def parse(self):
        total=0
        total+=self.parse_facebook()
        total+=self.parse_instagram()
        total+=self.parse_telegram()
        total+=self.parse_whatsapp()

        print("")
        print("Total messages parsed ",total,"::::::::::::::")
        print ("")


    def cleanup_text(self,s):
        cleaned=str(s)

        #remove unwanted characters
        removeList=['"','#', '$', '%', '(', ')', '=', ';' ,':',  '*', '+', '£' , '—','’','@']
        for r in removeList:
          if r in cleaned:
            cleaned=cleaned.replace(r, '')

        #remove emojis
        cleaned=self.strip_emoji(cleaned)

        #remove urls
        cleaned=re.sub(r"http\S+", "", cleaned)

        if len(cleaned)<self.minchars:
            cleaned= False

        return cleaned

    def strip_emoji(self,text):
        new_text = re.sub(emoji.get_emoji_regexp(), r"", text)
        return new_text

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
