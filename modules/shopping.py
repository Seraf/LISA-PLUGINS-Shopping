# -*- coding: UTF-8 -*-
import urllib, json, os, inspect
from pymongo import MongoClient
from lisa import configuration

import gettext

path = os.path.realpath(os.path.abspath(os.path.join(os.path.split(
    inspect.getfile(inspect.currentframe()))[0],os.path.normpath("../lang/"))))
_ = translation = gettext.translation(domain='shopping', localedir=path, languages=[configuration['lang']]).ugettext

class Shopping:
    def __init__(self):
        self.configuration_lisa = configuration
        self.mongo = MongoClient(self.configuration_lisa['database']['server'],
                            self.configuration_lisa['database']['port'])
        self.configuration = self.mongo.lisa.plugins.find_one({"name": "Shopping"})
        self.build_default_list()
        self.answer = None

    def build_default_list(self):
        shoppingList = self.mongo.lisa.plugins.find_one({'_id': self.configuration['_id'], "lists.DefaultList": {"$exists": True}})
        if not shoppingList:
            self.mongo.lisa.plugins.update(
                 {'_id': self.configuration['_id']},
                 {
                     "$setOnInsert": {
                         'lists.DefaultList.name': 'DefaultList',
                         'lists.DefaultList.items': []
                     }
                 },
                 upsert=True
             )

    def list(self, jsonInput):
        shoppingList = self.mongo.lisa.plugins.find_one({'_id': self.configuration['_id'], "lists.DefaultList": {"$exists": True}})
        print shoppingList
        if shoppingList:
            listitem = []
            for item in shoppingList['lists']['DefaultList']['items']:
                if 'quantity' in item:
                    listitem.append(item['name'] + '(' + item['quantity'] + ')')
                else:
                    listitem.append(item['name'])
            self.answer = _(' then ').join(listitem)
        else:
            self.answer = _('no list')
        return {"plugin": "Shopping",
                "method": "list",
                "body": self.answer
        }

    def add(self, jsonInput):
        print self.mongo.lisa.plugins.find_one({'_id': self.configuration['_id'],
                'lists.DefaultList.items.name': jsonInput['outcome']['entities']['shopping_item']['value']})
        self.mongo.lisa.plugins.update(
            {
                '_id': self.configuration['_id']
            },
            {
                '$addToSet': {'lists.DefaultList.items': {'name': jsonInput['outcome']['entities']['shopping_item']['value']}}
            },
            upsert=True
        )
        self.answer = _('product added to the list')
        return {"plugin": "Shopping",
                "method": "add",
                "body": self.answer
        }