# marionbot-turfu

## Tested on ##
python 3.6
tensorflow 2.1.0


## Installation ##
create a sql database with collation "utf8mb4_general_ci" and load marionbot.sql to create tables

There will be a admin user with username "admin" and password "paZZworDXZ"


create a file "settings.py" in /app with the var:
```python
dbsettings={"host":"localhost",
            "username":"admin",
            "password":"password",
            "dbname":"marion-turfu"
            }
```

#web server

If you plan to deploy the webserver to a domain name, add your domain (and use SSL) to app/chat.py : line 52


#Data preparation

(OPTIONAL) tensorboard --logdir transfchatbot/logs
