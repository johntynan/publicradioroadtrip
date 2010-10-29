#########################################################################
## This scaffolding model makes your app work on Google App Engine too
#########################################################################

# import sys
# import os.path
# site_packages_path = os.path.join(request.env.web2py_path,'site-packages')
# if sys.path[0] != site_packages_path:
#     sys.path.insert(0, site_packages_path)
# print site_packages_path

from gluon.tools import *
auth = Auth(globals(),db)
auth.define_tables()
crud = Crud(globals(),db)

if auth.is_logged_in():
    user_id = auth.user.id
else:
    user_id = None

db.define_table(
    'roadtrip', 
    Field('title'),
    Field('description', 'text'),
    Field('created_by', db.auth_user, default=user_id, writable=False, readable=False),
    Field('created_on','datetime',default=request.now, writable=False, readable=False)
    )
                            
db.define_table(
    'story', 
    Field('nprid'),
    Field('title'), 
    Field('roadtrip','list:reference roadtrip'),
    Field('latitude'),
    Field('longitude'),
    Field('comment', 'text'),
    Field('created_by', db.auth_user, default=user_id, writable=False, readable=False),
    Field('created_on','datetime', default=request.now, writable=False, readable=False)
    )
    
db.story.roadtrip.requires=IS_IN_DB(db(db.roadtrip.created_by==auth.user_id),'roadtrip.id','%(title)s', multiple=True) 

