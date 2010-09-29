#########################################################################
## This scaffolding model makes your app work on Google App Engine too
#########################################################################

import sys
import os.path
site_packages_path = os.path.join(request.env.web2py_path,'site-packages')
if sys.path[0] != site_packages_path:
    sys.path.insert(0, site_packages_path)

from gluon.settings import settings
auth = Auth(globals(),db)
auth.define_tables()
crud = Crud(globals(),db)

if auth.is_logged_in(): 
    me=auth.user_id
else: 
    me=None 

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


db.define_table(
    'roadtrip', 
    Field('name'), 
    Field('description', 'text'),
    # Field('created_by', db.auth_user, default=auth.user_id, writable=False, readable=False),
    Field('created_by', default=me, writable=False, readable=False),
    Field('created_on','datetime',default=request.now, writable=False, readable=False)
    )
                            
db.define_table(
    'story', 
    Field('user_id', readable=False,writable=False),
    Field('roadtrip_id', db.roadtrip), 
    Field('story_id', 'integer'),
    Field('title'), 
    Field('latitude'),
    Field('longitude'),
    Field('comment', 'text'),
    # Field('created_by', db.auth_user, default=auth.user_id, writable=False, readable=False),
    Field('created_by', default=me, writable=False, readable=False),
    Field('created_on','datetime', default=request.now, writable=False, readable=False)
    )
    
# db.story.roadtrip_id.requires=IS_IN_DB(db(db.roadtrip.created_by==auth.user_id),'roadtrip.id','%(name)s', multiple=True) db.story.roadtrip_id.requires=IS_IN_DB(db(db.roadtrip.created_by==auth.user_id),'roadtrip.id','%(name)s', multiple=True) 
