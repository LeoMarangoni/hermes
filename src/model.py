"""Database manipulation module."""
import json
from config import dbconfig
from flask import Flask
from flask_mongoengine import MongoEngine

app = Flask(__name__)

app.config['MONGODB_SETTINGS'] = dbconfig

db = MongoEngine(app)


class CustomFilters(db.QuerySet):
    def filter_by_status(self, status):
        return self.filter(info__status=status)


class AccountInfo(db.EmbeddedDocument):
    name = db.StringField()
    status = db.StringField(default='idle')


class AccountCredentials(db.EmbeddedDocument):
    user1 = db.StringField(required=True, default="")
    user2 = db.StringField(required=True, default="")
    password1 = db.StringField()
    password2 = db.StringField()


class Accounts(db.EmbeddedDocument):
    meta = {'queryset_class': CustomFilters}
    info = db.EmbeddedDocumentField(AccountInfo,
                                    required=True,
                                    default=AccountInfo)
    credentials = db.EmbeddedDocumentField(AccountCredentials,
                                           required=True,
                                           default=AccountCredentials)


class ProjectInfo(db.EmbeddedDocument):
    meta = {'queryset_class': CustomFilters}
    name = db.StringField()
    status = db.StringField(default="idle")
    protocol = db.StringField(choices=["imap", "zimbra"],
                              required=True)
    threads = db.IntField(default=1)


class Projects(db.Document):
    info = db.EmbeddedDocumentField(ProjectInfo, default=ProjectInfo)
    configs = db.DynamicField()
    accounts = db.EmbeddedDocumentListField(Accounts)


class Queue(db.Document):
    index = db.IntField()  # Projects['project']['account_list'][<index>]
    projectId = db.StringField()
    command = db.StringField()
