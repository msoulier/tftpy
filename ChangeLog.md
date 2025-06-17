2025-06-17  Michael P. Soulier <msoulier@digitaltorque.ca>

	* pyproject.toml: Trying to include existing scripts. WTF is this so
	hard, and deprecated?

2025-02-25  Michael P. Soulier <msoulier@digitaltorque.ca>

	* : commit dbd3dc490069ac7e05f52a0b23714e2753cba0a0 Author: Michael
	P. Soulier <msoulier@digitaltorque.ca> Date:   Tue Feb 25 07:24:10
	2025 -0500

2025-02-21  Michael P. Soulier <msoulier@digitaltorque.ca>

	* .github/workflows/python-app.yml: Update python-app.yml

2025-02-21  Michael P. Soulier <msoulier@digitaltorque.ca>

	* .github/workflows/python-app.yml: Update python-app.yml - set
	PYTHONPATH

2025-02-21  Michael P. Soulier <msoulier@digitaltorque.ca>

	* .github/workflows/test.yml: Removing test.yml

2025-02-21  Michael P. Soulier <msoulier@digitaltorque.ca>

	* .github/workflows/python-app.yml: Test python-app.yml

2025-02-21  Michael P. Soulier <msoulier@digitaltorque.ca>

	* .github/workflows/pylint.yml: Create pylint.yml

2025-02-21  Michael P. Soulier <msoulier@digitaltorque.ca>

	* .github/workflows/test.yml: And again

2025-02-21  Michael P. Soulier <msoulier@digitaltorque.ca>

	* .github/workflows/test.yml: Adjusting workflow

2025-02-21  Michael P. Soulier <msoulier@digitaltorque.ca>

	* tftpy/py.typed: Not typed yet

2025-02-21  Michael P. Soulier <msoulier@digitaltorque.ca>

	* .github/workflows/test.yml, tftpy/py.typed: Proving that I know
	nothing about github workflows

2025-02-16  Michael P. Soulier <msoulier@digitaltorque.ca>

	* Makefile, bin/tftpy_server.py: Added testcase for short packet.
	Closes #144.

2025-02-16  Michael P. Soulier <msoulier@digitaltorque.ca>

	* Makefile, tests/stdin.py: Corrected the stdin testcase.

2025-02-16  Michael P. Soulier <msoulier@digitaltorque.ca>

	* Makefile, tests/stdin.py: Added a stdin testcase

2025-02-15  Michael P. Soulier <msoulier@digitaltorque.ca>

	* Makefile, tests/nologs.py, tests/stdout.py, tests/test.py,
	tftpy/TftpContexts.py: Fixed improper handling of stdout in python3.
	Closes #113.

2025-02-15  Michael P. Soulier <msoulier@digitaltorque.ca>

	* ChangeLog.md, bin/tftpy_client.py, bin/tftpy_server.py,
	tests/test.py, tftpy/TftpClient.py, tftpy/TftpContexts.py,
	tftpy/TftpServer.py: Added flock on client and server. Closes #14.

2025-02-15  Michael P. Soulier <msoulier@digitaltorque.ca>

	* tests/test.py: Fixing a test case that I broke renaming the tests
	directory.

2025-02-14  Michael P. Soulier <msoulier@digitaltorque.ca>

	* ChangeLog.md, README.md, pyproject.toml: Building 0.8.5

2025-02-14  Michael P. Soulier <msoulier@digitaltorque.ca>

	* tftpy/__init__.py: Removing pkg_resources requirement. Closes
	#145.

2025-02-14  Michael P. Soulier <msoulier@digitaltorque.ca>

	* ChangeLog.md, Makefile, README.md, bin/git2cl, notes/sfshell.txt,
	pyproject.toml, setup.py: Fixing some packaging issues with
	setuptools. I hope.

2025-02-11  Michael P. Soulier <msoulier@digitaltorque.ca>

	* README.md: Tweaking README

2025-02-11  Michael P. Soulier <msoulier@digitaltorque.ca>

	* Makefile, pyproject.toml, {t => tests}/test.py, tox.ini: Updated
	setuptools config

2025-02-11  Michael P. Soulier <msoulier@digitaltorque.ca>

	* .pylintrc, Makefile, tftpy/TftpClient.py: Added pylint target

2025-02-11  Michael P. Soulier <msoulier@digitaltorque.ca>

	* ChangeLog.md, README.rst => README.md, rpm/PKG-INFO,
	rpm/python-tftpy.spec, setup.py: Updated for 0.8.3

2025-02-11  Michael P. Soulier <msoulier@digitaltorque.ca>

	* Makefile: Added help target to makefile

2025-02-03  Michael P. Soulier <msoulier@digitaltorque.ca>

	* tftpy/TftpServer.py: Setting the server socket to non-blocking.
	Closes issue #6, I hope.

2024-11-30  Michael P. Soulier <msoulier@digitaltorque.ca>

	* : commit 67fe1a625a9d36dc75d6685f3bd49cd9202b4052 Author: Michael
	P. Soulier <msoulier@digitaltorque.ca> Date:   Sat Nov 30 09:08:25
	2024 -0500

2024-11-30  Michael P. Soulier <msoulier@digitaltorque.ca>

	* bin/tftpy_client.py, tftpy/TftpClient.py, tftpy/TftpContexts.py,
	tftpy/TftpPacketTypes.py, tftpy/TftpServer.py, tftpy/TftpStates.py,
	tftpy/__init__.py: Ran through autopep8

2024-07-03  Dave Wapstra <dwapstra@cisco.com>

	* t/test.py, tftpy/TftpPacketFactory.py: Add packet size check

2022-11-27  Michael P. Soulier <msoulier@digitaltorque.ca>

	* .github/workflows/test.yml: Experimenting with workflows

2022-11-26  Michael P. Soulier <msoulier@digitaltorque.ca>

	* t/test.py: Added spaces to directory names.

2022-04-18  Michael P. Soulier <msoulier@digitaltorque.ca>

	* tftpy/TftpStates.py: Removing error response if error received
	during RRQ or WRQ state. [106]

2022-04-18  Michael P. Soulier <msoulier@digitaltorque.ca>

	* : Merged PR 133 - handling duplicate ACK

2022-03-26  Michael P. Soulier <msoulier@digitaltorque.ca>

	* t/test.py, tftpy/TftpShared.py, tftpy/TftpStates.py: Adding a test
	hook for network unreliability.

2022-03-22  Marcin Lewandowski <marcin.lewandowski@intel.com>

	* t/test.py, tftpy/TftpContexts.py, tftpy/TftpServer.py,
	tftpy/TftpShared.py, tftpy/TftpStates.py: Fix race condition when
	waiting for ACK TFTPy is designed in a way that socket timeout is used to calculate
	timeout when waiting for packet. During that time another unexpected
	packet may arrive.  After that the socket operation is restarted and
	timeout is calculated from start.  This might be a problem because
	both sides have timeout and these timeout may be different or one
	host may be significantly faster that another.  In such situation
	the timeout will be never triggered as another host will always
	retransmit his packet faster.  For most cases it does not matter because TFTP is always responding
	to packet sent and transmission may continue. The only one exception
	is no response to duplicate ACK. It is necessary to prevent
	Sorcerer's Apprentice Syndrome.  This patch introduces additional exception TftpTimeoutExpectACK
	raised when reaching timeout during waiting on ACK of current block
	but receiving duplicate ACK of previous block.

2021-12-03  Michael P. Soulier <msoulier@digitaltorque.ca>

	* : Merge remote-tracking branch 'adehad/feature/remove_compat'

2021-12-03  Michael P. Soulier <msoulier@digitaltorque.ca>

	* : Merge remote-tracking branch 'adehad/feature/codespell'

2021-11-29  Michael P. Soulier <msoulier@digitaltorque.ca>

	* run_tests.bat: Added simple winblows test runner

2021-10-24  adehad <26027314+adehad@users.noreply.github.com>

	* tftpy/TftpContexts.py, tftpy/compat.py: remove py2/3 compat

2021-10-23  adehad <26027314+adehad@users.noreply.github.com>

	* .pre-commit-config.yaml, ChangeLog.md, README.rst,
	doc/rfc2347.txt, doc/rfc2348.txt, doc/rfc2349.txt,
	tftpy/TftpClient.py: run codespell

2021-10-23  adehad <26027314+adehad@users.noreply.github.com>

	* html/index.html, html/main.css, html/sphinx/_sources/index.txt,
	html/sphinx/_static/basic.css, html/sphinx/_static/default.css,
	html/sphinx/_static/doctools.js, html/sphinx/_static/jquery.js,
	html/sphinx/_static/pygments.css,
	html/sphinx/_static/searchtools.js, html/sphinx/_static/sidebar.js,
	html/sphinx/_static/underscore.js,
	html/sphinx/_static/websupport.js, html/sphinx/genindex.html,
	html/sphinx/index.html, html/sphinx/py-modindex.html,
	html/sphinx/search.html, html/sphinx/searchindex.js: remove
	committed HTML docs, run `tox -e docs` for docs

2021-10-23  adehad <26027314+adehad@users.noreply.github.com>

	* .pre-commit-config.yaml, bin/tftpy_client.py, doc/conf.py,
	setup.py, t/test.py, tftpy/TftpClient.py, tftpy/TftpContexts.py,
	tftpy/TftpPacketFactory.py, tftpy/TftpPacketTypes.py,
	tftpy/TftpServer.py, tftpy/TftpShared.py, tftpy/TftpStates.py,
	tftpy/__init__.py: run pyupgrade

2021-10-21  adehad <26027314+adehad@users.noreply.github.com>

	* .gitignore, pyproject.toml, tox.ini: add pytest config

2021-10-21  adehad <26027314+adehad@users.noreply.github.com>

	* .github/workflows/test.yml, .pre-commit-config.yaml,
	pyproject.toml, setup.py, tox.ini: update after py27 support dropped

2021-10-21  adehad <26027314+adehad@users.noreply.github.com>

	* tftpy/TftpClient.py, tftpy/TftpPacketFactory.py,
	tftpy/TftpPacketTypes.py, tftpy/TftpServer.py, tftpy/TftpStates.py: 
	re-lint after merge

2021-10-21  adehad <26027314+adehad@users.noreply.github.com>

	* : Merge remote-tracking branch 'upstream/master'

2021-10-19  Michael P. Soulier <msoulier@digitaltorque.ca>

	* .gitignore: Line endings good.

2021-10-19  Michael P. Soulier <msoulier@digitaltorque.ca>

	* : Merge pull request #125 from BuhtigithuB/tweak-git-ignore Ignore PyCharm working folder

2021-10-16  Adel Haddad <26027314+adehad@users.noreply.github.com>

	* ChangeLog.md: wrap math in `` to render properly

2021-10-16  Adel Haddad <26027314+adehad@users.noreply.github.com>

	* README.rst: Fix README bullet list syntax

2021-10-15  Richard VÈzina <ml.richard.vezina@gmail.com>

	* bin/tftpy_client.py: Enhance PEP8

2021-10-15  Richard VÈzina <ml.richard.vezina@gmail.com>

	* bin/tftpy_client.py: Optimize imports

2021-10-15  Richard VÈzina <ml.richard.vezina@gmail.com>

	* tftpy/TftpStates.py: Enhance PEP8

2021-10-15  Richard VÈzina <ml.richard.vezina@gmail.com>

	* tftpy/TftpStates.py: is None

2021-10-15  Richard VÈzina <ml.richard.vezina@gmail.com>

	* tftpy/TftpStates.py: 120 is good (80 -> 120 line length)

2021-10-15  Richard VÈzina <ml.richard.vezina@gmail.com>

	* tftpy/TftpShared.py: Enhance PEP8

