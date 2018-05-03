#!/usr/bin/env python2.7

# ----------------------------------------------------------------------------
#
# Title: djattendance_test_api.py
#
# Purpose: collects of the commonly used functions for testing Django server
#
# ----------------------------------------------------------------------------
"""
  Try to limit inserting fixed time delay to wait for web elements to appear
  Instead use "wait_for()" to make sure the specific web element to come up

  In case an implicit wait is used, time.sleep() is better over driver.implicitly_wait()
"""

import HtmlTestRunner
import time
import unittest
import traceback
import os
import json
from djattendance_test_setup import AutomationSetup
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
# from selenium.webdriver.common.keys import Keys
from optparse import OptionParser

auto = None
driver = None
DEBUG = False

with open("data/login.json") as data_file:
  login_data = json.load(data_file)


def initialize_test(testname):
  """ Initialize test suite
    -d: chrome, sauce, firefox(default) (eg. -d chrome)
    -i: travisci or none (eg. -i travisci)
    -u: url address (eg. -u https://www.ftta.org)
  """
  # option in command line
  parser = OptionParser()
  parser.add_option("-d", "--driver", action="store", dest="drivername")
  parser.add_option("-i", "--integration", action="store", dest="ciname")
  parser.add_option("-u", "--url", action="store", dest="urlname")
  parser.add_option("-e", "--email", action="store", dest="email")
  parser.add_option("-p", "--pass", action="store", dest="password")
  parser.add_option("--taemail", action="store", dest="taemail")
  parser.add_option("--tapass", action="store", dest="tapassword")
  (options, args) = parser.parse_args()

  # Test setup
  global auto
  auto = AutomationSetup(testname, options.drivername, options.ciname)
  auto.set_webdriver()
  global driver
  driver = auto.get_webdriver()

  # parsing the URL option
  if options.urlname:
    auto.set_urladdress(options.urlname)
  else:
    auto.set_urladdress(login_data["domain"])

  # parsing login option
  if options.email:
    auto.set_email(options.email)
  else:
    auto.set_email(login_data["username"])
  if options.password:
    auto.set_password(options.password)
  else:
    auto.set_password(login_data["password"])
  if options.taemail:
    auto.set_taemail(options.taemail)
  else:
    auto.set_taemail(login_data["tausername"])
  if options.tapassword:
    auto.set_tapassword(options.tapassword)
  else:
    auto.set_tapassword(login_data["tapassword"])


def finalize_test():
  """ Finalize the test suite
    - update Saucelab with the overall test results: Pass or Fail
    - close the webdriver object and free up the space
  """
  if auto.is_sauce_used():
    if auto.get_test_failcounts() != 0:
      auto.update_saucelab(False)
    else:
      auto.update_saucelab(True)
  driver.quit()


def wait_for(by, value, check_for='presence', time=10):
  """ Wait for a specific object to appear by checking object attribute value
    Check for either object presence or clickable - refer python-selenium API

    (eg. wait_for("class", "navbar-brand"))
    (eg. wait_for("class", "navbar-brand", "clickable"))
  """
  try:
    if by == 'class':
      method = By.CLASS_NAME
    elif by == 'CSS':
      method = By.CSS_SELECTOR
    elif by == 'id':
      method = By.ID
    elif by == 'name':
      method = By.NAME
    elif by == 'tag':
      method = By.TAG_NAME
    elif by == 'xpath':
      method = By.XPATH
    elif by == 'text':
      method = By.XPATH
      value = '//*[contains(text(), "' + value + '")]'
    elif by == 'value':
      method = By.XPATH
      value = '//*[@value="' + value + '"]'
    elif by == 'link':
      method = By.LINK_TEXT
    else:
      method = By.PARTIAL_LINK_TEXT

    if check_for == 'clickable':
      WebDriverWait(driver, time).until(EC.element_to_be_clickable((method, value)))
    else:
      WebDriverWait(driver, time).until(EC.presence_of_element_located((method, value)))
  except Exception as e:
    # TimeoutException because the element is not present
    raise Exception(e, "item [%s] is not present/clickable" % value)


def login(pose=0):
  """ Log into the URL address with passed username and password
    Use pose parameter to insert time sleep before the next executions
  """

  """ note: driver.get(): onload mechanism, wait until page is fully loaded """
  driver.get(auto.get_urladdress())
  driver.maximize_window()
  wait_for("class", "navbar-brand")  # wait for FTTA logo comes up

  # if there is hide button visible - only applicable when using dev mode
  hide_xpath = '//*[@title="Hide toolbar"]'
  if is_element_visible(hide_xpath, "xpath"):
    click_element("xpath", hide_xpath)
    time.sleep(2)

  # login with credentials
  log_into_account(auto.get_email(), auto.get_password())

  wait_for_brand()

  # check if the server is in use during the class time
  discard_message_server_used()
  time.sleep(pose)


