Participate in Code Development
===============================

Cell2Fire is an open source software project and contributions of
code, documentation, and examples are welcome.  If you want to help
with the project, you should start by following standard github
procedures as documented
`here <https://git-scm.com/book/en/v2/GitHub-Contributing-to-a-Project>`_.

For a contribution other than documentation or a quick fix, a new test
and test driver should be written and added to the pull request. New
tests should be placed in the sub-directory ``tests`` and the
file ``tests\test_20x20.py`` (or other tests in that directory)
can serve as the starting point for the new test. Drivers for tests
on github go in the subdirectory ``.github/workflows`` and the
driver ``sub20x20.yml`` does installation onto the github
virtual machine, runs Cell2Fire to produce output files,
and runs ``test_20x20.py`` to complete the test.


.. Note::
   As of late 2023 the C++ code is tested by the Python tests, but
   there are no direct unit tests of that code. Furthermore, the
   extant Python tests rely on the github yml drivers to run
   Cell2Fire once to avoid the need to call the C++ code
   from within the Python ``unittest`` framework (using
   the Cell2Fire ``--onlyProcessing`` option.)
   
