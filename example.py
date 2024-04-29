import couchdb_client

db = couchdb_client.CouchDB('admin', 'admin', 'database')

# create a document instance
doc = db.document({
    'host': 'test',
    'port': 25555
})
doc.create()  # create the document in the database

print(db.get_document(doc.id))  # get the document
# note: doc.id is the same as doc['_id']

# update the document
doc['host'] = 'test2'
doc.update()

# get the document again to the the updated data
print(db.get_document(doc.id))
