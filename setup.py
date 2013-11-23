#!/usr/bin/env python

from distutils.core import setup

try:
    from distutils.command.build_py import build_py_2to3 as build_py
except ImportError:
    from distutils.command.build_py import build_py

try:
    from distutils.command.build_scripts import build_scripts_2to3 as build_scripts
except ImportError:
    from distutils.command.build_scripts import build_scripts

setup(name='tftpy',
      version='0.6.1',
      description='Python TFTP library',
      author='Michael P. Soulier',
      author_email='msoulier@digitaltorque.ca',
      url='http://tftpy.sourceforge.net',
      packages=['tftpy'],
      scripts=['bin/tftpy_client.py','bin/tftpy_server.py'],
      cmdclass = {'build_py': build_py, 'build_scripts':build_scripts},
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
