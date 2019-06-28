class Stash():
  def __init__(self):
    self.__attendance_report_records = list()
    self.__teams = list()
    self.__localities = list()
    self.__headers = list()
    self.__averages = dict()

  def set_records(self, item):
    self.__attendance_report_records = item

  def append_records(self, item):
    self.__attendance_report_records.append(item)
    return self.__attendance_report_records

  def get_records(self):
    return self.__attendance_report_records

  def set_teams(self, item):
    self.__teams = item

  def get_teams(self):
    return self.__teams

  def set_localities(self, item):
    self.__localities = item

  def get_localities(self):
    return self.__localities

  def set_headers(self, item):
    self.__headers = item

  def get_headers(self):
    return self.__headers

  def get_averages(self):
    if not self.__averages:
      for header in self.__headers:
        self.__averages.setdefault(header, 0)

      for record in self.__attendance_report_records:
        for header in self.__headers:
          val = record[header]
          self.__averages[header] = self.__averages[header] + float(val[:-1])

      for header in self.__headers:
        self.__averages[header] = round(self.__averages[header] / len(self.__attendance_report_records), 2)

    return self.__averages
