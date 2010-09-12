"""This is an example database module. Using some metaclass magic, the kohlrabi
instance that imports this file will learn about the query report.
"""
from sqlalchemy import *
from kohlrabi.db import Base, ReportMeta, ReportColumn, session

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

    display_name = 'Query Report'
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
