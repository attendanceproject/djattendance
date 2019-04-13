from itertools import chain

from .models import IndividualSlip, GroupSlip

def find_next_leaveslip(current_ls):
  individual = IndividualSlip.objects.raw('''
    SELECT i_s.id, min(a_r.date) AS min_date
    FROM leaveslips_individualslip AS i_s
    JOIN leaveslips_individualslip_rolls AS is_r
    ON i_s.id = is_r.individualslip_id
    JOIN attendance_roll AS a_r
    ON is_r.roll_id = a_r.id
    JOIN terms_term AS t_t
    ON t_t.start < a_r.date
    WHERE (i_s.status = 'P' OR i_s.status = 'S') AND i_s."TA_id" = {} AND t_t.current = 't'
    GROUP BY i_s.id
    ORDER BY min_date ASC
    LIMIT 2;'''.format(current_ls.TA.id))
  group = GroupSlip.objects.filter(status__in=['P', 'S'], TA=current_ls.TA).order_by('start')[:2]
  # slip.get_date() is expensive so don't call this function too much
  both = sorted(chain(group, individual), key=lambda slip: slip.get_date())
  for slip in both:
    if slip == current_ls:
      continue
    return slip
