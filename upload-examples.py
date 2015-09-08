from merlin import Uploader
from merlin.upload import Add, Update, Delete

# To add documents
company = "yoursite"
env = "dev"
instance = "myinstance"
username = "me@yoursite.com"

# Authtoken can be found on the Admin API dashboard
authtoken = "1234567890ABCDEF"

# Instantiate an uploader engine
engine = Uploader(company, env, instance,
    username=username,
    authtoken=authtoken
)

# To add documents
add = Add()
add += {"id": "123", "title": "red dress"}
add += {"id": "456", "title": "blue shoes"}

with engine(add) as results:
    print(results.msg)

# To delete documents
delete = Delete()
delete += {"id": "123"}

# Can also use straight ids
delete += "456"

with engine(delete) as results:
    print(results.msg)

# To update a set of documents
update = Update()

# Only include the fields needed for updating
update += {"id": "456", "images": ["http://path/to/image.jpg"]}

with engine(update) as results:
    print(results.msg)
