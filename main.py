from __future__ import with_statement

import os
import optparse
import yaml
import logging
try:
    import daemon
    import lockfile
except ImportError:
    daemon, lockfile = None, None

import tornado.httpserver
import tornado.ioloop

import kohlrabi.db
import kohlrabi.handlers

if __name__ == '__main__':
    parser = optparse.OptionParser()
    parser.add_option('-c', '--config', default='./config.yaml', help='The config file to use')
    if daemon:
        parser.add_option('-d', '--daemon', default=False, action='store_true', help='run as a daemon')
    parser.add_option('-m', '--module', default=None, help='which database module to load')
    parser.add_option('-p', '--port', type='int', default=8888, help='What port to listen on')
    opts, args = parser.parse_args()

    try:
        with open(opts.config, 'r') as config_file:
            config = yaml.load(config_file)
    except IOError:
        parser.error('Failed to load config file %r' % (opts.config,))
    
    module = opts.module or config.get('module')
    if not module:
        parser.error('Must specify a database module')

    base_path = os.path.dirname(__file__)
    if not base_path:
        base_path = os.getcwd()
    base_path = os.path.abspath(base_path)
    def run_application():
        debug = config.get('debug', False)
        path_prefix = config.get('path_prefix', None)
        if path_prefix:
            path_prefix = '/' + path_prefix.strip('/') + '/'

        application = kohlrabi.handlers.application(
            static_path=os.path.join(base_path, 'static'),
            template_path=os.path.join(base_path, 'templates'),
            debug=debug,
            path_prefix=path_prefix
            )

        kohlrabi.db.bind(config.get('database', 'sqlite:///:memory:'), module, create_tables=debug)

        http_server = tornado.httpserver.HTTPServer(application)
        http_server.listen(opts.port)
        tornado.ioloop.IOLoop.instance().start()

    if daemon and opts.daemon:
        tmpdir = os.environ.get('TMPDIR', '/tmp')
        pidfile = lockfile.FileLock(os.path.join(tmpdir, 'kohlrabi.pid'))
        with daemon.DaemonContext(pidfile=pidfile):
            logging.basicConfig(filename=os.path.join(tmpdir, 'kohlrabi.log'))
            run_application()
    else:
        run_application()
