import datetime
from sqlalchemy import *
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base, DeclarativeMeta

report_tables = set()

metadata = MetaData()
session = None

def bind(engine_path, import_module):
    global session
    engine = create_engine(engine_path)
    metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()

    if import_module:
        __import__(import_module)
        for v in report_tables:
            if v.__name__ not in globals().keys():
                globals()[v.__name__] = v

Base = declarative_base(metadata=metadata)

class ReportMeta(DeclarativeMeta):

    def __init__(cls, name, bases, cls_dict):
        super(ReportMeta, cls).__init__(name, bases, cls_dict)
        report_tables.add(cls)

        def format_float(v):
            return '%1.3f' % (v or 0)

        def format_int(v):
            return '%d' % (v or 0)

        def format_str(s):
            return str(s)

        for r in cls.html_table:
            coltype = type(cls.__table__._columns[r.name].type)
            if coltype is Float:
                r.format = format_float
                if not r.css_class:
                    r.css_class = 'number'
            elif coltype is Integer:
                r.format = format_int
                if not r.css_class:
                    r.css_class = 'number'
            else:
                r.format = format_str

    def load_report(cls, data, date=None):
        date = date or datetime.date.today()
        for row in session.query(cls).filter(cls.date == date):
            session.delete(row)
        for datum in data:
            if hasattr(cls, 'column_map'):
                datum = dict((cls.column_map[k], v) for k, v in datum.iteritems())
            datum['date'] = date
            session.add(cls(**datum))
        session.commit()
    
    def dates(cls):
        return (row.date for row in session.query(cls).group_by(cls.date))

class ReportColumn(object):

    def __init__(self, display, name, css_class=''):
        self.display = display
        self.name = name
        self.css_class = css_class