def wait_for_brand():
  wait_for("class", "navbar-brand")


def log_into_account(username, password, pose=0):
  """ Log into the account with credentials
    Tag name of elements are used; username, password
  """
  send_text("name", "username", username)
  send_text("name", "password", password, True)
  time.sleep(pose)


def discard_message_server_used(pose=0):
  """ Close the message saying "using the server in class"
    Use in order to move on with next script executions
  """
  if is_server_used_in_class():
    click_element("text", "OK")
  time.sleep(pose)


def is_server_used_in_class(pose=3):
  """ Check if the server is used during class time
    - pose: to insert random time delay for the pop up message to appear

    * TODO: develop further error catching for another pop ups(eg. notification from TA) *
  """
  time.sleep(pose)
  try:
    text = get_child_element(".modal.fade.in", ".modal-title").get_attribute('textContent')
  except Exception as e:
    return False
  return "you are using the server in class" in text.lower()


def get_the_element(by, value, pose=0):
  """ Locate a web element in the DOM tree by attribute and value pair
    - by id   : use id attribute and its value
    - by name   : use name attribute and its value
    - by xpath   : use Xpath attribute and its value
    - by class   : use class name and its value
    - by CSS   : use CSS selector and its value

  """
  time.sleep(pose)
  if by == "id":
    return driver.find_element_by_id(value)
  elif by == "name":
    return driver.find_element_by_name(value)
  elif by == "xpath":
    return driver.find_element_by_xpath(value)
  elif by == "class":
    return driver.find_element_by_class_name(value)
  else:
    return driver.find_element_by_css_selector(value)


def get_list_elements(by, value, pose=0):
  """ Same operation with get_the_element(), return list of elements
  """
  time.sleep(pose)
  if by == "id":
    return driver.find_elements_by_id(value)
  elif by == "name":
    return driver.find_elements_by_name(value)
  elif by == "xpath":
    return driver.find_elements_by_xpath(value)
  elif by == "class":
    return driver.find_elements_by_class_name(value)
  else:
    return driver.find_elements_by_css_selector(value)


def get_child_element(parent, child, by='css'):
  """ Locate child node from parent in DOM tree by attribute values
    - by id   : use id attribute values in pair
    - by name   : use name attribute values in pair
    - by xpath   : use Xpath attribute values in pair
    - by class   : use class attribute values in pair
    - by CSS   : use CSS selector values in pair(default)

    (eg. locate_child_element(parent-class-name, child-class-name))
    (eg. locate_child_element(.parent.css.selector, .child.css.selector))
  """
  if by == "id":
    return driver.find_element_by_id(parent).find_element_by_id(child)
  elif by == "name":
    return driver.find_element_by_name(parent).find_element_by_name(child)
  elif by == "xpath":
    return driver.find_element_by_xpath(parent).find_element_by_xpath(child)
  elif by == "class":
    return driver.find_element_by_class_name(parent).find_element_by_class_name(child)
  else:
    return driver.find_element_by_css_selector(parent).find_element_by_css_selector(child)


def click_element(by, value, pose=0):
  """ Click web element based on the attribute and value pair
    - by text: click upon visible text(should not be hidden by another frame)
    - by value: click upon the value attribute
    - by id:  click upon the id
    - by class:  click upon the class name
    - by CSS:  click upon the class selector
    - by xpath: click upon xpath of element
  """
  if by == "text":
    driver.find_element_by_xpath('//*[contains(text(), "' + value + '")]').click()
  elif by == "value":
    driver.find_element_by_xpath('//*[@value="' + value + '"]').click()
  elif by == "id":
    driver.find_element_by_id(value).click()
  elif by == "class":
    driver.find_element_by_class_name(value).click()
  elif by == "CSS":
    driver.find_element_by_css_selector(value).click()
  else:
    driver.find_element_by_xpath(value).click()

  time.sleep(pose)


def click_element_actionchain(by, value, pose=0):
  """ Same operation with "click_element()" but using ActionChains

    Arguments: refer click_element()
  """
  if by == "text":
    elem = driver.find_element_by_xpath('//*[contains(text(), "' + value + '")]')
  elif by == "value":
    elem = driver.find_element_by_xpath('//*[@value="' + value + '"]')
  elif by == "id":
    elem = driver.find_element_by_id(value)
  elif by == "class":
    elem = driver.find_element_by_class_name(value)
  elif by == "CSS":
    elem = driver.find_element_by_css_selector(value)
  else:
    elem = driver.find_element_by_xpath(value)
  ActionChains(driver).move_to_element(elem).click().perform()

  time.sleep(pose)


