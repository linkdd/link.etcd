Tutorial
========

This tutorial covers how to use the ``Etcd`` middleware and the provided
configuration driver.

A functional instance of **etcd** must be running.

Configure the middleware
------------------------

Configuration file for the middleware is stored in:

.. code-block:: text

   $B3J0F_CONF_DIR/link/etcd/middleware.conf

Here is the default configuration if nothing is specified:

.. code-block:: ini

   [ETCD]
   host = localhost
   port = 4001
   # srv_domain is not defined
   version_prefix = /v2
   read_timeout = 60
   allow_redirect = True
   protocol = http
   # cert is not defined
   # ca_cert is not defined
   # username is not defined
   # password is not defined
   allow_reconnect = False
   use_proxies = False
   # expected_cluster_id is not defined
   per_host_pool_size = 10

Then you can instantiate the middleware:

.. code-block:: python

   from link.etcd.middleware import EtcdMiddleware

   client = EtcdMiddleware()

The dict protocol has been (partially) implemented to access data:

.. code-block:: python

   client['/collection'] = {
       'subcollection': [
           'item1',
           'item2'
       ]
   }

   # This will write:
   #   - item1 in /collection/subcollection/1
   #   - item2 in /collection/subcollection/2

   tree = client['/collection']

   # tree will contains the dict set above

   del client['/collection']

   # this will erase the whole tree

Using the configuration driver
------------------------------

When creating a configurable, just use the provided configuration driver:

.. code-block:: python

   from b3j0f.conf import Configurable, category, Parameter
   from link.etcd.driver import EtcdConfDriver


   @Configurable(
       paths='myproject/myconfigurable.conf',
       conf=category(
           'MYCONF',
           Parameter(name='myparam')
       ),
       drivers=[EtcdConfDriver()]
   )
   class MyConfigurable(object):
       pass

Then, your configuration will be stored in **etcd** at the following path:

.. code-block:: text

   /myproject/myconfigurable.conf/
   /myproject/myconfigurable.conf/MYCONF
   /myproject/myconfigurable.conf/MYCONF/myparam
