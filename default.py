import sys, json, re
from urllib.request import Request, urlopen
from urllib.parse import parse_qs, urlencode

import xbmcgui
import xbmcplugin
import xbmcaddon
import xbmc
from resources.lib.ListItems import ListItems

try:
    import StorageServer
except:
    from resources.lib.cache import storageserverdummy as StorageServer
cache = StorageServer.StorageServer('plugin.audio.indigitube', 24)  # (Your plugin name, Cache time in hours)

USER_AGENT    = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36'
CONTENT_QUERY = 'https://api.appbooks.com/content/_query/{}'
CONTENT_ALBUM = 'https://api.appbooks.com/content/album/{}'

def urlopen_ua(url):
    headers = {
        'User-Agent': USER_AGENT,
        'Authorization': 'Bearer $2a$10$x2Zy/TgIAOC0UUMi3NPKc.KY49e/ZLUJFOpBCNYAs8D72UUnlI526',
    }
    return urlopen(Request(url, headers=headers), timeout=5)

def get_json(url):
    return urlopen_ua(url).read().decode()

def get_json_obj(url):
    return json.loads(get_json(url))

def get_query_content(media_id):
    return get_json_obj(CONTENT_QUERY.format(media_id))

def get_album_content(media_id):
    return get_json_obj(CONTENT_ALBUM.format(media_id))


def build_main_menu():
    root_items = list_items.get_root_items()
    xbmcplugin.addDirectoryItems(addon_handle, root_items, len(root_items))
    xbmcplugin.endOfDirectory(addon_handle)

def build_radio_list():
    radio_json = get_query_content('5d1aeac759dd785afe88ec0b')
    radio_items = list_items.get_radio_items(radio_json)
    xbmcplugin.addDirectoryItems(addon_handle, radio_items, len(radio_items))
    xbmcplugin.endOfDirectory(addon_handle)

def build_song_list(album_id):
    album_json = get_album_content(album_id)
    album_items = list_items.get_track_items(album_json)
    xbmcplugin.addSortMethod(addon_handle, xbmcplugin.SORT_METHOD_UNSORTED)
    xbmcplugin.setContent(addon_handle, 'songs')
    xbmcplugin.addDirectoryItems(addon_handle, album_items, len(album_items))
    xbmcplugin.endOfDirectory(addon_handle)

"""
def build_search_result_list(items):
    item_list = []
    for item in items:
        if isinstance(item, Band):
            item_list += list_items.get_band_items([item], from_search=True)
        elif isinstance(item, Album):
            item_list += list_items.get_album_items([item])
    xbmcplugin.addDirectoryItems(addon_handle, item_list, len(item_list))
    xbmcplugin.endOfDirectory(addon_handle)
"""

def play_song(url):
    play_item = xbmcgui.ListItem(path=url)
    xbmcplugin.setResolvedUrl(addon_handle, True, listitem=play_item)

"""
def search(query):
    build_search_result_list(bandcamp.search(query))
"""

def main():
    args = parse_qs(sys.argv[2][1:])
    mode = args.get('mode', None)
    if mode is None:
        build_main_menu()
    elif mode[0] == 'stream':
        play_song(args.get('url', [''])[0])
    elif mode[0] == 'list_radio':
        build_radio_list()
    elif mode[0] == 'list_songs':
        album_id = args.get('album_id', [''])[0]
        build_song_list(album_id)
    """
    elif mode[0] == 'list_search_albums':
        band, albums = bandcamp.get_band(args.get('band_id', [''])[0])
        build_album_list(albums, band)
    elif mode[0] == 'list_albums':
        bands = bandcamp.get_collection(bandcamp.get_fan_id())
        band, albums = bandcamp.get_band(args.get('band_id', [''])[0])
        build_album_list(bands[band], band)
    elif mode[0] == 'search':
        action = args.get('action', [''])[0]
        query = args.get('query', [''])[0]
        if action == 'new':
            query = xbmcgui.Dialog().input(addon.getLocalizedString(30103))
        if query:
            search(query)
    elif mode[0] == 'url':
        url = args.get('url', [''])[0]
        build_song_list(*bandcamp.get_album_by_url(url), autoplay=True)
    elif mode[0] == 'settings':
        addon.openSettings()
    """

if __name__ == '__main__':
    xbmc.log('sys.argv:' + str(sys.argv), xbmc.LOGDEBUG)
    addon = xbmcaddon.Addon()
    list_items = ListItems(addon)
    addon_handle = int(sys.argv[1])
    main()
