.. TFTPy documentation master file, created by
   sphinx-quickstart on Sun Jul 11 18:48:32 2010.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

TFTPy
=====

TFTPy is a pure python TFTP implementation.

.. toctree::
   :maxdepth: 2

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

Requirements
============
Python 2.3+, I think. I haven't tested in Python 2.3 in a while but it should
still work. Let me know if it doesn't.

Installation
============

Examples
========

API Documentation
=================

Front-end Modules
-----------------
These modules are the ones that you will need to use directly to implement a
TFTP client or server.

The :mod:`tftpy` Module
~~~~~~~~~~~~~~~~~~~~~~~
.. automodule:: tftpy
   :members:
   :show-inheritance:

The `TftpClient` Module
~~~~~~~~~~~~~~~~~~~~~~~
.. automodule:: tftpy.TftpClient
   :members:
   :show-inheritance:

The `TftpServer` Module
~~~~~~~~~~~~~~~~~~~~~~~
.. automodule:: tftpy.TftpServer
   :members:
   :show-inheritance:

Back-end Modules
----------------

The `TftpPacketFactory` Module
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
.. automodule:: tftpy.TftpPacketFactory
   :members:
   :show-inheritance:

The `TftpPacketTypes` Module
~~~~~~~~~~~~~~~~~~~~~~~~~~~~
.. automodule:: tftpy.TftpPacketTypes
   :members:
   :show-inheritance:

The `TftpShared` Module
~~~~~~~~~~~~~~~~~~~~~~~
.. automodule:: tftpy.TftpShared
   :members:
   :show-inheritance:

The `TftpStates` Module
~~~~~~~~~~~~~~~~~~~~~~~
.. automodule:: tftpy.TftpStates
   :members:
   :show-inheritance:
