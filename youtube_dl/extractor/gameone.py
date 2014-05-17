# coding: utf-8
from __future__ import unicode_literals

import re
import xml.etree.ElementTree as ET

from .common import InfoExtractor
from ..utils import xpath_with_ns

NAMESPACE_MAP = {
    'media': 'http://search.yahoo.com/mrss/',
}

# URL prefix to download the mp4 files directly instead of streaming via rtmp
# Credits go to XBox-Maniac http://board.jdownloader.org/showpost.php?p=185835&postcount=31 
RAW_MP4_URL = 'http://cdn.riptide-mtvn.com/'

class GameOneIE(InfoExtractor):
    _VALID_URL = r'https?://(?:www\.)?gameone\.de/tv/(?P<id>\d+)'
    _TEST = {
        'url': 'http://www.gameone.de/tv/288',
        'md5': '136656b7fb4c9cb4a8e2d500651c499b',
        'info_dict': {
            'id': '288',
            'ext': 'mp4',
            'title': 'Game One - Folge 288',
            'duration': 1238,
            'thumbnail': 'http://s3.gameone.de/gameone/assets/video_metas/teaser_images/000/643/636/big/640x360.jpg',
            'description': 'Puh, das ist ja wieder eine volle Packung! Erst begleiten wir Nils zum '
                'FIFA-Pressepokal 2014, den er nach 2010 nun zum zweiten Mal gewinnen will.\n'
                'Danach gibt’s eine Vorschau auf die drei kommenden Hits “Star Citizen”, “Kingdom Come: Deliverance” und “Project Cars”.\n'
                'Und dann geht’s auch schon weiter mit der nächsten Folge vom Nerdquiz! Der schöne Trant foltert seine Kandidaten wieder '
                'mit fiesen Fragen. Hier gibt’s die erste Hälfte, in Folge 289 geht’s weiter.'
        }
    }

    def _real_extract(self, url):
        mobj = re.match(self._VALID_URL, url)
        video_id = mobj.group('id')

        webpage = self._download_webpage(url, video_id)
        og_video = self._og_search_video_url(webpage, secure=False)
        mrss_url = self._search_regex(r'mrss=([^&]+)', og_video, 'mrss')

        mrss = self._download_xml(mrss_url, video_id, 'Downloading mrss')
        title = mrss.find('.//item/title').text
        thumbnail = mrss.find('.//item/image').get('url')
        description = self._extract_description(mrss)
        content = mrss.find(xpath_with_ns('.//media:content', NAMESPACE_MAP))
        content_url = content.get('url')

        content = self._download_xml(content_url, video_id, 'Downloading media:content')
        rendition_items = content.findall('.//rendition')
        duration = int(rendition_items[0].get('duration'))
        formats = [
                {
                    'url': re.sub(r'.*/(r2)', RAW_MP4_URL + r'\1', r.find('./src').text),
                    'width': int(r.get('width')),
                    'height': int(r.get('height')),
                    'tbr': int(r.get('bitrate')),
                }
            for r in rendition_items
        ]

        return {
            'id': video_id,
            'title': title,
            'thumbnail': thumbnail,
            'duration': duration,
            'formats': formats,
            'description': description,
        }

    def _extract_description(self, mrss):
        description = mrss.find('.//item/description')
        return u''.join(t for t in description.itertext())
