# -*- coding: utf-8 -*- 

#########################################################################
## This is a samples controller
## - index is the default action of any application
## - user is required for authentication and authorization
## - download is for downloading files uploaded in the db (does streaming)
## - call exposes all registered services (none by default)
#########################################################################  

import gluon.contrib.simplejson

from kcrw.nprapi.story import (StoryAPI,
                               StoryMapping,
                               NPRError,
                               OUTPUT_FORMATS,
                               QUERY_TERMS,
                               )

api = StoryAPI('MDAxNzgwMDQ5MDEyMTQ4NzYyMjU4YmY1Yw004', 'JSON')

def url(f, args=[]): return URL(r=request,f=f,args=args)

error_page=URL(r=request,f='error')

def index():
    """
    example action using the internationalization operator T and flash
    rendered by views/default/index.html or views/generic.html
    """
    response.flash = T('Welcome to web2py')
    return dict(message=T('Hello World'))
    
@auth.requires_login()
def list_roadtrips():
    roadtrips=db(db.roadtrip.created_by==auth.user_id).select(orderby=db.roadtrip.title)
    return dict(roadtrips=roadtrips)

@auth.requires_login()
def edit_roadtrip():
    id=request.args(0)
    return dict(form=crud.update(db.roadtrip,id))
    
@auth.requires_login()
def add_roadtrip():

    form = SQLFORM(db.roadtrip)

    if form.accepts(request.vars, session): 
        response.flash='record inserted'

        roadtrip_id = dict(form.vars)['id']
        roadtrip = db(db.roadtrip.id==roadtrip_id).select()

        redirect(URL(r=request, f='list_roadtrips'))

    elif form.errors: response.flash='form errors'
    return dict(form=form)

@auth.requires_login()
def add_story():


    form = SQLFORM(db.story, _id='story_form')

    if request.vars.nprid:
        form.vars.nprid = request.vars.nprid

    if request.vars.title:
        form.vars.title = request.vars.title

    if form.accepts(request.post_vars, session):

        response.flash='record inserted'

        story_id = dict(form.vars)['id']
        story = db(db.story.id==story_id).select()

        redirect(URL(r=request, f='list_stories'))

    elif form.errors: response.flash='form errors'
    return dict(form=form)    

@auth.requires_login()
def list_stories():
    stories=db(db.story.created_by==auth.user_id).select(orderby=db.story.title)
    return dict(stories=stories)
    
@auth.requires_login()
def view_story():
    id=request.args(0)
    story=db.story[id] or redirect(error_page)

    # Stripping out the pipe character:
    nprid = story.nprid
    nprid = str(nprid).strip('|')

    # get the story from the npr api as a json string
    # json = api.query(story.nprid)

    # since the value for story.nprid is not saved as cleanly as it should be:
    json = api.query(nprid)

    # turn the json string into a dictionary
    results = json
    results = gluon.contrib.simplejson.loads(results)

    # get the teaser for the story
    # teaser = 'Some sample text.'
    teaser = results['list']['story'][0]['teaser'].values()[0]

    # get the teaser for the story
    # link = 'http://www.npr.com'
    link = results['list']['story'][0]['link'][2].values()[0]

    # just a test to see that the site-packages folder is in the sys.path
    # teaser = str(site_packages_path)

    # get the pubdDate for the story
    # pubDate = 'Sat, 09 Oct 2010 14:05:00 -0400'
    pubDate = results['list']['story'][0]['pubDate'].values()[0]

    return dict(story=story,json=json,results=results,teaser=teaser,link=link,pubDate=pubDate)

@auth.requires_login()
def view_roadtrip():
    roadtrip_id=int(request.args(0))
    roadtrip=db.roadtrip[roadtrip_id] or redirect(error_page)
    stories=db(db.story.roadtrip[roadtrip_id]).select(orderby=db.story.title)
    return dict(roadtrip=roadtrip, stories=stories)

@auth.requires_login()
def edit_story():
    story_id=request.args(0)
    story=db.story[story_id] or redirect(error_page)
    form=crud.update(db.story,story,next=url('view_story',story_id))
    return dict(form=form)


def user():
    """
    exposes:
    http://..../[app]/default/user/login 
    http://..../[app]/default/user/logout
    http://..../[app]/default/user/register
    http://..../[app]/default/user/profile
    http://..../[app]/default/user/retrieve_password
    http://..../[app]/default/user/change_password
    use @auth.requires_login()
        @auth.requires_membership('group name')
        @auth.requires_permission('read','table name',record_id)
    to decorate functions that need access control
    """
    return dict(form=auth())


def download():
    """
    allows downloading of uploaded files
    http://..../[app]/default/download/[filename]
    """
    return response.download(request,db)


def call():
    """
    exposes services. for example:
    http://..../[app]/default/call/jsonrpc
    decorate with @services.jsonrpc the functions to expose
    supports xml, json, xmlrpc, jsonrpc, amfrpc, rss, csv
    """
    session.forget()
    return service()
