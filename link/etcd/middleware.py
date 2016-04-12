# -*- coding: utf-8 -*-

from b3j0f.conf import Configurable, Category, Parameter
from b3j0f.middleware import Middleware

from etcd import Client, EtcdKeyNotFound
import os


@Configurable(
    paths='etcd-conf/middleware.conf',
    conf=Category(
        'ETCD',
        Parameter('host', value='localhost'),
        Parameter('port', value=4001),
        Parameter('allow_redirect', value=True),
        Parameter('protocol', value='http')
    )
)
class EtcdMiddleware(Middleware):

    __protocols__ = ['etcd']

    def __init__(self, *args, **kwargs):
        super(EtcdMiddleware, self).__init__(*args, **kwargs)

        self._conn = None

    def _connect(self):
        return Client(
            host=self.host,
            port=self.port,
            allow_redirect=self.allow_redirect,
            protocol=self.protocol
        )

    def _disconnect(self, conn):
        del conn

    def _isconnected(self, conn):
        return conn is not None

    @property
    def conn(self):
        self.connect()
        return self._conn

    def isconnected(self):
        return self._isconnected(self._conn)

    def connect(self):
        if not self.isconnected():
            self._conn = self._connect()

    def disconnect(self):
        if self.isconnected():
            self._disconnect(self._conn)
            self._conn = None

    def __getitem__(self, path):
        try:
            node = self.conn.read(path)

        except EtcdKeyNotFound as err:
            raise KeyError(str(err))

        if node.dir:
            dirnode = self.conn.read(path, recursive=True)

            result = {
                child.key: child.value
                for child in dirnode.leaves
            }

        else:
            result = node.value

        return result

    def _writeval(self, path, val):
        if isinstance(val, dict):
            self.conn.write(path, dir=True)

            for key in val:
                keypath = os.path.join(path, key)
                self._writeval(keypath, val[key])

        elif isinstance(val, list):
            self.conn.write(path, dir=True)

            for item in val:
                self.conn.write(path, item, append=True)

        else:
            self.conn.write(path, val)

    def __setitem__(self, path, val):
        dirname = os.dirname(path)

        if dirname != '/':
            self.conn.write(dirname, dir=True)

        self._writeval(path, val)

    def __delitem__(self, path):
        self.conn.delete(path, recursive=True)

    def __contains__(self, path):
        return path in self.conn
