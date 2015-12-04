import unittest
from urllib import quote_plus as enc

from merlin import Merlin
from merlin.error import ValidationError
from merlin.facet import Facet as F
from merlin.filter import Field, NF
from merlin.sort import Sort as S
from merlin.search import Search
from merlin.geo import Geo
from merlin.group import Group

class MerlinTest(unittest.TestCase):

    def test_simple_search(self):
        s = Search(q="shirt")
        self.assertEquals(s.build(), "products/search?q=shirt")

    def test_simple_search_1(self):
        s = Search(q="", num=10)
        self.assertEquals(s.build(), "products/search?q=&num=10")

    def test_simple_search_2(self):
        s = Search(q="shirt", num=10, start=20)
        self.assertEquals(s.build(), "products/search?q=shirt&start=20&num=10")

    def test_enum_facet(self):
        s = Search(
            q = "shirt",
            facets = F.enum("brand", num=10)
        )
        self.assertEquals(s.build(), 
            "products/search?q=shirt&facet=" + enc("field=brand/type=enum/num=10")
        )

    def test_enum_facet_named(self):
        s = Search(
            q = "shirt",
            facets = F.enum("brand", num=10, key='ponies')
        )
        self.assertEquals(s.build(), 
            "products/search?q=shirt&facet=" + enc("field=brand/type=enum/key=ponies/num=10")
        )

    def test_enum_facet_excluding(self):
        s = Search(
            q = "shirt",
            facets = F.enum("brand", num=10, key='ponies', exclude=['foo', 'bar'])
        )
        self.assertEquals(s.build(), 
            "products/search?q=shirt&facet=" + 
            enc("field=brand/type=enum/key=ponies/num=10/ex=foo,bar")
        )

    def test_hist_facet(self):
        s = Search(
            q = "shirt",
            facets = F.hist("price", start=10, end=100, gap=5, key='prices')
        )
        self.assertEquals(s.build(), 
            "products/search?q=shirt&facet=" + 
            enc("field=price/type=hist/key=prices/range=[10:100:5]")
        )

    def test_range_facet(self):
        s = Search(
            q = "shirt",
            facets = F.range("price", key='prices')
        )
        self.assertEquals(s.build(), 
            "products/search?q=shirt&facet=" + 
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
            "products/search?q=shirt" + 
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
            "products/search?q=pants" + 
            '&sort=' + enc("brand:desc,price:asc")
        )

    def test_fields(self):
        s = Search(
            q = "socks",
            fields=["one", "two", "three"]
        )
        self.assertEquals(s.build(), 
            "products/search?q=socks" + 
            '&fields=' + enc("one,two,three")
        )

    def test_filters(self):
        s = Search(
            filter=NF.cnf(
                (Field('Color') == 'Red') & (Field('Color') != 'Blue')
            )
        )
        self.assertEquals(s.build(), 
            "products/search?q=" + 
            '&filter=' + enc(r"exp=Color:Red,Color:!Blue/type=cnf")
        )

    def test_filter_tags(self):
        s = Search(
            filter=NF.cnf(
                (Field('Color') == 'Red') & (Field('Color') != 'Blue'),
                tag="redandblue"
            )
        )
        self.assertEquals(s.build(), 
            "products/search?q=" + 
            '&filter=' + enc(r"exp=Color:Red,Color:!Blue/type=cnf/tag=redandblue")
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
            "products/search?q=" + 
            '&filter=' + enc(r"exp=Color:Red,Color:!Blue/type=cnf") +
            '&filter=' + enc(r"exp=Price:[0:100]/type=dnf")
        )

    def test_multi_values(self):
        s = Search(
            filter=NF.cnf(
                (Field('Color') == ('Blue', 'Red')) & \
                (Field('Color') != ('Teal', 'Green'))
            )
        )
        self.assertEquals(s.build(),
            "products/search?q=" +
            "&filter=" + enc(r"exp=Color:Blue|Color:Red,Color:!Teal,Color:!Green/type=cnf")
        )

    def test_single_filter(self):
        s = Search(
            q='hoodie',
            filter=NF.cnf(Field('price') <= 20)
        )
        self.assertEquals(s.build(), 
            "products/search?q=hoodie" + 
            '&filter=' + enc(r"exp=price:[:20]/type=cnf")
        )

    def test_lt_gt_facet(self):
        s = Search(
            q='hoodie',
            filter=NF.cnf(
                (Field('price') < 20) & (Field('age') > 10)
            )
        )
        self.assertEquals(s.build(), 
            "products/search?q=hoodie" + 
            '&filter=' + enc(r"exp=price:[:20),age:(10:]/type=cnf")
        )

    def test_group(self):
        s = Search(
            q='hoodie',
            group=Group(field='category', num=10, sort=S.asc('price'))
        )

        self.assertEquals(s.build(), 
            "products/search?q=hoodie" + 
            '&group=' + enc(r"field=category/sort=price:asc/num=10")
        )

    def test_geo(self):
        s = Search(
            q='hoodie',
            geo=Geo(field='geo', pt=(37.774929, -122.419416), dist=35)
        )

        self.assertEquals(s.build(),
            "products/search?q=hoodie" +
            '&geo=' + enc(r"field=geo/pt=(37.774929,-122.419416)/d=35.000")
        )

    def test_mode(self):
        make_s = lambda m: Search(q='hoodie', mode=m)
        for m in ('semantic', 'keyword'):
            self.assertEquals(make_s(m).build(),
                "products/search?q=hoodie" +
                '&mode=' + enc(m)
            )

        with self.assertRaises(ValidationError):
            make_s('foo').build()
            self.fail("Should have failed!")

    def test_needs_num(self):
        with self.assertRaises(AssertionError):
            Field('price') <= '10'

        with self.assertRaises(AssertionError):
            Field('price').between('a', 10)

    def test_proper_fieldnames(self):
        with self.assertRaises(AssertionError):
            Field('')

        with self.assertRaises(AssertionError):
            Field(123)

