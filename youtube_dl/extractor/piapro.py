# coding: utf-8
from __future__ import unicode_literals

import re
import datetime

from .common import InfoExtractor
from ..utils import (
	clean_html,
	get_element_by_class,
	get_elements_by_class,
	int_or_none,
	parse_duration,
	parse_filesize,
	unified_timestamp,
	url_or_none,
	urlencode_postdata,
)


class PiaproBaseInfoExtractor(InfoExtractor):
	# long id        [a-z0-9]{16}
	# short id       [A-Za-z0-9_-]{4}
	# date           [0-9]{14}
	# uploader id    [A-Za-z0-9_]+

	_LICENSE_TYPES = {
		'nc': '非営利目的に限ります',
		'nd': 'この作品を改変しないで下さい',
		'by': '作者の氏名を表示して下さい',
		'org': 'オリジナルライセンス',
		'clb': 'コラボのメンバーのみダウンロードできます',
	}

	# https://piapro.jp/music/
	# https://piapro.jp/illust/
	# https://piapro.jp/text/
	# https://piapro.jp/illust/?tag=&3dm=1
	_MEDIA_TYPES_2 = {
		'music': 'オンガク',
		'illust': 'イラスト',
		'text': 'テキスト',
	}

	# https://piapro.jp/content_list/?pid=____&view=audio
	# https://piapro.jp/content_list/?pid=____&view=image
	# https://piapro.jp/content_list/?pid=____&view=text
	# https://piapro.jp/content_list/?pid=____&view=3dm
	_MEDIA_TYPES = {
		False: {
			True: None,
			'0': None,
		},
		'audio': {
			True: 'オンガク',
			'0': '全て',
			'1': '音楽',
			'2': 'その他',
			'21': 'ボカロ音楽',
			'22': '音素材/その他',
			'23': 'カラオケ/インスト',
			'24': '歌ってみた',
			'25': '弾いてみた',
		},
		'image': {
			True: 'イラスト',
			'0': '全て',
			'3': 'クリプトン公式',
			'9': '他社ボカロ',
			'4': '創作ボカロ',
			'5': '素材画像',
			'6': 'その他',
		},
		'text': {
			True: 'テキスト',
			'0': '全て',
			'7': '歌詞',
			'10': '小説',
			'8': 'その他',
		},
		'3dm': {
			True: '3Dモデル',
			'11': 'クリプトン公式',
			'12': '他社ボカロ',
			'13': '創作ボカロ',
			'14': '素材データ',
			'15': 'その他',
		},
	}

	def _convert_a_to_categories(self, text):
		mobj = re.search(
			r'>(.+)</a>',
			text)
		cat_sub_name = mobj.group(1)

		if '3dm' in text:
			return ['3Dモデル', cat_sub_name]

		mobj = re.search(
			r'/([a-z0-9]+)/\?categoryId=(\d+)',
			text)
		cat_id = mobj.group(1)
		#cat_sub_id = mobj.group(2)
		cat_name = self._MEDIA_TYPES_2[cat_id]

		return [cat_name, cat_sub_name]

	def _convert_content_list_page_to_categories(self, website):
		els = get_elements_by_class('now', website)
		cats = []
		for el in els:
			text = clean_html(el)
			if (text != '作品一覧') and (text != ''):
				text = re.sub(r'\d+$', '', text)
				cats.append(text)
		return cats

