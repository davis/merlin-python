import unittest
from urllib import quote_plus as enc

from merlin import Merlin
from merlin.filter import Field, NF
from merlin.vrec import Vrec

class VrecTest(unittest.TestCase):

    def test_simple_vrec(self):
        s = Vrec(id="a1234")
        self.assertEquals(s.build(), "vrec?id=a1234")

    def test_simple_vrec_1(self):
        s = Vrec(id="a1234", num=10)
        self.assertEquals(s.build(), "vrec?id=a1234&num=10")

    def test_fields(self):
        s = Vrec(
            id = "asdf235",
            fields=["one", "two", "three"]
        )
        self.assertEquals(s.build(), 
            "vrec?id=asdf235" + 
            '&fields=' + enc("one,two,three")
        )

    def test_multi_filters(self):
        s = Vrec(
            id="abcd1234",
            filter=[
                NF.cnf(
                    (Field('Color') == 'Red') & (Field('Color') != 'Blue')
                ),
                NF.dnf(
                    Field('Price').between(0, 100)
                )
            ]
        )
        self.assertEquals(s.build(), 
            "vrec?id=abcd1234" + 
            '&filter=' + enc(r"exp=Color:Red,Color:!Blue/type=cnf") +
            '&filter=' + enc(r"exp=Price:[0:100]/type=dnf")
        )

class EngineTest(unittest.TestCase):

    def setUp(self):
        self.engine = Merlin('blackbird', 'dev', 'agathon')

    def test_simple_id(self):
        doc_id = '111f49eacc7dbc9ab2df53f8ce52ec64'
        s = Vrec(id=doc_id)
        with self.engine(s) as r:
            self.assertEquals(r.hits.numFound, 2)
            self.assertEquals(r.doc['id'], doc_id)
            self.assertEquals(r.hits[0]['id'], 'c05ef333b5dbd9f31123a65221762395')
            self.assertEquals(r.hits[1]['id'], 'a873aa71028568e76d473f9f4ecf770e')
    
if __name__ == '__main__':
    unittest.main()
