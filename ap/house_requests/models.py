from django.db import models
from django.core.urlresolvers import reverse

from houses.models import House, Room
from aputils.utils import RequestMixin
from accounts.models import User


class HouseRequest(models.Model, RequestMixin):
  class Meta:
    abstract = True

  STATUS = (
      ('C', 'Work Order Created'),
      ('P', 'Pending'),
      ('F', 'Marked for Fellowship'),
  )

  status = models.CharField(max_length=1, choices=STATUS, default='P')
  date_requested = models.DateTimeField(auto_now_add=True)
  trainee_author = models.ForeignKey(User, null=True, on_delete=models.SET_NULL)
  TA_comments = models.TextField(null=True, blank=True)
  house = models.ForeignKey(House, on_delete=models.SET_NULL, null=True)

  def get_category(self):
    return self.type + ' - ' + str(self.house)

  def get_status(self):
    return self.get_status_display()

  def get_date_created(self):
    return self.date_requested

  def get_trainee_requester(self):
    return self.trainee_author

  @staticmethod
  def get_button_template():
    return 'request_list/buttons.html'

  @staticmethod
  def get_ta_button_template():
    return 'request_list/ta_buttons.html'


class MaintenanceRequest(HouseRequest, models.Model):
  type = 'Maintenance'
  description = models.TextField()
  urgent = models.BooleanField(default=False)
  room = models.ForeignKey(Room, null=True, blank=True, on_delete=models.SET_NULL)

  request_types = (
      ('AIR', 'Air - Includes issues related to air conditioning, air filters, condensation, heating, thermostats, and ventilation.'),
      ('APPL', 'Appliances - Includes issues related to refrigerators, ranges, ovens, dishwashers, microwaves, washers, and dryers.'),
      ('BLIND', 'Blinds/curtains - Includes issues related to brackets, drapery, head rails, roller shades, valances, vanes, and wands.'),
      ('CARP', 'Carpentry - Includes issues related to cabinetry, drawers, drawer handles, handrails, refinishing, and rot.'),
      ('DOOR', 'Doors - Includes issues related to door frames, hinges, knobs, locks, and rubber sweeps for interior doors, patio doors, shower doors, screen doors, etc.'),
      ('ELECT', 'Electrical - Includes issues related to electrical outlets, extension cords, light switches, and power interruptions.'),
      ('FLOOR', 'Flooring - Includes issues related to baseboards, carpeting, floor tiles, hardwood flooring, laminate flooring, and vinyl flooring.'),
      ('FURN', 'Furniture - Includes issues related to replacing bed frames, bookshelves, chairs, couches, couch cushions, desks, dressers, lamps, lamp shades, mattresses, nightstands, shoe racks, tables, and wardrobes. See Carpentry for repairing drawers and drawer handles. Requests for alternate bed frames and mattresses must first be fellowshipped with Jerome Keh; reasons for request must be substantial and related to a medical need.'),
      ('LAND', 'Landscaping'),
      ('LIGHT', 'Lights - Includes issues related to ballasts, ceiling lights, ceiling fan light bulbs, diffusers, and lenses. See Furniture for lamps and lamp shades. See Electrical for electrical outlets.'),
      ('OTHER', 'Other'),
      ('PAINT', 'Paint'),
      ('PESTS', 'Pests'),
      ('PLUMB', 'Plumbing - Includes issues related to bathtubs, clogs, drains, faucets, garbage disposers, leaks, showers, sinks, toilets, water heaters, and water pressure.'),
      ('ROOF', 'Roof - Includes issues related to leaks.'),
      ('TOWEL', 'Towel bars'),
      ('WIND', 'Windows - Includes issues related to locks, panes, privacy films, screens, and window frames.'),
  )

  request_type = models.CharField(max_length=5, choices=request_types)

  @staticmethod
  def get_create_url():
    return reverse('house_requests:maintenance-request')

  def get_absolute_url(self):
    return reverse('house_requests:maintenance-detail', kwargs={'pk': self.id})

  def get_update_url(self):
    return reverse('house_requests:maintenance-update', kwargs={'pk': self.id})

  def get_delete_url(self):
    return reverse('house_requests:maintenance-delete', kwargs={'pk': self.id})

  @staticmethod
  def get_detail_template():
    return 'maintenance/description.html'

  @staticmethod
  def get_table_template():
    return 'maintenance/table.html'

  @staticmethod
  def get_report():
    return reverse('house_requests:maintenance-report')


class LinensRequest(HouseRequest, models.Model):
  type = 'Linens'
  quantity = models.PositiveSmallIntegerField()

  request_types = (
      ('BAM', 'Bath Mat'),
      ('BLT', 'Blanket'),
      ('CMP', 'Cloth Matress Pad'),
      ('COM', 'Comforter'),
      ('DRM', 'Door Mat'),
      ('FMP', 'Foam Matress Pad'),
      ('FFS', 'Full Fitted Sheet'),
      ('FFLS', 'Full Flat Sheet'),
      ('IBC', 'Ironing Board Cover'),
      ('KFS', 'King Fitted Sheet'),
      ('KFLS', 'King Flat Sheet'),
      ('LSC', 'Love Seat Cover'),
      ('PLW', 'Pillow'),
      ('PLWC', 'Pillow Case'),
      ('QFS', 'Queen Fitted Sheet'),
      ('QFLS', 'Queen Flat Sheet'),
      ('SHC', 'Shower Curtain'),
      ('SHR', 'Shower Curtain Ring'),
      ('SCC', 'Single Couch Cover'),
      ('SLB', 'Sleeping Bag'),
      ('TBC', 'Tablecloth'),
      ('TWL', 'Towel'),
      ('TSCC', 'Triple Seat Couch Cover'),
      ('TFS', 'Twin Fitted Sheet'),
      ('TFLS', 'Twin Flat Sheet'),
      ('WSC', 'Washcloth')
  )

  request_type = models.CharField(max_length=5, choices=request_types)

  request_reasons = (
      ('STD', 'Stained'),
      ('RWO', 'Ragged/Worn Out'),
      ('TRN', 'Torn'),
      ('MMP', 'Missing/Misplaced'),
      ('OTR', 'Other')
  )

  request_reason = models.CharField(max_length=3, choices=request_reasons)

  @staticmethod
  def get_create_url():
    return reverse('house_requests:linens-request')

  def get_absolute_url(self):
    return reverse('house_requests:linens-detail', kwargs={'pk': self.id})

  def get_update_url(self):
    return reverse('house_requests:linens-update', kwargs={'pk': self.id})

  def get_delete_url(self):
    return reverse('house_requests:linens-delete', kwargs={'pk': self.id})

  @staticmethod
  def get_detail_template():
    return 'linens/description.html'

  @staticmethod
  def get_table_template():
    return 'linens/table.html'


class FramingRequest(HouseRequest, models.Model):
  type = 'Framing'
  location = models.TextField()
  frame = models.TextField()
  approved = models.BooleanField()
  frame_already_there = models.BooleanField()

  @staticmethod
  def get_create_url():
    return reverse('house_requests:framing-request')

  def get_absolute_url(self):
    return reverse('house_requests:framing-detail', kwargs={'pk': self.id})

  def get_update_url(self):
    return reverse('house_requests:framing-update', kwargs={'pk': self.id})

  def get_delete_url(self):
    return reverse('house_requests:framing-delete', kwargs={'pk': self.id})

  @staticmethod
  def get_detail_template():
    return 'framing/description.html'

  @staticmethod
  def get_table_template():
    return 'framing/table.html'
