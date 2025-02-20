import typing
if typing.TYPE_CHECKING:
    from .document import Document

class Attachment:
    document: 'Document'
    name: str
    content_type: str
    length: int
    _data: bytes
    is_stub: bool

    def __init__(self, document: 'Document', name: str, data: bytes = bytes(), is_stub: bool = False):
        self.document = document
        self.name = name
        self.data = data
        self.is_stub = is_stub  # stub is an attachment of which we don't have the data (yet)
        if not self.is_stub:
            pass
            # TODO: insert into db & resolve content_type, length

    @classmethod
    def from_stub(cls, document: 'Document', name: str, content_type: str, length: int):
        att = Attachment(document, name, is_stub=True)
        att.content_type = content_type
        att.length = length
        att.is_stub = True
        return att

    @property
    def data(self) -> bytes:
        if self.is_stub:  # we don't have the data, fetch it from the db
            self._data = self.document.db.req(f'{self.document.id}/{self.name}').content
        return self._data
    @data.setter
    def data(self, value: bytes):
        self._data = value

    def __repr__(self):
        return f'<Attachment "{self.name}" {self.content_type}>'