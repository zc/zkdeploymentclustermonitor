The zkdeployment cluster monitor monitors a zkdeployment-managed
cluster to make sure it's converged.

The monitor doesn't take any configuration data. Nor does it require
configuration.  There's a prober that always retrieves a single
monitor.

    >>> import pkg_resources
    >>> [monitor] = pkg_resources.load_entry_point(
    ...     pkg_resources.working_set.find(
    ...         pkg_resources.Requirement.parse(
    ...             'zim.zkdeploymentclustermonitor')),
    ...     'zim.monitor.probers', 'default')()

    >>> monitor.name
    'zim.zkdeploymentclustermonitor'

    >>> monitor.interval
    300

    >>> print monitor.__doc__
    Monitor ZooKeeper /hosts for convergence

    >>> monitor.setup(dict(name='mymonitor', interval=300))

    >>> monitor.name
    'mymonitor'

    >>> monitor.interval
    300

    >>> monitor.describe()
    ['/zim.zkdeploymentclustermonitor']

    >>> import pprint
    >>> monitor.process(printing_callback)
    mymonitor
      /zim.zkdeploymentclustermonitor CRITICAL
        No node: /hosts

Oe need to set up a /hosts tree::

  /hosts
    version = 1

.. -> tree

    >>> import zc.zk
    >>> zk = zc.zk.ZK('zookeeper:2181')
    >>> zk.import_tree(tree)

Now, we should be cool:

    >>> monitor.process(printing_callback)
    mymonitor
      /zim.zkdeploymentclustermonitor INFO
        Converged (1 since Thu Oct  4 19:14:11 2012)

Time passes:

    >>> import time
    >>> time.time.return_value += 301
    >>> monitor.process(printing_callback)
    mymonitor
      /zim.zkdeploymentclustermonitor INFO
        Converged (1 since Thu Oct  4 19:14:11 2012)

Now, we get a new host:

  /hosts
    version = 1

    /xxx
      version = None

.. -> tree
    >>> zk.import_tree(tree)

    >>> monitor.process(printing_callback)
    mymonitor
      /zim.zkdeploymentclustermonitor INFO
        Unconverged (xxx after 0 minutes)

Time passes:

    >>> time.time.return_value += 601

We get a new host:

  /hosts
    version = 1

    /xxx
      version = None

    /yyy
      name = 'app42.zope.com'
      version = None


.. -> tree
    >>> zk.import_tree(tree)

    >>> monitor.process(printing_callback)
    mymonitor
      /zim.zkdeploymentclustermonitor INFO
        Unconverged (xxx after 10 minutes)

More time passes and we get antsey:

    >>> time.time.return_value += 601
    >>> monitor.process(printing_callback)
    mymonitor
      /zim.zkdeploymentclustermonitor WARNING
        Unconverged (xxx after 20 minutes)

And eventually, we get pissed:

    >>> time.time.return_value += 901
    >>> monitor.process(printing_callback)
    mymonitor
      /zim.zkdeploymentclustermonitor CRITICAL
        Unconverged (xxx after 35 minutes)

We sort it out:

  /hosts
    version = 1

    /xxx
      version = 1

    /yyy
      name = 'app42.zope.com'
      version = None


.. -> tree
    >>> zk.import_tree(tree)
    >>> monitor.process(printing_callback)
    mymonitor
      /zim.zkdeploymentclustermonitor WARNING
        Unconverged (app42.zope.com after 25 minutes)

But the other host is still unconverged, but we sort that out too:

  /hosts
    version = 1

    /xxx
      version = 1

    /yyy
      name = 'app42.zope.com'
      version = 1


.. -> tree
    >>> zk.import_tree(tree)
    >>> monitor.process(printing_callback)
    mymonitor
      /zim.zkdeploymentclustermonitor INFO
        Converged (1 since Thu Oct  4 19:54:15 2012)

More time passes:

    >>> time.time.return_value += 901
    >>> monitor.process(printing_callback)
    mymonitor
      /zim.zkdeploymentclustermonitor INFO
        Converged (1 since Thu Oct  4 19:54:15 2012)

Update cluster version:

  /hosts
    version = 2

    /xxx
      version = 1

    /yyy
      name = 'app42.zope.com'
      version = 1


.. -> tree
    >>> zk.import_tree(tree)
    >>> monitor.process(printing_callback)
    mymonitor
      /zim.zkdeploymentclustermonitor INFO
        Unconverged (xxx after 0 minutes)

and time passes:

    >>> time.time.return_value += 901
    >>> monitor.process(printing_callback)
    mymonitor
      /zim.zkdeploymentclustermonitor INFO
        Unconverged (xxx after 15 minutes)