class PiaproIE(PiaproBaseInfoExtractor):
	IE_NAME = 'piapro'
	_NETRC_MACHINE = 'piapro'
	_VALID_URL = r'https?://piapro\.jp/(?:a/content/\?id=|content\/|t/)(?P<id>[A-Za-z0-9]{16}|[A-Za-z0-9_-]{4}/[0-9]{14}|[A-Za-z0-9_-]{4})'
	_TESTS = [
		{
			# test 0
			'note': 'Has multiple associated artworks (2019 August 31)',
			'url': 'https://piapro.jp/t/LWnC',
			'info_dict': {
				'id': 'hqfe875u1o1al9br_20080225042431',
				'title': '桜ノ雨',
				#'formats': [
				#	{
				#		'url': 'https://cdn.piapro.jp/mp3_a/hq/hqfe875u1o1al9br_20080225042431_audition.mp3',
				#		'format_id': 'cdn',
				#	},
				#	{
				#		'url': 're:https://dl\.piapro\.jp/audio/hq/hqfe875u1o1al9br_20080225042431\.mp3.*',
				#		'format_id': 'dl',
				#	},
				#],
				'formats': list,
				'ext': 'mp3',
				'alt_title': 'hqfe875u1o1al9br',
				'display_id': 'LWnC',
				'thumbnails': [ # freely editable by users
					{
						'id': 'yyolktkwb1j3ygre_20080223162956',
						'url': 'https://cdn.piapro.jp/thumb_i/yy/yyolktkwb1j3ygre_20080223162956_0740_0500.jpg',
					},
					{
						'id': 'maobv87r1xkeyjtg_20100314003053',
						'url': 'https://cdn.piapro.jp/thumb_i/ma/maobv87r1xkeyjtg_20100314003053_0740_0500.jpg',
					},
				],
				'description': 'md5:d7b5eeebdb2063defce3619030e895bd',
				'uploader': 'halyosy',
				'license': '非営利目的に限ります\n作者の氏名を表示して下さい',
				'timestamp': int, # 20080225042431
				'upload_date': '20080225',
				'uploader_id': 'halyosy',
				'uploader_url': 'https://piapro.jp/halyosy',
				'duration': float,
				'view_count': int,
				'like_count': int,
				'comment_count': int,
				'webpage_url': 'https://piapro.jp/t/LWnC',
				'categories': ['オンガク', '音楽'],
				'tags': [ # freely editable by users
					'初音ミク', '桜ノ雨', 'ｈａｌｙｏｓｙ', '卒業',
					'卒業ソング', '桜', '春', '思い出', '前向き', '名曲'],
			},
			'params': {
				#'skip_download': True,
				#'username': raw_input("[test 0] USERNAME: "),
				#'password': raw_input("[test 0] PASSWORD: "),
			},
		},
		{
			# test 1
			'note': 'Has past versions; has no associated artworks (2019 August 31)',
			'url': 'https://piapro.jp/content/wzbannuehci39y5c',
			'info_dict': {
				'id': 'wzbannuehci39y5c',
			},
			'playlist': [
				{
					'info_dict': {
						'id': 'wzbannuehci39y5c_20091108090114',
						'title': '1925カラオケ　コーラス残しver',
						'formats': list,
						'ext': 'mp3',
						'alt_title': 'wzbannuehci39y5c',
						'display_id': '0on9',
						'thumbnails': list,
						'description': 'md5:6d72b59b5dd36d8634783fab49442ada',
						'uploader': 'とみー　T＿POCKET',
						'license': '非営利目的に限ります',
						'timestamp': int, # 20091108090114
						'upload_date': '20091108',
						'uploader_id': 't_pocket',
						'uploader_url': 'https://piapro.jp/t_pocket',
						'duration': float,
						'view_count': int,
						'like_count': int,
						'comment_count': int,
						'webpage_url': 'https://piapro.jp/t/0on9', # or 'https://piapro.jp/content/wzbannuehci39y5c'?
						'categories': ['オンガク', '音楽'],
						'tags': list,
					},
				},
				{
					'info_dict': {
						'id': 'wzbannuehci39y5c_20091108085816',
						'title': '1925カラオケ',
						'formats': list,
						'ext': 'mp3',
						'alt_title': 'wzbannuehci39y5c',
						'display_id': '0on9',
						'thumbnails': list,
						'description': 'md5:844316da89abae9d88d79ecaef401bd2',
						'uploader': 'とみー　T＿POCKET',
						'license': '非営利目的に限ります',
						'timestamp': int, # 20091108085816
						'upload_date': '20091108',
						'uploader_id': 't_pocket',
						'uploader_url': 'https://piapro.jp/t_pocket',
						'duration': float,
						'view_count': int,
						'like_count': int,
						'comment_count': int,
						'webpage_url': 'https://piapro.jp/t/0on9/20091108085816',
						'categories': ['オンガク', '音楽'],
						'tags': list,
					},
				},
				{
					'info_dict': {
						'id': 'wzbannuehci39y5c_20091108085115',
						'title': '1925',
						'formats': list,
						'ext': 'mp3',
						'alt_title': 'wzbannuehci39y5c',
						'display_id': '0on9',
						'thumbnails': list,
						'description': 'md5:1e975f8dca96d81b22b698c5078203c8',
						'uploader': 'とみー　T＿POCKET',
						'license': '非営利目的に限ります',
						'timestamp': int, # 20091108085115
						'upload_date': '20091108',
						'uploader_id': 't_pocket',
						'uploader_url': 'https://piapro.jp/t_pocket',
						'duration': float,
						'view_count': int,
						'like_count': int,
						'comment_count': int,
						'webpage_url': 'https://piapro.jp/t/0on9/20091108085115',
						'categories': ['オンガク', '音楽'],
						'tags': list,
					},
				},
			],
			'params': {
				#'skip_download': True,
				#'username': raw_input("[test 1] USERNAME: "),
				#'password': raw_input("[test 1] PASSWORD: "),
			},
		},
		{
			# test 2
			'note': 'Same test as above, but using the URL to a past version',
			'url': 'https://piapro.jp/t/0on9/20091108085115',
			'info_dict': {
				'id': 'wzbannuehci39y5c',
			},
			'playlist': [
				{
					'info_dict': {
						'id': 'wzbannuehci39y5c_20091108090114',
						'title': '1925カラオケ　コーラス残しver',
						# required by tests:
						'ext': 'mp3',
						'description': 'md5:6d72b59b5dd36d8634783fab49442ada',
						'uploader': 'とみー　T＿POCKET',
						'timestamp': int,
						'upload_date': '20091108',
						'uploader_id': 't_pocket',
					},
				},
				{
					'info_dict': {
						'id': 'wzbannuehci39y5c_20091108085816',
						'title': '1925カラオケ',
						#
						'ext': 'mp3',
						'description': 'md5:844316da89abae9d88d79ecaef401bd2',
						'uploader': 'とみー　T＿POCKET',
						'timestamp': int,
						'upload_date': '20091108',
						'uploader_id': 't_pocket',
					},
				},
				{
					'info_dict': {
						'id': 'wzbannuehci39y5c_20091108085115',
						'title': '1925',
						#
						'ext': 'mp3',
						'description': 'md5:1e975f8dca96d81b22b698c5078203c8',
						'uploader': 'とみー　T＿POCKET',
						'timestamp': int,
						'upload_date': '20091108',
						'uploader_id': 't_pocket',
					},
				},
			],
			'params': {
				'skip_download': True,
			},
		},
		{
			# test 3
			'note': 'Illustration',
			'url': 'https://piapro.jp/t/i-lO',
			'info_dict': {
				'id': 'hpnp7eyvn1tb8uit',
			},
			'playlist': [
				{
					'info_dict': {
						'id': 'hpnp7eyvn1tb8uit_20080123025754',
						'title': 'ミク',
						'formats': list,
						'ext': 'jpg',
						'alt_title': 'hpnp7eyvn1tb8uit',
						'display_id': 'i-lO',
						'thumbnails': list,
						'description': 'md5:cf25aff04c6860b900889a811466157e',
						'uploader': 'nezuki',
						'license': '非営利目的に限ります',
						'timestamp': int, # 20080123025754
						'upload_date': '20080123',
						'uploader_id': 'nezuki',
						'uploader_url': 'https://piapro.jp/nezuki',
						'view_count': int,
						'like_count': int,
						'comment_count': int,
						'webpage_url': 'https://piapro.jp/t/i-lO',
						'categories': ['イラスト', 'クリプトン公式'],
						'tags': list,
					},
				},
				{
					'info_dict': {
						'id': 'hpnp7eyvn1tb8uit_20071224204741',
						'title': 'ミク',
						'formats': list,
						'ext': 'jpg',
						'alt_title': 'hpnp7eyvn1tb8uit',
						'display_id': 'i-lO',
						'thumbnails': list,
						'description': 'md5:540bd729a8aa4af2770b752f11b8954a',
						'uploader': 'nezuki',
						'license': '非営利目的に限ります',
						'timestamp': int, # 20071224204741
						'upload_date': '20071224',
						'uploader_id': 'nezuki',
						'uploader_url': 'https://piapro.jp/nezuki',
						'view_count': int,
						'like_count': int,
						'comment_count': int,
						'webpage_url': 'https://piapro.jp/t/i-lO/20071224204741',
						'categories': ['イラスト', 'クリプトン公式'],
						'tags': list,
					},
				},
			],
			'params': {
				#'skip_download': True,
				#'username': raw_input("[test 3] USERNAME: "),
				#'password': raw_input("[test 3] PASSWORD: "),
			},
		},
		{
			# test 4
			'note': 'Text',
			'skip': 'Needs an account',
			'url': 'https://piapro.jp/t/esIT',
			'info_dict': {
				'id': 'lzw1fwnk06l2b8ro_20110930071803',
				'title': 'カゲロウデイズ　歌詞',
				'formats': list,
				'ext': 'txt',
				'alt_title': 'lzw1fwnk06l2b8ro',
				'display_id': 'esIT',
				#'thumbnails': list,
				'description': 'md5:0769539590c06c91a30ea74265fea6fc',
				'uploader': 'じん',
				'license': '非営利目的に限ります',
				'timestamp': int, # 20110930071803
				'upload_date': '20110930',
				'uploader_id': 'jin_jin_suruyo',
				'uploader_url': 'https://piapro.jp/jin_jin_suruyo',
				'view_count': int,
				'like_count': int,
				'comment_count': int,
				'webpage_url': 'https://piapro.jp/t/esIT',
				'categories': ['テキスト', '歌詞'],
				'tags': list,
			},
			'params': {
				#'skip_download': True,
				#'username': raw_input("[test 4] USERNAME: "),
				#'password': raw_input("[test 4] PASSWORD: "),
			},
		},
		{
			# test 5
			'note': '3D model',
			#'skip': 'Needs an account',
			'url': 'https://piapro.jp/t/KPU3',
			'info_dict': {
				'id': 'dtuhicgnptro9jc3_20121229020229',
				'title': 'Appearance Miku　あぴミク',
				'formats': list,
				'ext': 'x',
				'alt_title': 'dtuhicgnptro9jc3',
				'display_id': 'KPU3',
				#'thumbnails': list,
				'description': 'md5:718f391bd10161ea92c3b70ab795e1e6',
				'uploader': 'ままま',
				'license': '非営利目的に限ります\n作者の氏名を表示して下さい',
				'timestamp': int, # 20121229020229
				'upload_date': '20121229',
				'uploader_id': 'mamamana',
				'uploader_url': 'https://piapro.jp/mamamana',
				'view_count': int,
				'like_count': int,
				'comment_count': int,
				'webpage_url': 'https://piapro.jp/t/KPU3',
				'categories': ['3Dモデル', '素材データ'],
				'tags': list,
			},
			'params': {
				#'skip_download': True,
				#'username': raw_input("[test 5] USERNAME: "),
				#'password': raw_input("[test 5] PASSWORD: "),
			},
		},
		{
			'only_matching': True,
			'url': 'http://piapro.jp/a/content/?id=qj6lvuictzc8lp1q',
		},
	]
	# TODO: https://piapro.jp/t/x1z6 has lyrics

	is_logged_in = None

	def _real_initialize(self):
		self.is_logged_in = self._login()

	def _login(self):
		# ref. niconico.py, afreecatv.py
		username, password = self._get_login_info()
		if not username:
			self.to_screen('Did not log in')
			return False

		webpage = self._request_webpage(
			'https://piapro.jp/login/',
			None,
			note = 'Preparing cookies')

		form_data = {
			'_username': username,
			'_password': password,
		}
		response = self._request_webpage(
			'https://piapro.jp/login/exe',
			None,
			note = 'Logging in',
			data = urlencode_postdata(form_data))
		if response.url == 'https://piapro.jp/login/':
			self._downloader.report_warning('Unable to log in')
			return False

		return True

	def _get_media_data(self, url, webpage):
		categories = self._search_regex(
			r'<span>カテゴリ：</span>(<a[^>]+>.+</a>)',
			webpage,
			'categories',
			fatal = False)
		categories = self._convert_a_to_categories(categories)

		content_id = None
		create_date = None

		twitter_thumbnail_url = self._html_search_meta('twitter:image', webpage)

		if 'イラスト' in categories:
			mobj = re.search(
				r'(?P<content_id>[a-z0-9]{16})_(?P<create_date>[0-9]{14})',
				twitter_thumbnail_url)
			if mobj is not None:
				content_id = mobj.group('content_id')
				create_date = mobj.group('create_date')

		content_id_short = self._html_search_regex(
			[
				r'value="https://piapro.jp/t/([A-Za-z0-9_-]{4})" id="_page_url"',
				r'"http://twitter.com/share?url=https://piapro.jp/t/([A-Za-z0-9_-]{4})"',
				r'from:\'([A-Za-z0-9_-]{4})\'',
			],
			webpage,
			'content_id_short')
		if not content_id:
			content_id = self._html_search_regex(
				[
					r'contentId:\s*\'([a-z0-9]{16})\'',
					r'name="(?:DownloadOnly|DownloadWithBookmark)\[contentId\]"[^>]+value="([a-z0-9]{16})"',
				],
				webpage,
				'content_id')
		if not create_date:
			create_date = self._html_search_regex(
				[
					r'createDate:\s*\'([0-9]{14})\'',
					r'name="(?:DownloadOnly|DownloadWithBookmark)\[createDate\]"[^>]+value="([0-9]{14})"',
				],
				webpage,
				'create_date')

		title = self._html_search_regex(
			r'<h1[^>]+>(.+?)</h1>',
			webpage,
			'title')
		description = self._search_regex(
			r'<p class="cd_dtl_cap">(.+?)</p>',
			webpage,
			'description',
			flags = re.DOTALL,
			fatal = False)
		uploader_id = None
		uploader = None
		mobj = re.search(
			r'<a class="cd_user-name" href="/(?P<uploader_id>[A-Za-z0-9_]+)">(?P<uploader>.+)さん</a>',
			webpage)
		if mobj is not None:
			uploader_id = mobj.group('uploader_id')
			uploader = mobj.group('uploader')
		license_terms = None
		mobj = self._search_regex(
			r'<span>ライセンス：</span>(.*?)</p>',
			webpage,
			'license_terms',
			flags = re.DOTALL,
			fatal = False)
		mobj = re.findall(
			r'([a-z]+)\.svg',
			mobj)
		if mobj is not None:
			license_terms = []
			for license_term in mobj:
				license_term_name = self._LICENSE_TYPES[license_term]
				license_terms.append(license_term_name)
		duration = None
		dimensions = None
		ext = None
		filesize = None
		mobj = re.search(
			r'<span>タイム/サイズ：</span>(?P<duration>[0-9:]+)/\((?P<filesize>[0-9,]+KB)\）',
			webpage)
		if mobj is not None:
			duration = mobj.group('duration')
			filesize = mobj.group('filesize')
		mobj = re.search(
			r'<span>サイズ：</span>(?P<dimensions>[0-9:]+)\（(?P<filesize>[0-9,]+KB)\）',
			webpage)
		if mobj is not None:
			dimensions = mobj.group('duration') # unused
			filesize = mobj.group('filesize')
		mobj = re.search(
			r'<span>サイズ/拡張子：</span>(?P<filesize>[0-9,]+KB)/(?P<ext>.+)形式ファイル',
			webpage)
		if mobj is not None:
			filesize = mobj.group('filesize')
			ext = mobj.group('ext')
		if 'テキスト' in categories:
			ext = 'txt'
		view_count = self._html_search_regex(
			r'<span>閲覧数：</span>([0-9,]+)',
			webpage,
			'view_count',
			fatal = False)
		like_count = self._html_search_regex(
			r'<span id="spanBookmarkCount">([0-9]+)</span>',
			webpage,
			'like_count',
			fatal = False)
		comment_count = self._html_search_regex(
			r'作品へのコメント<span>([0-9]+)</span>',
			webpage,
			'comment_count',
			fatal = False)
		tags = self._html_search_regex(
			r'<ul class="taglist">(.*?)</ul>',
			webpage,
			'tags',
			flags = re.DOTALL,
			fatal = False)
		tags = re.split(r'\t+', tags)
		if tags[-1] == '[編集]':
			tags.pop()

		thumbnails = []
		if 'bigJacket' in webpage:
			mobj = re.findall(
				r'id="bigJacket_\d+" src="([^"]+)"',
				webpage)
			if mobj is not None:
				for url in mobj:
					print(url)
					thumbnail_id = self._search_regex(
						r'([a-z0-9]{16}_[0-9]{14})',
						url,
						'thumbnail_id',
						fatal = False)
					thumbnails.append(
						{
							'id': thumbnail_id,
							'url': url,
						}
					)
		else:
			thumbnails = [
				{
					'url': twitter_thumbnail_url,
				}
			]

		formats = []
		if 'オンガク' in categories:
			formats.append(
				{
					'url': (
						'https://cdn.piapro.jp/mp3_a/' +
						content_id[:2] +
						'/' +
						content_id + '_' + create_date + '_audition.mp3'
					),
					'ext': 'mp3',
					'format_id': 'cdn',
					'quality': -1,
				}
			)
		elif 'イラスト' in categories:
			formats.append(
				{
					'url': self._search_regex(
						r'<div class="illust-whole">\s*<img src="([^"]+)"',
						webpage,
						'url',
						flags = re.DOTALL),
					'format_id': 'cdn',
					'quality': -1,
				}
			)
		if self.is_logged_in:
			download_token = self._html_search_regex(
				r'name="(?:DownloadOnly|DownloadWithBookmark)\[_token\]"[^>]+value="([^"]+)"',
				webpage,
				'download_token')
			form_data = {
				'DownloadOnly[contentId]': content_id,
				'DownloadOnly[createDate]': create_date,
				'DownloadOnly[_token]': download_token,
				'DownloadOnly[license]': 1,
			}
			response = self._request_webpage(
				'https://piapro.jp/download/content/',
				content_id + '_' + create_date,
				data = urlencode_postdata(form_data),
				note = 'Requesting final URL')
			media_url = response.geturl() + '' # XXX: WTF?
			formats.append(
				{
					'url': media_url,
					'ext': ext,
					'format_id': 'dl',
					'quality': 1,
					'filesize': parse_filesize(filesize),
				}
			)

		return {
			'id': content_id + '_' + create_date,
			'title': title,
			'formats': formats,
			'alt_title': content_id,
			'display_id': content_id_short,
			'thumbnails': thumbnails,
			'description': description,
			'uploader': uploader,
			'license': (license_terms and '\n'.join(license_terms)),
			'timestamp': unified_timestamp(
				str(datetime.datetime.strptime(create_date, '%Y%m%d%H%M%S')) # XXX: this doesn't seem right
			),
			'upload_date': create_date[:8],
			'uploader_id': uploader_id,
			'uploader_url': 'https://piapro.jp/' + uploader_id,
			'duration': parse_duration(duration),
			'view_count': int_or_none(view_count.replace(",", "")),
			'like_count': int_or_none(like_count),
			'comment_count': int_or_none(comment_count),
			'webpage_url': url,
			'categories': categories,
			'tags': tags,
		}

	def _get_past_versions(self, content_id_short):
		webpage = self._download_webpage(
			'https://piapro.jp/ex_content/history_list/' + content_id_short + '/1',
			content_id_short,
			note = 'Checking for past versions')
		#if '過去のバージョンは見つかりませんでした' in webpage:
		#	return
		mobj = re.findall(r'<td class="title"><a href="/t/([^"]+)"', webpage)
		if len(mobj) == 0:
			mobj = re.findall(r'<a class="i_image" href="/t/([^"]+)"', webpage) # イラスト
		return mobj

	def _real_extract(self, url):
		video_id = self._match_id(url)
		webpage = self._download_webpage(url, video_id)

		media_data = self._get_media_data(url, webpage)
		content_id_short = media_data['display_id']
		content_id = media_data['alt_title']

		if 'すべてのバージョンを表示' in webpage:
			past_versions = self._get_past_versions(content_id_short)
			entries = []
			for past_version in past_versions:
				# TODO: one of these has been downloaded before.
				# Try to avoid downloading it twice
				url = url_or_none('https://piapro.jp/t/' + past_version)
				webpage = self._download_webpage(url, past_version)
				media_data = self._get_media_data(url, webpage)
				entries.append(media_data)
			return {
				'_type': 'multi_video',
				'entries': entries,
				'id': content_id,
			}
		return media_data

