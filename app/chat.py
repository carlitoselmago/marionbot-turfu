from flask import Flask, request,redirect, abort,render_template,session,copy_current_request_context
from flask import render_template, flash, redirect, session, url_for, request, g
from flask_login import LoginManager, login_user, current_user, UserMixin
from flask_socketio import SocketIO, emit, send
from flask_uploads import UploadSet, configure_uploads, IMAGES, patch_request_class
from flask_socketio import join_room, leave_room
from .forms import LoginForm, MessageForm, PasswordForm, DeleteUser
from flask_dropzone import Dropzone
from flask_cors import CORS, cross_origin
import locale
import os
import datetime
import time
import hashlib
from app.db import db
import sys
sys.path.append("transfchatbot")
from botapi import botapi
from werkzeug.middleware.proxy_fix import ProxyFix

locale.setlocale(locale.LC_TIME, "fr_FR.UTF-8")

bot=True

app = Flask(__name__)

cors = CORS(app, resources={r"/*": {"origins": "*"}})
#app.secret_key ='kskskskdkdkddi__DDD'
app.config['DROPZONE_UPLOAD_MULTIPLE'] = False
app.config['DROPZONE_ALLOWED_FILE_CUSTOM'] = True
app.config['DROPZONE_ALLOWED_FILE_TYPE'] = '.jpg, .png'#'image/*'
app.config['DROPZONE_REDIRECT_VIEW'] = 'results'
app.config['UPLOADED_PHOTOS_DEST'] = os.getcwd() + '/images'
app.config['DROPZONE_DEFAULT_MESSAGE'] ="+"
app.config['DROPZONE_INVALID_FILE_TYPE'] ="Formats acceptés : .jpg, .png"
app.config['DROPZONE_FILE_TOO_BIG'] ="La taille de l'image est trop grande ( {{filesize}} ), merci de ne pas dépasser {{maxFilesize}}Mo."
app.config['DROPZONE_SERVER_ERROR'] ="Erreur de chargement de l'image"
app.config['SECRET_KEY'] = 'maarionnbooot'
app.config['MAX_CONTENT_LENGTH'] = 5 * 1024 * 1024

photos = UploadSet('photos', IMAGES)
configure_uploads(app, photos)
patch_request_class(app)  # set maximum file size, default is 16MB

DB=db()
BOT=botapi()

dropzone = Dropzone(app)

login = LoginManager(app)
cors = CORS(app,resources={r"/*":{"origins":"*"}})
socketio = SocketIO(app,cors_allowed_origins=["https://www.esam-c2.fr","http://htmlfiesta.com","https://marionbot.ddns.net","https://turfu-festival.ddns.net/"])

app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1)

clients={}
@cross_origin(origin='*',headers=['Content- Type','Authorization'])
@login.user_loader
def user_loader(id):
    return User(id)

class User(UserMixin):
    def __init__(self, username):
        self.id = username

@app.route('/')
@app.route('/home')
@app.route('/index', methods=['GET', 'POST'])
def index():
    browser = request.user_agent.browser
    form = MessageForm()
    session["ismarion"]=False

    if "user" not in session:
        return redirect("/login")

    if session["user"]["id"]==1:
        session["ismarion"]=True
        speakers=DB.getChats()
        session["chatid"]=speakers[0]["id"]
        return render_template("indexmarion.html", title="Marion", form=form,speakers=speakers,to=session["chatid"],browser=browser)
    else:
        #session["chatid"]=#session["user"]["id"]
        if "chatid" not in session:
            session["chatid"]=DB.getUserChatId(session["user"]["id"])
        session["access"]=DB.getUserAccess(session["user"]["id"])
        return render_template("index.html", title="Marion", form=form,to=session["chatid"],browser=browser,useraccess=session["access"])

