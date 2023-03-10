import sys
import xbmcgui
from urllib.parse import urlencode

class ListItems:
    INDIGITUBE_ACCESS_KEY            = 'access_token=%242a%2410%24x2Zy%2FTgIAOC0UUMi3NPKc.KY49e%2FZLUJFOpBCNYAs8D72UUnlI526'
    INDIGITUBE_ALBUM_URL             = 'https://api.appbooks.com/content/album/{}?' + INDIGITUBE_ACCESS_KEY
    INDIGITUBE_TRACK_URL             = 'https://api.appbooks.com/get/{}?' + INDIGITUBE_ACCESS_KEY
    INDIGITUBE_ALBUM_ART_URL         = 'https://api.appbooks.com/get/{}/file/file.jpg?w={}&quality=90&' + INDIGITUBE_ACCESS_KEY + '&ext=.jpg'

    def __init__(self, addon):
        self.addon = addon
        quality = self.addon.getSetting('image_quality')
        self.quality = int(quality) if quality else 1

    def _album_quality(self):
        if self.quality == 0:
            return '700'
        if self.quality == 1:
            return '350'
        if self.quality == 2:
            return '200'

    def _build_url(self, query):
        base_url = sys.argv[0]
        return base_url + '?' + urlencode(query)

    def get_root_items(self):
        items = []
        # discover menu
        li = xbmcgui.ListItem(label=self.addon.getLocalizedString(30101))
        li.setArt({'icon': 'DefaultMusicSources.png'})
        url = self._build_url({'mode': 'list_radio'})
        items.append((url, li, True))

        li = xbmcgui.ListItem(label=self.addon.getLocalizedString(30102))
        li.setArt({'icon': 'DefaultMusicSources.png'})
        url = self._build_url({'mode': 'list_songs', 'album_id': '629c1a22df379220b662d31f'})
        items.append((url, li, True))

        # search
        li = xbmcgui.ListItem(label=self.addon.getLocalizedString(30103))
        li.setArt({'icon': 'DefaultMusicSearch.png'})
        url = self._build_url({'mode': 'search', 'action': 'new'})
        items.append((url, li, True))
        return items

    def get_radio_items(self, radio_data):
        items = []
        for station in radio_data:
            title   = station.get('title')
            artist  = station.get('realms', [{}])[0].get('title')
            url     = station.get('data', {}).get('feedSource')
            art_id  = station.get('data', {}).get('coverImage', {}).get('_id')
            art_url = self.INDIGITUBE_ALBUM_ART_URL.format(art_id, self._album_quality())

            li = xbmcgui.ListItem(label=title)
            li.setInfo('music', {'title': title, 'artist': artist})
            li.setArt({'thumb': art_url})
            li.setProperty('IsPlayable', 'true')
            # url = self._build_url({'mode': 'stream', 'url': track.file, 'title': title})
            li.setPath(url)
            items.append((url, li, False))
        return items

    def get_track_items(self, album_json):
        items = []
        album_title = album_json.get('title', '')
        album_data = album_json.get('data', {})
        art_id  = album_data.get('coverImage', {}).get('_id')
        art_url = self.INDIGITUBE_ALBUM_ART_URL.format(art_id, self._album_quality())

        track_num = 1
        for track in album_data.get('items', []):
            title   = track.get('title')
            artist  = track.get('artist')
            url     = self.INDIGITUBE_TRACK_URL.format(track.get('file', {}).get('_id'))

            li = xbmcgui.ListItem(label=title)
            li.setInfo('music', {
                'title': title, 
                'artist': artist,
                'mediatype': 'song',
                'tracknumber': track_num,
                'album': album_title,
            })
            li.setArt({'thumb': art_url})
            li.setProperty('IsPlayable', 'true')
            # url = self._build_url({'mode': 'stream', 'url': track.file, 'title': title})
            li.setPath(url)
            items.append((url, li, False))
            track_num += 1
        return items

"""
    def get_album_items(self, albums, band=None, group_by_artist=False):
        items = []
        if group_by_artist:
            li = xbmcgui.ListItem(label=self.addon.getLocalizedString(30106))
            li.setArt({'icon': 'DefaultMusicArtists.png'})
            url = self._build_url({'mode': group_by_artist + '_band'})
            items.append((url, li, True))
        for album in albums:
            if band:
                album_title = '{} - {}'.format(band.band_name, album.album_name)
            elif album.band:
                album_title = '{} - {}'.format(album.band.band_name, album.album_name)
            else:
                album_title = album.album_name

            li = xbmcgui.ListItem(label=album_title)
            url = self._build_url({'mode': 'list_songs', 'album_id': album.album_id, 'item_type': album.item_type})
            band_art = band.get_art_img(quality=self._band_quality()) if band else None
            album_art = album.get_art_img(quality=self._album_quality())
            li.setArt({'thumb': album_art, 'fanart': band_art if band_art else album_art})
            items.append((url, li, True))
        return items

    def get_track_items(self, band, album, tracks, to_album=False):
        items = []
        for track in tracks:
            title = u"{band} - {track}".format(band=band.band_name, track=track.track_name)
            li = xbmcgui.ListItem(label=title)
            li.setInfo('music', {'duration': int(track.duration), 'album': album.album_name, 'genre': album.genre,
                                 'mediatype': 'song', 'tracknumber': track.number, 'title': track.track_name,
                                 'artist': band.band_name})
            band_art = band.get_art_img(quality=self._band_quality())
            album_art = album.get_art_img(quality=self._album_quality())
            li.setArt({'thumb': album_art, 'fanart': band_art if band_art else album_art})
            li.setProperty('IsPlayable', 'true')
            url = self._build_url({'mode': 'stream', 'url': track.file, 'title': title})
            li.setPath(url)
            if to_album:
                album_url = self._build_url(
                    {'mode': 'list_songs', 'album_id': album.album_id, 'item_type': album.item_type})
                cmd = 'Container.Update({album_url})'.format(album_url=album_url)
                commands = [(self.addon.getLocalizedString(30202), cmd)]
                li.addContextMenuItems(commands)
            items.append((url, li, False))
        return items
"""
