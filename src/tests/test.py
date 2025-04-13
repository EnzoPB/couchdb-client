import unittest
import uuid
from context import couchdb_client


class TestCouchDBClient(unittest.TestCase):
    def setUp(self):
        self.client = couchdb_client.CouchDB(
            username='admin',
            password='admin',
            db=f'tests-{uuid.uuid4()}'
        )
        self.client.req_json('', 'PUT', {'id': 'tests', 'name': 'tests'})

    def tearDown(self):
        self.client.req_json('', 'DELETE')

    def test_create_document(self):
        """Test basic document creation"""
        doc_data = {'name': 'Test Document'}
        doc_in = self.client.document(doc_data)
        doc_in.create()

        # verify if document exists
        doc_out = self.client.get_document(doc_in.id)
        self.assertEqual(doc_out.data['name'], 'Test Document')

        # check if the revision has been updated in the original doc
        self.assertEqual(doc_in['_rev'], doc_out['_rev'])

    def test_create_multiple_documents(self):
        """Test basic bulk documents creation"""
        docs_data = [self.client.document({'name': 'Test Document', 'i': i}) for i in range(10)]
        self.client.create_documents(docs_data)

        # verify if documents exists
        # TODO: check with ids
        docs_out = self.client.find_documents({
            'name': 'Test Document',
            'i': {'$lt': 10}
        })
        self.assertEqual(10, len(docs_out))

    def test_get_bulk_documents(self):
        """Test get mulitple documents at once"""
        docs_data = [self.client.document({'name': 'Test Document', 'i': i}) for i in range(10)]
        self.client.create_documents(docs_data)

        ids = [d.id for d in docs_data]

        docs_check = self.client.get_bulk_documents(ids)
        self.assertListEqual(docs_check, docs_data)

    def test_get_nonexistent_document(self):
        """Test error handling for missing document"""
        self.assertIsNone(self.client.get_document('non_existent_id'))

    def test_update_document(self):
        """Test document update workflow"""
        # create initial document
        doc = self.client.document({'counter': 1})
        doc.create()
        original_data = doc.data.copy()

        # update document
        doc.data['counter'] = 2
        doc.update()

        # check if revision has been updated
        self.assertNotEqual(original_data['_rev'], doc.data['_rev'])

        # verify update
        updated = self.client.get_document(doc.id)
        self.assertEqual(updated['counter'], 2)

    def test_delete_document(self):
        """Test document deletion"""
        doc = self.client.document({'toBe': 'deleted'})
        doc.create()

        # delete document
        doc.delete()

        # verify deletion
        self.assertIsNone(self.client.get_document(doc.id))

    def test_attachment(self):
        """Test document attachment creation & read"""
        doc_in = self.client.document({})
        doc_in.create()

        doc_in.add_attachment('testfile', b'1234')

        doc = self.client.get_document(doc_in.id)

        self.assertEqual(doc.attachments[0].data, b'1234')


if __name__ == '__main__':
    unittest.main()