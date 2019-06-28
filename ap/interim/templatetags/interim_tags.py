from django import template

register = template.Library()

@register.filter(name='itinerary_length_in_days')
def itinerary_length_in_days(istart, iend):
	return (iend - istart).days + 1
