import couchdb_client

db = couchdb_client.CouchDB('admin', 'admin', 'database')

print(db.find_document({
    'port': {
        '$gte': 25566
    }
}))
