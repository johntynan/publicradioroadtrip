#########################################################################
## This scaffolding model makes your app work on Google App Engine too
#########################################################################

#import sys
#import os.path
#site_packages_path = os.path.join(request.env.web2py_path,'site-packages')
#if sys.path[0] != site_packages_path:
#    sys.path.insert(0, site_packages_path)

# if running on Google App Engine
#if settings.web2py_runtime_gae:
#    from gluon.contrib.gql import *      
    # connect to Go0ogle BigTable
#    db = DAL('gae')
    # and store sessions there
 #   session.connect(request, response, db=db)  
#else:
    # if not, use SQLite or other DB
    # db = DAL('sqlite://storage.sqlite')  

db = DAL('sqlite://storage.sqlite')

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
    Field('roadtrip_id', 'integer', writable=False, readable=False),
    Field('title'),
    Field('description', 'text'),
    Field('created_by', db.auth_user, default=user_id, writable=False, readable=False),
    Field('created_on','datetime',default=request.now, writable=False, readable=False)
    )
                            
db.define_table(
    'story', 
    Field('story_id', 'integer', writable=False, readable=False),
    Field('npr_id', 'integer'),
    Field('roadtrip','list:reference roadtrip'),
    Field('title'), 
    Field('latitude'),
    Field('longitude'),
    Field('comment', 'text'),
    Field('created_by', db.auth_user, default=user_id, writable=False, readable=False),
    Field('created_on','datetime', default=request.now, writable=False, readable=False)
    )
    
db.story.roadtrip.requires=IS_IN_DB(db(db.roadtrip.created_by==auth.user_id),'roadtrip.id','%(title)s', multiple=True) 

