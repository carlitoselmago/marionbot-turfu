import pymysql
import pymysql.cursors
from sqlalchemy.sql import func
import time
from .settings import dbsettings
class db():

    db=False

    def __init__(self):
        print("DB STARTED")
        # Open database connection

    def getConnection(self):
        return pymysql.connect(dbsettings["host"],dbsettings["username"],dbsettings["password"],dbsettings["dbname"],cursorclass=pymysql.cursors.DictCursor)

    def getUsers(self):
        db=self.getConnection()
        cursor = db.cursor()
        sql = "SELECT * FROM  people"
        cursor.execute(sql)
        results = cursor.fetchall()
        db.close()
        return results

    def getChats(self):
        db=self.getConnection()
        cursor = db.cursor()
        sql = "SELECT c.id, c.userid , p.name, c.notseen FROM chats c LEFT JOIN `people` p ON c.userid = p.id WHERE `archived`=0 ORDER BY c.lastupdated DESC"
        #sql = "SELECT * FROM chats"
        cursor.execute(sql)
        results = cursor.fetchall()
        db.close()
        return results

    def userExists(self,username):
        db=self.getConnection()
        cursor = db.cursor()
        sql = "SELECT * FROM  people WHERE name='%s'" % \
        (username)

        cursor.execute(sql)
        results = cursor.fetchall()
        db.close()
        print("len(results)",len(results))
        if len(results)>0:
            return results
        else:
            return False

    def getUserName(self,userid):
        db=self.getConnection()
        cursor = db.cursor()
        sql = "SELECT name FROM  people WHERE id='%d'" % \
        (userid)
        cursor.execute(sql)
        results = cursor.fetchone()
        db.close()
        return results["name"]

    def getUserChatId(self,userid):
        db=self.getConnection()
        cursor = db.cursor()
        sql = "SELECT id FROM chats WHERE userid=%d" % \
        (userid)
        cursor.execute(sql)
        results = cursor.fetchone()
        db.close()
        return results["id"]

    def getUserAccess(self,userid):
        db=self.getConnection()
        cursor = db.cursor()
        sql = "SELECT access FROM people WHERE id=%d" % \
        (userid)
        cursor.execute(sql)
        results = cursor.fetchone()
        db.close()
        return results["access"]

    def checkUserPassword(self,user,password):
        db=self.getConnection()
        cursor = db.cursor()
        sql = "SELECT * FROM  people WHERE name='%s' AND password='%s'" % \
        (user,password)

        cursor.execute(sql)

        results = cursor.fetchall()
        db.close()
        if len(results)>0:
            if results[0]["name"]==user:
                if results[0]["password"]==password:
                    return results[0]
        return False


    def getMessages(self,chatid,lastMsgDate=False):
        if lastMsgDate:
            if lastMsgDate=="undefined":
                lastMsgDate=False
        db=self.getConnection()
        cursor = db.cursor()
        #sql = "SELECT * FROM  messages WHERE `from` = "+str(chatid)
        if lastMsgDate:
            sql = "SELECT m.id, m.date, m.from, m.chat, m.text, m.tipo, p.name FROM messages m LEFT JOIN `people` p ON m.from = p.id WHERE `chat` = "+str(chatid)+" AND date>"+str(lastMsgDate)+" ORDER BY m.date"
        else:
            sql = "SELECT m.id, m.date, m.from, m.chat, m.text, m.tipo, p.name FROM messages m LEFT JOIN `people` p ON m.from = p.id WHERE `chat` = "+str(chatid)+" ORDER BY m.date"

        cursor.execute(sql)
        results = cursor.fetchall()
        # Commit your changes in the database
        db.close()
        return results

    def addunseen(self,chatid):
        db=self.getConnection()

        cursor = db.cursor()
        sql = "UPDATE chats SET `notseen` = `notseen` + 1 WHERE id="+str(chatid)
        cursor.execute(sql)
        db.commit()
        # disconnect from server
        db.close()

    def removeNotSeen(self,chatid):
        db=self.getConnection()
        cursor = db.cursor()
        sql = "UPDATE chats SET `notseen` = 0 WHERE id="+str(chatid)
        cursor.execute(sql)
        db.commit()
        # disconnect from server
        db.close()

    def archiveChat(self,chatid):
        db=self.getConnection()
        cursor = db.cursor()
        sql = "UPDATE chats SET `archived` = 1 WHERE id="+str(chatid)
        cursor.execute(sql)
        db.commit()
        # disconnect from server
        db.close()

    def saveMessage(self,user,chat,msg,tipo=0,botmade=0):
        db=self.getConnection()
        cursor = db.cursor()
        #text=db.escape(msg)
        text=msg
        sql = "INSERT INTO messages( \
           `date`,`text` ,`from`,`chat`,`tipo`,`botmade`) \
           VALUES (%s, %s, %s,%s,%s,%s)"

        cursor.execute(sql,(int(time.time()), text, int(user),int(chat),int(tipo),int(botmade)))
        db.commit()
        if user>1:
            #not marion
            self.addunseen(chat)
        # disconnect from server
        db.close()

    def createUser(self,username,role,password=""):
        db=self.getConnection()

        cursor = db.cursor()
        sql = "INSERT INTO people( \
           `access`,`name` ,`password`) \
           VALUES (%d, '%s', '%s')" % \
           (role, username, password)

        cursor.execute(sql)
        db.commit()
        userID=cursor.lastrowid
        # disconnect from server
        db.close()
        chatID=self.createChat(userID)
        print("userID,chatID",userID,chatID)
        return userID,chatID

    def createChat(self,userID):
        db=self.getConnection()
        cursor = db.cursor()
        sql = "INSERT INTO chats( \
           `userid`) \
           VALUES (%d)" % \
           (userID)

        cursor.execute(sql)
        db.commit()
        chatID=cursor.lastrowid
        # disconnect from server
        db.close()
        return chatID

    def ismarionOnline(self):
        db=self.getConnection()
        cursor = db.cursor()
        sql = "SELECT value FROM globals WHERE name='marionlastcheck'"
        cursor.execute(sql)
        results = cursor.fetchone()
        db.close()
        #lastmarion = datetime.datetime.fromtimestamp(results["ismariononline"])
        lastmarion=int(results["value"])
        now=time.time()

        margin=5*60

        if (lastmarion+margin)>now:
            return True
        else:
            return False

    def setMarionStatus(self):
        db=self.getConnection()
        cursor = db.cursor()
        sql = "UPDATE globals SET value = '"+str(int(time.time()))+ "' WHERE name='marionlastcheck'"

        cursor.execute(sql)
        db.commit()
        # disconnect from server
        db.close()

    def getLastTimeNotified(self):
        db=self.getConnection()
        cursor = db.cursor()
        sql = "SELECT value FROM globals WHERE name='lasttimenotified'"
        cursor.execute(sql)
        results = cursor.fetchone()
        db.close()
        #lastmarion = datetime.datetime.fromtimestamp(results["ismariononline"])
        lastmarion=int(results["value"])
        return lastmarion

    def updateGlobal(self,name,value):
        db=self.getConnection()
        cursor = db.cursor()
        sql = "UPDATE globals SET value = '"+str(value)+ "' WHERE name='"+name+"'"

        cursor.execute(sql)
        db.commit()
        # disconnect from server
        db.close()
