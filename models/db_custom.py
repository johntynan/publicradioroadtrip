#########################################################################
## This scaffolding model makes your app work on Google App Engine too
#########################################################################

# import sys
# import os.path
# site_packages_path = os.path.join(request.env.web2py_path,'site-packages')
# if sys.path[0] != site_packages_path:
#     sys.path.insert(0, site_packages_path)
# print site_packages_path

# import os

# declare your google analytics id as a global variable 
google_analytics_id = 'UA-1449777-15'

import uuid

from gluon.tools import *
auth = Auth(globals(),db)
auth.define_tables()
crud = Crud(globals(),db)

if auth.is_logged_in():
    user_id = auth.user.id
else:
    user_id = None

COLLECTION_TYPES = ('Roadtrip','Walking Tour','Audio Guide','Mixtape')
SORT_TYPES = ('None','Date','Sort Values')

db.define_table(
    'collection', 
    # Field('uuid', length=64, default=uuid.uuid4(),writable=False,readable=False),
    Field('title'),
    Field('type'),
    Field('sort_type'),    
    Field('description', 'text'),
    Field('published', 'boolean', default=False),
    Field('created_by', db.auth_user, default=user_id, writable=False, readable=False),
    Field('created_on','datetime',default=request.now, writable=False, readable=False),
    Field('modified_on','datetime',default=request.now,writable=False,readable=False)
    )
db.collection.type.requires=IS_IN_SET(COLLECTION_TYPES)
db.collection.sort_type.requires=IS_IN_SET(SORT_TYPES)

db.define_table(
    'topic', 
    # Field('uuid', length=64, default=uuid.uuid4(),writable=False,readable=False),
    Field('title'),
    Field('description', 'text'),
    Field('created_by', db.auth_user, default=user_id, writable=False, readable=False),
    Field('created_on','datetime',default=request.now, writable=False, readable=False),
    Field('modified_on','datetime',default=request.now,writable=False,readable=False)
    )

db.define_table(
    'region', 
    # Field('uuid', length=64, default=uuid.uuid4(),writable=False,readable=False),
    Field('title'),
    Field('description', 'text'),
    Field('area','text'),
    Field('created_by', db.auth_user, default=user_id, writable=False, readable=False),
    Field('created_on','datetime',default=request.now, writable=False, readable=False),
    Field('modified_on','datetime',default=request.now,writable=False,readable=False)
    )

db.define_table(
    'story', 
    # Field('uuid', length=64, default=uuid.uuid4(),writable=False,readable=False),
    Field('nprid'),
    Field('title'), 
    Field('url'),
    Field('date','datetime',default=request.now),
    Field('collection','list:reference collection'),
    Field('latitude'),
    Field('longitude'),
    Field('address'),
    Field('sort_value'),
    Field('description','text'),
    Field('topic','list:reference topic'),
    Field('region','list:reference region'),
    Field('image','upload'),
    Field('image_url'),
    Field('audio','upload'),
    Field('audio_url'),
    Field('published', 'boolean', default=False),
    Field('created_by', db.auth_user, default=user_id, writable=False, readable=False),
    Field('created_on','datetime', default=request.now, writable=False, readable=False),
    Field('modified_on','datetime',default=request.now,writable=False,readable=False)
    )

db.story.collection.requires=IS_IN_DB(db(db.collection.created_by==auth.user_id),'collection.id','%(title)s', multiple=True)
db.story.topic.requires=IS_IN_DB(db(db.topic.created_by==auth.user_id),'topic.id','%(title)s', multiple=True) 
db.story.region.requires=IS_IN_DB(db(db.region.created_by==auth.user_id),'region.id','%(title)s', multiple=True) 
db.story.date.requires=IS_DATETIME('%Y-%m-%d %H:%M:%S')