2021-10-15  Richard VÈzina <ml.richard.vezina@gmail.com>

	* tftpy/TftpServer.py: Enhance PEP8

2021-10-15  Richard VÈzina <ml.richard.vezina@gmail.com>

	* tftpy/TftpServer.py: is None

2021-10-15  Richard VÈzina <ml.richard.vezina@gmail.com>

	* tftpy/TftpServer.py: Improve natural english language readability

2021-10-15  Richard VÈzina <ml.richard.vezina@gmail.com>

	* tftpy/TftpServer.py: No inline if

2021-10-15  Richard VÈzina <ml.richard.vezina@gmail.com>

	* tftpy/TftpServer.py: Create list directly

2021-10-15  Richard VÈzina <ml.richard.vezina@gmail.com>

	* tftpy/TftpServer.py: 120 is good (80 -> 120 line length)

2021-10-15  Richard VÈzina <ml.richard.vezina@gmail.com>

	* tftpy/TftpServer.py: Optimize imports

2021-10-15  Richard VÈzina <ml.richard.vezina@gmail.com>

	* tftpy/TftpPacketTypes.py: Enhance PEP8

2021-10-15  Richard VÈzina <ml.richard.vezina@gmail.com>

	* tftpy/TftpPacketFactory.py: Enhance PEP8

2021-10-15  Richard VÈzina <ml.richard.vezina@gmail.com>

	* tftpy/TftpContexts.py: Enhance PEP8

2021-10-15  Richard VÈzina <ml.richard.vezina@gmail.com>

	* tftpy/TftpContexts.py: Fix typos

2021-10-15  Richard VÈzina <ml.richard.vezina@gmail.com>

	* tftpy/TftpClient.py: Enhance PEP8

2021-10-15  Richard VÈzina <ml.richard.vezina@gmail.com>

	* tftpy/compat.py: Optimize import

2021-10-15  Richard VÈzina <ml.richard.vezina@gmail.com>

	* tftpy/compat.py: Enhance PEP8

2021-10-15  Richard VÈzina <ml.richard.vezina@gmail.com>

	* bin/tftpy_server.py: Enhance PEP8

2021-10-15  Richard VÈzina <ml.richard.vezina@gmail.com>

	* bin/tftpy_server.py: Optimize imports

2021-10-15  Richard VÈzina <ml.richard.vezina@gmail.com>

	* bin/tftpy_server.py: Forgo WARN -> WARNING

2021-10-15  devopsadmin <devopsadmin@leddartech.com>

	* .gitignore: Ignore PyCharm working folder

2021-10-15  adehad <26027314+adehad@users.noreply.github.com>

	* tftpy/TftpPacketTypes.py: fix py2 syntax?

2021-09-23  adehad <26027314+adehad@users.noreply.github.com>

	* .github/workflows/test.yml, .gitignore, .pre-commit-config.yaml,
	ChangeLog => ChangeLog.md, MANIFEST.in, README => README.rst,
	bin/tftpy_client.py, bin/tftpy_server.py, doc/conf.py,
	doc/rfc2347.txt, doc/rfc2348.txt, doc/rfc2349.txt,
	html/sphinx/_static/basic.css, html/sphinx/_static/default.css,
	html/sphinx/_static/jquery.js, html/sphinx/_static/pygments.css,
	html/sphinx/_static/searchtools.js, html/sphinx/_static/sidebar.js,
	html/sphinx/genindex.html, html/sphinx/index.html,
	html/sphinx/py-modindex.html, html/sphinx/search.html,
	html/sphinx/searchindex.js, pyproject.toml, setup.py, t/test.py,
	tftpy/TftpClient.py, tftpy/TftpContexts.py,
	tftpy/TftpPacketFactory.py, tftpy/TftpPacketTypes.py,
	tftpy/TftpServer.py, tftpy/TftpShared.py, tftpy/TftpStates.py,
	tftpy/__init__.py, tftpy/compat.py, tox.ini: first attempt with
	github actions, various linting

2021-08-13  Michael P. Soulier <msoulier@digitaltorque.ca>

	* ChangeLog, README, setup.py: Whoops, missed setup.py update

2021-06-06  pucgenie <pucgenie@hotmail.com>

	* tftpy/TftpStates.py: Fix def serverInitial to support Windows There are multiple places where hard-coded forward-slashes occur
	that can be replaces by `os.sep`.  This fixes just one showstopper.

2021-06-03  Michael P. Soulier <msoulier@digitaltorque.ca>

	* README, setup.py: Updating for 0.8.1

2021-06-03  Michael P. Soulier <msoulier@digitaltorque.ca>

	* Makefile: Defaulting to python3 interpreter

2021-06-03  Michael P. Soulier <msoulier@digitaltorque.ca>

	* : Merge remote-tracking branch 'mikepurvis/patch-1'

2021-05-19  Michael P. Soulier <msoulier@digitaltorque.ca>

	* : Merge remote-tracking branch 'ulidtko/fix/binary-stdin' Merging PR 116.

2021-03-11  israelv <yisrael97@gmail.com>

	* tftpy/TftpClient.py, tftpy/TftpServer.py: Add retires paramater to
	client and server sessions

2021-03-11  israelv <yisrael97@gmail.com>

	* tftpy/TftpContexts.py, tftpy/TftpServer.py, tftpy/TftpShared.py: 
	Add retires to context initializers

2021-02-17  max ulidtko <ulidtko@gmail.com>

	* tftpy/TftpContexts.py, tftpy/compat.py: Fix #109: reading binary
	data from sys.stdin

2021-02-01  Michael P. Soulier <msoulier@digitaltorque.ca>

	* : commit 5270ee1cd6cc878cb6371c7ab22f9a90f8d2db79 Author: Thomas
	Grainger <tagrain@gmail.com> Date:   Mon Feb 1 09:48:45 2021 +0000

2021-01-19  Michael P. Soulier <msoulier@digitaltorque.ca>

	* : Merge pull request #108 from graingert/patch-1 replace deprecated log.warn( with log.warning(

2020-09-29  Mike Purvis <mike@uwmike.com>

	* setup.py: Setup with setuptools instead of distutils.

2020-08-28  Robert Scott <code@humanleg.org.uk>

	* t/test.py, tftpy/TftpStates.py: TftpServerState.serverInitial:
	prevent access to prefix-sharing siblings of tftproot do this by ensuring the tftproot we compare against is terminated
	with a slash.  Fixes #110 include tests proving the fix, along with some more fleshed out
	tests around permitted and disallowed request paths

