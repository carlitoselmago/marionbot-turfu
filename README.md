# marionbot-turfu

python 3.6
tensorflow 2.1.0
tensorflow-estimator=2.1.0


#installation
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
