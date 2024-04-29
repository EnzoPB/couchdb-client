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
        result = self.db.req(self.id, 'PUT', self.data)
        self.data['_rev'] = result['rev']
        return result

    def create(self):
        return self.db.req(self.id, 'PUT', self.data)

    def delete(self):
        d = self.db.req(self.id, 'DELETE', None, {
            'rev': self.data['_rev']
        })
        return d

    def __getitem__(self, key: str):
        return self.data[key]

    def __setitem__(self, key: str, value):
        self.data[key] = value

    def __repr__(self):
        return f'<{self.__class__.__name__} {self.data}>'
