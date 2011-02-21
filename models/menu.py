# -*- coding: utf-8 -*- 

#########################################################################
## Customize your APP title, subtitle and menus here
#########################################################################

# response.title = request.application
response.title = T('Public Radio Roadtrip!')
response.subtitle = T('Map, Share and Publish your own stories from NPR.org as a Public Radio Roadtrip!')

##########################################
## this is the main application menu
## add/remove items as required
##########################################

if auth.is_logged_in():
    response.menu = [
        ['Home', False, URL(request.application,'default','index')],
        ['My Stories', False, URL(request.application,'default','list_stories')],
        ['Add Story', False, URL(request.application,'default','add_story')],
        ['My Topics', False, URL(request.application,'default','list_topics')],
        ['Add Topic', False, URL(request.application,'default','add_topic')],
        ['My Collections', False, URL(request.application,'default','list_collections')],
        ['Add Collection', False, URL(request.application,'default','add_collection')],
        ['Published Collections', False, URL(request.application,'default','published_collections')],
        ]
else:
    response.menu = [
        ['Home', False, URL(request.application,'default','index')],
        ['Published Collections', False, URL(request.application,'default','published_collections')],
        ]
'''
response.menu = [
    ['Home', False, URL(request.application,'default','index')],
    ['Stories', False, URL(request.application,'default','list_stories')],
    ['Add Story', False, URL(request.application,'default','add_story')],
    ['My Roadtrips', False, URL(request.application,'default','list_roadtrips')],
    ['Add Roadtrip', False, URL(request.application,'default','add_roadtrip')],
    ['Published Roadtrips', False, URL(request.application,'default','published_roadtrips')],
    ]
'''
