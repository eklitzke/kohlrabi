"""This is an example database module. Using some metaclass magic, the kohlrabi
instance that imports this file will learn about the query report.
"""
from sqlalchemy import *
from kohlrabi.db import *

class MySQLQueryReport(Base):

    __tablename__ = 'mysql_query_report'
    __metaclass__ = ReportMeta

    id = Column(Integer, primary_key=True)
    date = Column(Date, nullable=False)
    servlet = Column(String, nullable=False)
    servlet_count = Column(Integer, nullable=False)
    query_text = Column(String, nullable=False)
    query_count = Column(Integer, nullable=False)
    query_mean = Column(Float, nullable=False)
    query_median = Column(Float, nullable=False)
    query_total = Column(Float, nullable=False)
    query_95 = Column(Float, nullable=False)
    query_stddev = Column(Float, nullable=False)

    display_name = 'MySQL Query Report'
    html_table = [
        ReportColumn('Servlet', 'servlet'),
        ReportColumn('Weight', 'query_total'),
        ReportColumn('Query Text', 'query_text', css_class='tiny'),
        ReportColumn('Servlet Count', 'servlet_count'),
        ReportColumn('Count', 'query_count'),
        ReportColumn('Mean', 'query_mean'),
        ReportColumn('Median', 'query_median'),
        ReportColumn('95th', 'query_95'),
        ReportColumn('Std. Dev.', 'query_stddev'),
        ]

    @classmethod
    def report_data(cls, date):
        return session.query(cls).filter(cls.date == date).order_by(cls.servlet).order_by(desc(cls.query_total))

class MemcacheReport(Base):

    __tablename__ = 'memcache_report'
    __metaclass__ = ReportMeta

    id = Column(Integer, primary_key=True)
    date = Column(Date, nullable=False)
    servlet = Column(String, nullable=False)
    servlet_count = Column(Integer, nullable=False)
    cache_name = Column(String, nullable=False)
    hits = Column(Integer, default=0, nullable=False)
    misses = Column(Integer, default=0, nullable=False)
    hit_rate = Column(Float, default=0, nullable=False)
    frequency = Column(Float, default=0, nullable=False)
    latency_mean = Column(Float, default=0, nullable=False)
    latency_stddev = Column(Float, default=0, nullable=False)
    bytes_mean = Column(Float, default=0, nullable=False)
    bytes_stddev = Column(Float, default=0, nullable=False)
    miss_latency_mean = Column(Float, default=0, nullable=False)
    miss_latency_stddev = Column(Float, default=0, nullable=False)
    time_saved = Column(Float, default=0, nullable=False)

    display_name = 'Memcache Report'
    html_table = [
        ReportColumn('Servlet', 'servlet'),
		ReportColumn('Cache Name', 'cache_name'),
		ReportColumn('Frequency', 'frequency'),
		ReportColumn('Time Saved', 'time_saved'),
		ReportColumn('Servlet Count', 'servlet_count'),
		ReportColumn('Hits', 'hits'),
		ReportColumn('Misses', 'misses'),
		ReportColumn('Hit Rate', 'hit_rate', format=format_percentage),
		ReportColumn('Latency Mean', 'latency_mean'),
		ReportColumn('Latency Stddev', 'latency_stddev'),
		ReportColumn('Miss Latency Mean', 'miss_latency_mean'),
		ReportColumn('Miss Latency Stddev', 'miss_latency_stddev'),
		ReportColumn('Kb Mean', 'bytes_mean', format=format_kb),
		ReportColumn('Kb Stddev', 'bytes_stddev', format=format_kb),
        ]

    @classmethod
    def report_data(cls, date):
        return session.query(cls).filter(cls.date == date).order_by(cls.servlet).order_by(desc(cls.frequency)).order_by(desc(cls.hits))
