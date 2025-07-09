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
Python 3.8+, I think. I am not testing in all intermediate Python versions, so let me know if you find
any problems.

Installation
============
If you download the source distribution, you can simply use distutils to
install, via::

    python setup.py build
    python setup.py install

Or, as this has been uploaded to pypi, you can use easy_install or pip::

    easy_install tftpy
    pip install tftpy

Once installed you should have the sample client and server scripts in bin,
and you should be able to import the `tftpy` module.

Examples
========
The simplest tftp client::

    import tftpy

    client = tftpy.TftpClient('tftp.digitaltorque.ca', 69)
    client.download('remote_filename', 'local_filename')

The simplest tftp server::

    import tftpy

    server = tftpy.TftpServer('/tftpboot')
    server.listen('0.0.0.0', 69)

See the sample client and server for slightly more complex examples.

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

The `TftpContexts` Module
~~~~~~~~~~~~~~~~~~~~~~~~~
.. automodule:: tftpy.TftpContexts
   :members:
   :show-inheritance:

The `TftpStates` Module
~~~~~~~~~~~~~~~~~~~~~~~
.. automodule:: tftpy.TftpStates
   :members:
   :show-inheritance:
