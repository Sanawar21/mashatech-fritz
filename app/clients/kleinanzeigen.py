import requests
import base64

from xml.etree.ElementTree import fromstring
from xmljson import BadgerFish

from ..models import Ad
from ..utils import KA_USERNAME, KA_PASSWORD


class KleinanzeigenClient:
    URL_PREFIX = 'https://api.kleinanzeigen.de/api'

    def __init__(self):
        headers = {
            'sec-ch-ua': '"Chromium";v="118", "Google Chrome";v="118", "Not=A?Brand";v="99"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'sec-gpc': '1',
            'host': 'api.kleinanzeigen.de',
            'Authorization': self.__basic_auth_encode(KA_USERNAME, KA_PASSWORD),
            'Cookie': '_abck=C3591C451A4DAA07DBA046209B75C443~-1~YAAQFzdlXyfvNjSLAQAAEOUzPgp8O4856ZrV2NTArPhpimHdGPEpDrU0HXYgILICARC0vFNyW0Q6XIfI8dEkAGio7hI5oS86YWpR74QfERkSEFnRxFrtBxyfK0a/gTHJjMb0BVnd++3a6NVwCtMLNbdWiHLFQAF+WcsU7rwVsyxp4bt9GCdvvLrKyZhP9W8H4N2uhdJKFtAbrxT1Ji3qspkTatHNgWAmZeuI2QxaM5gl9l4w2NKDjUj3CBl6bgcnWStslxknVeTJ8xp31Ak7weIEMrOATMDdeocWRaBWei6nNe5zhH+2ZQNi7TO2Wen+ByxfKFz6TpBUjW40idnLLJBJTxieYfTrTgbs6TOgb81mHV33WdqMP4XWJyrBXRTyC/tKODAzfaLAVyyj86TnFA==~-1~-1~-1; bm_sz=5125A3E2B709F14332A433DDBBE33721~YAAQFzdlXyjvNjSLAQAAEOUzPhUMBHEBo9+fVZfAZhEomBJY3EKrmr725IGXqKUPLPHFmqRpeuxq4JMfu5yYibJa9ofpT9IsFjuo6u/suYgUICQV4+NgnFgIm8DPFTQTJQUJZd8QpgQYBlACUcSUU6mOhvcf+kjKp0SKvjG2a16DsHG5fwhTECSScGy7tGDKAgpX8HX6qEHM3Bd09+2whROhiFPKDaX4vbpBVEnmgvmhGP1stxmmfnzOyxtsNyJuuN7jJZEeOOjpRqCO8HDCVOF9lNutm3kReyZGSEw4WxuB5WOYGHx5gmc=~4469814~4272693'
        }

        self._session = requests.session()
        self._session.headers.update(headers)
        self.__previous_1000_ads = []

    def __find_difference(self, list1, list2):
        diff_list = []

        for i in list2:
            if i not in list1:
                diff_list.append(i)

        return diff_list

    def __basic_auth_encode(self, username, password):
        credentials = f"{username}:{password}"
        credentials_bytes = credentials.encode('utf-8')
        base64_credentials = base64.b64encode(
            credentials_bytes).decode('utf-8')
        auth_header = f"Basic {base64_credentials}"
        return auth_header

    def _validate_http_response(self, r):
        if r.status_code < 400:
            return

        # print("Error response body:\n" + r.content.decode('utf-8'))

        if r.status_code == 401:
            raise AttributeError(f'Access Denied {r.status_code}')
        elif r.status_code == 404:
            raise FileNotFoundError(f'Not found {r.status_code}')
        elif r.status_code >= 500:
            raise SystemError(f'Server Error {r.status_code}')

        raise AttributeError(f'Client error {r.text}')

    def __get_json_content(self, response, api_v2: bool = False):
        data = response.json()

        if not api_v2:
            schema_key = [k for k in data.keys() if k.startswith('{http')][0]
            data = data[schema_key]['value']

        return data

    def _http_get(self, url_suffix):
        response = self._session.get(self.URL_PREFIX + url_suffix)
        self._validate_http_response(response)
        return response

    def __http_get_json_content(self, url):
        api_v2 = url.startswith('/v2/')

        return self.__get_json_content(self._http_get(url), api_v2=api_v2)

    def get_public_ads(self, keyword="fritz"):
        r = self._http_get(f"/ads?q={keyword}")
        xml = r.text
        xml = xml.replace("ad:", "")
        xml = xml.replace("types:", "")
        xml = xml.replace("loc:", "")
        xml = xml.replace("attr:", "")
        xml = xml.replace("pic:", "")
        xml = xml.replace("displayoption:", "")
        xml = xml.replace("document:", "")
        xml = xml.replace("feat:", "")
        xml = xml.replace("cat:", "")
        xml = xml.replace("payment:", "")
        xml = xml.replace("media:", "")

        bf = BadgerFish(dict_type=dict)
        content = bf.data(fromstring(xml))
        return content

    def get_ad(self, id) -> Ad:
        url = f'/ads/{id}.json'
        return Ad(self.__http_get_json_content(url))

    def get_view_count(self, id: int):
        """
        Retrieves the view count.

        :param id: Ad ID.
        :type id: int
        :return: How many impressions this add has.
        :rtype: int
        """
        url = f'/v2/counters/ads/vip/{id}.json'

        return self.__http_get_json_content(url)['value']

    def get_fritz_ads(self):
        to_return = []

        keywords = ["fritz", "fritzbox", "fritz%21box"]

        for keyword in keywords:
            try:
                ads = self.get_public_ads(keyword=keyword)
                ads = ads["ads"]["ad"]
                fresh_ads = [ad["@id"] for ad in ads]
                new_ads = self.__find_difference(
                    self.__previous_1000_ads, fresh_ads)

                self.__previous_1000_ads.extend(new_ads)
                self.__previous_1000_ads = self.__previous_1000_ads[len(
                    self.__previous_1000_ads) - 1000:]

                for id in new_ads:

                    try:
                        ad = self.get_ad(id)
                    except FileNotFoundError:
                        continue

                    ad_dict = ad.as_dict()
                    to_return.append(ad_dict)
            except Exception:
                pass

        return to_return