2020-06-11  Thomas Grainger <tagrain@gmail.com>

	* tftpy/TftpStates.py: replace deprecated log.warn( with
	log.warning(

2019-09-17  Rafael Gago <rgc@hms.se>

	* tftpy/TftpServer.py: TftpServer: lower log level for clean
	shutdown msgs Before this commit all clean shutdown sequences (without active
	sessions) were issuing warnings on the logs. Closing the server
	without active sessions is normal behavior, so it should not
	generate error messages.  This commit fixes this.

2018-09-13  Michael P. Soulier <msoulier@digitaltorque.ca>

	* README, setup.py: Wording change.

2018-09-13  Michael P. Soulier <msoulier@digitaltorque.ca>

	* README, setup.py: README update

2018-09-13  Michael P. Soulier <msoulier@digitaltorque.ca>

	* setup.py: Updating setup.py

2018-09-13  Michael P. Soulier <msoulier@digitaltorque.ca>

	* t/test.py: Fixing another broken test case

2018-09-13  Michael P. Soulier <msoulier@digitaltorque.ca>

	* Makefile, t/test.py: Fixing some broken test-cases.

2018-09-13  Michael P. Soulier <msoulier@digitaltorque.ca>

	* tftpy/TftpPacketTypes.py, tftpy/TftpStates.py: Fixing more
	encoding issues for python3.

2018-09-13  Michael P. Soulier <msoulier@digitaltorque.ca>

	* t/test.py, tftpy/TftpPacketTypes.py: Fixing some encoding issues
	in python3

2018-09-12  Michael P. Soulier <msoulier@digitaltorque.ca>

	* Makefile, tftpy/TftpStates.py: Fixed testClientServerUploadOptions
	testcase

2018-09-10  ®Andreas <®andreas.dachsberger@gmail.com®>

	* tftpy/TftpPacketTypes.py: Compatibility tested Tested compatibility with easy test client and test server. So far,
	no errors anymore. (In Both python2 and python3) Just tested basic
	functionality!

2018-09-10  ®Andreas <®andreas.dachsberger@gmail.com®>

	* tftpy/TftpPacketTypes.py: Made parts concerning test program
	compatible Not complete code is compatible, just my use case for the moment.

2018-09-10  ®Andreas <®andreas.dachsberger@gmail.com®>

	* tftpy/TftpPacketTypes.py: Solved some 2 to 3 issues

2018-09-10  ®Andreas <®andreas.dachsberger@gmail.com®>

	* tftpy/TftpClient.py, tftpy/TftpContexts.py,
	tftpy/TftpPacketFactory.py, tftpy/TftpPacketTypes.py,
	tftpy/TftpServer.py, tftpy/TftpShared.py, tftpy/TftpStates.py,
	tftpy/__init__.py: 2to3 Not finished, a few type conversion errors still occur.2to3

2018-09-02  Michael P. Soulier <msoulier@digitaltorque.ca>

	* : Merge pull request #91 from eRaid6/patch-3 Update version in python-tftpy.spec

2018-09-02  Michael P. Soulier <msoulier@digitaltorque.ca>

	* : Merge pull request #89 from eRaid6/patch-1 Fix encoding position in setup.py

2018-08-29  Nick <36430733+eRaid6@users.noreply.github.com>

	* rpm/PKG-INFO: Create PKG-INFO for use in python-tftpy.spec python-tftpy.spec depends on PKG-INFO existing.  This Patch creates
	PKG-INFO with the required information.

2018-08-29  Nick <36430733+eRaid6@users.noreply.github.com>

	* setup.py: Fix encoding position in setup.py Per PEP-0263 encoding needs to be on the first or second line,
	https://www.python.org/dev/peps/pep-0263/#defining-the-encoding.
	This change moves the encoding to the second line which resolves
	this error: ./setup.py build   File "./setup.py", line 47 SyntaxError: Non-ASCII character '\xc5'
	in file ./setup.py on line 48, but no encoding declared; see
	http://www.python.org/peps/pep-0263.html for details

2018-05-18  Michael P. Soulier <msoulier@digitaltorque.ca>

	* bin/tftpy_client.py, bin/tftpy_server.py, doc/conf.py, setup.py,
	t/test.py, tftpy/TftpClient.py, tftpy/TftpContexts.py,
	tftpy/TftpPacketFactory.py, tftpy/TftpPacketTypes.py,
	tftpy/TftpServer.py, tftpy/TftpShared.py, tftpy/TftpStates.py,
	tftpy/__init__.py: Adding some boilerplate

2018-05-18  Michael P. Soulier <msoulier@digitaltorque.ca>

	* setup.py: Added a long_description

2018-05-18  Michael P. Soulier <msoulier@digitaltorque.ca>

	* README: README fix

2018-05-18  Michael P. Soulier <msoulier@digitaltorque.ca>

	* README: README update

2018-05-18  Michael P. Soulier <msoulier@digitaltorque.ca>

	* Makefile: Changing makefile to use twine

2018-05-18  Michael P. Soulier <msoulier@digitaltorque.ca>

	* MANIFEST, setup.py: setup.py changes

2018-05-18  Michael P. Soulier <msoulier@digitaltorque.ca>

	* setup.py: Updating release to 0.7.0

2018-05-18  Michael P. Soulier <msoulier@digitaltorque.ca>

	* ChangeLog, setup.py: Preparing for 0.6.3 release

2018-05-15  Michael P. Soulier <msoulier@digitaltorque.ca>

	* tftpy/TftpContexts.py: Fixing closure of stdout on context close.
	#76

2018-05-15  Michael P. Soulier <msoulier@digitaltorque.ca>

	* tftpy/TftpPacketTypes.py, tftpy/TftpStates.py: Dropping str() in
	favour of bytestring input, and fixing logging calls in
	TftpPacketTypes. Merging fixes for #78 and #79.

2018-05-15  Michael P. Soulier <msoulier@digitaltorque.ca>

	* : commit 791def3f55081cebd1f27019776c628293a931fc Author: Michael
	P. Soulier <msoulier@digitaltorque.ca> Date:   Tue May 15 12:57:37
	2018 -0400

2018-05-15  Michael P. Soulier <msoulier@digitaltorque.ca>

	* bin/tftpy_client.py: Fixed bad reference to TftpPacketOACK in
	tftpy_client.py

2018-05-15  Michael P. Soulier <msoulier@digitaltorque.ca>

	* bin/tftpy_client.py, bin/tftpy_server.py, t/test.py,
	tftpy/__init__.py: Putting TftpClient and TftpServer back into the
	tftpy module context for convenience. Also improving the test
	logger.

2018-05-15  Michael P. Soulier <msoulier@digitaltorque.ca>

	* bin/tftpy_client.py, bin/tftpy_server.py, lib/tftpy_twisted.py,
	t/test.py, tftpy/TftpClient.py, tftpy/TftpContexts.py,
	tftpy/TftpPacketFactory.py, tftpy/TftpPacketTypes.py,
	tftpy/TftpServer.py, tftpy/TftpShared.py, tftpy/TftpStates.py,
	tftpy/__init__.py: Rationalized module includes and logging.

2018-05-09  Michael P. Soulier <msoulier@digitaltorque.ca>

	* : Merge remote-tracking branch 'drlef/leave-filelike-object-open'
	into fileobj

2018-05-09  Michael P. Soulier <msoulier@digitaltorque.ca>

	* : commit e05557b23ad212e5526ede716cbdeeebc4f747ed Author: Michael
	P. Soulier <msoulier@digitaltorque.ca> Date:   Wed May 9 10:51:02
	2018 -0400

2018-04-11  Michael P. Soulier <msoulier@digitaltorque.ca>

	* : Merged with NWiBGRsK

2018-04-11  Michael P. Soulier <msoulier@digitaltorque.ca>

	* tftpy/TftpServer.py, tftpy/TftpStates.py: Fixing 2 exceptions for
	python3

2018-04-04  sedrubal <dev@sedrubal.de>

	* setup.py, t/test.py, tftpy/TftpContexts.py, tftpy/TftpServer.py,
	tftpy/TftpStates.py: Fix some deprecations and python3
	incompatibilities

2017-09-04  Steff Richards <drlef147@googlemail.com>

	* tftpy/TftpContexts.py: Leave filelike object open in client
	download context.

2017-06-06  John W Kerns <jkerns@packetsar.com>

	* tftpy/TftpStates.py: Added logic to TftpStates.sendError to fix
	issue #79

2017-05-15  John W Kerns <jkerns@packetsar.com>

	* tftpy/TftpPacketFactory.py, tftpy/TftpPacketTypes.py: Struct pack
	and unpack require a string format

2017-05-09  Michael P. Soulier <msoulier@digitaltorque.ca>

	* : Merged style updates, minor bug fixes

2017-05-01  Christopher Chavez <chrischavez@gmx.us>

	* tftpy/TftpClient.py: TftpClient.py: use UDP port 69 by default

2016-10-24  Reverend Homer <mk.43.ecko@gmail.com>

	* t/test.py: make testStreamLogger and testFileLogger clearer

2016-08-31  NWiBGRsK <ihatespam@gmx.net>

	* tftpy/TftpStates.py: changed raise exception line to be compatible
	with python3

2016-08-31  NWiBGRsK <ihatespam@gmx.net>

	* tftpy/TftpServer.py: change an raise exception line, to be
	compatible with python3

2016-07-07  Paul Weaver <paul.weaver@osirium.com>

	* : commit a68924f2a66916b2d967b011d981259752556ae4 Author: Michael
	P. Soulier <msoulier@digitaltorque.ca> Date:   Wed Jul 6 07:20:21
	2016 -0400

2016-07-05  Michael P. Soulier <msoulier@digitaltorque.ca>

	* t/test.py, tftpy/TftpPacketTypes.py, tftpy/TftpServer.py: Fixing
	some python3 syntax errors

2016-07-05  Michael P. Soulier <msoulier@digitaltorque.ca>

	* tftpy/TftpClient.py, tftpy/TftpContexts.py,
	tftpy/TftpPacketFactory.py, tftpy/TftpPacketTypes.py,
	tftpy/TftpServer.py, tftpy/TftpShared.py, tftpy/TftpStates.py,
	tftpy/__init__.py: Added recommended imports for python3
	compatibility.

2016-07-04  Michael P. Soulier <msoulier@digitaltorque.ca>

	* : Merging with master

2016-06-17  Paul Weaver <paul.weaver@osirium.com>

	* t/test.py, tftpy/TftpServer.py, tftpy/TftpStates.py: Add a context
	to dynamic upload_open

2016-06-17  Paul Weaver <paul.weaver@osirium.com>

	* t/test.py, tftpy/TftpContexts.py, tftpy/TftpServer.py,
	tftpy/TftpStates.py: Implement dynamic upload support

2016-06-17  Paul Weaver <paul.weaver@osirium.com>

	* .gitignore: Ignore egg-info file

2016-06-17  Paul Weaver <paul.weaver@osirium.com>

	* tftpy/TftpServer.py: Clarify docs around dyn_file_func in
	TftpServer

2016-03-09  Carl van Schaik <carl@cog.systems>

	* tftpy/TftpServer.py: listen loop: Use epoll / poll instead of
	select Update the main server loop to use more efficient epoll, or if not
	available, poll. This removes work recreating the select list on
	each itteration.  Also add a dictionary to speed up translation of file descriptor
	back to a matching session.

2016-04-12  Carl van Schaik <carl@cog.systems>

	* t/test.py, tftpy/TftpServer.py: tests: fix failure due to alarm Test cases raises an alarm in the server to call the stop()
	function. This actually interrupts the select system call and raises
	an exception instead. We catch the interrupted syscall in select and
	allow it to restart.

2016-03-13  Carl van Schaik <carl@cog.systems>

	* t/test.py: tests: Rate limit test with timing dependency When running tests on a fast server, or with output redirected, some
	test cases would complete a transfer before the test delay to inject
	an error.

2016-04-09  Michael P. Soulier <msoulier@digitaltorque.ca>

	* tftpy/TftpStates.py: Fixing tab char

2015-12-01  Martin Ulmschneider <mu@ocedo.com>

	* tftpy/TftpStates.py: Also send OACK for options other than tsize This restores the behaviour pre commit 72a9dfb.

2015-10-15  Michael P. Soulier <msoulier@digitaltorque.ca>

	* : commit a8885154628fb3795fcda7143db09feb437a8eef Author: Michael
	P. Soulier <msoulier@digitaltorque.ca> Date:   Thu Oct 15 09:45:33
	2015 -0400

2015-10-14  Michael P. Soulier <msoulier@digitaltorque.ca>

	* : commit 4b182006181cc1192c419f2c46432ebdfba304f2 Author: Michael
	P. Soulier <msoulier@digitaltorque.ca> Date:   Wed Oct 14 20:01:42
	2015 -0400

2015-10-14  Michael P. Soulier <msoulier@digitaltorque.ca>

	* tftpy/TftpShared.py: Updating logging function convention and
	adding arguments to the rotating file handler.

2015-10-14  Michael P. Soulier <msoulier@digitaltorque.ca>

	* tftpy/TftpShared.py: Whitespace fix.

2015-09-08  Michael P. Soulier <msoulier@digitaltorque.ca>

	* : Merge remote-tracking branch
	'posbourne/tftpy-server-quiet-option' into quiet

2015-09-08  Michael P. Soulier <msoulier@digitaltorque.ca>

	* : Merge remote-tracking branch 'zuljinsbk/local_ip_bind' into
	merge

2015-07-21  Francesco Fiorentino <f.fiorentino@camlintechnologies.com>

	* .gitignore, MANIFEST, dist/tftpy-0.6.2.tar.gz.asc: update
	.gitignore remove MANIFEST file remove dist folder

2015-07-17  Francesco Fiorentino <f.fiorentino@camlintechnologies.com>

	* .gitignore, README, bin/tftpy_client.py, bin/tftpy_server.py,
	setup.py, t/README.txt, t/test.py, t/testWin.py,
	tftpy/TftpClient.py, tftpy/TftpContexts.py,
	tftpy/TftpPacketFactory.py, tftpy/TftpPacketTypes.py,
	tftpy/TftpServer.py, tftpy/TftpShared.py, tftpy/TftpStates.py,
	tftpy/__init__.py: Release version 0.6.3_fork (forked version) Contains: Bug fixes in log.debug Fixes in broken code Fixes many
	PEP8 issues Created testWin Unit for Win environment

2015-06-23  Paul Osborne <Paul.Osborne@digi.com>

	* bin/tftpy_server.py: server: add -q option to supress liberal INFO
	level debugging In my test from U-Boot tftp client to a server running on windows
	this increase the transfer rate from 1.8MB/s to 4.9MB/s (nearly 3x
	performance improvement).  Signed-off-by: Paul Osborne <Paul.Osborne@digi.com>

2015-06-07  Zoltan Gyarmati <mr.zoltan.gyarmati@gmail.com>

	* tftpy/TftpStates.py: server RRQ OACK: only send tsize option when
	its requested

2014-07-04  Zoltan Gyarmati <mr.zoltan.gyarmati@gmail.com>

	* tftpy/TftpStates.py: set correct tsize option in server OACK when
	negotiating download

2015-03-05  Doug O'Riordan <oriordan@mail.be>

	* tftpy/TftpClient.py, tftpy/TftpContexts.py,
	tftpy/TftpPacketFactory.py, tftpy/TftpPacketTypes.py,
	tftpy/TftpServer.py, tftpy/TftpShared.py, tftpy/TftpStates.py,
	tftpy/__init__.py: Adding python3 support

2015-01-25  Greg Prosser <gprosser@oanda.com>

	* tftpy/TftpPacketTypes.py: Adjust ACK handling to truncate too long
	packets.  It appears (at least) a Dell PowerConnect 6248 will send ACK packets
	that are 29 bytes long.  The first 4 match the correct format (2b
	opcode, 2b block), and it appears the rest of the message is padding
	with null bytes (at least via some cursory debugging).  By default, tftpy will barf when this happens complaining it can't
	unpack 29 bytes with a format of "!HH".  This change will ignore anything not "in spec" for an ACK packet by
	truncating the message ro 4 bytes before continuing.  This causes tftpy to work fine for my PC6248 switch.

2014-11-16  Michael P. Soulier <msoulier@digitaltorque.ca>

	* doc/conf.py, html/sphinx/genindex.html, html/sphinx/index.html,
	html/sphinx/py-modindex.html, html/sphinx/search.html: Updated
	version in docs.

2014-11-16  Michael P. Soulier <msoulier@digitaltorque.ca>

	* .gitignore, MANIFEST, dist/tftpy-0.6.2.tar.gz.asc,
	html/sphinx/_static/basic.css, html/sphinx/_static/default.css,
	html/sphinx/_static/doctools.js, html/sphinx/_static/jquery.js,
	html/sphinx/_static/pygments.css,
	html/sphinx/_static/searchtools.js, html/sphinx/_static/sidebar.js,
	html/sphinx/_static/underscore.js,
	html/sphinx/_static/websupport.js, html/sphinx/genindex.html,
	html/sphinx/index.html, html/sphinx/py-modindex.html,
	html/sphinx/search.html, html/sphinx/searchindex.js: Updated
	website.

2014-11-15  Michael P. Soulier <msoulier@digitaltorque.ca>

	* Makefile: Added pypi makefile target

2014-11-15  Michael P. Soulier <msoulier@digitaltorque.ca>

	* ChangeLog, README, setup.py: Updates for 0.6.2 release.

2014-09-06  Michael P. Soulier <msoulier@digitaltorque.ca>

	* tftpy/TftpServer.py: Added a comment.

2014-06-13  Philip Derrin <philip@cog.systems>

	* t/test.py: Test case for dynamic server listenport

2014-06-02  Philip Derrin <philip@cog.systems>

	* tftpy/TftpServer.py: Set listenport to the port chosen by bind() The server can be run with listenport=0, in which case bind() will
	select a port. In this case, it can be useful to inspect the port
	number, so we set self.listenport.

2014-06-02  Philip Derrin <philip@cog.systems>

	* tftpy/TftpServer.py: Set an event while TftpServer.listen() runs Most non-trivial uses of TftpServer.listen() are in a dedicated
	thread. In this case, it can be useful to wait until the server
	thread is running, so we signal this with a threading.Event.

2013-11-24  Jaroslaw Niec <zuljin@go2.pl>

	* tftpy/TftpClient.py, tftpy/TftpContexts.py: Added localip
	parameter for TFTPClient

2013-11-11  Michael P. Soulier <msoulier@digitaltorque.ca>

	* t/test.py: Added a test for last change.

2013-11-01  Nathan Bird <nathan@acceleration.net>

	* tftpy/TftpStates.py: Fixing #11: server accept leading '/' in
	uploads Some devices, when uploading, always have a leading '/' that led to
	the joined path being outside the server's root directory causing
	"bad file path" TftpExceptions. The only way to work around this is
	if the remote client knew the full path on this server
	(unnecessarily tight coupling).  This patch removes the leading '/' so that all paths are relative to
	the server's root directory.  To help preserve backwards compatibility there is an exception to
	the above rule that if the client's specified path starts with the
	server's root directory then accept it.

2013-09-27  Michael P. Soulier <msoulier@digitaltorque.ca>

	* t/test.py, tftpy/TftpServer.py: Added tests for server api stop.

2013-09-26  Michael P. Soulier <msoulier@digitaltorque.ca>

	* ChangeLog, README, setup.py: Setting up for the 0.6.1 release.

2013-09-26  Michael P. Soulier <msoulier@digitaltorque.ca>

	* t/test.py: Fixed testcases.

2013-09-26  Michael P. Soulier <msoulier@digitaltorque.ca>

	* tftpy/TftpClient.py, tftpy/TftpContexts.py,
	tftpy/TftpPacketFactory.py, tftpy/TftpPacketTypes.py,
	tftpy/TftpServer.py, tftpy/TftpStates.py: Fixing debug calls to be
	lazy when debug is off.

2013-09-26  Michael P. Soulier <msoulier@digitaltorque.ca>

	* t/test.py: Fixing a testcase.

2013-07-28  Michael P. Soulier <msoulier@digitaltorque.ca>

	* t/test.py, tftpy/TftpStates.py: Fixing unit tests

2013-07-27  Michael P. Soulier <msoulier@digitaltorque.ca>

	* tftpy/TftpServer.py: Adding graceful exit condition.

2013-07-27  Michael P. Soulier <msoulier@digitaltorque.ca>

	* .gitignore, tftpy/TftpContexts.py, tftpy/TftpServer.py: Adding a
	TftpServer.stop() method.

2013-05-15  Michael P. Soulier <msoulier@digitaltorque.ca>

	* Makefile, t/test.py, tftpy/TftpStates.py: Increasing test file
	size to 50MB and removed the assertion of a block zero, as that will
	happen at block number rollover. Closes issue #36.

2012-10-04  Michael P. Soulier <msoulier@digitaltorque.ca>

	* tftpy/TftpServer.py: Removing trailing whitespace

2012-10-04  Michael P. Soulier <msoulier@digitaltorque.ca>

	* : Merge remote branch 'micolous/master' into merge

2012-09-30  Michael P. Soulier <msoulier@digitaltorque.ca>

	* : Merge remote branch 'jawschwa/master' into merge

2012-09-29  Michael P. Soulier <msoulier@digitaltorque.ca>

	* t/test.py: Fixing testcase for pre python 2.7

2012-08-07  Michael Farrell <micolous+git@gmail.com>

	* tftpy/__init__.py: raise ImportError when Python version is wrong
	instead of AssertionError

2012-08-07  Michael Farrell <micolous+git@gmail.com>

	* tftpy/__init__.py: Improved version check so it is much cleaner,
	fix relative import issue with Python 2.5 not working

2012-05-03  Jay Weisskopf <jay@jayschwa.net>

	* tftpy/TftpClient.py, tftpy/TftpContexts.py: Allow file objects to
	be used for download output or upload input.  Objects are considered file-like if they have read() or write()
	functions. If they do not, they are assumed to be strings to a local
	path (existing behavior).

2012-04-26  Fabian Knittel <fabian.knittel@lettink.de>

	* tftpy/TftpStates.py: tftpy/TftpStates.py: fix security problem
	regarding path check This patch fixes the request path check.  It makes sure that
	requested paths are _below_ the specified root directory.

2012-04-26  Fabian Knittel <fabian.knittel@lettink.de>

	* t/test.py: t/test.py: add unit test for insecure path access The test currently fails, because the request path is improperly
	checked / sanitised.

2012-04-26  Fabian Knittel <fabian.knittel@lettink.de>

	* tftpy/TftpStates.py: refactor TftpState: move server-specific
	stuff to TftpServerState

2012-04-26  Fabian Knittel <fabian.knittel@lettink.de>

	* tftpy/TftpContexts.py: minor clean-up: remove duplicate
	dyn_file_func setting `self.dyn_file_func` is currently set twice: Once in the base class
	and once in the server child class.  As it's only used in the
	non-server case, remove it from the base class.

2012-04-12  Michael Farrell <micolous+git@gmail.com>

	* tftpy/TftpServer.py: improve the check on dyn_file_func of
	TftpServer

2012-04-11  Michael Farrell <micolous+git@gmail.com>

	* tftpy/TftpServer.py: allow TftpServer.root not to exist if a
	dyn_file_func is provided

2012-04-11  Michael Farrell <micolous+git@gmail.com>

	* tftpy/__init__.py: allow running the script on python 3.0 - 3.2
	(though unsure of compatibility)

2012-03-10  Michael P. Soulier <msoulier@digitaltorque.ca>

	* t/test.py, tftpy/TftpClient.py, tftpy/TftpStates.py: Fixing issue
	#26, with the server not creating the full path to the filename
	being uploaded.

2011-09-01  Michael P. Soulier <msoulier@digitaltorque.ca>

	* t/test.py, tftpy/TftpStates.py: Adding subdirectory support.
	Hopefully closes issue 25.

2011-07-26  Michael P. Soulier <msoulier@digitaltorque.ca>

	* doc/conf.py, doc/index.rst, html/index.html,
	html/sphinx/_sources/index.txt, html/sphinx/_static/basic.css,
	html/sphinx/_static/default.css, html/sphinx/_static/doctools.js,
	html/sphinx/_static/jquery.js, html/sphinx/_static/pygments.css,
	html/sphinx/_static/searchtools.js, html/sphinx/_static/sidebar.js,
	html/sphinx/_static/underscore.js, html/sphinx/genindex.html,
	html/sphinx/index.html, html/sphinx/modindex.html,
	html/sphinx/py-modindex.html, html/sphinx/search.html,
	html/sphinx/searchindex.js: Documentation update for 0.6.0

2011-07-26  Michael P. Soulier <msoulier@digitaltorque.ca>

	* Makefile, rpm/python-tftpy.spec, run_tests: Makefile update, and
	adding rpm specfile.

2011-07-24  Michael P. Soulier <msoulier@digitaltorque.ca>

	* ChangeLog, README, setup.py: Updating metadata for 0.6.0 release.

2011-07-24  Michael P. Soulier <msoulier@digitaltorque.ca>

	* t/test.py, tftpy/TftpClient.py, tftpy/TftpContexts.py,
	tftpy/TftpShared.py, tftpy/TftpStates.py: Fixing issue #3, expanding
	unit tests.

2011-07-23  Michael P. Soulier <msoulier@digitaltorque.ca>

	* Makefile, bin/tftpy_server.py, tftpy/TftpClient.py,
	tftpy/TftpContexts.py, tftpy/TftpPacketTypes.py,
	tftpy/TftpServer.py, tftpy/TftpStates.py: Fixing some pyflakes
	complaints

2011-07-23  Michael P. Soulier <msoulier@digitaltorque.ca>

	* tftpy/TftpClient.py, tftpy/TftpContexts.py, tftpy/TftpServer.py,
	tftpy/TftpStates.py, tftpy/__init__.py: Fixes issue #23, breaking up
	TftpStates into TftpStates and TftpContexts.

2011-07-23  Michael P. Soulier <msoulier@digitaltorque.ca>

	* bin/tftpy_client.py, tftpy/TftpClient.py, tftpy/TftpStates.py: 
	Fixing issue #9, removing blksize option from client if not
	supplied.

2011-07-23  Michael P. Soulier <msoulier@digitaltorque.ca>

	* tftpy/TftpStates.py: Fixing issue #16 on github, server failing to
	use timeout time in checkTimeout() method.

2011-07-23  Michael P. Soulier <msoulier@digitaltorque.ca>

	* tftpy/TftpServer.py, tftpy/TftpShared.py, tftpy/TftpStates.py: 
	Adding retries on timeouts, still have to exhaustively test.  Should
	close issue #21 on github.

2011-06-02  Michael P. Soulier <msoulier@digitaltorque.ca>

	* run_tests, tftpy/TftpStates.py: Fixing a file descriptor leak.
	Closes issue 22.

2011-06-02  Michael P. Soulier <msoulier@digitaltorque.ca>

	* t/test.py: Adding a server download state test to the unit tests.

2010-10-18  Kenny Millington <kenny@helios.(none)>

	* tftpy/TftpServer.py, tftpy/TftpStates.py: Fix exceptions
	propagating out of TftpServer.listen() Signed-off-by: Michael P. Soulier <msoulier@digitaltorque.ca>

2010-10-18  Kenny Millington <kenny@helios.(none)>

	* tftpy/TftpStates.py: Allow dyn_file_func to trigger a FileNotFound
	error.  Signed-off-by: Michael P. Soulier <msoulier@digitaltorque.ca>

2010-10-13  Michael P. Soulier <msoulier@digitaltorque.ca>

	* tftpy/TftpPacketTypes.py: Forcing decode mode to lower case, fixes
	bug 17.

2010-07-20  Michael P. Soulier <msoulier@digitaltorque.ca>

	* tftpy/TftpStates.py: Fixing setNextBlock to roll over at 2**16 - 1
	instead of 2**16, which was causing problems when uploading large
	files.  Thanks to LawrenceK for the bug report. Fixes issue15.

2010-07-14  Michael P. Soulier <msoulier@digitaltorque.ca>

	* README: Updating README for 0.5.1

2010-07-14  Michael P. Soulier <msoulier@digitaltorque.ca>

	* ChangeLog: Updated changelog for 0.5.1.

2010-07-14  Michael P. Soulier <msoulier@digitaltorque.ca>

	* ChangeLog, bin/tftpy_client.py, doc/index.rst,
	html/sphinx/_sources/index.txt, html/sphinx/_static/default.css,
	html/sphinx/genindex.html, html/sphinx/index.html,
	html/sphinx/modindex.html, html/sphinx/search.html,
	html/sphinx/searchindex.js, setup.py: Added simple doc examples and
	install info.

2010-07-12  Michael P. Soulier <msoulier@digitaltorque.ca>

	* doc/conf.py, doc/index.rst, html/sphinx/_sources/index.txt,
	html/sphinx/_static/default.css, html/sphinx/genindex.html,
	html/sphinx/index.html, html/sphinx/modindex.html,
	html/sphinx/search.html, html/sphinx/searchindex.js: Playing with
	sphinx formatting

2010-07-11  Michael P. Soulier <msoulier@digitaltorque.ca>

	* doc/index.rst, html/sphinx/_sources/index.txt,
	html/sphinx/_static/default.css, html/sphinx/genindex.html,
	html/sphinx/index.html, html/sphinx/modindex.html,
	html/sphinx/search.html, html/sphinx/searchindex.js,
	tftpy/TftpClient.py, tftpy/TftpPacketFactory.py,
	tftpy/TftpServer.py, tftpy/TftpShared.py, tftpy/TftpStates.py,
	tftpy/__init__.py: Latest doc updates

2010-07-11  Michael P. Soulier <msoulier@digitaltorque.ca>

	* doc/Makefile, html/index.html, html/sphinx/_sources/index.txt,
	html/sphinx/_static/basic.css, html/sphinx/_static/default.css,
	html/sphinx/_static/doctools.js, html/sphinx/_static/jquery.js,
	html/sphinx/_static/pygments.css,
	html/sphinx/_static/searchtools.js, html/sphinx/genindex.html,
	html/sphinx/index.html, html/sphinx/modindex.html,
	html/sphinx/objects.inv, html/sphinx/search.html,
	html/sphinx/searchindex.js, html/tftpy-doc/api-objects.txt,
	html/tftpy-doc/class-tree.html, html/tftpy-doc/epydoc.css,
	html/tftpy-doc/epydoc.js, html/tftpy-doc/frames.html,
	html/tftpy-doc/help.html, html/tftpy-doc/identifier-index.html,
	html/tftpy-doc/index.html, html/tftpy-doc/module-tree.html,
	html/tftpy-doc/redirect.html, html/tftpy-doc/tftpy-module.html,
	html/tftpy-doc/tftpy-pysrc.html,
	html/tftpy-doc/tftpy.TftpClient'-module.html,
	html/tftpy-doc/tftpy.TftpClient'-pysrc.html,
	html/tftpy-doc/tftpy.TftpClient'.TftpClient-class.html,
	html/tftpy-doc/tftpy.TftpPacketFactory'-module.html,
	html/tftpy-doc/tftpy.TftpPacketFactory'-pysrc.html,
	html/tftpy-doc/tftpy.TftpPacketFactory'.TftpPacketFactory-class.htm
	l, html/tftpy-doc/tftpy.TftpPacketTypes-module.html,
	html/tftpy-doc/tftpy.TftpPacketTypes-pysrc.html,
	html/tftpy-doc/tftpy.TftpPacketTypes.TftpPacket-class.html,
	html/tftpy-doc/tftpy.TftpPacketTypes.TftpPacketACK-class.html,
	html/tftpy-doc/tftpy.TftpPacketTypes.TftpPacketDAT-class.html,
	html/tftpy-doc/tftpy.TftpPacketTypes.TftpPacketERR-class.html,
	html/tftpy-doc/tftpy.TftpPacketTypes.TftpPacketInitial-class.html,
	html/tftpy-doc/tftpy.TftpPacketTypes.TftpPacketOACK-class.html,
	html/tftpy-doc/tftpy.TftpPacketTypes.TftpPacketRRQ-class.html,
	html/tftpy-doc/tftpy.TftpPacketTypes.TftpPacketWRQ-class.html,
	html/tftpy-doc/tftpy.TftpPacketTypes.TftpPacketWithOptions-class.ht
	ml, html/tftpy-doc/tftpy.TftpPacketTypes.TftpSession-class.html,
	html/tftpy-doc/tftpy.TftpServer'-module.html,
	html/tftpy-doc/tftpy.TftpServer'-pysrc.html,
	html/tftpy-doc/tftpy.TftpServer'.TftpServer-class.html,
	html/tftpy-doc/tftpy.TftpShared-module.html,
	html/tftpy-doc/tftpy.TftpShared-pysrc.html,
	html/tftpy-doc/tftpy.TftpShared.TftpErrors-class.html,
	html/tftpy-doc/tftpy.TftpShared.TftpException-class.html,
	html/tftpy-doc/tftpy.TftpStates-module.html,
	html/tftpy-doc/tftpy.TftpStates-pysrc.html,
	html/tftpy-doc/tftpy.TftpStates.TftpContext-class.html,
	html/tftpy-doc/tftpy.TftpStates.TftpContextClientDownload-class.htm
	l,
	html/tftpy-doc/tftpy.TftpStates.TftpContextClientUpload-class.html,
	html/tftpy-doc/tftpy.TftpStates.TftpContextServer-class.html,
	html/tftpy-doc/tftpy.TftpStates.TftpMetrics-class.html,
	html/tftpy-doc/tftpy.TftpStates.TftpState-class.html,
	html/tftpy-doc/tftpy.TftpStates.TftpStateExpectACK-class.html,
	html/tftpy-doc/tftpy.TftpStates.TftpStateExpectDAT-class.html,
	html/tftpy-doc/tftpy.TftpStates.TftpStateSentRRQ-class.html,
	html/tftpy-doc/tftpy.TftpStates.TftpStateSentWRQ-class.html,
	html/tftpy-doc/tftpy.TftpStates.TftpStateServerRecvRRQ-class.html,
	html/tftpy-doc/tftpy.TftpStates.TftpStateServerRecvWRQ-class.html,
	html/tftpy-doc/tftpy.TftpStates.TftpStateServerStart-class.html,
	html/tftpy-doc/toc-everything.html,
	html/tftpy-doc/toc-tftpy-module.html,
	html/tftpy-doc/toc-tftpy.TftpClient'-module.html,
	html/tftpy-doc/toc-tftpy.TftpPacketFactory'-module.html,
	html/tftpy-doc/toc-tftpy.TftpPacketTypes-module.html,
	html/tftpy-doc/toc-tftpy.TftpServer'-module.html,
	html/tftpy-doc/toc-tftpy.TftpShared-module.html,
	html/tftpy-doc/toc-tftpy.TftpStates-module.html,
	html/tftpy-doc/toc.html: Replacing epydoc output on website.

2010-07-11  Michael P. Soulier <msoulier@digitaltorque.ca>

	* doc/Makefile, doc/conf.py, doc/index.rst, tftpy/TftpClient.py,
	tftpy/TftpPacketTypes.py: Adding initial Sphinx docs

2010-05-25  Michael P. Soulier <msoulier@digitaltorque.ca>

	* t/test.py: Fixing typo in unit test

2010-05-25  Michael P. Soulier <msoulier@digitaltorque.ca>

	* bin/tftpy_client.py, tftpy/TftpClient.py, tftpy/TftpStates.py: 
	Adding support for input/output as stdin/stdout

2010-05-24  Michael P. Soulier <msoulier@digitaltorque.ca>

	* tftpy/TftpStates.py: Fixing failure to set default blocksize if
	options were provided but blksize was not one of them.

2010-05-12  Patrick Oppenlander <patrick@motec.com.au>

	* tftpy/TftpStates.py: fix incorrectly assigned state transition

2010-05-12  Patrick Oppenlander <patrick@motec.com.au>

	* tftpy/TftpStates.py: fix divide by zero in speed calculation for
	short transfers

2010-05-10  Michael P. Soulier <msoulier@digitaltorque.ca>

	* html/index.html: Updated site html formatting

2010-05-10  Michael P. Soulier <msoulier@digitaltorque.ca>

	* html/index.html: Website update

2010-05-10  Michael P. Soulier <msoulier@digitaltorque.ca>

	* notes/sfshell.txt: Updating notes

2010-05-10  Michael P. Soulier <msoulier@digitaltorque.ca>

	* setup.py: Fixing the license in the setup.py

2010-05-10  Michael P. Soulier <msoulier@digitaltorque.ca>

	* html/index.html: Updated website

2010-05-10  Michael P. Soulier <msoulier@digitaltorque.ca>

	* ChangeLog, README, setup.py: Updating metadata for 0.5.0 release

2010-05-10  Michael P. Soulier <msoulier@digitaltorque.ca>

	* tftpy/TftpClient.py, tftpy/TftpServer.py, tftpy/TftpStates.py: 
	Fixing buffering issue in upload. Uploads work now.

2010-05-10  Michael P. Soulier <msoulier@digitaltorque.ca>

	* README: Updated README

2010-05-10  Michael P. Soulier <msoulier@digitaltorque.ca>

	* bin/tftpy_client.py, tftpy/TftpServer.py, tftpy/TftpStates.py: 
	First working upload with new state machine. Not usable yet, upload
	fails to always send all data for some reason.

2010-05-10  Michael P. Soulier <msoulier@digitaltorque.ca>

	* tftpy/TftpStates.py: Fixed an obvious error introduced with the
	dyn_file_func merge

2010-04-24  Michael P. Soulier <msoulier@digitaltorque.ca>

	* : Merge commit 'angry-elf/master' into merge

2010-02-18  Alexey Loshkarev <elf2001@gmail.com>

	* tftpy/TftpStates.py: Fix dyn_file_func (was broken?) Fix error
	message (filename was not displayed)

2009-10-24  Michael P. Soulier <msoulier@digitaltorque.ca>

	* Makefile, html/index.html, html/tftpy-doc/api-objects.txt,
	html/tftpy-doc/class-tree.html, html/tftpy-doc/epydoc.css,
	html/tftpy-doc/epydoc.js, html/tftpy-doc/frames.html,
	html/tftpy-doc/help.html, html/tftpy-doc/identifier-index.html,
	html/tftpy-doc/index.html, html/tftpy-doc/module-tree.html,
	html/tftpy-doc/redirect.html, html/tftpy-doc/tftpy-module.html,
	html/tftpy-doc/tftpy-pysrc.html,
	html/tftpy-doc/tftpy.TftpClient'-module.html,
	html/tftpy-doc/tftpy.TftpClient'-pysrc.html,
	html/tftpy-doc/tftpy.TftpClient'.TftpClient-class.html,
	html/tftpy-doc/tftpy.TftpPacketFactory'-module.html,
	html/tftpy-doc/tftpy.TftpPacketFactory'-pysrc.html,
	html/tftpy-doc/tftpy.TftpPacketFactory'.TftpPacketFactory-class.htm
	l, html/tftpy-doc/tftpy.TftpPacketTypes-module.html,
	html/tftpy-doc/tftpy.TftpPacketTypes-pysrc.html,
	html/tftpy-doc/tftpy.TftpPacketTypes.TftpPacket-class.html,
	html/tftpy-doc/tftpy.TftpPacketTypes.TftpPacketACK-class.html,
	html/tftpy-doc/tftpy.TftpPacketTypes.TftpPacketDAT-class.html,
	html/tftpy-doc/tftpy.TftpPacketTypes.TftpPacketERR-class.html,
	html/tftpy-doc/tftpy.TftpPacketTypes.TftpPacketInitial-class.html,
	html/tftpy-doc/tftpy.TftpPacketTypes.TftpPacketOACK-class.html,
	html/tftpy-doc/tftpy.TftpPacketTypes.TftpPacketRRQ-class.html,
	html/tftpy-doc/tftpy.TftpPacketTypes.TftpPacketWRQ-class.html,
	html/tftpy-doc/tftpy.TftpPacketTypes.TftpPacketWithOptions-class.ht
	ml, html/tftpy-doc/tftpy.TftpPacketTypes.TftpSession-class.html,
	html/tftpy-doc/tftpy.TftpServer'-module.html,
	html/tftpy-doc/tftpy.TftpServer'-pysrc.html,
	html/tftpy-doc/tftpy.TftpServer'.TftpServer-class.html,
	html/tftpy-doc/tftpy.TftpShared-module.html,
	html/tftpy-doc/tftpy.TftpShared-pysrc.html,
	html/tftpy-doc/tftpy.TftpShared.TftpErrors-class.html,
	html/tftpy-doc/tftpy.TftpShared.TftpException-class.html,
	html/tftpy-doc/tftpy.TftpStates-module.html,
	html/tftpy-doc/tftpy.TftpStates-pysrc.html,
	html/tftpy-doc/tftpy.TftpStates.TftpContext-class.html,
	html/tftpy-doc/tftpy.TftpStates.TftpContextClientDownload-class.htm
	l,
	html/tftpy-doc/tftpy.TftpStates.TftpContextClientUpload-class.html,
	html/tftpy-doc/tftpy.TftpStates.TftpContextServer-class.html,
	html/tftpy-doc/tftpy.TftpStates.TftpMetrics-class.html,
	html/tftpy-doc/tftpy.TftpStates.TftpState-class.html,
	html/tftpy-doc/tftpy.TftpStates.TftpStateExpectACK-class.html,
	html/tftpy-doc/tftpy.TftpStates.TftpStateExpectDAT-class.html,
	html/tftpy-doc/tftpy.TftpStates.TftpStateSentRRQ-class.html,
	html/tftpy-doc/tftpy.TftpStates.TftpStateSentWRQ-class.html,
	html/tftpy-doc/tftpy.TftpStates.TftpStateServerRecvRRQ-class.html,
	html/tftpy-doc/tftpy.TftpStates.TftpStateServerRecvWRQ-class.html,
	html/tftpy-doc/tftpy.TftpStates.TftpStateServerStart-class.html,
	html/tftpy-doc/toc-everything.html,
	html/tftpy-doc/toc-tftpy-module.html,
	html/tftpy-doc/toc-tftpy.TftpClient'-module.html,
	html/tftpy-doc/toc-tftpy.TftpPacketFactory'-module.html,
	html/tftpy-doc/toc-tftpy.TftpPacketTypes-module.html,
	html/tftpy-doc/toc-tftpy.TftpServer'-module.html,
	html/tftpy-doc/toc-tftpy.TftpShared-module.html,
	html/tftpy-doc/toc-tftpy.TftpStates-module.html,
	html/tftpy-doc/toc.html: Updated epydoc output for website.

2009-09-24  Michael P. Soulier <msoulier@digitaltorque.ca>

	* COPYING, setup.py: Changed licenses to the MIT License

2009-09-24  Michael P. Soulier <msoulier@digitaltorque.ca>

	* tftpy/TftpPacketFactory.py, tftpy/TftpPacketTypes.py,
	tftpy/TftpShared.py, tftpy/TftpStates.py: Fixing some log messages
	and bad variable references.

2009-08-18  Michael P. Soulier <msoulier@digitaltorque.ca>

	* tftpy/TftpClient.py, tftpy/TftpServer.py, tftpy/TftpStates.py: 
	Updated resent_data in metrics.

2009-08-18  Michael P. Soulier <msoulier@digitaltorque.ca>

	* tftpy/TftpClient.py, tftpy/TftpServer.py, tftpy/TftpStates.py: 
	Fixed server metrics summary.

2009-08-16  Michael P. Soulier <msoulier@digitaltorque.ca>

	* .gitignore, bin/tftpy_client.py, bin/tftpy_server.py,
	tftpy/TftpClient.py, tftpy/TftpPacketTypes.py, tftpy/TftpServer.py,
	tftpy/TftpStates.py: First successful download with both client and
	server.

2009-08-15  Michael P. Soulier <msoulier@digitaltorque.ca>

	* tftpy/TftpClient.py, tftpy/TftpPacketFactory.py,
	tftpy/TftpPacketTypes.py, tftpy/TftpServer.py, tftpy/TftpShared.py,
	tftpy/TftpStates.py: Did some rework for the state machine in a
	server context.  Removed the handler framework in favour of a
	TftpContextServer used as the session.

2009-06-20  Michael P. Soulier <msoulier@digitaltorque.ca>

	* tftpy/TftpClient.py, tftpy/TftpStates.py: Fixing up some of the
	upload code.

2009-07-21  Michael P. Soulier <msoulier@digitaltorque.ca>

	* tftpy/TftpServer.py: Adding patch for dynamic content from Alex ?
	<yix@ya.ru>

2009-04-10  Michael P. Soulier <msoulier@digitaltorque.ca>

	* tftpy/TftpClient.py: Fixing a merge error in rebase

2009-04-10  Michael P. Soulier <msoulier@digitaltorque.ca>

	* tftpy/TftpStates.py: Fixed bug in tidport handling, and lack of
	OACK response.

2009-04-10  Michael P. Soulier <msoulier@digitaltorque.ca>

	* tftpy/TftpStates.py: Fixing OACK handling with new state machine.

2009-04-10  Michael P. Soulier <msoulier@digitaltorque.ca>

	* tftpy/TftpClient.py, tftpy/TftpPacketFactory.py,
	tftpy/TftpStates.py: Fixed TftpClient with new state machine.

2009-04-08  Michael P. Soulier <msoulier@digitaltorque.ca>

	* tftpy/TftpClient.py, tftpy/TftpPacketTypes.py,
	tftpy/TftpServer.py, tftpy/TftpShared.py, tftpy/TftpStates.py: 
	Started overhaul of state machine.

2009-04-10  Michael P. Soulier <msoulier@digitaltorque.ca>

	* bin/tftpy_client.py, tftpy/TftpClient.py: Improving sample client
	output on error and fixing default blocksize when server ignores
	options.

2009-04-10  Michael P. Soulier <msoulier@digitaltorque.ca>

	* : Merged upload patch.

2009-04-08  Michael P. Soulier <msoulier@digitaltorque.ca>

	* html/index.html: Website update

2009-04-07  Michael P. Soulier <msoulier@digitaltorque.ca>

	* tftpy/TftpServer.py: Fixing bogus warnings in options handling.

2009-04-07  Michael P. Soulier <msoulier@digitaltorque.ca>

	* : commit d05864202541cc5fda0e71292627cbd23861c4f3 Author: Michael
	P. Soulier <msoulier@digitaltorque.ca> Date:   Tue Apr 7 17:22:37
	2009 -0400

2009-03-15  Michael P. Soulier <msoulier@digitaltorque.ca>

	* html/index.html, html/main.css: Updated site with stylesheet

2009-03-15  Michael P. Soulier <msoulier@digitaltorque.ca>

	* html/index.html: Website update

2009-03-14  Michael P. Soulier <msoulier@digitaltorque.ca>

	* html/index.html, notes/sfshell.txt: Adding website

2008-10-08  Michael P. Soulier <msoulier@digitaltorque.ca>

	* README, bin/tftpy_client.py, tftpy/TftpPacketTypes.py: Fixed the
	use of the tsize option in RRQ packets.

2008-10-05  Michael P. Soulier <msoulier@digitaltorque.ca>

	* ChangeLog, README, tftpy/TftpPacketTypes.py: Rolling 0.4.6

2008-10-04  Michael P. Soulier <msoulier@digitaltorque.ca>

	* .gitignore, bin/tftpy_client.py, doc/rfc2349.txt, setup.py,
	tftpy/TftpClient.py, tftpy/TftpPacketTypes.py, tftpy/TftpServer.py: 
	Rebased tsize branch and added a --tsize option to the client.  Now
	sending all packets to the progresshook, not just DAT packets, so
	that the client can see the OACK. Not yet making use of the returned
	tsize. Need to test this on a server that supports tsize.

2008-07-30  Michael P. Soulier <msoulier@digitaltorque.ca>

	* tftpy/TftpServer.py: Adding transfer size option patch from Kuba
	Ko≈Ñczyk.  Patch 2018609 in SF tracker.

2008-10-03  Michael P. Soulier <msoulier@digitaltorque.ca>

	* : Merged from SVN trunk after register to PyPi

2008-07-30  Michael P. Soulier <msoulier@digitaltorque.ca>

	* bin/tftpy_client.py, tftpy/TftpClient.py: Adding upload patch from
	Lorenz Schori - patch 1897344 in SF tracker

2008-05-28  msoulier <msoulier@63283fd4-ec1e-0410-9879-cb7f675518da>

	* ChangeLog, README, setup.py, tftpy/TftpPacketTypes.py: Tagging
	0.4.5.  git-svn-id:

	https://tftpy.svn.sourceforge.net/svnroot/tftpy/tags/release-0.4.5@85 63283fd4-ec1e-0410-9879-cb7f675518da

2008-05-28  msoulier <msoulier@63283fd4-ec1e-0410-9879-cb7f675518da>

	* ChangeLog, README, setup.py: Updated for v0.4.5 release.  git-svn-id: https://tftpy.svn.sourceforge.net/svnroot/tftpy/trunk@84
	63283fd4-ec1e-0410-9879-cb7f675518da

2008-05-28  msoulier <msoulier@63283fd4-ec1e-0410-9879-cb7f675518da>

	* tftpy/TftpPacketTypes.py: Fix for bug 1967647, referencing
	self.sock instead of sock.  git-svn-id: https://tftpy.svn.sourceforge.net/svnroot/tftpy/trunk@83
	63283fd4-ec1e-0410-9879-cb7f675518da

2008-05-20  msoulier <msoulier@63283fd4-ec1e-0410-9879-cb7f675518da>

	* tftpy/TftpServer.py: Fix for [ 1932310 ] security check always
	fail for windows.  git-svn-id: https://tftpy.svn.sourceforge.net/svnroot/tftpy/trunk@82
	63283fd4-ec1e-0410-9879-cb7f675518da

2008-05-20  msoulier <msoulier@63283fd4-ec1e-0410-9879-cb7f675518da>

	* tftpy/TftpClient.py: Fixed division by zero error in rate
	calculations in download function of client. Thanks to Stefaan
	Vanheesbeke for the report.  git-svn-id: https://tftpy.svn.sourceforge.net/svnroot/tftpy/trunk@81
	63283fd4-ec1e-0410-9879-cb7f675518da

2008-05-20  msoulier <msoulier@63283fd4-ec1e-0410-9879-cb7f675518da>

	* tftpy/TftpServer.py: Fix for bug [ 1932330 ] binary downloads fail
	in Windows.  git-svn-id: https://tftpy.svn.sourceforge.net/svnroot/tftpy/trunk@80
	63283fd4-ec1e-0410-9879-cb7f675518da

2008-01-31  msoulier <msoulier@63283fd4-ec1e-0410-9879-cb7f675518da>

	* README: Updated README.  git-svn-id: https://tftpy.svn.sourceforge.net/svnroot/tftpy/trunk@78
	63283fd4-ec1e-0410-9879-cb7f675518da

2008-01-31  msoulier <msoulier@63283fd4-ec1e-0410-9879-cb7f675518da>

	* ChangeLog: Updated ChangeLog git-svn-id: https://tftpy.svn.sourceforge.net/svnroot/tftpy/trunk@77
	63283fd4-ec1e-0410-9879-cb7f675518da

2008-01-31  msoulier <msoulier@63283fd4-ec1e-0410-9879-cb7f675518da>

	* setup.py: Updating version to 0.4.4 git-svn-id: https://tftpy.svn.sourceforge.net/svnroot/tftpy/trunk@76
	63283fd4-ec1e-0410-9879-cb7f675518da

2007-12-16  msoulier <msoulier@63283fd4-ec1e-0410-9879-cb7f675518da>

	* tftpy/TftpServer.py: Fixing 1851544 - server not tolerant of
	unsupported options Thanks to Landon Jurgens for the report.  git-svn-id: https://tftpy.svn.sourceforge.net/svnroot/tftpy/trunk@75
	63283fd4-ec1e-0410-9879-cb7f675518da

2007-07-17  msoulier <msoulier@63283fd4-ec1e-0410-9879-cb7f675518da>

	* ChangeLog, README, setup.py: Updated for 0.4.3 release.  git-svn-id: https://tftpy.svn.sourceforge.net/svnroot/tftpy/trunk@73
	63283fd4-ec1e-0410-9879-cb7f675518da

2007-07-16  msoulier <msoulier@63283fd4-ec1e-0410-9879-cb7f675518da>

	* tftpy/TftpServer.py: Removed redundant comparison.  git-svn-id: https://tftpy.svn.sourceforge.net/svnroot/tftpy/trunk@72
	63283fd4-ec1e-0410-9879-cb7f675518da

2007-07-16  msoulier <msoulier@63283fd4-ec1e-0410-9879-cb7f675518da>

	* tftpy/TftpServer.py: Fixing string/integer comparison.  Thanks to
	Simon P. Ditner, bug #1755146.  git-svn-id: https://tftpy.svn.sourceforge.net/svnroot/tftpy/trunk@71
	63283fd4-ec1e-0410-9879-cb7f675518da

2007-06-05  msoulier <msoulier@63283fd4-ec1e-0410-9879-cb7f675518da>

	* ChangeLog, README, setup.py: Updated for 0.4.2 git-svn-id: https://tftpy.svn.sourceforge.net/svnroot/tftpy/trunk@69
	63283fd4-ec1e-0410-9879-cb7f675518da

2007-06-05  msoulier <msoulier@63283fd4-ec1e-0410-9879-cb7f675518da>

	* t/test.py: Fixed unit test for factory git-svn-id: https://tftpy.svn.sourceforge.net/svnroot/tftpy/trunk@68
	63283fd4-ec1e-0410-9879-cb7f675518da

2007-03-31  msoulier <msoulier@63283fd4-ec1e-0410-9879-cb7f675518da>

	* tftpy/TftpClient.py, tftpy/TftpPacketFactory.py,
	tftpy/TftpPacketTypes.py: Updating docs for epydoc.  git-svn-id: https://tftpy.svn.sourceforge.net/svnroot/tftpy/trunk@67
	63283fd4-ec1e-0410-9879-cb7f675518da

2007-03-31  msoulier <msoulier@63283fd4-ec1e-0410-9879-cb7f675518da>

	* Makefile: Updated build process.  git-svn-id: https://tftpy.svn.sourceforge.net/svnroot/tftpy/trunk@66
	63283fd4-ec1e-0410-9879-cb7f675518da

2007-03-31  msoulier <msoulier@63283fd4-ec1e-0410-9879-cb7f675518da>

	* Makefile: Adding epydoc target.  git-svn-id: https://tftpy.svn.sourceforge.net/svnroot/tftpy/trunk@65
	63283fd4-ec1e-0410-9879-cb7f675518da

2007-03-15  msoulier <msoulier@63283fd4-ec1e-0410-9879-cb7f675518da>

	* ChangeLog: Updated ChangeLog git-svn-id: https://tftpy.svn.sourceforge.net/svnroot/tftpy/trunk@64
	63283fd4-ec1e-0410-9879-cb7f675518da

2007-02-23  msoulier <msoulier@63283fd4-ec1e-0410-9879-cb7f675518da>

	* bin/tftpy_client.py, bin/tftpy_server.py: Simplifying use of
	optparse. Thanks to Steven Bethard for the suggestions.  git-svn-id: https://tftpy.svn.sourceforge.net/svnroot/tftpy/trunk@63
	63283fd4-ec1e-0410-9879-cb7f675518da

2007-02-17  msoulier <msoulier@63283fd4-ec1e-0410-9879-cb7f675518da>

	* tftpy/TftpServer.py: Removed mention of sorceror's apprentice
	problem.  git-svn-id: https://tftpy.svn.sourceforge.net/svnroot/tftpy/trunk@62
	63283fd4-ec1e-0410-9879-cb7f675518da

2007-02-17  msoulier <msoulier@63283fd4-ec1e-0410-9879-cb7f675518da>

	* tftpy/TftpPacketTypes.py, tftpy/TftpShared.py: Rearranged
	packaging a bit to fix an importing problem.  git-svn-id: https://tftpy.svn.sourceforge.net/svnroot/tftpy/trunk@61
	63283fd4-ec1e-0410-9879-cb7f675518da

2007-02-17  msoulier <msoulier@63283fd4-ec1e-0410-9879-cb7f675518da>

	* bin/tftpy_client.py, tftpy/TftpServer.py: Supplying a default
	blksize options in the server.  Fix for 1633625.  git-svn-id: https://tftpy.svn.sourceforge.net/svnroot/tftpy/trunk@60
	63283fd4-ec1e-0410-9879-cb7f675518da

2007-02-10  msoulier <msoulier@63283fd4-ec1e-0410-9879-cb7f675518da>

	* tftpy/TftpServer.py, tftpy/TftpShared.py: Added a check for rogue
	packets in the server.  git-svn-id: https://tftpy.svn.sourceforge.net/svnroot/tftpy/trunk@59
	63283fd4-ec1e-0410-9879-cb7f675518da

2007-02-09  msoulier <msoulier@63283fd4-ec1e-0410-9879-cb7f675518da>

	* tftpy/TftpPacketTypes.py, tftpy/TftpServer.py,
	tftpy/TftpShared.py, tftpy/__init__.py: Making the lib
	backwards-compatible to Python 2.3.  git-svn-id: https://tftpy.svn.sourceforge.net/svnroot/tftpy/trunk@58
	63283fd4-ec1e-0410-9879-cb7f675518da

2006-12-17  msoulier <msoulier@63283fd4-ec1e-0410-9879-cb7f675518da>

	* ChangeLog, README, setup.py: Rolling to version 0.4.1.  git-svn-id: https://tftpy.svn.sourceforge.net/svnroot/tftpy/trunk@56
	63283fd4-ec1e-0410-9879-cb7f675518da

2006-12-17  msoulier <msoulier@63283fd4-ec1e-0410-9879-cb7f675518da>

	* setup.py: Restructuring single lib into a package.  git-svn-id: https://tftpy.svn.sourceforge.net/svnroot/tftpy/trunk@55
	63283fd4-ec1e-0410-9879-cb7f675518da

2006-12-17  msoulier <msoulier@63283fd4-ec1e-0410-9879-cb7f675518da>

	* tftpy.py: Restructuring single lib into a package.  git-svn-id: https://tftpy.svn.sourceforge.net/svnroot/tftpy/trunk@54
	63283fd4-ec1e-0410-9879-cb7f675518da

2006-12-17  msoulier <msoulier@63283fd4-ec1e-0410-9879-cb7f675518da>

	* : Restructuring single lib into a package.  git-svn-id: https://tftpy.svn.sourceforge.net/svnroot/tftpy/trunk@53
	63283fd4-ec1e-0410-9879-cb7f675518da

2006-12-17  msoulier <msoulier@63283fd4-ec1e-0410-9879-cb7f675518da>

	* tftpy.py, tftpy/TftpClient.py, tftpy/TftpPacketFactory.py,
	tftpy/TftpPacketTypes.py, tftpy/TftpServer.py, tftpy/TftpShared.py,
	tftpy/__init__.py: Restructuring single lib into a package.  git-svn-id: https://tftpy.svn.sourceforge.net/svnroot/tftpy/trunk@52
	63283fd4-ec1e-0410-9879-cb7f675518da

2006-12-17  msoulier <msoulier@63283fd4-ec1e-0410-9879-cb7f675518da>

	* setup.py, lib/tftpy.py => tftpy.py: Fixing install location of
	library.  git-svn-id: https://tftpy.svn.sourceforge.net/svnroot/tftpy/trunk@51
	63283fd4-ec1e-0410-9879-cb7f675518da

2006-12-16  msoulier <msoulier@63283fd4-ec1e-0410-9879-cb7f675518da>

	* setup.py: Added server to package.  git-svn-id: https://tftpy.svn.sourceforge.net/svnroot/tftpy/trunk@49
	63283fd4-ec1e-0410-9879-cb7f675518da

2006-12-16  msoulier <msoulier@63283fd4-ec1e-0410-9879-cb7f675518da>

	* ChangeLog, README, lib/tftpy.py, setup.py: Updated ChangeLog, and
	rolled version to 0.4 git-svn-id: https://tftpy.svn.sourceforge.net/svnroot/tftpy/trunk@48
	63283fd4-ec1e-0410-9879-cb7f675518da

2006-12-15  msoulier <msoulier@63283fd4-ec1e-0410-9879-cb7f675518da>

	* bin/tftpy_server.py, lib/tftpy.py: Making server exit gracefully.  git-svn-id: https://tftpy.svn.sourceforge.net/svnroot/tftpy/trunk@47
	63283fd4-ec1e-0410-9879-cb7f675518da

2006-12-15  msoulier <msoulier@63283fd4-ec1e-0410-9879-cb7f675518da>

	* lib/tftpy.py: Tweak to EOF handling in server.  git-svn-id: https://tftpy.svn.sourceforge.net/svnroot/tftpy/trunk@46
	63283fd4-ec1e-0410-9879-cb7f675518da

2006-12-15  msoulier <msoulier@63283fd4-ec1e-0410-9879-cb7f675518da>

	* lib/tftpy.py: First working server tests with two clients.  git-svn-id: https://tftpy.svn.sourceforge.net/svnroot/tftpy/trunk@45
	63283fd4-ec1e-0410-9879-cb7f675518da

2006-12-15  msoulier <msoulier@63283fd4-ec1e-0410-9879-cb7f675518da>

	* README, bin/tftpy_client.py, lib/tftpy.py: Added lots in the
	server to support a download, with timeouts.  Not yet tested with a
	client, but the damn thing runs.  git-svn-id: https://tftpy.svn.sourceforge.net/svnroot/tftpy/trunk@44
	63283fd4-ec1e-0410-9879-cb7f675518da

2006-12-15  msoulier <msoulier@63283fd4-ec1e-0410-9879-cb7f675518da>

	* lib/tftpy.py: Fixed a bug in handling block number rollovers.  git-svn-id: https://tftpy.svn.sourceforge.net/svnroot/tftpy/trunk@43
	63283fd4-ec1e-0410-9879-cb7f675518da

2006-12-14  msoulier <msoulier@63283fd4-ec1e-0410-9879-cb7f675518da>

	* lib/tftpy.py: Got handling of file not found working in server.  git-svn-id: https://tftpy.svn.sourceforge.net/svnroot/tftpy/trunk@42
	63283fd4-ec1e-0410-9879-cb7f675518da

2006-12-14  msoulier <msoulier@63283fd4-ec1e-0410-9879-cb7f675518da>

	* bin/tftpy_server.py: Starting on sample server.  git-svn-id: https://tftpy.svn.sourceforge.net/svnroot/tftpy/trunk@41
	63283fd4-ec1e-0410-9879-cb7f675518da

2006-12-14  msoulier <msoulier@63283fd4-ec1e-0410-9879-cb7f675518da>

	* bin/tftpy_client.py, lib/tftpy.py: Successful test on basic select
	loop git-svn-id: https://tftpy.svn.sourceforge.net/svnroot/tftpy/trunk@40
	63283fd4-ec1e-0410-9879-cb7f675518da

2006-12-11  msoulier <msoulier@63283fd4-ec1e-0410-9879-cb7f675518da>

	* lib/tftpy.py: Added some security checks around the tftproot.
	Further fleshed-out the handler. Still not actually starting the
	transfer.  git-svn-id: https://tftpy.svn.sourceforge.net/svnroot/tftpy/trunk@39
	63283fd4-ec1e-0410-9879-cb7f675518da

2006-12-10  msoulier <msoulier@63283fd4-ec1e-0410-9879-cb7f675518da>

	* README, lib/tftpy.py: Fleshing out server handler implementation.  git-svn-id: https://tftpy.svn.sourceforge.net/svnroot/tftpy/trunk@38
	63283fd4-ec1e-0410-9879-cb7f675518da

2006-12-10  msoulier <msoulier@63283fd4-ec1e-0410-9879-cb7f675518da>

	* README, bin/tftpy_client.py, lib/tftpy.py: Started on the server git-svn-id: https://tftpy.svn.sourceforge.net/svnroot/tftpy/trunk@37
	63283fd4-ec1e-0410-9879-cb7f675518da

2006-12-09  msoulier <msoulier@63283fd4-ec1e-0410-9879-cb7f675518da>

	* bin/tftpy_client.py: Added --debug option to sample client.  git-svn-id: https://tftpy.svn.sourceforge.net/svnroot/tftpy/trunk@36
	63283fd4-ec1e-0410-9879-cb7f675518da

2006-12-09  msoulier <msoulier@63283fd4-ec1e-0410-9879-cb7f675518da>

	* MANIFEST.in: Adding license git-svn-id: https://tftpy.svn.sourceforge.net/svnroot/tftpy/trunk@34
	63283fd4-ec1e-0410-9879-cb7f675518da

2006-12-09  msoulier <msoulier@63283fd4-ec1e-0410-9879-cb7f675518da>

	* ChangeLog, MANIFEST.in, README: Adding ChangeLog git-svn-id: https://tftpy.svn.sourceforge.net/svnroot/tftpy/trunk@33
	63283fd4-ec1e-0410-9879-cb7f675518da

2006-12-09  msoulier <msoulier@63283fd4-ec1e-0410-9879-cb7f675518da>

	* setup.py: Bumped the version.  git-svn-id: https://tftpy.svn.sourceforge.net/svnroot/tftpy/trunk@32
	63283fd4-ec1e-0410-9879-cb7f675518da

2006-12-09  msoulier <msoulier@63283fd4-ec1e-0410-9879-cb7f675518da>

	* lib/tftpy.py: Changed the port variables to something more
	intelligent.  git-svn-id: https://tftpy.svn.sourceforge.net/svnroot/tftpy/trunk@31
	63283fd4-ec1e-0410-9879-cb7f675518da

2006-12-09  msoulier <msoulier@63283fd4-ec1e-0410-9879-cb7f675518da>

	* lib/tftpy.py: Fixing poor TID implementation.  git-svn-id: https://tftpy.svn.sourceforge.net/svnroot/tftpy/trunk@30
	63283fd4-ec1e-0410-9879-cb7f675518da

2006-10-25  msoulier <msoulier@63283fd4-ec1e-0410-9879-cb7f675518da>

	* t/test.py: Added testcase for TftpPacketFactory.  git-svn-id: https://tftpy.svn.sourceforge.net/svnroot/tftpy/trunk@29
	63283fd4-ec1e-0410-9879-cb7f675518da

2006-10-13  msoulier <msoulier@63283fd4-ec1e-0410-9879-cb7f675518da>

	* lib/tftpy.py: Implemented retries on download timeouts.  git-svn-id: https://tftpy.svn.sourceforge.net/svnroot/tftpy/trunk@28
	63283fd4-ec1e-0410-9879-cb7f675518da

2006-10-13  msoulier <msoulier@63283fd4-ec1e-0410-9879-cb7f675518da>

	* lib/tftpy.py: Added some info statements regarding option
	negotiation.  git-svn-id: https://tftpy.svn.sourceforge.net/svnroot/tftpy/trunk@27
	63283fd4-ec1e-0410-9879-cb7f675518da

2006-10-13  msoulier <msoulier@63283fd4-ec1e-0410-9879-cb7f675518da>

	* lib/tftpy.py, t/test.py: Updated testcases, fixed one error in
	decode_options git-svn-id: https://tftpy.svn.sourceforge.net/svnroot/tftpy/trunk@26
	63283fd4-ec1e-0410-9879-cb7f675518da

2006-10-11  msoulier <msoulier@63283fd4-ec1e-0410-9879-cb7f675518da>

	* lib/tftpy.py, t/test.py: Updated testcases git-svn-id: https://tftpy.svn.sourceforge.net/svnroot/tftpy/trunk@25
	63283fd4-ec1e-0410-9879-cb7f675518da

2006-10-11  msoulier <msoulier@63283fd4-ec1e-0410-9879-cb7f675518da>

	* Makefile: Updated makefile git-svn-id: https://tftpy.svn.sourceforge.net/svnroot/tftpy/trunk@24
	63283fd4-ec1e-0410-9879-cb7f675518da

2006-10-11  msoulier <msoulier@63283fd4-ec1e-0410-9879-cb7f675518da>

	* Makefile, {test => t}/test.py: Adding makefile git-svn-id: https://tftpy.svn.sourceforge.net/svnroot/tftpy/trunk@23
	63283fd4-ec1e-0410-9879-cb7f675518da

2006-10-10  msoulier <msoulier@63283fd4-ec1e-0410-9879-cb7f675518da>

	* LICENSE => COPYING, README: Moved LICENSE to COPYING git-svn-id: https://tftpy.svn.sourceforge.net/svnroot/tftpy/trunk@22
	63283fd4-ec1e-0410-9879-cb7f675518da

2006-10-09  msoulier <msoulier@63283fd4-ec1e-0410-9879-cb7f675518da>

	* test/test.py: Added test for WRQ packet git-svn-id: https://tftpy.svn.sourceforge.net/svnroot/tftpy/trunk@21
	63283fd4-ec1e-0410-9879-cb7f675518da

2006-10-09  msoulier <msoulier@63283fd4-ec1e-0410-9879-cb7f675518da>

	* bin/tftpy_client.py, lib/tftpy.py, test/test.py: Fixed broken
	decode, and adjusted the client options.  git-svn-id: https://tftpy.svn.sourceforge.net/svnroot/tftpy/trunk@20
	63283fd4-ec1e-0410-9879-cb7f675518da

2006-10-08  msoulier <msoulier@63283fd4-ec1e-0410-9879-cb7f675518da>

	* lib/tftpy.py, test/test.py: Starting on unit tests git-svn-id: https://tftpy.svn.sourceforge.net/svnroot/tftpy/trunk@19
	63283fd4-ec1e-0410-9879-cb7f675518da

2006-10-05  msoulier <msoulier@63283fd4-ec1e-0410-9879-cb7f675518da>

	* bin/tftpy_client.py: Fixed handling of port git-svn-id: https://tftpy.svn.sourceforge.net/svnroot/tftpy/trunk@17
	63283fd4-ec1e-0410-9879-cb7f675518da

2006-10-05  msoulier <msoulier@63283fd4-ec1e-0410-9879-cb7f675518da>

	* bin/tftpy_client.py, lib/tftpy_twisted.py: Updating for production git-svn-id: https://tftpy.svn.sourceforge.net/svnroot/tftpy/trunk@16
	63283fd4-ec1e-0410-9879-cb7f675518da

2006-10-05  msoulier <msoulier@63283fd4-ec1e-0410-9879-cb7f675518da>

	* README: Freezing 0.2 git-svn-id: https://tftpy.svn.sourceforge.net/svnroot/tftpy/trunk@14
	63283fd4-ec1e-0410-9879-cb7f675518da

2006-10-05  msoulier <msoulier@63283fd4-ec1e-0410-9879-cb7f675518da>

	* lib/tftpy.py: Fixed poor EOF detection git-svn-id: https://tftpy.svn.sourceforge.net/svnroot/tftpy/trunk@13
	63283fd4-ec1e-0410-9879-cb7f675518da

2006-10-05  msoulier <msoulier@63283fd4-ec1e-0410-9879-cb7f675518da>

	* bin/tftpy_client.py, lib/tftpy.py: Got variable blocksizes
	working.  git-svn-id: https://tftpy.svn.sourceforge.net/svnroot/tftpy/trunk@12
	63283fd4-ec1e-0410-9879-cb7f675518da

2006-10-04  msoulier <msoulier@63283fd4-ec1e-0410-9879-cb7f675518da>

	* lib/tftpy.py: Added confirmation of incoming traffic to known
	remote host.  git-svn-id: https://tftpy.svn.sourceforge.net/svnroot/tftpy/trunk@11
	63283fd4-ec1e-0410-9879-cb7f675518da

2006-10-04  msoulier <msoulier@63283fd4-ec1e-0410-9879-cb7f675518da>

	* lib/tftpy.py: Restructured in preparation for tftp options git-svn-id: https://tftpy.svn.sourceforge.net/svnroot/tftpy/trunk@10
	63283fd4-ec1e-0410-9879-cb7f675518da

2006-10-04  msoulier <msoulier@63283fd4-ec1e-0410-9879-cb7f675518da>

	* README: Updated README git-svn-id: https://tftpy.svn.sourceforge.net/svnroot/tftpy/trunk@9
	63283fd4-ec1e-0410-9879-cb7f675518da

2006-10-04  msoulier <msoulier@63283fd4-ec1e-0410-9879-cb7f675518da>

	* README: Updated README git-svn-id: https://tftpy.svn.sourceforge.net/svnroot/tftpy/trunk@8
	63283fd4-ec1e-0410-9879-cb7f675518da

2006-10-04  msoulier <msoulier@63283fd4-ec1e-0410-9879-cb7f675518da>

	* lib/tftpy.py: Added seconds to logs git-svn-id: https://tftpy.svn.sourceforge.net/svnroot/tftpy/trunk@7
	63283fd4-ec1e-0410-9879-cb7f675518da

2006-10-04  msoulier <msoulier@63283fd4-ec1e-0410-9879-cb7f675518da>

	* setup.py: Upping version to 0.2 git-svn-id: https://tftpy.svn.sourceforge.net/svnroot/tftpy/trunk@6
	63283fd4-ec1e-0410-9879-cb7f675518da

2006-10-04  msoulier <msoulier@63283fd4-ec1e-0410-9879-cb7f675518da>

	* bin/tftpy_client.py, lib/tftpy.py: Added OACK packet, and
	factored-out client code.  git-svn-id: https://tftpy.svn.sourceforge.net/svnroot/tftpy/trunk@5
	63283fd4-ec1e-0410-9879-cb7f675518da

2006-10-03  msoulier <msoulier@63283fd4-ec1e-0410-9879-cb7f675518da>

	* lib/tftpy.py: Updated a comment git-svn-id: https://tftpy.svn.sourceforge.net/svnroot/tftpy/trunk@4
	63283fd4-ec1e-0410-9879-cb7f675518da

2006-10-03  msoulier <msoulier@63283fd4-ec1e-0410-9879-cb7f675518da>

	* LICENSE, MANIFEST.in, README, bin/tftpy_client.py,
	doc/rfc1350.txt, doc/rfc2347.txt, doc/rfc2348.txt, lib/tftpy.py,
	lib/tftpy_twisted.py, setup.py: Restructuring git-svn-id: https://tftpy.svn.sourceforge.net/svnroot/tftpy/trunk@3
	63283fd4-ec1e-0410-9879-cb7f675518da

2006-10-03  msoulier <msoulier@63283fd4-ec1e-0410-9879-cb7f675518da>

	* Restructuring git-svn-id: https://tftpy.svn.sourceforge.net/svnroot/tftpy/trunk@2
	63283fd4-ec1e-0410-9879-cb7f675518da

