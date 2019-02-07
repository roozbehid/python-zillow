import xmltodict

from .error import ZillowError
from .result_fields import Place
from .result_fields import Region

from .url_utils import request_url


class ValuationApi(object):
    """
    A python interface into the Zillow Valuation API
    By default, the Api caches results for 1 minute.
    Example usage:
      To create an instance of the zillow.ValuationApi class:
        >>> import zillow
        >>> api = zillow.ValuationApi()

    All available methods include:
        >>> data = api.GetSearchResults("<your key here>", "<your address here>", "<your zip here>")
    """

    def __init__(self):
        self._base_url = "https://www.zillow.com/webservice"
        self._input_encoding = None
        self._request_headers = None

    @property
    def base_url(self):
        return self._base_url

    def GetSearchResults(self, zws_id, address, citystatezip, rentzestimate=False):
        """
        The GetSearchResults API finds a property for a specified address.
        The content returned contains the address for the property or properties as
        well as the Zillow Property ID (ZPID) and current Zestimate. It also includes
        the date the Zestimate was computed, a valuation range and the Zestimate
        ranking for the property within its ZIP code. The GetSearchResults API Web
        Service is located at: http://www.zillow.com/webservice/GetSearchResults.htm

        :param zws_id: The Zillow Web Service Identifier. Each subscriber to
            Zillow Web Services is uniquely identified by an ID sequence and every
            request to Web services requires this ID.
        :param address: The address of the property to search. This string
            should be URL encoded.
        :param citystatezip: The city+state combination and/or ZIP code for which to
            search. This string should be URL encoded. Note that giving both city and
            state is required. Using just one will not work.
        :param retnzestimat: Return Rent Zestimate information if available
            (boolean true/false, default: false)
        :return:
        """
        url = '%s/GetSearchResults.htm' % (self._base_url)
        parameters = {'zws-id': zws_id}
        if address and citystatezip:
            parameters['address'] = address
            parameters['citystatezip'] = citystatezip
        else:
            raise ZillowError({'message': "Specify address and citystatezip."})
        if rentzestimate:
            parameters['rentzestimate'] = 'true'

        resp = request_url(url, 'GET', data=parameters)
        data = resp.content.decode('utf-8')

        xmltodict_data = xmltodict.parse(data)

        place = Place()
        try:
            place.set_data(xmltodict_data['SearchResults:searchresults']['response']['results']['result'])
        except Exception:
            raise ZillowError({'message': "Zillow did not return a valid response: %s" % data})

        return place

    def GetZEstimate(self, zws_id, zpid, rentzestimate=False):
        """
        The GetZestimate API will only surface properties for which a Zestimate exists.
        If a request is made for a property that has no Zestimate, an error code is returned.
        Zillow doesn't have Zestimates for all the homes in its database.
        For such properties, we do have tax assessment data, but that is not provided through the API.
        For more information, see our Zestimate coverage.
        :zws_id: The Zillow Web Service Identifier.
        :param zpid: The address of the property to search. This string should be URL encoded.
        :param rentzestimate: Return Rent Zestimate information if available (boolean true/false, default: false)
        :return:
        """
        url = '%s/GetZestimate.htm' % (self._base_url)
        parameters = {'zws-id': zws_id,
                      'zpid': zpid}
        if rentzestimate:
            parameters['rentzestimate'] = 'true'

        resp = request_url(url, 'GET', data=parameters)
        data = resp.content.decode('utf-8')

        xmltodict_data = xmltodict.parse(data)

        place = Place()
        try:
            place.set_data(xmltodict_data.get('Zestimate:zestimate', None)['response'])
        except Exception:
            raise ZillowError({'message': "Zillow did not return a valid response: %s" % data})

        return place

    def GetDeepSearchResults(self, zws_id, address, citystatezip, rentzestimate=False):
        """
        The GetDeepSearchResults API finds a property for a specified address.
        The result set returned contains the full address(s), zpid and Zestimate
        data that is provided by the GetSearchResults API.  Moreover, this API call
        also gives rich property data like lot size, year built, bath/beds, last
        sale details etc.

        :zws_id: The Zillow Web Service Identifier.
        :param address: The address of the property to search. This string
            should be URL encoded.
        :param citystatezip: The city+state combination and/or ZIP code
            for which to search.
        :param retnzestimate: Return Rent Zestimate information if available
            (boolean true/false, default: false)
        :return:

        Example:
        """
        url = '%s/GetDeepSearchResults.htm' % (self._base_url)
        parameters = {'zws-id': zws_id,
                      'address': address,
                      'citystatezip': citystatezip
                      }

        if rentzestimate:
            parameters['rentzestimate'] = 'true'

        resp = request_url(url, 'GET', data=parameters)
        data = resp.content.decode('utf-8')

        xmltodict_data = xmltodict.parse(data)

        place = Place(has_extended_data=True)
        try:
            place.set_data(xmltodict_data.get('SearchResults:searchresults', None)['response']['results']['result'])
        except Exception:
            raise ZillowError({'message': "Zillow did not return a valid response: %s" % data})

        return place

    def GetDeepComps(self, zws_id, zpid, count=10, rentzestimate=False):
        """
        The GetDeepComps API returns a list of comparable recent sales for
        a specified property.
        The result set returned contains the address, Zillow property identifier, and
        Zestimate for the comparable properties and the principal property for which
        the comparables are being retrieved.
        This API call also returns rich property data for the comparables.

        :param zws_id: The Zillow Web Service Identifier.
        :param zpid: The address of the property to search. This string should be URL encoded.
        :param count: The number of comparable recent sales to obtain (integer between 1 and 25)
        :param rentzestimate: Return Rent Zestimate information if available (boolean true/false, default: false)
        :return:
        Example
            >>> data = api.GetDeepComps("<your key here>", 2100641621, 10)
        """
        url = '%s/GetDeepComps.htm' % (self._base_url)
        parameters = {'zws-id': zws_id,
                      'zpid': zpid,
                      'count': count}
        if rentzestimate:
            parameters['rentzestimate'] = 'true'

        resp = request_url(url, 'GET', data=parameters)
        data = resp.content.decode('utf-8')

        # transform the data to an dict-like object
        xmltodict_data = xmltodict.parse(data)

        # get the principal property data
        principal_place = Place()
        principal_data = xmltodict_data.get('Comps:comps')['response']['properties']['principal']

        try:
            principal_place.set_data(principal_data)
        except Exception:
            raise ZillowError({'message': 'No principal data found: %s' % data})

        # get the comps property_data
        comps = xmltodict_data.get('Comps:comps')['response']['properties']['comparables']['comp']

        comp_places = []
        for datum in comps:
            place = Place()
            try:
                place.set_data(datum)
                comp_places.append(place)
            except Exception:
                raise ZillowError({'message': 'No valid comp data found %s' % datum})

        output = {
            'principal': principal_place,
            'comps': comp_places
        }

        return output

    def GetComps(self, zws_id, zpid, count=25, rentzestimate=False):
        """
        The GetComps API returns a list of comparable recent sales for a specified property.
        The result set returned contains the address, Zillow property identifier, and Zestimate
        for the comparable properties and the principal property for which the comparables
        are being retrieved.

        :param zpid: The address of the property to search. This string should be URL encoded.
        :param count: The number of comparable recent sales to obtain (integer between 1 and 25)
        :param rentzestimate: Return Rent Zestimate information if available (boolean true/false, default: false)
        :return:
        """
        url = '%s/GetComps.htm' % (self._base_url)
        parameters = {'zws-id': zws_id,
                      'zpid': zpid,
                      'count': count}
        if rentzestimate:
            parameters['rentzestimate'] = 'true'

        resp = request_url(url, 'GET', data=parameters)
        data = resp.content.decode('utf-8')

        # transform the data to an dict-like object
        xmltodict_data = xmltodict.parse(data)

        # get the principal property data
        principal_place = Place()
        principal_data = xmltodict_data.get('Comps:comps')['response']['properties']['principal']

        try:
            principal_place.set_data(principal_data)
        except Exception:
            raise ZillowError({'message': 'No principal data found: %s' % data})

        # get the comps property_data
        comps = xmltodict_data.get('Comps:comps')['response']['properties']['comparables']['comp']

        comp_places = []
        for datum in comps:
            place = Place()
            try:
                place.set_data(datum)
                comp_places.append(place)
            except Exception:
                raise ZillowError({'message': 'No valid comp data found %s' % datum})

        output = {
            'principal': principal_place,
            'comps': comp_places
        }

        return output