@app.route('/login', methods=['GET', 'POST'])
def login():
    """
    if g.user and g.user.is_authenticated:
        flash("You are already logged in")
        return redirect('/index')
    """
    form = LoginForm()
    if form.validate_on_submit():
        """
        users=DB.userExists(form.username.data)
        if len(users) != 1:
            flash('User %s does not exist' %
                  (form.username.data))
            return render_template('login.html',
                                   title='Sign In',
                                   form=form)
        """
        #user = users.first()
        user=DB.checkUserPassword(form.username.data,encript(form.password.data))
        if not user:
        #if not user.check_password(form.password.data):
            flash('Mot de passe incorrect')
            return render_template('login.html',
                                   title='Sign In',
                                form=form)
        session["user"]=user

        if user["id"]==1:
            session["ismarion"]=True
            DB.setMarionStatus()
        else:
            session["chatid"]=DB.getUserChatId(session["user"]["id"])

        return redirect('/index')
    return render_template('login.html',
                           title='Sign In',
                           form=form)

@app.route('/messages',methods=['GET'])
def get_messages():
    #msgs = Message.query.order_by(Message.id.desc()).limit(20).all()[::-1]
    speakerID=request.args.get("id")
    lastMsg=request.args.get("last")
    msgs=False

    if speakerID:
        #marion custom speaker
        msgs = DB.getMessages(speakerID,lastMsg)
    else:
        #user with marion
        #print('session["chatid"]',session["chatid"])
        if "chatid" in session:
            msgs = DB.getMessages(session["chatid"],lastMsg)
    if msgs:
        return render_template("messages.html", messages=msgs,current=current_user)
    return ""

