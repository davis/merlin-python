import unittest
from merlin import Merlin
from merlin.facet import Facet
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

    def test_facetted_search(self):
        pass

if __name__ == '__main__':
    unittest.main()