class PiaproUserIE(PiaproBaseInfoExtractor):
	_VALID_URL = r'https?://piapro\.jp/(?:my_page/\?.*pid=|content_list/\?.*pid=|)(?P<id>[A-Za-z0-9_]+)'
	_TESTS = [
		{
			'url': 'https://piapro.jp/namakobcg_rnd',
			'info_dict': {
				'id': 'namakobcg_rnd',
				'title': '投稿作品',
				'uploader': 'namakobcg',
				'uploader_id': 'namakobcg_rnd',
			},
			'playlist_mincount': 90,
		},
		{
			'note': 'Same as above',
			'url': 'https://piapro.jp/my_page/?pid=namakobcg_rnd&view=content&order=sd',
			'info_dict': {
				'id': 'namakobcg_rnd',
				'title': '投稿作品',
				'uploader': 'namakobcg',
				'uploader_id': 'namakobcg_rnd',
			},
			'playlist_mincount': 90,
		},
		{
			'url': 'https://piapro.jp/content_list/?pid=Raine_3893&view=image',
			'info_dict': {
				'id': 'Raine_3893 image 0',
				'title': '投稿作品 イラスト 全て',
				'uploader': 'Ruuya',
				'uploader_id': 'Raine_3893',
			},
			'playlist_mincount': 20,
		},
		{
			'url': 'https://piapro.jp/content_list/?pid=Raine_3893&view=image&category_id=9&order=sd',
			'info_dict': {
				'id': 'Raine_3893 image 9',
				'title': '投稿作品 イラスト 他社ボカロ',
				'uploader': 'Ruuya',
				'uploader_id': 'Raine_3893',
			},
			'playlist_mincount': 1,
		},
		{
			'note': 'Horizontal page layout',
			'url': 'https://piapro.jp/content_list/?pid=n_buna&view=audio&category_id=23&order=sd',
			'info_dict': {
				'id': 'n_buna audio 23',
				'title': '投稿作品 オンガク カラオケ/インスト',
				'uploader': 'n-buna',
				'uploader_id': 'n_buna',
			},
			'playlist_mincount': 1,
		},
		{
			'note': 'Horizontal page layout',
			'url': 'https://piapro.jp/content_list/?pid=n_buna&view=text&order=sd',
			'info_dict': {
				'id': 'n_buna text 0',
				'title': '投稿作品 テキスト 全て',
				'uploader': 'n-buna',
				'uploader_id': 'n_buna',
			},
			'playlist_mincount': 20,
		},
		{
			'note': '',
			'url': 'https://piapro.jp/content_list/?pid=maebari&view=3dm&category_id=11&order=sd',
			'info_dict': {
				'id': 'maebari 3dm 11',
				'title': '投稿作品 3Dモデル クリプトン公式',
				'uploader': 'maebari',
				'uploader_id': 'maebari',
			},
			'playlist_mincount': 10,
		},
		{
			'skip': 'Not a user page',
			'url': 'http://piapro.jp/login/',
		},
		{
			'only_matching': True,
			'url': 'http://piapro.jp/login',
		},
	]

	def _real_extract(self, url):
		user_id = self._match_id(url)

		if 'pid' not in url:
			url = 'https://piapro.jp/my_page/?view=content&pid=' + user_id
		url = re.sub(r'[?&]start_rec=\d+', '', url)
		url = re.sub(r'[?&]order=\d+', '', url)
		webpage = self._download_webpage(url, user_id)

		uploader = self._html_search_regex(
			r'<h2>(.+?)</h2>',
			webpage,
			'uploader')
		uploader = re.sub(r'さん$', '', uploader)

		#categories = self._convert_content_list_page_to_categories(webpage)
		view = None
		category_id = None
		view = self._search_regex(
			r'[?&]view=([a-z0-9]+)',
			url,
			'view',
			fatal = False,
			default = False)
		if view == 'content':
			view = False
		category_id = self._search_regex(
			r'[?&]category_id=(\d+)',
			url,
			'view',
			fatal = False,
			default = '0')

		categories = []
		cat_name = self._MEDIA_TYPES[view][True]
		cat_sub_name = self._MEDIA_TYPES[view][category_id]
		if cat_name:
			categories.append(cat_name)
		if cat_sub_name:
			categories.append(cat_sub_name)

		playlist_id = None
		playlist_title = None
		playlist_id = user_id
		if view:
			playlist_id += ' ' + view
			if category_id:
				playlist_id += ' ' + category_id
		playlist_title = '投稿作品'
		if len(categories) > 0:
			playlist_title += ' ' + ' '.join(categories)

		webpages = {
			0: webpage,
		}
		el = get_element_by_class('paging', webpage)
		if el:
			mobj = re.findall(r'(<li.*?</li>)', el)
			mobj.pop(0) # "BACK"
			mobj.pop() # "NEXT"
			for li in mobj:
				mobj = re.search(r'([?&]start_rec=(\d+))', li)
				if mobj is not None:
					query = mobj.group(1)
					start_rec = mobj.group(2)
					webpages[query] = self._download_webpage(
						url + query,
						user_id + query)

		entries = []
		for start_rec in webpages:
			webpage = webpages[start_rec]
			els = get_elements_by_class('i_main', webpage)
			if not els:
				els = get_elements_by_class('title', webpage)
			for el in els:
				video_id = self._search_regex(
					r'href="/t/([A-Za-z0-9_-]{4})"',
					el,
					'href')
				entries.append(
					{
						'_type': 'url',
						'url': 'https://piapro.jp/t/' + video_id,
						'ie_key': PiaproIE.ie_key(),
					}
				)

		return {
			'_type': 'playlist',
			'id': playlist_id,
			'title': playlist_title,
			'uploader': uploader,
			'uploader_id': user_id,
			'entries': entries,
		}