def select_dropdown_menu(by, main_item, menu_item, pose=0):
  """ Click on the web element in the drop-down menu
    - by text: refer the comment in click_element()
    - by value: refer the comment in click_element()
    - by id: refer the comment in click_element()
    - by class: refer the comment in click_element()
    - by xpath: refer the comment in click_element()

    - main_item: drop-down menu
    - menu_item: one of the drop-down list items

    note: main_item and menu_item should have the same attribute with different values
  """
  click_element(by, main_item)
  wait_for(by, menu_item, "clickable")
  click_element(by, menu_item, pose)


def send_text(by, value, text, enter=False, pose=0):
  """ Type text to the specified web element
    Clear the text field first and then send the text

    - by: refer comment in "get_the_element()"
    - value: refer comment in "get_the_element()"
    - text:  to be written in the text field
    - enter: set True if you want to submit after writting text

    * note for driver bug: if used for non-user-editable element, error occurs *
    (eg. InvalidElementStateException, WebDriverException: cannot focus element)
  """
  elem = get_the_element(by, value)
  elem.clear()
  elem.send_keys(text)
  if enter:
    elem.submit()
  time.sleep(pose)


def send_text_actionchain(by, value, text, enter=False, pose=0):
  """ Same operation with "send_text()" but using ActionChains

    Arguments: refer send_text()
  """
  elem = get_the_element(by, value)
  ActionChains(driver).move_to_element(elem).click().send_keys(text).perform()
  if enter:
    elem.submit()
  time.sleep(pose)


def get_element_attribute(by, value, attribute, pose=0):
  """ Get the value of attribute of the web element

    (eg. To get the value of the "role" attribute in the follow element,
      <a href="#", class="dropdown-toggle", data-toggle="dropdown", role="button"></a>

      get_element_attribute("class", "dropdown-toggle", "role")
    )

    - by: refer comment in "get_the_element()"
    - value: refer comment in "get_the_element()"
    - attribute: attribute interested
  """
  return get_the_element(by, value, pose).get_attribute(attribute)


def get_element_text(by, value, pose=0):
  """ Get the displayed text of the web element

    - by: refer comment in "get_the_element()"
    - value: refer comment in "get_the_element()"

    "textContent" or "innerHTML" attribute is used
  """
  displayed = get_element_attribute(by, value, "textContent", pose)
  if displayed == "undefined" or displayed == "None":
    displayed = get_element_attribute(by, value, "innerHTML", pose)

  return displayed


def execute_javascript(javascript, *args):
  """ Synchronously execute the JavaScript in the current web browser console

    - javascript: pass a string of JavaScript to be executed
    - *args: non-keyworded variable for applicable arguments with JavaScript execution

    note: 1. javascript must be working in the web console(verification needed)
        2. for asynchronous execution, use execute_async_javascript(javascript, *args)
  """
  command = "return " + javascript
  return driver.execute_script(command, *args)


def execute_async_javascript(javascript, *args):
  """ Asynchronously execute the JavaScript in the current web browser console

    - javascript: pass a string of JavaScript to be executed
    - *args: non-keyworded variable for applicable arguments with JavaScript execution

    Script must explicitly signal it is finished by invoking the provided callback
    This callback is always injected into the executed function as the last argument.
  """
  return driver.execute_async_script(javascript, *args)


def get_element_focused(by, value, pose=0):
  """ Focus on the web element for better visibility
  """
  # get the x-y coordinates of element or none if element does not exist
  position = get_the_element(by, value, pose).location_once_scrolled_into_view
  script = "window.scrollTo(" + str(position["x"]) + ", " + str(position["y"]) + ")"
  execute_javascript(script)

  time.sleep(pose)


def is_element_visible(item, by='id'):
  """  Determine if a given web element is visible on the page
    - by xpath: pass the xpath of element
    - by name:  pass the name of the element
    - by class: pass the name of the class
    - by id:  pass the id of the element(default)

    If cannot find element, it means the element is not visible to the user,
    so generate an exception and return False
  """
  try:
    if "//" in item or by == "xpath":
      elem = driver.find_element_by_xpath(item)
    elif by == "name":
      elem = driver.find_element_by_name(item)
    elif by == "class":
      elem = driver.find_element_by_class_name(item)
    else:
      elem = driver.find_element_by_id(item)
    return elem.is_displayed()
  except Exception as e:
    return False


