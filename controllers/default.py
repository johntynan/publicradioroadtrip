# -*- coding: utf-8 -*- 

#########################################################################
## This is a samples controller
## - index is the default action of any application
## - user is required for authentication and authorization
## - download is for downloading files uploaded in the db (does streaming)
## - call exposes all registered services (none by default)
#########################################################################  

import gluon.contrib.rss2 as rss2

import time, datetime, uuid, StringIO
from sets import Set


##################
# begin create_qrcode
# be sure to add pygooglechart.py from http://pygooglechart.slowchop.com/
# to your site-packages directory

import os
import sys
import math

ROOT = os.path.dirname(os.path.abspath(request.application))
ROOT = ROOT + '/applications/publicradioroadtrip/static/qrcodes/'

# print ROOT

from pygooglechart import QRChart, Chart

try:
    # we're on Python3
    from urllib.request import urlopen
    from urllib.parse import quote

except ImportError:
    # we're on Python2.x
    from urllib2 import urlopen
    from urllib import quote
    
    
import settings

def create_qrcode(filename, data):

    filename = str(filename)

    # Create a 400x400 QR chart
    chart = QRChart(400, 400)

    # Add the text
    chart.add_data(data)

    # "Level H" error correction with a 0 pixel margin
    chart.set_ec('H', 0)

    # filename = ROOT + filename + '.png'

    # Download
    # Calling the download function within pygooglechart
    # unfortunately, I cannot save to the filesystem with GAE
    # otherwise, this would work:
    # chart.download(ROOT + filename + '.png')

    # modifying the Dowload function myself, here goes:
    
    Chart.BASE_URL = 'http://chart.apis.google.com/chart'

    opener = urlopen(Chart.BASE_URL, Chart.get_url_extension(chart, data_class=None))
    
    """
    if opener.headers['content-type'] != 'image/png':
        raise BadContentTypeException('Server responded with a ' \
            'content-type of %s' % opener.headers['content-type'])
    """

    # again, if I could write to the filesystem, this would be a piece of cake:
    # open(filename, 'wb').write(opener.read())
    
    # created a qrcode property for stories
    # updating this property with the generated png file
    story_id = int(filename)
    filename = filename + '.png'
    myset = db(db.story.id == story_id)
    # commenting this out for a bit
    myset.update(qrcode = db.story.qrcode.store(opener, filename))

# end create_qrcode

#############

# begin PyGeoRSSGen
# https://github.com/JoeGermuska/pygeorss

import gluon.contrib.rss2 as PyRSS2Gen
import types

def _seq_to_string(l):
    """
        Take an argument which may be a string or may be sequence.
        if it's a string, return it unchanged; otherwise, return a string which has 
        one space between each element as typical for GeoRSS formatting.
        
        Nothing is done to ensure that the string is formatted correctly, 
        nor that the values of the sequence are correctly formatted. You're on
        your own for that.
    """
    if type(l) in types.StringTypes:
        return l
    return " ".join(l)
    
class GeoRSSFeed(PyRSS2Gen.RSS2):
    """Add the 'georss' namespace to the generated feed."""
    def __init__(self,*args,**kwargs):
        PyRSS2Gen.RSS2.__init__(self, *args, **kwargs)
        self.rss_attrs['xmlns:georss'] = 'http://www.georss.org/georss'

class GeoRSSItem(PyRSS2Gen.RSSItem):
    """
        Add the following properties to an RSSItem, with support for rendering them 
        in the "simple" representation.
            * point (sequence)
            * line (sequence)
            * polygon (sequence)
            * box (sequence)
            * featuretypetag
            * relationshiptag
            * featurename
            * elev
            * floor
            * radius
            
        Each of these may be a string.  The types labeled "sequence" may also be a 
        sequence, in which case they will be joined with whitespace separators according
        to the GeoRSS standards.
        
        See http://www.georss.org/simple for more information.
    """
    properties = [
        'point',
        'line',
        'polygon',
        'box',
        'featuretypetag',
        'relationshiptag',
        'featurename',
        'elev',
        'floor',
        'radius',
        'content',
    ]

    point = None
    line = None
    polygon = None
    box = None
    featuretypetag = None
    relationshiptag = None
    featurename = None
    elev = None
    floor = None
    radius = None
    content = None

    def publish_extensions(self, handler):
        for p in GeoRSSItem.properties:
            value = getattr(self,p)
            if value is not None:
                PyRSS2Gen._element(handler,"georss:%s" % p, _seq_to_string(value))    

    def __init__(self,**kwargs):
        geokwargs = {}
        for p in GeoRSSItem.properties:
            if kwargs.has_key(p):
                geokwargs[p] = kwargs.pop(p)
        PyRSS2Gen.RSSItem.__init__(self, **kwargs)
        for key in geokwargs:
            setattr(self,key,geokwargs[key])

