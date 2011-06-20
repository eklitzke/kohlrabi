from __future__ import with_statement

import os
import optparse
import yaml
import logging
import sys
try:
    import daemon
    import lockfile
except ImportError:
    daemon, lockfile = None, None

import tornado.httpserver
import tornado.ioloop

import kohlrabi.db
import kohlrabi.handlers

log = logging.getLogger('kohlrabi')

def get_application(base_path, config, debug):
    """Get a runnable instance of torando.web.Application"""
    application = kohlrabi.handlers.application(
        static_path=os.path.join(base_path, 'static'),
        template_path=os.path.join(base_path, 'templates'),
        debug=debug,
        config=config
        )

    db_path = config.get('database', 'sqlite:///:memory:')
    kohlrabi.db.bind(db_path, module, create_tables=debug)
    return application

if __name__ == '__main__':
    parser = optparse.OptionParser()
    parser.add_option('-c', '--config', default='./config.yaml', help='The config file to use')
    parser.add_option('--debug', default=False, action='store_true', help='Run in debug mode')
    if daemon:
        parser.add_option('-d', '--daemon', default=False, action='store_true', help='run as a daemon')
    parser.add_option('-m', '--module', default=None, help='which database module to load')
    parser.add_option('-p', '--port', type='int', default=8888, help='What port to listen on')
    opts, args = parser.parse_args()

    try:
        with open(opts.config, 'r') as config_file:
            config = yaml.load(config_file)
    except IOError:
        print >> sys.stderr, 'Failed to load config file %r' % (opts.config,)
        config = {}

    if opts.debug:
        debug = opts.debug
    else:
        debug = config.get('debug', False)

    module = opts.module or config.get('module')
    if not module:
        parser.error('Must specify a database module (e.g. -m kohlrabi.modules.example)')

    base_path = os.path.dirname(__file__)
    if not base_path:
        base_path = os.getcwd()
    base_path = os.path.abspath(base_path)

    # TODO: this whole daemon thing is kind of ghetto... it might be better to
    # just require zygote to run the application in daemon mode

    def run_application():
        app = get_application(base_path, config, debug)
        http_server = tornado.httpserver.HTTPServer(app)
        http_server.listen(opts.port)
        tornado.ioloop.IOLoop.instance().start()

    if daemon and opts.daemon:
        tmpdir = os.environ.get('TMPDIR', '/tmp')
        pidfile = lockfile.FileLock(os.path.join(tmpdir, 'kohlrabi.pid'))
        with daemon.DaemonContext(pidfile=pidfile):
            logging.basicConfig(filename=os.path.join(tmpdir, 'kohlrabi.log'))
            run_application()
    else:
        stream_handler = logging.StreamHandler()
        stream_handler.setLevel(logging.DEBUG if debug else logging.INFO)
        log.addHandler(stream_handler)
        run_application()
