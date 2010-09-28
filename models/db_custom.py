#########################################################################
## This scaffolding model makes your app work on Google App Engine too
#########################################################################

import sys
import os.path
site_packages_path = os.path.join(request.env.web2py_path,'site-packages')
if sys.path[0] != site_packages_path:
    sys.path.insert(0, site_packages_path)

from gluon.settings import settings

# if running on Google App Engine
if settings.web2py_runtime_gae:
    from gluon.contrib.gql import *      
    # connect to Go0ogle BigTable
    db = DAL('gae')
    # and store sessions there
    session.connect(request, response, db=db)  
else:
    # if not, use SQLite or other DB
    db = DAL('sqlite://storage.sqlite')  

if auth.is_logged_in():
    me=auth.user.id
else:
    me=None

db.define_table(
    'users', 
    Field('name'), 
    Field('email')
    )

db.define_table(
    'roadtrip', 
    Field('name'), 
    Field('description', 'text'),
    Field('created_by',default=me,writable=False,readable=False),
    Field('created_on','datetime',default=request.now,writable=False,readable=False)
    )
                            
db.define_table(
    'story', 
    Field('user_id', db.users,readable=False,writable=False),
    Field('roadtrip_id', db.roadtrip), 
    Field('story_id', 'integer'),
    Field('title'), 
    Field('latitude'),
    Field('longitude'),
    Field('comment', 'text'),
    Field('created_by',default=me,writable=False,readable=False),
    Field('created_on','datetime',default=request.now,writable=False,readable=False)
    )
    
db.story.roadtrip_id.requires=IS_IN_DB(db(db.roadtrip.created_by==me),'roadtrip.id','%(name)s')
