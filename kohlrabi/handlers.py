import os
import math
from collections import defaultdict
import datetime
try:
    import simplejson as json
except ImportError:
    import json

import tornado.web
from kohlrabi import db

config = None
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
            'title': '(kohlrabi)',
            'uri': self.uri,
            'use_ssl': config.get('ssl', False)
        }

    def parse_date(self, date_string):
        if date_string:
            return datetime.datetime.strptime(date_string, '%Y-%m-%d').date()
        else:
            return datetime.date.today()

    def uri(self, path):
        if config['path_prefix']:
            return os.path.join(config['path_prefix'], path.lstrip('/'))
        else:
            return path

    def render(self, template, **kw):
        self.env.update(kw)
        super(RequestHandler, self).render(template, **self.env)

class Home(RequestHandler):

    path = '/[0-9]*'

    DATES_PER_PAGE = 14

    def get(self):
        # this is pretty inefficient
        date_map = defaultdict(list)
        for tbl in db.report_tables:
            for d in tbl.dates():
                date_map[d].append(tbl)

        dates = sorted(date_map.keys(), reverse=True)
        self.env['num_pages'] = int(math.ceil(len(dates) / float(self.DATES_PER_PAGE)))

        # show DATES_PER_PAGE things per page
        page = int(self.request.uri.split('/')[-1] or 1)
        self.env['page'] = page
        dates = dates[self.DATES_PER_PAGE * (page - 1) : self.DATES_PER_PAGE * page]

        self.env['reports'] = []
        for k in dates:
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
        components = path.split('/')
        tbl, date = components[-2:]
        date = self.parse_date(date)
        self.env['data'] = getattr(db, tbl).report_data(date)
        self.env['columns'] = getattr(db, tbl).html_table
        self.env['title'] = getattr(db, tbl).display_name + ' ' + date.strftime('%Y-%m-%d')
        self.render('report.html')

def application(**settings):
    """Create a tornado.web.Application object for kohlrabi"""
    global config
    config = settings.pop('config')
    path_prefix = config.get('path_prefix', None)
    if path_prefix:
        path_prefix = '/' + path_prefix.strip('/') + '/'
    config['path_prefix'] = path_prefix

    settings['static_url_prefix'] = os.path.join(path_prefix, 'static/') if path_prefix else '/static'
    norm_path = lambda x: os.path.join(path_prefix, x.lstrip('/')) if x else x
    uri_map = [(norm_path(handler.path), handler) for handler in handlers if hasattr(handler, 'path')]
    app = tornado.web.Application(uri_map, **settings)
    return app
