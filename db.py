from datetime import datetime

from peewee import *

db = SqliteDatabase('user_history.db')


class RequestHistory(Model):
    user_id = IntegerField()
    query = TextField()
    timestamp = DateTimeField(default=datetime.now)

    class Meta:
        database = db


db.connect()
db.create_tables([RequestHistory])