def handle_exception(exception):
  """ Handle the error during the test execution
    Print out the traceback in the console

    - exception: any error occured
  """
  if auto.is_sauce_used():
    auto.increase_test_failcounts()
  traceback.print_exc()
  raise exception


def debug():
  """ Debug the code with pdb
    Print out variable values wherever set
  """
  global DEBUG
  DEBUG = True
  import pdb
  pdb.set_trace()


def generate_report(suite, testname, format='html'):
  """ Generate test result in text output to console or HTML file

    - suite: test suite
    - testname: only used in HTML output as the file name
    - format: "text" or "html"(default)
  """
  if format == 'text':
    unittest.TextTestRunner(verbosity=2).run(suite)
  else:
    if not os.path.exists('reports'):
      os.mkdir('reports')

    """ if the name of file needs to contain time stamp, uncomment below """
    # test_time = datetime.strftime(datetime.now(), '%Y-%m-%d_%H:%M:%S')
    # test_report = '../reports/' + testname + '_' + test_time + '_.html'

    HtmlTestRunner.HTMLTestRunner(output=testname).run(suite)


def browser_back_and_forward(direction, by, value, pose=0):
  """ Move the web browser backward or forward
    After moving, wait for a specific web element to appear

    - direction: back or forward
    - by: refer comment in wait_for()
    - value: refer comment in wait_for()
  """
  if direction == "back":
    driver.back()
  else:
    driver.forward()
  wait_for(by, value)

  time.sleep(pose)


def search_and_select(by, value, partial_text, text, pose=0):
  """ Select from searchable drop-down menu with partial text

    - by: refer comment in send_text()
    - value: refer comment in send_text()
    - partial_text: used for generating popup list
    - text: actual text used for selection

    * note: searchable drop-down text field is not user-editable element *
  """
  send_text_actionchain(by, value, partial_text)
  try:
    # check the list including the text as available option
    options = get_element_text(by, value, pose)
    if DEBUG:
      print "drop-down menu:  ", options
    assert text in options
  except Exception as e:
    raise Exception(e, "element[@%s=%s] drop-down menu not including [%s]" % (by, value, text))
  click_element_actionchain("xpath", "//*[@%s='%s']//*[text()='%s']" % (by, value, text))

  time.sleep(pose)


def element_context_click(by, value, r_by, r_value, pose=0):
  """ Perform right click on an element to select an option

    - by: attribute of original element
    - value: value of the attribute of original element
    - r_by: attribute of element in the context menu
    - r_value: value of the attribute of element in the context menu
  """
  ActionChains(driver).move_to_element(get_the_element(by, value)).context_click() \
      .move_to_element(get_the_element(r_by, r_value)).click() \
      .perform()

  time.sleep(pose)


def visit_the_website(url, elements, interval=10, pose=0):
  """ Perform visiting a website in the same browser window by tab

    - url: website address to visit
    - elements: dictionary to verify presence/clicking of web element
          - by: the method to check(e.g. "id")
          - value: value for "by"
          - check_for: checking presence or clickable
          - click_demo: True if wanting to click element
          - by_demo: the method to check(e.g. "id")
          - value_demo: value for "by_demo"
          - check_for_demo: checking presence or clickable
          (refer the comments in wait_for())
    - interval: wait time interval for WebDriverWait in wait_for()
  """
  # TODO: research the ActionChains bug to open a new tab
  # ActionChains(driver).key_down(Keys.CONTROL).send_keys("t").key_up(Keys.CONTROL).perform()
  execute_javascript("window.open('" + url + "')")
  driver.switch_to.window(driver.window_handles[-1])
  wait_for(elements["by"], elements["value"], elements["check_for"], interval)
  if elements["click_demo"]:
    click_element(elements["by"], elements["value"])
    wait_for(elements["by_demo"], elements["value_demo"], elements["check_for_demo"], interval)
  time.sleep(pose)  # for display purpose
  execute_javascript("window.close()")
  driver.switch_to.window(driver.window_handles[0])
  # ActionChains(driver).key_down(Keys.CONTROL).send_keys("w").key_up(Keys.CONTROL).perform()


""" api functions """
# def get_screen_shot():
""" get screen shot for HTML report """

# def get_request_summary():
""" get contents of submitted request (eg. leaveslip) """

# def get_report_contents():
""" opens in another window, get the contents and compare with the file """
""" PDF report form, HTML form ? """

# def element_drag_and_drop():

# def element_hovoer_over():
""" condition check if popup message needs to return """

# def open_tab_execute_operations():

# def refresh_current_window():

# def select_date_on_popup_calendar():

# def switch_to_window():

# def alert_handle():

""" page object """
""" note: class method, learn anotation with @ """

# def bible_reading_is_status_set_correctly():

# def upload_file():
