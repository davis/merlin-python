import unittest
from urllib import quote_plus as enc

from merlin import Merlin
from merlin.facet import Facet as F
from merlin.filter import Field, NF
from merlin.sort import Sort as S
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

    def test_hist_facet(self):
        s = Search(
            q = "shirt", 
            facets = F.hist("price", start=10, end=100, gap=5, key='prices')
        )
        self.assertEquals(s.build(), 
            "search?q=shirt&facet=" + 
            enc("field=price/type=hist/key=prices/range=[10:100:5]")
        )

    def test_range_facet(self):
        s = Search(
            q = "shirt", 
            facets = F.range("price", key='prices')
        )
        self.assertEquals(s.build(), 
            "search?q=shirt&facet=" + 
            enc("field=price/type=range/key=prices")
        )

    def test_multiple_facets(self):
        s = Search(
            q = "shirt", 
            facets = [
                F.enum('brand', num=10, key='top_brands'),
                F.hist('price', start=0, end=100, gap=10)
            ]
        )
        self.assertEquals(s.build(), 
            "search?q=shirt" + 
            '&facet=' + enc("field=brand/type=enum/key=top_brands/num=10") +
            '&facet=' + enc("field=price/type=hist/range=[0:100:10]")
        )

    def test_sorting(self):
        s = Search(
            q = "pants", 
            sort = [
                S.desc('brand'),
                S.asc('price')
            ]
        )
        self.assertEquals(s.build(), 
            "search?q=pants" + 
            '&sort=' + enc("brand:desc,price:asc")
        )

    def test_fields(self):
        s = Search(
            q = "socks",
            fields=["one", "two", "three"]
        )
        self.assertEquals(s.build(), 
            "search?q=socks" + 
            '&fields=' + enc("one,two,three")
        )

    def test_filters(self):
        s = Search(
            filter=NF.cnf(
                (Field('Color') == 'Red') & (Field('Color') != 'Blue')
            )
        )
        self.assertEquals(s.build(), 
            "search?q=" + 
            '&filter=' + enc(r"exp=Color:Red,Color:!Blue/type=cnf")
        )

    def test_multi_filters(self):
        s = Search(
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
            "search?q=" + 
            '&filter=' + enc(r"exp=Color:Red,Color:!Blue/type=cnf") +
            '&filter=' + enc(r"exp=Price:[0:100]/type=dnf")
        )

if __name__ == '__main__':
    unittest.main()
