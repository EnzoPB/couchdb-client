import requests
import json
import uuid

from .document import Document


class CouchDB:
    def __init__(self, username: str, password: str, db: str, host: str = 'localhost', port: int = 5984):
        self.base_url = f'http://{username}:{password}@{host}:{port}/'
        self.db_name = db

    def req(self,
            endpoint: str,
            method: str = 'GET',
            db: str | None = None,
            data: dict | None = None):
        data = requests.request(
            method,
            self.base_url + (db+'/' if db is not None else '') + endpoint,
            json=data if data is not None else {})
        return json.loads(data.text)

    def get_document(self, document_id: str):
        try:
            return Document(self, self.req(document_id, 'GET', self.db_name))
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 404:
                return None
            else:
                raise e

    def find_document(self, selector: dict, fields: dict = None, sort: list = None, limit: int = None, skip: int = None):
        data = {
            'selector': selector
        }
        if sort is not None:
            data['sort'] = sort
        if fields is not None:
            data['fields'] = fields
        if limit is not None:
            data['limit'] = limit
        if skip is not None:
            data['skip'] = skip

        result = []
        for doc in self.req('_find', 'POST', self.db_name, data)['docs']:
            result.append(Document(self, doc))
        return result

    def document(self, data: dict | None = None):
        return Document(self, data)