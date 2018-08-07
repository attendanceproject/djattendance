class Stash():
  def __init__(self):
    self.__attendance_report_records = list()
    self.__teams = list()
    self.__localities = list()

  def set_records(self, item):
    self.__attendance_report_records = item
    return self.__attendance_report_records

  def append_records(self, item):
    self.__attendance_report_records.append(item)
    return self.__attendance_report_records

  def get_records(self):
    return self.__attendance_report_records

  def set_teams(self, item):
    self.__teams = item
    return self.__teams

  def get_teams(self):
    return self.__teams

  def set_localities(self, item):
    self.__localities = item
    return self.__localities

  def get_localities(self):
    return self.__localities
