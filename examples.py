1.
from merlin import Merlin
engine = Merlin(
    company     = 'my_company', 
    environment = 'prod', 
    instance    = 'my_instance'
)

2.
from merlin.search import Search

with engine(Search(q="dress")) as results:
    print results

3.
# A query where we want 50 results starting from the 100th result
s = Search(q="red dress", start=100, num=50)

with engine(s) as results:
    print results

4.
# a query where we only want back the "id" and "title" fields 
s = Search(q="red dress", fields=["id", "title"])

with engine(s) as results:
    print results

5.
# Get all fields including debug fields
s = Search(q='red dress', fields=['[debug]'])

with engine(s) as results:
    print results

6.
from merlin.sort import Sort as S
s = Search(q='red dress', sort=S.asc('price'))

with engine(s) as results:
    print results

7.
s = Search(q='red dress', sort = [S.asc('price'), S.desc('size')])

with engine(s) as results:
    print results

8.
from merlin.filter import NF, Field
s = Search(
    q      = 'red dress',
    filter = NF.cnf(
        Field('price') < 100
    )
)

with engine(s) as results:
    print results

9.
s = Search(
    q      = "red dress",
    filter = NF.cnf(
        (Field('size') == ('S', 'M')) & (Field('price') < 100)
    )
)

with engine(s) as results:
    print results

10.
# a query where we want red dresses in size 'S' or in size 'M' and 
# tag it as 'smallormedium'
s = Search(
    q      = "red dress",
    filter = NF.cnf(
        (Field("size") == ('S', 'M')),
        tag="smallormedium"
    )
)

with engine(s) as results:
    print results

11.
# a query where we want red dresses under $100 
# and the top 5 brands returned as facets
from merlin.facet import Facet as F
s = Search(
    q      = 'red dress',
    filter = NF.cnf(Field('price') < 100),
    facet  = F.enum('brand', num=5)
)

with engine(s) as results:
    print results.facets.enums

12.
# a query where we want red dresses and the range of prices returned
s = Search(
    q      = 'red dress',
    facets = F.range('price')
)

with engine(s) as results:
    print results.facets.ranges

13.
# a query where we want red dresses and a histogram of their 
# price fields from 0-500 in increments of 100.
s = Search(
    q      = 'red dress',
    facets = F.hist('price', start=0, end=500, gap=100)
)

with engine(s) as results:
    print results.facets.histograms

14.
# a search with multiple keyed facets on the 'brand' field
s = Search(
    q      = 'red dress',
    facets = [
        F.range('price', tag="price_range"),
        F.hist('price', start=0, end=500, gap=100, tag='price_hist')
    ]
)

with engine(s) as results:
    print results.facets

15.
#  pass array of tags to exclude into the facet 
s = Search(
    q = "red dress",
    facets = [
        F.enum("brand", num=200, exclude=["tag1", "tag2"])
    ]
)

16.
# search for 'red dress' with spelling correction turned off
S = Search(q="red dress", correct=False)
