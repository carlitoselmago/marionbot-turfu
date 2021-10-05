import threading
import time
import random
import requests

from interface import *

class botapi():

    minWait=0.1
    maxWait=1.0
    #wait in seconds

    def __init__(self):
        pass

    def kill(self):
        thread_id = self.get_id()
        res = ctypes.pythonapi.PyThreadState_SetAsyncExc(thread_id,
              ctypes.py_object(SystemExit))
        if res > 1:
            ctypes.pythonapi.PyThreadState_SetAsyncExc(thread_id, 0)
            print('Exception raise failure')

    def respond(self,text,userID,chatID,DB,lastMsgs,errorCallback):

        waitTime=random.uniform(self.minWait, self.maxWait)
        time.sleep(waitTime)
        print("USER ASKED:",text)
        #response= "response to: "+text+": yes!"
        response=answer(text,lastMsgs)
        if isinstance(response,dict):
            if "error" in response:
                print("Error contacting the bot server")
                errorCallback("yes")
                return False
        if response:
            print("BOT RESPONSE:",response)
            #self.sendToServer(response)

            DB.saveMessage(1,chatID, response,0,1) #last 1 means botmade
            #callbackResponse(response)
            return True

    def manageTalk(self,userID,chatID,text,DB,lastMsgs=[],callbackError=False):
        #response= self.respond(text)
        return self.respond(text,userID,chatID,DB,lastMsgs,callbackError)
        #t = threading.Thread(target=self.respond, args=(text,userID,chatID,DB,lastMsgs,callbackError,)) #tuple args, must end in comma
        #t.start()

    """
    def sendToServer(self,response):
        #send the response by POST
        data={"message":response}
        r = requests.post(url ="/post", data = data)
        print(r.text)
    """
