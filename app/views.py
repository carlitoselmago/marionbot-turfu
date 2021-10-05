from app import app, db, lm
from flask import render_template, flash, redirect, session, url_for, request, g
from flask import request

from flask_login import login_user, logout_user, current_user, login_required
from .forms import LoginForm, MessageForm, PasswordForm, DeleteUser
from .models import User, Message
from app.db import db
import datetime
import time
import hashlib
import locale
import urllib.request
import os
from flask_uploads import UploadSet, configure_uploads, IMAGES, patch_request_class
from app.botAIapi.botapi import botapi

locale.setlocale(locale.LC_TIME, "fr_FR.UTF-8")

bot=True



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


photos = UploadSet('photos', IMAGES)
configure_uploads(app, photos)
patch_request_class(app)  # set maximum file size, default is 16MB

DB=db()
BOT=botapi()

dropzone = Dropzone(app)

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

#ESTO SE SUBSTITUYE::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
@app.route('/post', methods=['POST'])
def post():
    form = MessageForm()

    # Handle the case when we send a message
    #if form.validate_on_submit():


    if "chatid" not in session:
        session["chatid"]=DB.getUserChatId(session["user"]["id"])

    #alert marion
    if not session["ismarion"]:
        #if not DB.ismarionOnline():

        ##TEMPORARY TILL WE USE SSL
        urllib.request.urlopen('https://maker.ifttt.com/trigger/user_talks/with/key/co3YbjnMnanNOITh4W6vQp')
        print("marion will be notified!!!!!")
        ##REMOVE ON SSL

        lastTimeNotified=int(DB.getLastTimeNotified())
        #margin=60*60 #1hour
        margin=60*1 #1minute
        if (lastTimeNotified+margin)<time.time():
            #urllib.request.urlopen('https://maker.ifttt.com/trigger/user_talks/with/key/co3YbjnMnanNOITh4W6vQp')
            DB.updateGlobal("lasttimenotified",int(time.time()))
            #print("marion will be notified!!!!!")

    # Adding the message to the database
    if session["ismarion"]:
        chatid=request.form["to"]
        print("chatid marion",chatid)
        DB.saveMessage(session["user"]["id"],chatid, form.message.data)
    else:

        DB.saveMessage(session["user"]["id"],session["chatid"], form.message.data)
    #Message.create(g.user, form.message.data)
    # We redirect, we do not render the template. Otherwise
    # the form will be filled again.
    lastMsg=request.args.get("last")

    msgs = DB.getMessages(session["chatid"],lastMsg)
    #print("msgs",msgs)
    #msgs = Message.query.order_by(Message.id.desc()).limit(20).all()[::-1]

    if bot:
        BOT.manageTalk(session["user"]["id"],session["chatid"],form.message.data,DB,msgs)

    return render_template("messages.html", messages=msgs,current=current_user)
    #return redirect("/index")


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
        return render_template("index.html", title="Marion", form=form,to=session["chatid"],browser=browser)


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


@app.route('/guest')
def initguest():
    ts = int(time.time())
    username="guest_"+str(ts)
    userID,chatID=DB.createUser(username,0)
    session["user"]={"id":userID,"name":username}
    session["chatid"]=chatID
    return redirect("/index")

@app.route('/images',methods=['GET'])
def showImage():
    return ""

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

@app.route('/speakers',methods=['GET'])
def get_speakers():
    speakerID=request.args.get("speaker")
    if not isAdmin():
        return redirect("/")
    DB.setMarionStatus()
    speakers=DB.getChats()
    return render_template("speakers.html", title="speakers", speakers=speakers,activespeaker=speakerID)


@lm.user_loader
def load_user(id):
    return User.query.get(int(id))


@app.before_request
def before_request():
    g.user = current_user


@app.route('/admin/user/delete', methods=['POST'])
def delete_user():
    if not isAdmin():
        return redirect("/")
    form = DeleteUser()
    if form.validate_on_submit():

        u = User.find(form.username.data)

        if u.username == g.user.username:
            flash("You cannot remove yourself")
            return redirect('/admin/user/list')
        if u:
            db.session.delete(u)
            db.session.commit()
    return redirect('/admin/user/list')

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

@app.route('/admin/user/add', methods=['GET', 'POST'])
def adduser():
    if not isAdmin():
        return redirect("/")

    form = LoginForm()
    if form.validate_on_submit():
        # Check if users with this name exists
        if len(form.password.data) < 5:
            flash("Password should be at least 5 chars")
            return render_template('adduser.html',
                                   title='Add User',
                                   form=form)
        # Let's create the user
        if User.create(form.username.data, form.password.data):
            return redirect('/admin/user/list')

    return render_template('adduser.html',
                           title='Add User',
                           form=form)


@app.route('/admin/user/change-password', methods=['POST'])
def change_password():
    if not isAdmin():
        return redirect("/")
    form = PasswordForm()
    u = User.query.filter(User.username == form.username.data)
    if u.count() != 1:
        flash("did not found user {}".format(form.username.data))
        return redirect("/admin/user/list")
    if len(form.password.data) < 5:
        flash("message length too small")
        return redirect("/admin/user/list")
    user_to_modify = u.first()
    user_to_modify.set_password(form.password.data)
    db.session.commit()
    return redirect("/admin/user/list")

@app.route('/admin/user/list', methods=['GET'])
def list_users():

    # If the user is not admin, he comes
    if not isAdmin():
        return redirect("/")
    #allusers=User.query.all()
    allusers=DB.getUsers()
    print(allusers)
    forms={}
    forms_delete={}
    for u in allusers:
        forms[u["name"]] = PasswordForm(username=u["name"])
        forms_delete[u["name"]] = DeleteUser(username=u["name"])
    return render_template('listusers.html',
                           title='List Users',
                           users=allusers,
                           forms=forms,
                           forms_delete=forms_delete)


@app.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    form = PasswordForm(username=g.user.username)
    if form.validate_on_submit():
        g.user.set_password(form.password.data)
        db.session.commit()
        return redirect('/index')
    return render_template('profile.html',
                           title='Profile',
                           form=form)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.errorhandler(404)
def not_found_error(error):
    flash("Page not found")
    return redirect("/")


@app.errorhandler(500)
def internal_error(error):
    flash("Internal error")
    return redirect("/")

@app.template_filter('strftime')
def _jinja2_filter_datetime(date, fmt=None):
    date = datetime.datetime.fromtimestamp(date)

    return date.strftime("%a %d %b %H:%M")


def isAdmin():
    if session["ismarion"]:
        return True
    return False

def encript(password):
    hashed=hashlib.md5(password.encode('utf-8'))
    hashed=str(hashed.hexdigest())
    return hashed
