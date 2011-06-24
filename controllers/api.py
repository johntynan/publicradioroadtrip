# -*- coding: utf-8 -*-

#########################################################################
## This is the API controller for the Public Radio Roadtrip
#########################################################################  

@request.restful()
def collection():
     def GET(*args,**vars):
         patterns = ['/by-id/{collection.id}']
         parsed = db.parse_as_rest(patterns,args,vars)
         if parsed.status==200: return dict(content=parsed.response)
         raise HTTP(parsed.status,parsed.error)
     return locals()