# end PyGeoRSSGen

# begin KCRW’s python NPR API library
# The KCRW python NPR API library was created by Alec Mitchell for KCRW, an NPR station based in Santa Monica, California.
# kcrw.nprapi is copyright 2010 KCRW
# for additional information, see: http://packages.python.org/kcrw.nprapi/

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

# end KCRW’s python NPR API library

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
def list_regions():

    regions=db(db.region.created_by==auth.user_id).select(orderby=db.region.title)
    return dict(regions=regions)

@auth.requires_login()
def edit_region():
    id=request.args(0)
    return dict(form=crud.update(db.region,id))

@auth.requires_login()
def add_region():

    form = SQLFORM(db.region, _name='region_form')

    if form.accepts(request.vars, session): 
        response.flash='record inserted'

        region_id = dict(form.vars)['id']
        region = db(db.region.id==region_id).select()

        redirect(URL(r=request, f='list_regions'))

    elif form.errors: response.flash='form errors'
    return dict(form=form)


@auth.requires_login()
def list_topics():

    topics=db(db.topic.created_by==auth.user_id).select(orderby=db.topic.title)
    return dict(topics=topics)

@auth.requires_login()
def edit_topic():
    id=request.args(0)
    return dict(form=crud.update(db.topic,id))

@auth.requires_login()
def add_topic():

    form = SQLFORM(db.topic)

    if form.accepts(request.vars, session): 
        response.flash='record inserted'

        topic_id = dict(form.vars)['id']
        topic = db(db.topic.id==topic_id).select()

        redirect(URL(r=request, f='list_topics'))

    elif form.errors: response.flash='form errors'
    return dict(form=form)

    
@auth.requires_login()
def list_collections():

    # just a test to see that the site-packages folder is in the sys.path
    # test = str(site_packages_path)
    # test = []
    # for p in sys.path:
    #     if os.path.isdir(p):
    #         test.append(os.listdir(p))
            # print os.listdir(p)

    test = ''

    collections=db(db.collection.created_by==auth.user_id).select(orderby=db.collection.title)
    return dict(collections=collections, test=test)

def published_collections():

    collections=db(db.collection.published==1).select(orderby=db.collection.title)
    return dict(collections=collections)


@auth.requires_login()
def edit_collection():
    id=request.args(0)
    return dict(form=crud.update(db.collection,id))
    
@auth.requires_login()
def add_collection():

    form = SQLFORM(db.collection)

    if form.accepts(request.vars, session): 
        response.flash='record inserted'

        collection_id = dict(form.vars)['id']
        collection = db(db.collection.id==collection_id).select()

        redirect(URL(r=request, f='list_collections'))

    elif form.errors: response.flash='form errors'
    return dict(form=form)

@auth.requires_login()
def add_story():


    form = SQLFORM(db.story, _name='story_form', hidden_fields=['title'])

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

    stories = {}

    stories = story
    regions=story.region
    topics=story.topic
    sort_value=story.sort_value
    length=len(stories)

    story_list = []

    if story.nprid != '':
        npr_story = format_npr_story(story.nprid, story.id)
        story_list.append(npr_story)
        print story_list
    else:
        x = format_local_story(story.id)
        story_list.append(x)

    return dict(collection=story.collection, story=story, stories=stories, length=length, regions=regions, topics=topics, story_list=story_list)

def format_npr_story(nprid, story_id):
    story=db.story[story_id]

    # get the story from the npr api as a json string
    json = api.query(nprid)

    # turn the json string into a dictionary
    # json = 'Some sample text.'
    # results = 'Some sample text.'
    results = json
    results = simplejson.loads(results)
    # print results

    # get title
    title = results['list']['story'][0]['title'].values()[0]

    # get description
    description = results['list']['story'][0]['teaser'].values()[0]

    # get url
    try:
        results['list']['story'][0]['link'][2].values()[0]
    except IndexError:
        url = 'http://npr.org'
    else:
        url = results['list']['story'][0]['link'][2].values()[0]

    # get date
    date = results['list']['story'][0]['pubDate'].values()[0]

    # get image
    try:
        results['list']['story'][0]['image'][0]['src']
    except KeyError:
        image_url = ''
    else:
        image_url = results['list']['story'][0]['image'][0]['src']

    # get image
    try:
        results['list']['story'][0]['audio'][0]['format']['mp3']['$text']
    except KeyError:
        audio_url = ''
    else:
        audio_url = results['list']['story'][0]['audio'][0]['format']['mp3']['$text']
        
    # get qrcode
    if story.qrcode != '':
        qrcode_url = '../download/' + str(story.qrcode)
    else:
        qrcode_url = str(story.qrcode)

    # print(image_url)

    # get topic
    topics=story.topic

    # get region
    regions=story.region

    # get latitude
    latitude=story.latitude

    # get longitude
    longitude=story.longitude

    # get address
    address=story.address

    return dict(story_id=story_id,title=title,description=description,url=url,date=date,audio_url=audio_url,image_url=image_url,qrcode_url=qrcode_url,latitude=latitude,longitude=longitude,address=address,topics=topics,regions=regions)


