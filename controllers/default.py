# -*- coding: utf-8 -*- 

#########################################################################
## This is a samples controller
## - index is the default action of any application
## - user is required for authentication and authorization
## - download is for downloading files uploaded in the db (does streaming)
## - call exposes all registered services (none by default)
#########################################################################  

import logging
from urllib2 import build_opener
from urllib import quote_plus
# Some exception handling to support both python 2.4 and 2.5+
try:
    from xml.etree.cElementTree import fromstring
except ImportError:
    from cElementTree import fromstring
try:
    from json import loads
except ImportError:
    # from simplejson import loads
    from django.utils import simplejson

# Configure default null logging
class NullHandler(logging.Handler):
    def emit(self, record):
        pass

npr_log = logging.getLogger('kcrw.nprapi')
npr_log.setLevel(logging.INFO)
npr_log.addHandler(NullHandler())

BASE_URL = 'http://api.npr.org/query'
OUTPUT_FORMATS = ('NPRML', 'RSS', 'MediaRSS', 'Podcast', 'ATOM', 'JSON',
                  'HTML', 'JS')
QUERY_TERMS = (
    # query input
    'id', 'date', 'startDate', 'endDate', 'orgId', 'searchTerm', 'searchType',
    # output control
    'fields', 'callback', 'sort','startNum', 'numResults', 'action',
    'requiredAssets', 'title', 'remap','blah'
    )


class NPRError(Exception):
    """An error response from the NPR API.

    :param code: The NPR error code
    :param text: The NPR error message
    """

    def __init__(self, code, text=u''):
        self.code = code
        self.text = text

    def __str__(self):
        """Returns the error code and message."""
        return '%s - %s'%(self.code, self.text)


class StoryAPI(object):
    """Makes requests to the NPR Story API.

    :param api_key: Your NPR API key string, you must register to get this.
    :param output_format: The output format type.  Accepts any of the values
        in :const:`OUTPUT_FORMATS`, which are described in the
        `NPR API input reference <http://www.npr.org/api/inputReference.php>`_.
    """

    def __init__(self, api_key, output_format=None):
        self.api_key = api_key
        if output_format is not None:
            assert output_format in OUTPUT_FORMATS, 'Invalid output format'
        self.output_format = output_format
        # We construct a URL opener so we can easily swap it out
        # when unit testing
        self.opener = build_opener()

    def _make_url(self, query):
        """Construct a url for the given query parameters"""
        if self.output_format:
            query['output'] = self.output_format
        query['apiKey'] = self.api_key
        url_query = '&'.join('='.join(quote_plus(str(i)) for i in pair)
                             for pair in query.iteritems())
        return BASE_URL + '?' + url_query

    def query(self, ids, **kw):
        """Request data from the NPR API. Valid query parameters
        listed in the QUERY_TERMS constant.  Returns the response
        string after checking for errors.

        :param ids: An integer or string story id or a list of such ids
        :param kw: Accepts any of the NPR query parameters listed in
          :const:`QUERY_TERMS`.  These are described in detail in the
          `NPR API input reference <http://www.npr.org/api/inputReference.php>`_.
          All of these parameters must be strings or integers, except for
          the *fields* parameter which may be a list of field names.
        :except: Raises an :class:`NPRError` when an error response is
          returned by the NPR API.  Raises an :class:`urllib2.URLError` or an
          :class:`urllib2.HTTPError` when there is a problem accessing the
          NPR API service.
        :rtype: string
        """
        query = kw.copy()
        # If the ids are a list, convert to a string
        if not isinstance(ids, basestring) and hasattr(ids, '__iter__'):
            ids = ','.join(str(i) for i in ids)
        query['id'] = ids

        # We expect a list of field names for 'fields', convert to a string
        if not isinstance(query.get('fields', ''), basestring):
            query['fields'] = ','.join(query['fields'])

        # Filter so we have only allowed terms and terms with non-null
        # values
        allowed_terms = dict((term,None) for term in QUERY_TERMS)
        query = dict((k,v) for k,v in query.iteritems()
                         if k in allowed_terms and v is not None)

        # Make the request
        response = self.opener.open(self._make_url(query))
        response_text = response.read()

        # check for errors
        if response_text.startswith('<?xml') and 'message' in response_text:
            xml = fromstring(response_text)
            messages = xml.findall('message')
            for message in messages:
                text = message.find('text').text
                if message.get('level') == 'error':
                    # Raise the error
                    raise NPRError(message.get('id'), text)
                else:
                    # Log warning message
                    npr_log.warning('NPR API log: %s: %s - %s',
                                    message.get('level').upper(),
                                    message.get('id'), text)
        return response_text


