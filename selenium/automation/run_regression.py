#!/usr/bin/env python2.7

# --------------------------------------------------------------------
#
# Title: run_regression.py - execute all the tests
#
# --------------------------------------------------------------------

from subprocess import call
from datetime import datetime
import logging
import os

# list of the running test scripts
scripts = [
    "web_access_request.py",
]

# directory for reports
if not os.path.exists('reports'):
  os.mkdir('reports')

# log the test execution
logging.basicConfig(level=logging.NOTSET, format="%(message)s", filename="reports/regression.log")
log = logging.getLogger("regression")

if __name__ == '__main__':
  log_file = open("reports/regression.log", "w")
  start_time = datetime.now()
  test_time = datetime.strftime(start_time, "%Y-%m-%d  %H:%M:%S")
  log.info("---------------------------------------------------------------------------------")
  log.info("regression:[Date]: %s" % test_time)
  log.info("regression:[Scripts]: " + ", ".join(scripts))

  # execute tests
  for script in scripts:
    try:
      log.info("test script:[Begins]: " + script)
      call("python %s -d sauce -i travisci" % script, shell=True)
    except Exception as e:
      log.exception("test script[ErrorMessage]: " + str(e))
    finally:
      log.info("test script:[Ends]\n")

  # calculate elapsed time
  finish_time = datetime.now()
  elapsed = finish_time - start_time
  log.info("regression:[Elapsed]: " + str(elapsed))
  log.info("---------------------------------------------------------------------------------")
  log_file.close()
