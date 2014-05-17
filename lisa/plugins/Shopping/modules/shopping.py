# -*- coding: UTF-8 -*-
from lisa.server.plugins.IPlugin import IPlugin
import gettext
import inspect
import os


class Shopping(IPlugin):
    def __init__(self):
        super(Shopping, self).__init__()
        self.configuration_plugin = self.mongo.lisa.plugins.find_one({"name": "Shopping"})
        self.path = os.path.realpath(os.path.abspath(os.path.join(os.path.split(
            inspect.getfile(inspect.currentframe()))[0],os.path.normpath("../lang/"))))
        self._ = translation = gettext.translation(domain='shopping',
                                                   localedir=self.path,
                                                   fallback=True,
                                                   languages=[self.configuration_lisa['lang']]).ugettext
        self.build_default_list()
        self.answer = None

    def build_default_list(self):
        shoppingList = self.mongo.lisa.plugins.find_one({'_id': self.configuration_plugin['_id'], "lists.DefaultList": {"$exists": True}})
        if not shoppingList:
            self.mongo.lisa.plugins.update(
                 {'_id': self.configuration_plugin['_id']},
                 {
                     "$set": {
                         'lists.DefaultList.name': 'DefaultList',
                         'lists.DefaultList.items': []
                     }
                 },
                 upsert=True
             )

    def list(self, jsonInput):
        shoppingList = self.mongo.lisa.plugins.find_one({'_id': self.configuration_plugin['_id'], "lists.DefaultList": {"$exists": True}})
        print shoppingList
        if shoppingList:
            listitem = []
            for item in shoppingList['lists']['DefaultList']['items']:
                if 'quantity' in item:
                    listitem.append(item['name'] + '(' + item['quantity'] + ')')
                else:
                    listitem.append(item['name'])
            self.answer = self._(' then ').join(listitem)
        else:
            self.answer = self._('no list')
        return {"plugin": "Shopping",
                "method": "list",
                "body": self.answer
        }

    def add(self, jsonInput):
        self.mongo.lisa.plugins.update(
            {
                '_id': self.configuration['_id']
            },
            {
                '$addToSet': {'lists.DefaultList.items': {'name': jsonInput['outcome']['entities']['shopping_item']['value']}}
            },
            upsert=True
        )
        self.answer = self._('product added to the list')
        return {"plugin": "Shopping",
                "method": "add",
                "body": self.answer
        }

    def delete(self, jsonInput):
        self.mongo.lisa.plugins.update(
            {
                '_id': self.configuration_plugin['_id']
            },
            {
                '$pull': {'lists.DefaultList.items': {'name': jsonInput['outcome']['entities']['shopping_item']['value']}}
            },
            upsert=True
        )
        self.answer = self._('product deleted')
        return {"plugin": "Shopping",
                "method": "delete",
                "body": self.answer
        }