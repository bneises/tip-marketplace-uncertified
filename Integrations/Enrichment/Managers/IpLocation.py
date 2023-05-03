import requests
import geocoder
from urllib.parse import quote
import json
class IpLocation(object):
    """
    Model for storing location of given IP address.
    This class provides the following attributes:
    .. attribute:: ip_address
      IP address.
    .. attribute:: city
      City where IP address is located.
    .. attribute:: region
      Region where IP address is located.
    .. attribute:: country
      Country where IP address is located (two letters country code).
    .. attribute:: latitude
      Latitude where IP address is located.
    .. attribute:: longitude
      Longitude where IP address is located.
    """

    _ip_address = None
    _city = None
    _region = None
    _country = None
    _latitude = None
    _longitude = None

    def __init__(self, ip_address, city=None, region=None, country=None,
                 latitude=None, longitude=None):
        self.ip_address = ip_address
        self.city = city
        self.region = region
        self.country = country
        self.latitude = latitude
        self.longitude = longitude

    @property
    def ip_address(self):
        return self._ip_address

    @ip_address.setter
    def ip_address(self, value):
        self._ip_address = value

    @property
    def city(self):
        return self._city

    @city.setter
    def city(self, value):
        self._city = value

    @property
    def region(self):
        return self._region

    @region.setter
    def region(self, value):
        self._region = value

    @property
    def country(self):
        return self._country

    @country.setter
    def country(self, value):
        self._country = value

    @property
    def latitude(self):
        return self._latitude

    @latitude.setter
    def latitude(self, value):
        self._latitude = value

    @property
    def longitude(self):
        return self._longitude

    @longitude.setter
    def longitude(self, value):
        self._longitude = value

    def to_json(self):
        return json.dumps(self.__dict__).replace('"_', '"')


    def to_csv(self, delimiter):
        return delimiter.join(self.__str__().split('\n'))

    def __str__(self):
        return '{ip_address}\n{city}\n{region}\n{country}\n{latitude}\n{longitude}'.format(
            ip_address=self.ip_address,
            city=self.city,
            region=self.region,
            country=self.country,
            latitude=self.latitude,
            longitude=self.longitude)

    def __repr__(self):
        return '{module}.{class_name}({data})'.format(
            module=self.__module__,
            class_name=self.__class__.__name__,
            data=self.ip_address)
            
class DbIpCity():
    """
    Class for accessing geolocation data provided by https://db-ip.com/api/.
    """

    @staticmethod
    def get(ip_address, api_key='free', db_path=None, username=None, password=None):
        # process request
        try:
            request = requests.get('https://api.db-ip.com/v2/'
                                   + quote(api_key)
                                   + '/' + quote(ip_address),
                                   timeout=62)
        except:
            raise
        
        # check for HTTP errors
        if request.status_code != 200:
            raise

        # parse content
        try:
            content = request.content.decode('utf-8')
            content = json.loads(content)
        except:
            raise

        # check for errors
        if content.get('error'):
            if content['error'] == 'invalid address':
                raise 
            elif content['error'] == 'invalid API key':
                raise 
            else:
                raise 
        # prepare return value
        
        ip_location = IpLocation(ip_address)
        
        # format data
        ip_location.country = content.get('countryCode')
        ip_location.region = content.get('stateProv')
        ip_location.city = content.get('city')

        # get lat/lon from OSM
        osm = geocoder.osm(content.get('city', '') + ', '
                           + content.get('stateProv', '') + ' '
                           + content.get('countryCode', ''),
                           timeout=62)
        if osm.ok:
            osm = osm.json
            ip_location.latitude = float(osm['lat'])
            ip_location.longitude = float(osm['lng'])
        else:
            osm = geocoder.osm(content.get('city', '') + ', ' + content.get('countryCode', ''), timeout=62)
            if osm.ok:
                osm = osm.json
                ip_location.latitude = float(osm['lat'])
                ip_location.longitude = float(osm['lng'])
            else:
                ip_location.latitude = None
                ip_location.longitude = None
        return ip_location