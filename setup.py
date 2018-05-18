#!/usr/bin/env python

from distutils.core import setup

setup(name='tftpy',
      version='0.7.0',
      description='Python TFTP library',
      author='Michael P. Soulier',
      author_email='msoulier@digitaltorque.ca',
      url='http://github.com/msoulier/tftpy',
      packages=['tftpy'],
      scripts=['bin/tftpy_client.py','bin/tftpy_server.py'],
      project_urls={
          'Documentation': 'http://tftpy.sourceforge.net/sphinx/index.html',
          'Source': 'https://github.com/msoulier/tftpy/',
          'Tracker': 'https://github.com/msoulier/tftpy/issues',
      },
      python_requires='>=2.7',
      classifiers=[
        'Programming Language :: Python :: 2.7',
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Environment :: No Input/Output (Daemon)',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Topic :: Internet',
        ]
      )
