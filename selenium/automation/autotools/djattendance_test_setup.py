#!/usr/bin/env python2.7

# -------------------------------------------------------------------------
#
# Title: djattendance_test_setup.py
#
# Purpose: setup for the automation running
#      check for selenium/driver version
#         - pip show selenium
#         - ./chromedriver --version
#
# -------------------------------------------------------------------------

import os
import json
import sys
from selenium import webdriver
from sauceclient import SauceClient
from datetime import datetime

with open("data/saucelab.json") as data_file:
  """ initially set the Saucelab WebDriver desired capacities """
  saucelab_setting = json.load(data_file)


class AutomationSetup:
  """ set up the webdriver in one of the three cases:
    1) Saucelab RemoteWebDriver - instantiate cloud webdriver with Saucelab credentials
                  - Sauce_Client is instantiated to update Saucelab cloud
    2) chrome webdriver - locally testing with chrome browser in either Mac or Linux
    3) firefox webdriver - locally testing with firefox browser(common for Mac or Linux)

    * for TravisCI, add attributes before instantiate Saucelab RemoteWebDriver *
    * currently not supporting Windows for automation, so if developed please update set_webdriver() method below *
  """

  def __init__(self, testname, drivertype=None, integration=None):
    self.testname = testname
    self.drivertype = drivertype
    self.integration = integration
    self.current_date = datetime.now()
    self.urladdress = None
    self.email = None
    self.password = None
    self.taemail = None
    self.tapassword = None
    self.webdriver = None
    self.Sauce_Client = None
    self.USE_SAUCE = False

    self.test_failcounts = 0
    """ use counter variable for Saucelab report - Saucelab currently considers last test cases
      to determine the overall testsuite result
    """
    self.saucelab_environment_details = saucelab_setting
    self.saucelab_environment_details['name'] = testname

    if integration == "travisci":
      # travisci-saucelab tunnel
      self.saucelab_environment_details['tunnel-identifier'] = os.environ.get('TRAVIS_JOB_NUMBER')
      self.saucelab_environment_details['build'] = os.environ.get('TRAVIS_BUILD_NUMBER')

  def set_webdriver(self):
    # saucelabs
    if self.drivertype == "sauce":
      # travisci environment variables
      self.USE_SAUCE = True
      username = os.environ.get('SAUCE_USERNAME', self.saucelab_environment_details.get('username', ''))
      access_key = os.environ.get('SAUCE_ACCESS_KEY', self.saucelab_environment_details.get('key', ''))
      self.Sauce_Client = SauceClient(username, access_key)
      self.saucelab_environment_details['username'] = username
      self.saucelab_environment_details['key'] = access_key
      self.webdriver = webdriver.Remote(
          command_executor='http://%s:%s@ondemand.saucelabs.com:80/wd/hub' % (username, access_key),
          desired_capabilities=self.saucelab_environment_details
      )
    elif self.drivertype == "chrome":
      if sys.platform == 'darwin':
        chromedriver = "../chromedriver_mac"
      elif sys.platform.startswith('linux'):
        chromedriver = "../chromedriver_linux"
      else:
        print "You need to run these scripts with Mac or Linux(currently not supporting Windows)."
        exit()
      self.webdriver = webdriver.Chrome(chromedriver)
    # default firefox webdriver
    else:
      if sys.platform == 'darwin':
        os.environ["PATH"] += ':%s' % os.path.abspath("../mac")
      elif sys.platform.startswith('linux'):
        os.environ["PATH"] += ':%s' % os.path.abspath("../linux")
      else:
        print "You need to run these scripts with Mac or Linux(currently not supporting Windows)."
        exit()
      profile = webdriver.FirefoxProfile()
      profile.set_preference("xpinstall.signatures.required", False)
      self.webdriver = webdriver.Firefox(firefox_profile=profile)

  def set_urladdress(self, urladdress):
    self.urladdress = urladdress

  def get_testname(self):
    return self.testname

  def get_current_date(self):
    return self.current_date

  def get_urladdress(self):
    return self.urladdress

  def set_email(self, email):
    self.email = email

  def get_email(self):
    return self.email

  def set_password(self, password):
    self.password = password

  def get_password(self):
    return self.password

  def set_taemail(self, taemail):
    self.taemail = taemail

  def get_taemail(self):
    return self.taemail

  def set_tapassword(self, tapassword):
    self.tapassword = tapassword

  def get_tapassword(self):
    return self.tapassword

  def get_webdriver(self):
    return self.webdriver

  def get_saucelab_client(self):
    return self.Sauce_Client

  def get_test_failcounts(self):
    return self.test_failcounts

  def set_test_failcounts(self, newcount):
    self.test_failcounts = newcount

  def increase_test_failcounts(self, increment=1):
    self.test_failcounts += increment

  def is_sauce_used(self):
    return self.USE_SAUCE

  def update_saucelab(self, res):
    self.Sauce_Client.jobs.update_job(self.webdriver.session_id, passed=res)