class EngineTest(unittest.TestCase):

    def setUp(self):
        self.engine = Merlin('blackbird', 'dev', 'agathon')

    def test_hosts(self):
        engine = Merlin('blackbird', 'dev', 'agathon')
        self.assertEquals(engine.host, 'search-dev.search.blackbird.am')
        engine = Merlin('blackbird', 'stage', 'agathon')
        self.assertEquals(engine.host, 'search-staging.search.blackbird.am')
        engine = Merlin('blackbird', 'prod', 'agathon')
        self.assertEquals(engine.host, 'search-prod.search.blackbird.am')

    def test_simple_q(self):
        s = Search(q='dress')
        with self.engine(s) as r:
            self.assertEquals(r.hits.numFound, 1)
            self.assertEquals(r.hits[0]['id'], '111f49eacc7dbc9ab2df53f8ce52ec64')

    def test_simple_q_fields(self):
        s = Search(q='dress', fields=['images'])
        with self.engine(s) as r:
            keys_found = set()
            for h in r.hits:
                keys_found.update(h.keys())

            self.assertEquals(len(keys_found), 1)
            self.assert_('images' in keys_found,
                "field 'images' not in returned results")

    def test_price_filter(self):
        s = Search(q='',
            filter=NF.cnf(Field('price') > 150),
            fields=['price']
        )
        with self.engine(s) as r:
            self.assertEquals(r.hits.numFound, 1)
            self.assertEquals(r.hits[0]['price'], '178.0 USD')

    def test_sort(self):
        s = Search(q='',
            sort = S.asc('price'),
            fields= ['price']
        )
        with self.engine(s) as r:
            self.assertEquals(r.hits.numFound, 5)
            self.assertEquals(r.hits[0]['price'], '59.0 USD')
            self.assertEquals(r.hits[-1]['price'], '178.0 USD')

    def test_or_search(self):
        s = Search(q='',
            filter=NF.cnf(
                Field('colors') == ('Red', 'Blue')
            )
        )
        with self.engine(s) as r:
            self.assertEquals(r.hits.numFound, 3)
            for h in r.hits:
                self.assertIn(h['colors'][0], set(['Red', 'Blue', 'red']))

    def test_and_search(self):
        s = Search(q='',
            filter=NF.cnf(
                (Field('colors') == 'Red') & (Field('price') < 178)
            )
        )
        with self.engine(s) as r:
            self.assertEquals(r.hits.numFound, 1)
            self.assertEquals(r.hits[0]['brand'], 'Raoul')

        s = Search(q='',
            filter=NF.cnf(
                (Field('colors') == 'Red') & (Field('price') <= 178)
            )
        )
        with self.engine(s) as r:
            self.assertEquals(r.hits.numFound, 2)

    def test_error(self):
        s = Search(fields=['ponies'])
        with self.assertRaises(IOError):
            with self.engine(s) as r:
                self.fail("should never get here")

    def test_hist_facet(self):
        s = Search(
            facets=F.hist('price', start=0, end=100, gap=50)
        )
        with self.engine(s) as r:
            res = set(r.facets.histograms['price'].items())
            wanted = set([(('0.0', '50.0'), 0), (('50.0', '100.0'), 4)])
            self.assertEquals(res, wanted)

if __name__ == '__main__':
    unittest.main()
