import requests
import json
import urllib.parse

from .document import Document


class CouchDBException(Exception):
    response: requests.Response


class CouchDB:
    def __init__(self, username: str, password: str, db: str, host: str = 'localhost', port: int = 5984, scheme: str = 'http'):
        self.base_url = f'{scheme}://{username}:{password}@{host}:{port}/'
        self.db_name = db

    def req(self,
            endpoint: str,
            method: str = 'GET',
            data: dict | None = None,
            query_params: dict | None = None):
        if query_params is not None:
            params = '?' + urllib.parse.urlencode(query_params)
        else:
            params = ''
        response = requests.request(
            method,
            self.base_url + self.db_name + '/' + endpoint + params,
            json=data if data is not None else {})
        
        if not response.ok:
            ex = CouchDBException(response.content)
            ex.response = response
            raise ex

        return json.loads(response.text)

    def get_all_documents(self, skip: int | None = None, limit: int | None = None):
        params = {
            'include_docs': True
        }
        if skip is not None:
            params['skip'] = skip
        if limit is not None:
            params['limit'] = limit

        result = []
        for doc in self.req('_all_docs', 'GET', query_params=params)['rows']:
            if not doc['id'].startswith('_design'):  # ignore design documents
                result.append(Document(self, doc['doc']))
        return result


    def get_document(self, document_id: str):
        try:
            return Document(self, self.req(document_id, 'GET'))
        except CouchDBException as e:
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
        for doc in self.req('_find', 'POST', data)['docs']:
            result.append(Document(self, doc))
        return result

    def document(self, data: dict | None = None):
        return Document(self, data)