class StoryMapping(object):
    """Uses the NPR API's JSON output to generate a simple data
    structure containing a list of NPR stories.

    The query method stores the full JSON-esque mapping in the
    :attr:`data` attribute and returns the list of story
    mappings. Additionally, a few properties are available on the
    class to allow easy retrieval of additional API metadata.

    :param api_key: Your NPR API key string, you must register to get this.
    :param prune_text_nodes: If this is set to true any single entry
      dictionaries in the query result with only the key ``$text``
      will be replaced with the value only.  This simplifies the data
      structure and makes it appear more 'pythonic' and less XML-ish.
      """

    def __init__(self, api_key, prune_text_nodes=True):
        self.story_api = StoryAPI(api_key, 'JSON')
        self.data = {}
        self._prune_text_nodes = prune_text_nodes

    def query(self, ids, **kw):
        """Make a query to the API, returns a list of story
        dictionaries and updates the :attr:`data` attribute.

        :param ids: An integer or string story id or a list of such ids
        :param kw: Accepts any of the NPR query parameters listed in
          :const:`QUERY_TERMS`.  These are described in detail in the
          `NPR API input reference <http://www.npr.org/api/inputReference.php>`_.
          All of these parameters must be strings or integers, except for
          the *fields* parameter which may be a list of field names.
        :except: Raises an :class:`NPRError` when an error response is
          returned by the NPR API.  Raises an :class:`urllib2.URLError` or an
          :class:`urllib2.HTTPError` when there is a problem accessing the
          NPR API service.
        :rtype: list of story mappings
        """
        self.data = loads(self.story_api.query(ids, **kw))
        if self._prune_text_nodes:
            self._process_data(self.data)
        return self.stories

    def _process_data(self, data):
        """Because of it's XML origins, the json data contains many
        entries with values of the form {'$text': ...}; this is not
        desirable, so we replace these single item dictionaries with
        the text value alone.  Entries with multiple item dictionaries
        will still have a '$text' key.  Additionally, the 'link'
        elements can be better represented as a mapping with the
        'type' as the key, than a list of dicts with type and $text
        keys.

        This modifies mutable data-structures in-place.
        """
        # Recurse through all mappings and lists, looking for single
        # item dictionaries with only the key '$text'
        if hasattr(data, 'keys'):
            for item in data:
                value = data[item]
                keys = hasattr(value, 'keys') and value.keys()
                if keys and len(keys) == 1 and keys[0] == '$text':
                    data[item] = value['$text']
                elif keys:
                    self._process_data(value)
                elif isinstance(value, list) and item == 'link':
                    # Lists of links are structured in an almost useless manner.
                    # Turn them into a sensible mapping
                    entries = set(value[0].keys())
                    if entries == set(('type', '$text')):
                        links = {}
                        for link in value:
                            links[link['type']] = link['$text']
                        data[item] = links
                elif isinstance(value, list):
                    self._process_data(value)
        elif isinstance(data, list):
            for item in data:
                self._process_data(item)

    @property
    def version(self):
        """The API version of the last query response.  This will not
        have a value until :meth:`query` is called."""
        return self.data.get('version', '')

    @property
    def title(self):
        """The title of the query response feed.  This will not have a
        value until :meth:`query` is called."""
        if 'list' not in self.data:
            return ''
        value = self.data['list']['title']
        if not self._prune_text_nodes:
            value = value['$text']
        return value

    @property
    def description(self):
        """The description of the query response feed.  This will not
        have a value until :meth:`query` is called."""
        if 'list' not in self.data:
            return ''
        value = self.data['list']['teaser']
        if not self._prune_text_nodes:
            value = value['$text']
        return value

    @property
    def stories(self):
        """The list of stories, this is identical to the last return
        value of :meth:`query`.  This will not have a value until
        :meth:`query` is called.
        """
        if 'list' in self.data:
            return self.data['list']['story']
        else:
            return []

