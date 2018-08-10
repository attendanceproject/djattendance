# Room Reservation program to be used on csv file with fields: ID, timestamp, date, time, roomID, content (as in attendance.ftta.lan db)
from datetime import *
from django.core.management.base import BaseCommand
from room_reservations.models import RoomReservation
from rooms.models import Room
from accounts.models import User
import os


class Command(BaseCommand):
  # to use: python ap/manage.py rr_script --settings=ap.settings.dev

  def roomlist(self):
    return {"26": "MC", "45": "NE3", "92": "SW120", "93": "NW201", "94": "NE209", "95": "NE210",
            "96": "NE212", "97": "NE213", "98": "NE215", "99": "NE216", "100": "NE217", "101": "NE218",
            "102": "NE219", "103": "NE220", "104": "NE221", "105": "NE222", "106": "NE223", "107": "NE224",
            "108": "NE225", "109": "SE238", "110": "SE239", "111": "SE240", "112": "SE241", "113": "SE242",
            "114": "SE243", "115": "SE244", "116": "SE245", "117": "NW108", "119": "SW227", "120": "SE131",
            "121": "SW229", "122": "SE132", "124": "SE133"}

  def read_file(self, file_name):
    if file_name == '':
      file_name = os.path.expanduser('~/workspace/djattendance/ap/room_reservations/management/commands/roomschedule.csv')
    current = open(file_name, 'r')
    result = current.read().split('\n')
    current.close()
    return result

  def parse(self, csv):
    result = []
    for each in csv:
      temp = []
      for part in each.split(','):
        temp.append(part.strip('"'))
      result.append(temp)
    return result

  def get_id(self, event):
    return event[0]

  def get_timestamp(self, event):
    if type(event[1]) == datetime:
      return event[1]
    timestamp = event[1].split(' ')
    date = timestamp[0].split('-')
    time = timestamp[1].split(':')
    return datetime(int(date[0]), int(date[1]), int(date[2]), int(time[0]), int(time[1]), int(time[2]))

  def get_date(self, event):
    if type(event[2]) == date:
      return event[2]
    dates = event[2].split('-')
    return date(int(dates[0]), int(dates[1]), int(dates[2]))

  def get_time(self, event):
    if len(event[3]) == 2:
      return event[3]
    hour = event[3].split(':')
    return datetime(1, 1, 1, int(hour[0]), int(hour[1]))

  def get_room(self, event):
    return event[4]

  def get_content(self, event):
    return event[5]

  def check_continuous(self, event1, event2):
    return (int(self.get_id(event1)) == int(self.get_id(event2)) - 1 and
            self.get_date(event1) == self.get_date(event2) and
            self.get_time(event1) == self.get_time(event2) - timedelta(0, 1800) and
            self.get_room(event1) == self.get_room(event2) and
            self.get_content(event1) == self.get_content(event2))

  def get_continuous(self, index, data):
    new = len(data)
    event = data[index]
    start_time = self.get_time(event)
    current = event
    for now in range(index + 1, len(data)):
      new = now
      other = data[now]
      if self.check_continuous(current, other):
        current = other
      else:
        break
    end_time = self.get_time(current) + timedelta(0, 1800)
    # return the index of the last part of the event
    return new, (start_time.hour, start_time.minute), (end_time.hour, end_time.minute)

  def check_repeat(self, event1, event2):
    return (self.get_date(event1) == self.get_date(event2) - timedelta(7) and
            self.get_time(event1) == self.get_time(event2) and
            self.get_room(event1) == self.get_room(event2) and
            self.get_content(event1) == self.get_content(event2))

  # Add 175 days for the Fall 2018 Term
  def get_repeat(self, index, data):
    new = len(data)
    event = data[index]
    start_date = self.get_date(event)
    current = event
    for now in range(index + 1, len(data)):
      new = now
      other = data[now]
      if self.check_repeat(current, other):
        current = other
      else:
        break
    end_date = self.get_date(current)
    frequency = 'Once'
    if start_date != end_date:
      frequency = 'Term'
    return new, start_date + timedelta(175), end_date + timedelta(175), frequency

  def merge_continuous(self, data):
    result = []
    all_index = len(data)
    i = 0
    while i < all_index:
      event = self.get_continuous(i, data)
      result.append((self.get_id(data[i]), self.get_timestamp(data[i]), self.get_date(data[i]), event[1:], self.get_room(data[i]), self.get_content(data[i])))
      i = event[0]
    return result

  def merge_repeat(self, data):
    result = []
    all_index = len(data)
    i = 0
    while i < all_index:
      event = self.get_repeat(i, data)
      result.append((self.get_id(data[i]), event[1:], self.get_time(data[i]), self.get_room(data[i]), self.get_content(data[i])))
      i = event[0]
    return result

  def delete_blank(self, data):
    result = []
    current = self.get_id(data[0])
    delete = []
    for i in range(0, len(data)):
      if len(data[i]) != 6 or data[i][3] == '' or self.get_id(data[i]) == current:
        delete.append(i)
      else:
        current = self.get_id(data[i])
    for j in range(len(data)):
      if j not in delete:
        result.append(data[j])
    return result

  def stop(self):
    if raw_input('Press Enter. ').lower() == 'quit':
      exit()

  def get_Term_events(self, data):
    result = []
    for i in data:
      if i[1][-1] == 'Term':
        result.append(i)
    return result

  def tuple_to_time(self, tup):
    return time(tup[0], tup[1])

  def save_rr(self, event):
    rl = self.roomlist()
    dt = datetime(2018, 8, 13)
    td = event[1][0]
    starts = self.tuple_to_time(event[2][0])
    ends = self.tuple_to_time(event[2][1])
    room_code = rl[event[3]]
    gp = event[4]
    freq = 'Term'
    # print dt, td, starts, ends, room_code, gp, freq
    res = RoomReservation(requester=User.objects.get(email="jerome@ftta.org"), submitted=dt, last_modified=dt, finalized=dt, date=td, start=starts, end=ends, room=Room.objects.get(code=room_code), group=gp, frequency=freq, status='A', reason='None')
    res.save()

  def handle(self, *args, **options):
    gold = self.get_Term_events(self.merge_repeat(self.merge_continuous(self.delete_blank(self.parse(self.read_file(raw_input("File name: ")))))))
    print('* Populating room reservation...')
    for i in gold:
      self.save_rr(i)
