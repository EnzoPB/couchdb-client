import unittest
from ..couchdb_client import CouchDB


class TestCouchDBClient(unittest.TestCase):
    def setUp(self):
        self.client = CouchDB(
            username='admin',
            password='admin',
            db='tests'
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


if __name__ == '__main__':
    unittest.main()