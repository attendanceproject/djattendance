#!/usr/bin/env python2.7

# ----------------------------------------------------------------------------
#
# How to run a script
#   - you can run the script with different webdrivers
#   (refer comments in 'api.initialize_test()' )
#   (eg. python script.py -d chrome -u localhost:8000)
#
#   - -u or --url option cannot take the actual IP address.
#    Hence, use site name and port
#   (ex. -u localhost:8000, not -u 127.0.0.1:8000)
#
# ----------------------------------------------------------------------------

from autotools import djattendance_test_api as api
from datetime import datetime, timedelta

testname = "WebAccessRequestsTest"


inputdata = "data/" + testname + ".json"
with open(inputdata) as data_file:
  data = api.json.load(data_file)
  request = data["request_page"]
  response = data["response_page"]


class DjattendanceAutomation(api.unittest.TestCase):
  @classmethod
  def setUpClass(cls):
    print "setUpClass"
    api.initialize_test(testname)

  def setUp(self):
    print "setUp"

  # @api.unittest.skip("skipping")
  def test_001_log_in(self):
    try:
      api.login(1)
    except Exception as e:
      api.handle_exception(e)

  # @api.unittest.skip("skipping")
  def test_002_menu_web_access_requests(self):
    try:
      api.select_dropdown_menu("text", data["main_menu"], data["sub_menu"], 1)
    except Exception as e:
      api.handle_exception(e)

  # @api.unittest.skip("skipping")
  def test_003_check_title(self):
    try:
      content = api.get_element_text("id", "content")
      for key in data["default_page"]:
        self.assertTrue(data["default_page"][key] in content, "%s is not present in front page" % data["default_page"][key])
    except Exception as e:
      api.handle_exception(e)

  # @api.unittest.skip("skipping")
  def test_004_verify_creating_new_requests(self):
    try:
      # create four reuqests
      req_date = datetime.strftime(api.auto.get_current_date() + timedelta(days=1), "%m/%d/%Y")  # get the current time and +1 day
      for i in range(len(request["reason"])):
        api.click_element("text", data["default_page"]["create_web"])
        api.wait_for("class", "request-form")
        api.click_element("value", request["reason_val"][i])
        api.get_element_focused("id", request["reason_id"])
        api.click_element("value", request["minutes"][i])
        api.get_element_focused("id", request["minutes_id"])
        api.send_text("id", request["expire_id"], req_date)
        api.ActionChains(api.driver).send_keys(api.Keys.ENTER).perform()
        api.time.sleep(1.5)
        # mark as urgent
        if i % 2 == 0:
          api.click_element("id", request["urgent_id"])
        api.send_text("id", request["comment_id"], request["comment"][i], True)
        api.wait_for("link", data["default_page"]["create_web"], "clickable")
    except Exception as e:
      api.handle_exception(e)

  # @api.unittest.skip("skipping")
  def test_005_login_ta_account(self):
    try:
      api.click_element("CSS", data["logout_toggle"])
      api.click_element("xpath", data["logout_button"])
      api.wait_for("link", data["guess_access_title"], "clickable")
      api.log_into_account(api.auto.get_taemail(), api.auto.get_tapassword(), 1)
      api.wait_for_brand()
    except Exception as e:
      api.handle_exception(e)

  # @api.unittest.skip("skipping")
  def test_006_verify_requests_from_ta_account(self):
    try:
      api.select_dropdown_menu("text", data["main_menu"], data["sub_menu"], 1)
      req_date = '{dt:%b}. {dt.day}, {dt.year}'.format(dt=api.auto.get_current_date() + timedelta(days=1))
      request_table = {}
      # verify each content
      for i in range(len(request["reason"])):
        api.click_element("xpath", "//*[@class='panel-heading']//*[contains(text(),'" + request["reason"][i] + "')]")
        api.wait_for("text", response["heading"])
        request_table["Status:"] = response["status_org"]
        request_table["Reason:"] = request["reason"][i]
        request_table["Minutes:"] = request["minutes"][i]
        request_table["Expires on:"] = req_date
        request_table["Comments:"] = request["comment"][i]
        request_table["TA comments:"] = response["ta_comment_org"]
        if i % 2 == 0:
          request_table["Urgent:"] = "True"
        else:
          request_table["Urgent:"] = "False"
        # get the list of value and examine it
        res = api.get_element_text("class", "table").splitlines()
        # print "request_table[web_access]: ", res # debug

        for j, item in enumerate(res):
          if ':' in item:  # table key contains ":"
            item = item.lstrip().rstrip()
            # print res[j+1].lstrip().rstrip(), request_table[item] # debug
            self.assertEqual(res[j + 1].lstrip().rstrip(), request_table[item])

        api.browser_back_and_forward("back", "text", data["default_page"]["title"])

        # mark the request
        ta_response = "//*[@class='panel-heading']//*[contains(text(), '" + request["reason"][i]
        ta_response += "')]/../..//*[@title='" + response["status_title"][i] + "']"
        api.click_element("xpath", ta_response)
        if response["status_title"][i] == "Comment":
          api.send_text("name", response["ta_comment_tag"], response["ta_comment_res"], True)

      api.wait_for_brand()
    except Exception as e:
      api.handle_exception(e)

  # @api.unittest.skip("skipping")
  def test_007_ta_direct_web_access(self):
    try:
      direct_access = data["direct_access"]
      api.click_element("text", direct_access["title"])
      api.wait_for("id", direct_access["mag_id"], "clickable")
      api.send_text("id", direct_access["mag_id"], direct_access["mag_value"])
      api.click_element("id", direct_access["time_id"])
      api.click_element("value", direct_access["time_value"])

      # TODO: bug in direct access
      # api.click_element("value", direct_access["allow_button"])
      # msg = api.get_element_text("class", direct_access["msg_clsname"])
      # self.assertTrue(direct_access["granted_msg"] in msg)

      api.browser_back_and_forward("back", "text", data["default_page"]["title"])
    except Exception as e:
      api.handle_exception(e)

  # @api.unittest.skip("skipping")
  def test_008_login_back_to_trainee(self):
    try:
      api.click_element("CSS", data["logout_toggle"])
      api.click_element("xpath", data["logout_button"])
      api.wait_for("link", data["guess_access_title"], "clickable")
      api.log_into_account(api.auto.get_email(), api.auto.get_password())
      api.wait_for_brand()
    except Exception as e:
      api.handle_exception(e)

  # @api.unittest.skip("skipping")
  def test_009_verify_responses_from_ta(self):
    try:
      api.select_dropdown_menu("text", data["main_menu"], data["sub_menu"], 1)
      reason = request["reason"]

      # verify the response status of each request by hoover over the element
      for i in range(len(reason)):
        xpath = "//*[contains(text(),'" + reason[i] + "')]"
        api.ActionChains(api.driver).move_to_element(api.get_the_element("xpath", xpath)).perform()
        api.time.sleep(1)
    except Exception as e:
      api.handle_exception(e)

  # @api.unittest.skip("skipping")
  def test_010_verify_approved_webaccess(self):
    try:
      # click start web access button
      api.select_dropdown_menu("text", data["main_menu"], data["sub_menu"], 3)      
      xpath = "//*[@title='" + response["approved_title"] + "']"
      api.get_list_elements("xpath", xpath)[0].click()
      api.time.sleep(5)

      # TODO: bug? check the approved message
      # text = api.get_element_text("CSS", data["msg_popup"])
      # self.assertTrue(response["web_granted_msg"] in text, "%s(expected) is not in the string, %s(web)" % (response["web_granted_msg"], text))

      demo_elem = {
          "by": "id",
          "value": "panel1d-heading",
          "check_for": "clickable",
          "click_demo": True,
          "by_demo": "link",
          "value_demo": "Purpose and Goal of the Training",
          "check_for_demo": "clickable",
      }
      api.visit_the_website(response["demo_website"], demo_elem, 3)
    except Exception as e:
      api.handle_exception(e)

  # @api.unittest.skip("skipping")
  def test_011_verify_eShepherding_request(self):
    try:
      # at this point, the page should be still within "Web Access Request"
      shepherding = data["e-shepherding"]
      api.click_element("text", shepherding["title"])
      api.wait_for("id", shepherding["companion_id"], "clickable")
      api.click_element("id", shepherding["submit_id"])
      api.time.sleep(5)

      # TODO: bug? Cannot get the popup message when attempting to start e-shepherding without companion
      # WebDriverWait(self.driver, 10).until(EC.alert_is_present())
      # alert = self.driver.switch_to_alert()

      # open Gamil and attempt to login
      demo_elem = {
          "by": "class",
          "value": "gb_P",
          "check_for": "clickable",
          "click_demo": True,
          "by_demo": "link",
          "value_demo": "SIGN IN",
          "check_for_demo": "clickable",
      }
      api.visit_the_website("http://www.google.com", demo_elem, 3)
    except Exception as e:
      api.handle_exception(e)

  # @api.unittest.skip("skipping")
  def test_012_delete_submitted_request(self):
    try:
      api.select_dropdown_menu("text", data["main_menu"], data["sub_menu"], 1)
      reason = request["reason"]
      delete = data["delete"]

      # verify the response status of each request by hoover over the element
      for i in range(len(reason)):
        xpath = "//*[contains(text(), '" + reason[i] + "')]/../.." \
            + delete["delete_xpath"]
        api.click_element("xpath", xpath)
        api.time.sleep(3)
        api.click_element("xpath", delete["delete_confirm"])
        api.time.sleep(3)
    except Exception as e:
      api.handle_exception(e)

  # @api.unittest.skip("skipping")
  def test_013_verify_request_deleted(self):
    try:
      reason = request["reason"]
      for i in range(len(reason)):
        xpath = "//*[contains(text(), '" + reason[i] + "')]"
        if api.is_element_visible(xpath):
          raise Exception("Trainee web access request is not deleted: %s" % reason[i])
    except Exception as e:
      api.handle_exception(e)

  def tearDown(self):
    print "tearDown"

  @classmethod
  def tearDownClass(cls):
    print "test done"
    if api.auto.is_sauce_used() and api.auto.get_test_failcounts() != 0:
      api.auto.update_saucelab(False)
    api.driver.close()
    api.driver.quit()


if __name__ == '__main__':
  suite = api.unittest.TestLoader().loadTestsFromTestCase(DjattendanceAutomation)

  """ set the format parameter as 'text' to print out the results to console """
  api.generate_report(suite, testname, 'html')
