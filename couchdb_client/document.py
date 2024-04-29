import uuid
import typing

if typing.TYPE_CHECKING:
    from .couchdb import CouchDB


class Document:
    data = {}

    def __init__(self, db: 'CouchDB', data: dict | None = None):
        if data is not None:
            self.data = data

        if '_id' not in data:
            self.data['_id'] = str(uuid.uuid4())

        self.id = self.data['_id']

        self.db = db

    def update(self):
        if '_rev' not in self.data:
            document = self.db.get_document(self.id)
            self.data['_rev'] = document['_rev']
        return self.db.req(self.id, 'PUT', self.db.db_name, self.data)

    def create(self):
        return self.db.req(self.id, 'PUT', self.db.db_name, self.data)

    def __getitem__(self, key):
        print('getting', key)
        return self.data[key]

    def __setitem__(self, key, value):
        self.data[key] = value

    def __repr__(self):
        return f'<{self.__class__.__name__} {self.data}>'
