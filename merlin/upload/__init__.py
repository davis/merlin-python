from collections import namedtuple
import json

UploadResults = namedtuple('UpResults', 'msg,status,success')

class IndexOp(object):
    endpoint = None
    def __init__(self, index='subjects'):
        self.index = index
        self.docs = []

    def build_json(self):
        return json.dumps({self.index: [{"data": self.docs}]})
    
    @staticmethod
    def process_results(raw):
        data = json.loads(raw)
        return UploadResults(data['msg'], data['status'], data['success'])

class Add(IndexOp):
    endpoint = 'add'
    def add_doc(self, doc):
        assert isinstance(doc, dict)
        self.docs.append(doc)

    def add_docs(self, it):
        for i in it:
            self.add_doc(doc)

class Update(IndexOp):
    endpoint = 'update'

    def update_doc(self, doc):
        assert isinstance(doc, dict)
        self.docs.append(doc)

    def update_docs(self, it):
        for i in it:
            self.delete_doc(doc)

class Delete(IndexOp):
    endpoint = 'delete'

    def delete_doc(self, doc):
        if isinstance(doc, (int, long, basestring)):
            doc = {"id": doc}

        assert isinstance(doc, dict)
        self.docs.append(doc)

    def delete_docs(self, it):
        for i in it:
            self.delete_doc(doc)

