Kohlrabi is a mini webapp, based off of Tornado, for viewing tabular report
data. You can try running it like this:

    python kohlrabi/main.py -c config.yaml.example

Customizing Kohlrabi
====================

Out of the box, Kohlrabi includes a module `kohlrabi.modules.example` that
demonstrates some example reports. These are meant to be an inspiration for the
types of reports you might want to put into Kohlrabi, and how to create a new
class. However, they're probably not very useful to most people; most people
will need to customize what data they store in Kohlrabi to be slightly or
entirely different.

The way customization works in Kohlrabi is to create a new Python module in the
same format as the one in `kohlrabi.modules.example` (look at the source
code). In the configuration file, you'll specify this as your `module`; this
module should be something available in `sys.path` that can be imported using
Python's `__import__` directive. Any SQLAlchemy tables in this module with the
metaclass `ReportMeta` will be detected by Kohlrabi as a potential data source,
which you can upload data for.

Reports are uploaded to Kohlrabi by making an HTTP POST request to the Kohlrabi
server, indicating the date, the data for the report, and the data source.

The next section will cover this in more detail.

Adding New Reports
------------------

It's easiest to explain this with an example. Suppose the report module
specified by the config `module` variable has the following code in it:

```python
from sqlalchemy import *
from kohlrabi.db import *

class DailySignups(Base):
    __tablename__ = 'daily_signups_report'
    __metaclass__ = ReportMeta

    id = Column(Integer, primary_key=True)
    date = Column(Date, nullable=False)
    referrer = Column(String, nullable=False)
    clickthroughs = Column(Integer, nullable=False, default=0)
    signups = Column(Integer, nullable=False, default=0)

    display_name = 'Daily Signups'
    html_table = [
        ReportColumn('Referrer', 'referrer'),
        ReportColumn('Click-Throughs', 'clickthroughs'),
        ReportColumn('Signups', 'signups'),
        ]

    @classmethod
    def report_data(cls, date):
        return session.query(cls).filter(cls.date == date).order_by(cls.signups.id)
```

This is a data source that will track users who sign up on your site, based on
the HTTP `Referrer` header. The table has three columns: `referrer` will track
the domain that referred the initial visit to your site, `clickthroughs` will
track who many people came to the site from that referrer, and `signups` will
track how many of those people actually signed up.

The next step is to create the table in your Kohlrabi SQLite database. If you
don't do this, Kohlrabi will automatically create the table, but the table won't
have any indexes. In most cases you should probably at least add an index on the
`date` column, and probably an index on the full set of columns you plan on
querying from the `report_data` method:

```sql
CREATE TABLE daily_signups_report (
    id INTEGER NOT NULL,
    date DATE NOT NULL,
    referrer VARCHAR NOT NULL,
    clickthroughs INTEGER NOT NULL,
    signups INTEGER NOT NULL,
    PRIMARY KEY (id)
);
CREATE INDEX daily_signups_date_idx ON daily_signups_report (date, signups);
```

OK, that's all the setup you need to do on the Kohlrabi side of things: create a
Python SQLAlchemy class, and create a table in your SQLite database. The second
step is to write a report that generates data to store in Kohlrabi. You can do
this however you want, in any language you want. This report should finish by
making a normal HTTP POST request to your Kohlrabi instance, with URL `/upload`,
and the following POST parameters:

* `date` -- the date for this data, in the format YYYY-MM-DD
* `table` -- the name of the Python class you defined earlier (in this example, `DailySignups`)
* `data` -- A JSON list of dictionaries mapping column names (excluding `id` and `date`) to their respective values

For instance, if we were running Kohlrabi on `http://localhost:8888`, then the
following Python code would generate a sample report for 2001-01-1:

```python
import json
import urllib

urllib.urlopen('http://localhost:8888/upload',
    urllib.urlencode({'date': '2010-01-01',
                      'data': json.dumps([{'referrer': 'www.yahoo.com',
                                           'clickthroughs': 100,
                                           'signups': 7},
                                          {'referrer': 'www.google.com',
                                           'clickthroughs': 500,
                                           'signups': 42}]),
                      'table': 'DailySignups'}))
```

Just to reiterate: because the interface to Kohlrabi is a normal HTTP request
using JSON, you can use any language to send data to Kohlrabi. You can use Java,
Ruby, a bash script, etc. Whatever works for you.

Configuration
-------------

This section describes the parameters that can be placed in the config file. The
config file should be in YAML format. You can specify the path to the
configuration file by invoking `kohlrabi/main.py` with the `-c` option, e.g.
`python kohlrabi/main.py -c /etc/kohlrabi.yaml`.

* `database` -- this is a string with the SQLAlchemy-style path to the
  database. An example would be `sqlite:///foo.sqlite` for a `foo.sqlite` file
  in the current directory, or `sqlite:////tmp/foo.sqlite` for
  `/tmp/foo.sqlite`. You can also use MySQL, PostgreSQL, etc. For more details,
  refer to the upstream
  [SQLAlchemy Documentation](http://www.sqlalchemy.org/docs/core/engines.html#sqlalchemy.create_engine)
  on creating engines.
* `debug` -- forces debug mode. You can also invoke `main.py` with the `--debug`
  option to get the same effect (debug mode is enabled if either switch is on).
* `module` -- this is the name of the Python database module you're using. For
  instance, a valid value might be `kohlrabi.modules.example`. See below for
  more details on setting this value.
* `path_prefix` -- this changes the prefix used for all URLs internally within
  kohlrabi. For instance, you might run kohlrabi via Apache's `mod_proxy`
  ProxyPass, and all URLs should be prefixed with `/kohlrabi/`. The use of
  initial/trailing slashes here is not signficant, they'll be added if you omit
  them.

Running custom database modules is achieved by specifying a `module` in your
config file, or invoking `main.py` with the `-m` options. Internally, this is
implemented by Kohlrabi by using Python's `__import__` bulitin to load the
module. This means that if the location of the module is in a place that's not
in your default Python path, you should export that location via the
`PYTHONPATH` environment setting when invoking Kohlrabi.

For instance, suppose Kohlrabi is installed somewhere like
`/usr/lib/python2.7/site-packages` (or in any other site package directory). For
you custom module report, you created a file named
`/tmp/kohlrabi_reports/my_report.py`. When invoking Kohlrabi, you should run it
like so:

    PYTHONPATH="/tmp:$PYTHONPATH" python kohlrabi/main.py -m my_report

This will ensure that the `__import__` statement is able to find the module you
specified.
