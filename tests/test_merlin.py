import unittest
from urllib import quote_plus as enc

from merlin import Merlin
from merlin.facet import Facet as F
from merlin.search import Search

class MerlinTest(unittest.TestCase):

    def setUp(self):
        pass

    def test_simple_search(self):
        s = Search(q="shirt")
        self.assertEquals(s.build(), "search?q=shirt")

    def test_simple_search_1(self):
        s = Search(q="", num=10)
        self.assertEquals(s.build(), "search?q=&num=10")

    def test_simple_search_2(self):
        s = Search(q="shirt", num=10, start=20)
        self.assertEquals(s.build(), "search?q=shirt&start=20&num=10")

    def test_enum_facet(self):
        s = Search(
            q = "shirt", 
            facets = F.enum("brand", num=10)
        )
        self.assertEquals(s.build(), 
            "search?q=shirt&facet=" + enc("field=brand/type=enum/num=10")
        )

    def test_enum_facet_named(self):
        s = Search(
            q = "shirt", 
            facets = F.enum("brand", num=10, key='ponies')
        )
        self.assertEquals(s.build(), 
            "search?q=shirt&facet=" + enc("field=brand/type=enum/key=ponies/num=10")
        )

    def test_enum_facet_excluding(self):
        s = Search(
            q = "shirt", 
            facets = F.enum("brand", num=10, key='ponies', exclude=['foo', 'bar'])
        )
        self.assertEquals(s.build(), 
            "search?q=shirt&facet=" + 
            enc("field=brand/type=enum/key=ponies/num=10/ex=foo,bar")
        )

if __name__ == '__main__':
    unittest.main()
