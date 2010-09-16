from collections import defaultdict
import datetime
try:
    import simplejson as json
except ImportError:
    import json

import tornado.web
from kohlrabi import db

handlers = []

class RequestMeta(type(tornado.web.RequestHandler)):

    def __init__(cls, name, bases, cls_dict):
        super(RequestMeta, cls).__init__(name, bases, cls_dict)
        handlers.append(cls)
    
class RequestHandler(tornado.web.RequestHandler):

    __metaclass__ = RequestMeta

    def initialize(self):
        super(RequestHandler, self).initialize()
        self.env = {
            'title': '(kohlrabi)'
        }
    
    def parse_date(self, date_string):
        if date_string:
            return datetime.datetime.strptime(date_string, '%Y-%m-%d').date()
        else:
            return datetime.date.today()
    
    def render(self, template, **kw):
        self.env.update(kw)
        super(RequestHandler, self).render(template, **self.env)

class Home(RequestHandler):

    path = '/'

    def get(self):
        date_map = defaultdict(list)
        for tbl in db.report_tables:
            for d in tbl.dates():
                date_map[d].append(tbl)

        self.env['reports'] = []
        for k in sorted(date_map.keys(), reverse=True):
            date = k.strftime('%Y-%m-%d')
            tables = sorted(date_map[k], key=lambda x: x.display_name)
            self.env['reports'].append((date, [{'name': table.display_name, 'table_name': table.__name__} for table in tables]))
        
        self.env['title'] = 'kohlrabi: home'
        self.render('home.html')

class Uploader(RequestHandler):
    """Handles uploads of pickled data."""

    path = '/upload'

    def post(self):
        table = self.get_argument('table')
        data = str(self.get_argument('data'))
        data = json.loads(data)
        date = self.parse_date(self.get_argument('date', None))
        getattr(db, table).load_report(data, date)
        self.set_status(204)

class Report(RequestHandler):

    path = '/report/.*/.*'

    def get(self):
        path = self.request.uri.strip('/')
        _, tbl, date = path.split('/')
        date = self.parse_date(date)
        self.env['data'] = getattr(db, tbl).report_data(date)
        self.env['columns'] = getattr(db, tbl).html_table
        self.env['title'] = getattr(db, tbl).display_name + ' ' + date.strftime('%Y-%m-%d')
        self.render('report.html')

def application(**settings):
    """Create a tornado.web.Application object for kohlrabi"""
    uri_map = [(handler.path, handler) for handler in handlers if hasattr(handler, 'path')]
    return tornado.web.Application(uri_map, **settings)
