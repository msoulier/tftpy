Copyright, Michael P. Soulier, 2010+

# Installation
While the module should just be in pypi, so you should be able to just do
pip install tftpy, if you have the source distribution you can also install
that with pip install <tarball>. 

I am new to setuptools, so if something isn't working, speak up, either
emailing me directly or opening an issue on github.

msoulier@digitaltorque.ca
https://github.com/msoulier/tftpy

# About Release 0.8.6:
- respin to pick up scripts in bin, hopefully

# About Release 0.8.5:

- it didn't fix it :) but this should, thanks to
  https://github.com/maurerle

# About Release 0.8.4:

Bugfix release:

- transition to setuptools broke some things, hopefully this fixes it

# About Release 0.8.3:

Bugfix release:

- Setting the server socket to non-blocking. Closes issue #6, I hope.
- Ran through autopep8 --aggressive
- Add packet size check
- Added spaces to directory names.
- Removing error response if error received during RRQ or WRQ state. [106]
- Merged PR 133 - handling duplicate ACK
- Updated unreliable network test case.
- Adding a test hook for network unreliability.
- Fix race condition when waiting for ACK
- Merged PR 104
- Merge pull request #125 from BuhtigithuB/tweak-git-ignore
- Optimize imports
- Enhance PEP8
- TftpServer: lower log level for clean shutdown msgs

# About Release 0.8.2:

Bugfix release:

- / hardcoded making problems for windows users

# About Release 0.8.1:

Bugfix release:

- replace deprecated log.warn( with log.warning(
- fixing a security issue in breaking out of the tftproot
- setup with setuptools instead of distutils.
- allow overriding select timeout in listen
- fixing reading binary data from stdin on multiple platforms
- defaulting Makefile to python3 interpreter

# About Release 0.8.0:
This version introduces Python 3.X support.
And there was much rejoicing.

# About Release 0.7.0:
Various bugfixes and refactoring for improved logging.
Now requiring python 2.7+ and tightening syntax in
preparation for supporting python 3.

# About Release 0.6.2:
Maintenance release to fix a couple of reported issues.

# About Release 0.6.1:
Maintenance release to fix several reported problems, including a rollover
at 2^16 blocks, and some contributed work on dynamic file objects.

# About Release 0.6.0:
Maintenance update to fix several reported issues, including proper
retransmits on timeouts, and further expansion of unit tests.

# About Release 0.5.1:
Maintenance update to fix a bug in the server, overhaul the documentation for
the website, fix a typo in the unit tests, fix a failure to set default
blocksize, and a divide by zero error in speed calculations for very short
transfers.

Also, this release adds support for input/output in client as stdin/stdout

# About Release 0.5.0:
Complete rewrite of the state machine.
Now fully implements downloading and uploading.

# About Release 0.4.6:
Feature release to add the tsize option.
Thanks to Kuba Kończyk for the patch.

# About Release 0.4.5:
Bugfix release for compatibility issues on Win32, among other small issues.

# About Release 0.4.4:
Bugfix release for poor tolerance of unsupported options in the server.

# About Release 0.4.3:
Bugfix release for an issue with the server's detection of the end of the file
during a download.

# About Release 0.4.2:
Bugfix release for some small installation issues with earlier Python
releases.

# About Release 0.4.1:
Bugfix release to fix the installation path, with some restructuring into a
tftpy package from the single module used previously.

# About Release 0.4:
This release adds a TftpServer class with a sample implementation in bin.
The server uses a single thread with multiple handlers and a select() loop to
handle multiple clients simultaneously.

Only downloads are supported at this time.

# About Release 0.3:
This release fixes a major RFC 1350 compliance problem with the remote TID.

# About Release 0.2:
This release adds variable block sizes, and general option support,
implementing RFCs 2347 and 2348. This is accessible in the TftpClient class
via the options dict, or in the sample client via the --blocksize option.

# About Release 0.1:

This is an initial release in the spirit of "release early, release often".
Currently the sample client works, supporting RFC 1350. The server is not yet
implemented, and RFC 2347 and 2348 support (variable block sizes) is underway,
planned for 0.2.

# About Tftpy:

## Purpose:
Tftpy is a TFTP library for the Python programming language. It includes
client and server classes, with sample implementations. Hooks are included for
easy inclusion in a UI for populating progress indicators. It supports RFCs
1350, 2347, 2348 and the tsize option from RFC 2349.

## Dependencies:
Python 3.8+, hopefully. Let me know if it fails to work.

## Trifles:
Home page: http://msoulier.github.io/tftpy
Project page: http://github.com/msoulier/tftpy

License is the MIT License

See COPYING in this distribution.

## Limitations:
- Only 'octet' mode is supported.
- The only options supported are blksize and tsize.

Author:
Michael P. Soulier <msoulier@digitaltorque.ca>
