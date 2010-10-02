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

response.menu = [
    ['Home', False, URL(request.application,'default','index')],
    ['Stories', False, URL(request.application,'default','list_stories')],
    ['Add Story', False, URL(request.application,'default','add_story')],
    ['Roadtrips', False, URL(request.application,'default','list_roadtrips')],
    ['Add Roadtrip', False, URL(request.application,'default','add_roadtrip')],
    ]