@app.route('/upload',methods=['GET', 'POST'])
def upload():
    if request.method == 'POST':
        f = request.files.get('file')
        extension=os.path.splitext(f.filename)[1]
        fileName="marion_"+str(session["user"]["id"])+str(time.time())+extension
        f.save(os.path.join('app/static/images',fileName))

        #save message

        chatid=int(request.values["to"])
        DB.saveMessage(session["user"]["id"],chatid, fileName,1)

    return render_template('uploaded.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = LoginForm()

    if form.validate_on_submit():
        username=form.username.data
        # Check if users with this name exists
        if DB.userExists(username):
            flash("Ce pseudonyme est déjà pris, merci d’en choisir un autre")
            return render_template('register.html',
                                   title='register',
                                   form=form)

        if len(form.password.data) < 5:
            flash("Le mot de passe doit contenir au moins 5 caractères")
            return render_template('register.html',
                                   title='register',
                                   form=form)

        #create user
        hashed=encript(form.password.data)
        userID,chatID=DB.createUser(username,1,hashed)
        session["user"]={"id":userID,"name":username}
        session["chatid"]=chatID

        return redirect("/index")
    return render_template('register.html',
                           title='register',
                           form=form)

@app.route('/guest')
def initguest():
    ts = int(time.time())
    username="guest_"+str(ts)
    userID,chatID=DB.createUser(username,0)
    session["user"]={"id":userID,"name":username}
    session["chatid"]=DB.getUserChatId(session["user"]["id"])
    #session["chatid"]=chatID

    print("user",session["user"],"chatid",session["chatid"])
    print("")

    session["ismarion"]=False
    #session["chatid"]=DB.getUserChatId(session["user"]["id"])
    #session["chatid"]=DB.getUserChatId(session["user"]["id"])

    return redirect("/index")


# MARION ADMIN :::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
@app.route('/archiveuser', methods=['GET'])
def archiveuser():
    if not isAdmin():
        return redirect("/")
    chatID=request.args.get("id")
    DB.archiveChat(chatID)
    return ""



@app.route('/markasseen', methods=['POST'])
def markasseen():
    #seenmessages=request.get_data(parse_form_data=False)
    seenmessages=request.form.getlist("seen[]")
    print("seenmessages",seenmessages)
    return ""

@app.route('/updatechatid', methods=['POST'])
def updatechatid():
    if not isAdmin():
        return redirect("/")
    chatID=request.form.get("chatid")

    session["chatid"]=chatID

    #update notseen to 0
    DB.removeNotSeen(chatID)
    #print("/messages?id="+str(chatID))
    #return redirect("/messages?id="+str(chatID))
    #print(session["chatid"])

    msgs = DB.getMessages(session["chatid"],False)

    return render_template("messages.html", messages=msgs,current=current_user)

@app.route('/speakers',methods=['GET'])
def get_speakers():
    speakerID=request.args.get("speaker")
    if not isAdmin():
        return redirect("/")
    DB.setMarionStatus()
    speakers=DB.getChats()
    return render_template("speakers.html", title="speakers", speakers=speakers,activespeaker=speakerID)

# END MARION ADMIN :::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::

@app.template_filter('strftime')
def _jinja2_filter_datetime(date, fmt=None):
    date = datetime.datetime.fromtimestamp(date)

    return date.strftime("%a %d %b %H:%M")


#SocketIO:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::


@socketio.on('imconnected')
def on_connect():
    print("imconnected recived")
    print(session)
    if "user" in session:
        print("userid",session["user"]["id"])
        print("NEW SESSION ",request.sid)
        #clients.append(request.sid)
        #room = session["user"]["id"]
        clients[session["user"]["id"]]=request.sid
        room=session.get('room')
        join_room(room)
        print("room",room)
        print("clients",clients)

        emit('welcome', {'userid': str(session["user"]["id"])},room=clients[session["user"]["id"]])


@socketio.on('heartbeat')
def heartbeat():
    #print("heartbeat")
    if "last" in session:
        last=session["last"]
        msgs = DB.getMessages(session["chatid"],last)
        htmlmessages=render_template("messages.html", messages=msgs,current=session["user"]["id"])
        emit("newmessages",htmlmessages,room=clients[session["user"]["id"]])
    emit("heartbeat")

@socketio.on('browser_ready')
def handle_browser_ready(data):
    print("GOT BROWSER READY!",data)
    if "chatid" in data["data"]:
        print("get messages from",data["data"]["chatid"])
        msgs = DB.getMessages(data["data"]["chatid"],False)
        session["chatid"]=int(data["data"]["chatid"])
        session["user"]["id"]=int(data["data"]["speakerid"])
    else:
        msgs = DB.getMessages(session["chatid"],False)

    htmlmessages=render_template("messages.html", messages=msgs,current=current_user)
    #XXX FIX NEXT LINE
    emit("initmessages",htmlmessages,room=clients[session["user"]["id"]])
    emit("heartbeat")

@socketio.on('post')
def handle_post(data):
    print("POSTED NEW MESSAGE",session["user"]["id"],data)
    message=data["message"]
    last=False
    if "last" in data:
        last=data["last"]
        session["last"]=last
    if session["ismarion"]:
        print("SAVING MESSAGE IS MARION WRITING")
        print("SESSION USER ID",session["user"]["id"])
        #chatid=1
        #print("chatid marion",chatid)
        DB.saveMessage(1,session["chatid"], message)
    else:
        DB.saveMessage(session["user"]["id"],session["chatid"], message)

    msgs = DB.getMessages(session["chatid"],last)


    if bot:
        #https://stackoverflow.com/questions/34581255/python-flask-socketio-send-message-from-thread-not-always-working
        bott=socketio.start_background_task(BOT.manageTalk,session["user"]["id"],session["chatid"],message,DB,msgs,botError)

    htmlmessages=render_template("messages.html", messages=msgs,current=session["user"]["id"])
    #print("htmlnewmessages",htmlmessages)
    print("EMIT TO",clients[session["user"]["id"]])
    emit("newmessages",htmlmessages,room=clients[session["user"]["id"]])

#functions::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::

def botError(nothing):
    emit("boterror",True)

def isAdmin():
    if session["ismarion"]:
        return True
    return False

def encript(password):
    hashed=hashlib.md5(password.encode('utf-8'))
    hashed=str(hashed.hexdigest())
    return hashed
