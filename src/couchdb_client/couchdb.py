import requests
import json
import urllib.parse

from .document import Document

class CouchDBException(Exception):
    response: requests.Response

    def __init__(self, message):
        try:  # try to parse the error message
            error_data = json.loads(message)
            message = f'{error_data["error"]}: {error_data["reason"]}'
        except:
            message = f'CouchDB returned {message}'

        super().__init__(message)


class CouchDB:
    def __init__(self,
                 username: str,
                 password: str,
                 db: str,
                 host: str = 'localhost',
                 port: int = 5984,
                 scheme: str = 'http',
                 base_path: str = ''):
        self.base_url = f'{scheme}://{username}:{password}@{host}:{port}/{base_path}'
        self.db_name = db

    def req(self,
            endpoint: str,
            method: str = 'GET',
            data: dict = None,
            query_params: dict = None) -> dict | list:
        if query_params is not None:
            query_params = {k: v for k, v in query_params.items() if v}  # remove None values
            params = '?' + urllib.parse.urlencode(query_params)
        else:
            params = ''

        if data is not None:
            data = {k: v for k, v in data.items() if v}  # remove None values
        response = requests.request(
            method,
            self.base_url + self.db_name + '/' + endpoint + params,
            json=data, verify=False)

        if not response.ok:
            ex = CouchDBException(response.content)
            ex.response = response
            raise ex

        return json.loads(response.text)

    def get_all_documents(self, skip: int = None, limit: int = None) -> list[Document]:
        params = {
            'include_docs': True,
            'skip': skip,
            'limit': limit
        }

        result = []
        for doc in self.req('_all_docs', 'GET', query_params=params)['rows']:
            if not doc['id'].startswith('_design'):  # ignore design documents
                result.append(Document(self, doc['doc']))
        return result

    def get_document(self, document_id: str) -> Document | None:
        try:
            return Document(self, self.req(document_id, 'GET'))
        except CouchDBException as e:
            if e.response.status_code == 404:
                return None
            else:
                raise e

    def find_documents(
        self,
        selector: dict,
        fields: dict = None,
        sort: list = None,
        limit: int = None,
        skip: int = None
    ) -> list[Document]:
        data = {
            'selector': selector,
            'fields': fields,
            'sort': sort,
            'limit': limit,
            'skip': skip
        }

        result = []
        for doc in self.req('_find', 'POST', data)['docs']:
            result.append(Document(self, doc))
        return result

    def find_one_document(self, selector: dict, fields: dict = None, sort: list = None, skip: int = None) -> Document | None:
        result = self.find_documents(selector, fields, sort, 1, skip)
        if not result:
            return None
        return result[0]

    def create_documents(self, documents: list[Document]) -> list[Document]:
        docs_data = list(map(lambda d: d.data, documents))
        result = self.req('_bulk_docs', 'POST', {'docs': docs_data})
        return_documents = []
        for doc in documents:
            inserted = [d for d in result if d['id'] == doc.id][0]  # retrieve the inserted object
            if inserted['ok']:
                doc['_rev'] = inserted['rev']
                return_documents.append(doc)
        return return_documents

    def get_view(self,
        design_doc: str,
        view: str,
        key: str,
        limit: int = None,
        skip: int = None,
        include_docs: bool = False
    ) -> list[dict]:
        params = {
            'key': key,
            'limit': limit,
            'skip': skip,
            'include_docs': include_docs
        }
        rows = self.req(f'_design/{design_doc}/_view/{view}', query_params=params)['rows']
        if include_docs:
            for i in range(len(rows)):
                rows[i]['doc'] = self.document(rows[i]['doc'])
        return rows

    def document(self, data: dict = None) -> Document:
        return Document(self, data)
