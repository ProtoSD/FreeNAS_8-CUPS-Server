#!/bin/sh

import os
import platform
import re
import sys
import stat
import signal

from flup.server.fcgi import WSGIServer
from subprocess import Popen, PIPE

HERE = os.path.abspath(os.path.dirname(__file__))
sys.path.insert(0, os.path.join(HERE, "lib/python2.7/site-packages"))

cups-server_pbi_path = "/usr/pbi/cups-server-" + platform.machine()
cups-server_etc_path = os.path.join(cups-server_pbi_path, "etc")
cups-server_mnt_path = os.path.join(cups-server_pbi_path, "mnt")
cups-server_fcgi_pidfile = "/var/run/fcgi_cups-server.pid"
cups-server_fcgi_wwwdir = os.path.join(cups-server_pbi_path, "www")
cups-server_control = "/usr/local/etc/rc.d/mysql-server"


def cups-server_fcgi_start(args):
    if len(args) < 2:
        return False

    ip = args[0]
    port = long(args[1])

    pid = os.fork()
    if pid < 0:
        return False
    if pid != 0:
        sys.exit(0)

    os.setsid()

    os.environ['DJANGO_SETTINGS_MODULE'] = 'cups-serverUI.settings'
    import django.core.handlers.wsgi
    app = django.core.handlers.wsgi.WSGIHandler()

    res = False
    with open(cups-server_fcgi_pidfile, "wb") as fp:
        fp.write(str(os.getpid()))
        fp.close()

        res = WSGIServer(app, bindAddress=(ip, port)).run()

    return res


def cups-server_fcgi_stop(args):
    res = False
    if os.access(cups-server_fcgi_pidfile, os.F_OK):
        with open(cups-server_fcgi_pidfile, "r") as fp:
            pid = long(fp.read())
            fp.close()

            os.kill(pid, signal.SIGHUP)
            res = True

    if os.access(cups-server_fcgi_pidfile, os.F_OK):
        os.unlink(cups-server_fcgi_pidfile)

    return res


def cups-server_fcgi_status(args):
    res = False
    if os.access(cups-server_fcgi_pidfile, os.F_OK):
        with open(cups-server_fcgi_pidfile, "r") as fp:
            pid = long(fp.read())
            fp.close()
            res = True

    return res


def cups-server_fcgi_configure(args):
    return True


def main(argc, argv):
    if argc < 2:
        sys.exit(1)

    commands = {
        'start': cups-server_fcgi_start,
        'stop': cups-server_fcgi_stop,
        'status': cups-server_fcgi_status,
        'configure': cups-server_fcgi_configure
    }

    if not commands.has_key(argv[0]):
        sys.exit(1)

    if not commands[argv[0]](argv[1:]):
        sys.exit(1)

    sys.exit(0)

if __name__ == '__main__':
    main(len(sys.argv), sys.argv[1:])
