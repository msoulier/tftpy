#!/usr/bin/env python

from distutils.core import setup

setup(name='tftpy',
      version='0.5.0',
      description='Python TFTP library',
      author='Michael P. Soulier',
      author_email='msoulier@digitaltorque.ca',
      url='http://tftpy.sourceforge.net',
      packages=['tftpy'],
      scripts=['bin/tftpy_client.py','bin/tftpy_server.py'],
      classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Environment :: No Input/Output (Daemon)',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Topic :: Internet',
        ]
      )