class NeighborhoodApi(object):
    """
    A python interface into the Zillow Neighborhood API
    Example usage:
      To create an instance of the zillow.NeighborhoodApi class:
        >>> import zillow
        >>> api = zillow.NeighborhoodApi()

    """

    def __init__(self):
        self._base_url = "https://www.zillow.com/webservice"

    @property
    def base_url(self):
        return self._base_url

    @staticmethod
    def _parse_out_regions(xml_response):
        def _create_region(data):
            region = Region()
            region.set_data(data)
            return region

        region_data = xml_response['RegionChildren:regionchildren']['response']['list']['region']
        regions = []
        try:
            for datum in region_data:
                regions.append(_create_region(datum))
        except Exception:
            raise ZillowError({'message': 'No valid comp data found %s' % datum})

        return {'regions': regions}

    def GetRegionChildren(self, zws_id, **kwargs):
        """
        For a specified region, the GetRegionChildren API returns a list of
        subregions with the following information:
            * Subregion Type
            * Region IDs
            * Region Names
            * URL to Corresponding Zillow Page (only for cities and neighborhoods)
            * Latitudes and Longitudes

        :param zws_id: The Zillow Web Service Identifier. Each subscriber to Zillow
            Web Services is uniquely identified by an ID sequence and every request
            to Web services requires this ID. Click here to get yours.	Yes
        :param region_id: The regionId of the region to retrieve subregions from.
            Either region_id or state must be passed.
        :param state: The state of the region to retrieve subregions from.
            Either region_id or state must be passed.
        :param county: The county of the region to retrieve subregions from.
        :param city: The city of the region to retrieve subregions from.
        :param childtype: The type of subregions to retrieve
            (available types: state, county, city, zipcode, and neighborhood).
        :return:

        Example:
        """
        kwarg_mappings = {
            'regionId': 'region_id',
            'state': 'state',
            'county': 'county',
            'city': 'city',
            'childtype': 'childtype',
        }

        if len(set(kwargs.keys()) & {'region_id', 'state'}) != 1:
            raise ValueError("One keyword argument of 'region_id' or "
                             "'state' is required")

        url = '%s/GetRegionChildren.htm' % (self._base_url)
        parameters = dict(
            [(zapi_arg, kwargs[f_arg])
             for zapi_arg, f_arg in kwarg_mappings.items()
             if f_arg in kwargs])
        parameters['zws-id'] = zws_id

        resp = request_url(url, 'GET', data=parameters)
        data = resp.content.decode('utf-8')

        xmltodict_data = xmltodict.parse(data)
        return self._parse_out_regions(xmltodict_data)