def format_local_story(story_id):
    story=db.story[story_id]

    title = story.title
    description = story.description
    url = story.url
    date = story.date

    # get image
    if story.image != '':
        image_url = '../download/' + story.image
    else:
        image_url = story.image_url

    # get audio
    if story.audio != '':
        audio_url = '../download/' + story.audio
    else:
        audio_url = story.audio_url

    # get qrcode
    if story.qrcode != '':
        qrcode_url = '../download/' + str(story.qrcode)
    else:
        qrcode_url = str(story.qrcode)

    # get topic
    topics=story.topic

    # get region
    regions=story.region

    # get latitude
    latitude=story.latitude

    # get longitude
    longitude=story.longitude

    # get address
    address=story.address

    return dict(story_id=story_id,title=title,description=description,url=url,date=date,audio_url=audio_url,image_url=image_url,qrcode_url=qrcode_url,latitude=latitude,longitude=longitude,address=address,topics=topics,regions=regions)


def view_collection():
    stories = {}
    stories_by_sort_value = {}
    collection_id=int(request.args(0))
    collection = db.collection[collection_id] or redirect(error_page)
    stories=db(db.story.collection.contains(collection_id)).select(orderby=db.story.date)
    stories_by_sort_value=db(db.story.collection.contains(collection_id)).select(orderby=db.story.sort_value)
    topics=db(db.story.topic.contains(collection_id)).select(orderby=db.story.title)
    length=len(stories)
    
    scheme = request.env.get('WSGI_URL_SCHEME', 'http').lower()
    # link = scheme + '://' + request.env.http_host + request.env.path_info
    link_to_feed = scheme + '://' + request.env.http_host + '/publicradioroadtrip/default/view_collection_feed/' + str(collection.id)
        
    story_list = []
    region_list = []
    topic_list = []
    
    end_latlang_length = length -1
    """
    # an attempt to get around the restriction:
    # "The maximum allowed waypoints is 8, plus the origin, and destination."
    if end_latlang_length > 8:
        end_latlang_length = 8
    """
    
    start_latlang = stories[0].latitude + ',' + stories[0].longitude
    end_latlang = stories[end_latlang_length].latitude + ',' + stories[end_latlang_length].longitude

    if collection.sort_type == 'Date':
        for story in stories:
            if story.nprid != '':
                npr_story = format_npr_story(story.nprid, story.id)
                story_list.append(npr_story)
                # print story_list
            else:
                x = format_local_story(story.id)
                story_list.append(x)
    elif collection.sort_type == 'Sort Values':
        for story in stories_by_sort_value:
            if story.nprid != '':
                npr_story = format_npr_story(story.nprid, story.id)
                story_list.append(npr_story)
                # print story_list
            else:
                x = format_local_story(story.id)
                story_list.append(x)
    else: 
        for story in stories:
            if story.nprid != '':
                npr_story = format_npr_story(story.nprid, story.id)
                story_list.append(npr_story)
                # print story_list
            else:
                x = format_local_story(story.id)
                story_list.append(x)
    
    # this needs to be fixed:
    """
    for story in stories:
        if story.region != '':
            x = int(story.region[0])
            y = db.region[x]
            if y not in region_list:
                region_list.append(y)

    for story in stories:
        if story.topic != '':
            x = int(story.topic[0])
            y = db.topic[x]
            if y not in topic_list:
                topic_list.append(y)
    """




    return dict(collection=collection, stories=stories, length=length, region_list=region_list, topic_list=topic_list, story_list=story_list, start_latlang=start_latlang, end_latlang=end_latlang, link_to_feed=link_to_feed)

