import unittest
import xmltodict

import zillow


class TestGetSearchResult(unittest.TestCase):

    def test_get_region_children(self):

        with open('./testdata/get_region_children.xml', 'r') as f:
            RAW_XML = ''.join(f.readlines())

        xml_data = xmltodict.parse(RAW_XML)
        regions_data = zillow.NeighborhoodApi._parse_out_regions(xml_data)

        self.assertEqual(regions_data['regions'][0].region_name, 'Alki')
        self.assertEqual(regions_data['regions'][0].zindex['#text'], '537360')
