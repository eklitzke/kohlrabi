import os
import math
from collections import defaultdict
import datetime
import sqlalchemy
import traceback
try:
    from sqlalchemy.exception import OperationalError
except ImportError:
    from sqlalchemy.exc import OperationalError
try:
    import simplejson as json
except ImportError:
    import json

import tornado.web
from tornado.escape import url_escape, url_unescape, xhtml_escape
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
            'jquery_url': '//ajax.googleapis.com/ajax/libs/jquery/2.0.0/jquery.min.js'
        }

    def parse_date(self, date_string):
        if date_string and date_string != 'current':
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

    def render_json(self, obj):
        self.set_header('Content-Type', 'application/json')
        self.write(json.dumps(obj))

    def get_error_html(self, status_code, **kwargs):
        db.session.rollback()
        self.set_header('Content-Type', 'text/plain')
        return traceback.format_exc()

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

        self.env['dates'] = dates
        report_names = set()
        for d in dates:
            report_names |= set((r.display_name, r.__name__) for r in date_map[d])

        self.env['report_names'] = list(sorted(report_names))
        self.env['reports'] = []

        # this is *also* really inefficient and ghetto
        for d in dates:
            links = []
            for report_name, report_table in self.env['report_names']:
                for t in date_map[d]:
                    if t.display_name == report_name:
                        links.append((report_name, report_table))
                        break
                else:
                    links.append(None)
            self.env['reports'].append((d.strftime('%Y-%m-%d'), links))

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
        path = self.request.uri.lstrip('/')
        components = path.split('/')
        tbl, date = components[-2:]
        if not date or date == 'current':
            date = getattr(db, tbl).current_date()
        else:
            date = self.parse_date(date)
        self.env['date'] = date
        self.env['data'] = getattr(db, tbl).report_data(date)
        self.env['columns'] = getattr(db, tbl).html_table
        self.env['first_column'] = getattr(db, tbl).html_table[0].display
        self.env['title'] = getattr(db, tbl).display_name + ' ' + date.strftime('%Y-%m-%d')
        self.render('report.html')

def get_previous_queries(self):
    previous_queries = self.get_cookie('queries', None)
    if previous_queries:
        try:
            previous_queries = json.loads(url_unescape(previous_queries))
        except Exception:
            previous_queries = []
    else:
        previous_queries = []
    return previous_queries

class Query(RequestHandler):

    path = '/query'

    def get(self):
        self.env['previous_queries'] = get_previous_queries(self)
        self.env['initial_sql'] = ''
        self.env['schemata'] = list(db.session.execute("SELECT name, sql FROM sqlite_master WHERE type = 'table'"))
        if self.env['schemata']:
            self.env['initial_sql'] = self.env['schemata'][0][1]
        self.render('query.html')

class ShowSchema(RequestHandler):

    path = '/query/schema/[-a-zA-Z0-9_]+'

    def get(self):
        table_name = self.request.uri.split('/')[-1]
        sql, = db.session.connection().execute(
            sqlalchemy.text("SELECT sql FROM sqlite_master WHERE type = 'table' AND name = :name"), name=table_name).first()
        self.render_json({'sql': sql.strip()})

class RunQuery(RequestHandler):
    path = '/query/run'

    def post(self):
        previous_queries = get_previous_queries(self)

        query = self.get_argument('query');
        query.rstrip(';')
        previous_queries = ([query] + previous_queries)[:5]
        try:
            rows = [list(row) for row in db.session.execute(query)]
        except OperationalError, e:
            self.render_json({'error': xhtml_escape(str(e))})
            return
        else:
            self.set_cookie('queries', url_escape(json.dumps(previous_queries)))
            safe_queries = [xhtml_escape(q) for q in previous_queries]
            self.render_json({'results': rows, 'previous_queries': safe_queries})

class Status(RequestHandler):

    path = '/status'

    def get(self):
        self.render_json({'status': 'ok'})

def application(**settings):
    """Create a tornado.web.Application object for kohlrabi"""
    global config
    config = settings.pop('config')
    path_prefix = config.get('path_prefix', '')
    if path_prefix:
        path_prefix = '/' + path_prefix.strip('/') + '/'
    else:
        path_prefix = '/'
    config['path_prefix'] = path_prefix

    settings['static_url_prefix'] = os.path.join(path_prefix, 'static/') if path_prefix else '/static'
    norm_path = lambda x: os.path.join(path_prefix, x.lstrip('/')) if x else x
    uri_map = [(norm_path(handler.path), handler) for handler in handlers if hasattr(handler, 'path')]
    app = tornado.web.Application(uri_map, **settings)
    return app
