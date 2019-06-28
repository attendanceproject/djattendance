HELP_TEXT = """
  Do not duplicate names! Do not use the following terms as a name:<br>
  <ul>
    <li> text </li>
    <li> destinations </li>
    <li> airports </li>
    <li> airlines </li>
    <li> date </li>
    <li> datetime </li>
  </ul>
"""

IATA_API_KEY = "dd806ddd-1f57-4ca0-866b-d44087df1f59"

ANSWER_TYPES = ['destinations', 'text', 'date', 'datetime', 'airports', 'airlines', 'None']

SHOW_TYPES = ['SHOW', 'HIDE', 'READ ONLY', '']

SHOW_CHOICES = [(x, x) for x in SHOW_TYPES]

DESTINATION_FIELDS = ['trainee_contacts', 'finance_coords', 'media_coords', 'stat_coords']