api = StoryAPI('MDAxNzgwMDQ5MDEyMTQ4NzYyMjU4YmY1Yw004', 'JSON')

# since there was some trouble using the KCRW.NPRAPI module on GAE, I am removing it completely... for the moment.

# this is what I should have been able to do:
# import gluon.contrib.simplejson
# from kcrw.nprapi.story import (StoryAPI,
#                          StoryMapping,
#                          NPRError,
#                          OUTPUT_FORMATS,
#                          QUERY_TERMS,
#                          )
#
# api = StoryAPI('MDAxNzgwMDQ5MDEyMTQ4NzYyMjU4YmY1Yw004', 'JSON')

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

    # just a test to see that the site-packages folder is in the sys.path
    # test = str(site_packages_path)
    # test = []
    # for p in sys.path:
    #     if os.path.isdir(p):
    #         test.append(os.listdir(p))
            # print os.listdir(p)

    test = ''

    roadtrips=db(db.roadtrip.created_by==auth.user_id).select(orderby=db.roadtrip.title)
    return dict(roadtrips=roadtrips, test=test)

def published_roadtrips():

    roadtrips=db(db.roadtrip.published==1).select(orderby=db.roadtrip.title)
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


    form = SQLFORM(db.story, _name='story_form')

    if request.vars.nprid:
        form.vars.nprid = request.vars.nprid

    if request.vars.title:
        form.vars.title = request.vars.title

    if request.vars.url:
        form.vars.url = request.vars.url

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

    # note: gutting kcrw.nprapi module from this part of the code.  At least until I am able to get Google App Engine to find the module from the appropriate site-packages directory.

    # get the story from the npr api as a json string
    json = api.query(story.nprid)

    # turn the json string into a dictionary
    # json = 'Some sample text.'
    # results = 'Some sample text.'
    results = json
    results = simplejson.loads(results)

    # get the teaser for the story
    # teaser = 'Some sample text.'
    teaser = results['list']['story'][0]['teaser'].values()[0]

    # get the teaser for the story
    # link = 'http://www.npr.com'
    link = results['list']['story'][0]['link'][2].values()[0]

    # get the pubdDate for the story
    # pubDate = 'Sat, 09 Oct 2010 14:05:00 -0400'
    pubDate = results['list']['story'][0]['pubDate'].values()[0]

    return dict(story=story,json=json,results=results,teaser=teaser,link=link,pubDate=pubDate)

def view_roadtrip():
    stories = {}
    roadtrip_id=int(request.args(0))
    roadtrip = db.roadtrip[roadtrip_id] or redirect(error_page)
    stories=db(db.story.roadtrip.contains(roadtrip_id)).select(orderby=db.story.title)
    length=len(stories);
    return dict(roadtrip=roadtrip, stories=stories, length=length)


def roadtrip_markers():
    response.headers['Content-Type']='text/xml'
    stories = {}
    roadtrip_id=int(request.args(0))
    roadtrip = db.roadtrip[roadtrip_id] or redirect(error_page)
    stories=db(db.story.roadtrip.contains(roadtrip_id)).select(orderby=db.story.title)
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
