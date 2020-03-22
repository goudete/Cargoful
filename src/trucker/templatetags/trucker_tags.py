from django import template
import googlemaps

register = template.Library()

@register.filter(is_safe=True)
def reverse_geo_pickup(order):
    gmaps = googlemaps.Client(key='AIzaSyCKmjFt91GOvHaqyxpoiiqFQURjFST7U2I')
    reverse_geo = gmaps.reverse_geocode((order.pickup_latitude, order.pickup_longitude))
    addy = reverse_geo[0]['formatted_address']
    return addy

@register.filter(is_safe=True)
def reverse_geo_delivery(order):
    gmaps = googlemaps.Client(key='AIzaSyCKmjFt91GOvHaqyxpoiiqFQURjFST7U2I')
    reverse_geo = gmaps.reverse_geocode((order.delivery_latitude, order.delivery_longitude))
    addy = reverse_geo[0]['formatted_address']
    return addy
