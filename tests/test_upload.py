import unittest
from urllib import quote_plus as enc

from merlin import Uploader
from merlin.upload import Add, Update, Upsert, Delete

class UploadTest(unittest.TestCase):
    def setUp(self):
        self.uploader = Uploader('blackbird', 'dev', 'client_test',
            username='foo@bar.com', 
            authtoken='123')

    def testUploadUrl(self):
        noops = [Add(), Update(), Delete()]
        for noop, ep in zip(noops, ['add', 'update', 'delete']):
            res = self.uploader(noop)
            self.assertEquals(res._build_url(), 
                "https://upload-dev.search.blackbird.am/%s?" % ep +
                "user="+enc("foo@bar.com") + "&token=123&company_id=blackbird&env=dev&"\
                "instance_name=client_test")

class UploadEngineTest(unittest.TestCase):

    def setUp(self):
        self.uploader = Uploader('blackbird', 'dev', 'client_test',
            username='blackbird@blackbird.am', 
            authtoken='b98980347a334d5c9ecd58438250e59c',
            host='falcon1.local:9300',
            use_ssl=False)

    def tearDown(self):
        deleter = Delete()
        deleter.delete_doc("123")
        with self.uploader(deleter) as results:
            pass

    def testSimpleUpload(self):
        "Tests simple uploader"
        doc = {"id": "123", "title": "red dress"}
        adder = Add()

        adder.add_doc(doc)
        with self.uploader(adder) as results:
            self.assert_(results.success, "Failed!")

    def testBadUpload(self):
        "Tests missing ID"
        doc = {"idd": "123", "title": "red dress"}
        adder = Add()

        adder.add_doc(doc)
        with self.uploader(adder) as results:
            self.assert_(not results.success, "Should have failed!")

    def testUpdate(self):
        self.testSimpleUpload()
        updater = Update()
        updater.update_doc({"id": "123", "title": 'redd dress'})
        with self.uploader(updater) as results:
            self.assert_(results.success, "Should have worked!")

    def testUpsert(self):
        upserter = Upsert()
        upserter.update_doc({"id": "123", "title": 'redd dress'})
        with self.uploader(upserter) as results:
            self.assert_(results.success, "Should have worked!")

if __name__ == '__main__':
    unittest.main()