def view_collection_feed():
    """ 
    Creates an rss feed.  Creates items (based on stories) for this feed.  Items have audio enclosures (will these always be mp3?).

    """

    stories = {}
    collection_id=request.args(0)
    collection = db.collection[collection_id] or redirect(error_page)
    stories=db(db.story.collection.contains(collection_id)).select(orderby=db.story.title)
    email = db(db.auth_user.id == db.auth_user.id==collection.created_by).select(db.auth_user.email).as_list()
    email = email[0]['email']
    first_name = db(db.auth_user.id == db.auth_user.id==collection.created_by).select(db.auth_user.first_name).as_list()
    first_name = first_name[0]['first_name']
    last_name = db(db.auth_user.id == db.auth_user.id==collection.created_by).select(db.auth_user.last_name).as_list()
    last_name = last_name[0]['last_name']
    length=len(stories)
    # print email
    # print first_name
    # print last_name
    scheme = request.env.get('WSGI_URL_SCHEME', 'http').lower()
    # rss = rss2.RSS2(title=collection.title,
    rss = GeoRSSFeed(title=collection.title,
        link = scheme + '://' + request.env.http_host + request.env.path_info,
        description = collection.description,
        lastBuildDate = collection.modified_on,
        items = [
            # rss2.RSSItem(title = story.title,
            GeoRSSItem(title = story.title,
            author = email + '(' + first_name + ' ' + last_name + ')',
            link = story.url,
            guid = scheme + '://' + request.env.http_host + '/publicradioroadtrip/default/view_story/' + str(story.id),
            enclosure = rss2.Enclosure(story.audio_url, 0, 'audio/mpeg'),
            description = story.description,
            content = '<p><a href="' + story.audio_url + '">Listen here</a></p>',
            point = story.latitude + ' ' + story.longitude,
            # comments = 'test',
            pubDate = story.date) for story in stories])
            
    response.headers['Content-Type']='application/rss+xml'
    return rss2.dumps(rss)

def view_collection_for_print():    
    stories = {}
    collection_id=int(request.args(0))
    collection = db.collection[collection_id] or redirect(error_page)
    stories=db(db.story.collection.contains(collection_id)).select(orderby=db.story.date)

    # table = SQLTABLE(stories, orderby=True, _class='sortable', _width="100%")
    table = SQLTABLE(stories, columns=['story.title', 'story.address', 'story.description'], truncate=250)

    response.title = collection.title
    
    if request.extension=="pdf":
        from gluon.contrib.pyfpdf import FPDF, HTMLMixin

        # create a custom class with the required functionalities 
        class MyFPDF(FPDF, HTMLMixin):
            def header(self): 
                "hook to draw custom page header"
                self.set_font('Arial','B',15)
                self.cell(65) # padding
                self.cell(60,10,response.title,1,0,'C')
                self.ln(20)
                
            def footer(self):
                "hook to draw custom page footer (printing page numbers)"
                self.set_y(-15)
                self.set_font('Arial','I',8)
                txt = 'Page %s of %s' % (self.page_no(), self.alias_nb_pages())
                self.cell(0,10,txt,0,0,'C')

        pdf=MyFPDF()
        # create a page and serialize/render HTML objects
        pdf.add_page()

        # pdf.write_html(str(XML(story_list)))
        # pdf.write_html(str(HTML(DIV(story_list))))

        # pdf.write_html(str(HTML(table)))
        
        # prepare PDF to download:
        response.headers['Content-Type']='application/pdf'
        return pdf.output(dest='S')
        
    else:
        # normal html view:
        # return dict(collection=collection, stories=stories)
        return str(table)

def collection_markers():
    response.headers['Content-Type']='text/xml'
    stories = {}
    collection_id=int(request.args(0))
    collection = db.collection[collection_id] or redirect(error_page)
    stories=db(db.story.collection.contains(collection_id)).select(orderby=db.story.title)
    return dict(collection=collection, stories=stories)

@auth.requires_login()
def edit_story():
    story_id=request.args(0)
    story=db.story[story_id] or redirect(error_page)
    form=crud.update(db.story,story,next=url('view_story',story_id))
    """
    form=crud.update(db.story,story)
    if form.accepts(request.vars, session):
        create_qrcode(story.id, story.audio_url)
        session.flash = 'Record Updated'
        redirect(URL('default/view_story',story_id))
    """
    return dict(form=form)

"""
@auth.requires_login()
def add_story():
    form = SQLFORM(db.story)
    if form.accepts(request.vars, session):
        create_qrcode(form.vars.id, form.vars.audio_url)
        session.flash = 'Record Updated'
    return dict(form=form)
"""

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
