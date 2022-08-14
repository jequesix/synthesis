from ytmusicapi import YTMusic
from os.path import exists
from PIL import Image


class BasicInfo:
    """Gather basic information needed by program"""

    def __init__(self, url, ytm_setup):
        self.url = url
        self.ytm_setup = ytm_setup

        self.link_type = ''
        self.url_id = ''

        self.ytm = ''

        self.ytm_song_info = []
        self.content_type = ''

        self.cover_url = ''

    # Initialize ytmusicapi class
    def initialize_ytm(self):
        if self.ytm_setup:
            YTMusic.setup(filepath='headers_auth.json')

        if exists('headers_auth.json'):
            self.ytm = YTMusic('headers_auth.json')
        else:
            self.ytm = YTMusic()

    # Find link type (long_url, short_url or playlist) from url
    def find_link_type(self):
        if 'v=' in self.url:
            self.link_type = 'long_url'  # long_url: youtube.com/watch?v...
        elif 'youtu.be' in self.url:
            self.link_type = 'short_url'  # short_url: youtu.be/...
        elif 'list=' in self.url:
            self.link_type = 'playlist'  # playlist: youtube.com/playlist?list...
        else:
            print('\033[0;31mError: Link type not found\033[0m')
            exit()

    # Find content or playlist id from url
    def find_url_id(self):
        if self.link_type == 'long_url':
            pre_id_marker = 'v='
        elif self.link_type == 'short_url':
            pre_id_marker = 'e/'
        elif self.link_type == 'playlist':
            pre_id_marker = 't='
        else:
            print('\033[0;31mError: Link type not found\033[0m')
            exit()

        id_index = self.url.index(pre_id_marker) + 2  # Index of url where id starts

        if '&' in self.url[id_index:]:
            end_symbol = '&'
        else:
            end_symbol = '%'
            self.url += end_symbol

        end_id_index = self.url.index(end_symbol)  # Index of url where id ends

        self.url_id = self.url[id_index:end_id_index]

    # Find type (song or video) of content being processed
    def find_content_type(self, search_string, strict_result: bool = True):
        if search_string is None:
            print('\033[0;31mError: Video unavailable\033[0m')
            self.content_type = None
            return
        elif search_string[0] == '-':
            search_string = f'"{search_string}"'

        self.ytm_song_info = self.ytm.search(query=search_string, filter='songs', ignore_spelling=strict_result)

        if len(self.ytm_song_info) == 0:
            self.content_type = 'video'
        elif self.ytm_song_info[0]['videoType'] == 'MUSIC_VIDEO_TYPE_ATV':
            self.content_type = 'song'
        else:
            self.content_type = 'video'


class Song:
    """Find song metadata and metadata related info"""

    def __init__(self, ytm, ytm_song_info):
        self.title = ''
        self.artist = ''
        self.date = ''
        self.album = ''
        self.album_artist = ''

        self.cover_url = ''

        self.ytm = ytm
        self.ytm_song_info = ytm_song_info

        self.album_id = self.ytm_song_info[0]['album']['id']
        self.ytm_album_info = self.ytm.get_album(self.album_id)

    # Find song metadata from ytm output
    def find_metadata(self):
        self.title = self.ytm_song_info[0]['title']
        self.artist = self.ytm_song_info[0]['artists'][0]['name']
        self.date = self.ytm_album_info['year']
        self.album = self.ytm_album_info['title']

        album_artist_list = self.ytm_album_info['artists']

        if len(album_artist_list) > 1:
            self.album_artist = 'Various Artists'
        else:
            self.album_artist = self.ytm_album_info['artists'][0]['name']

    # Find song cover url
    def find_cover_url(self):
        self.cover_url = self.ytm_album_info['thumbnails'][3]['url']


class Video:
    """Find video metadata and metadata related info"""

    def __init__(self, ytm, content_id):
        self.title = ''
        self.artist = ''
        self.date = ''
        self.album = ''
        self.album_artist = ''

        self.content_id = content_id

        self.ytm = ytm
        self.ytm_video_info = self.ytm.get_song(videoId=self.content_id)

        self.cover_url = ''

    # Find video metadata from ytm output
    def find_metadata(self):
        get_date = self.ytm_video_info['microformat']['microformatDataRenderer']['uploadDate']

        raw_title = self.ytm_video_info['videoDetails']['title']

        if ' - ' in raw_title:  #
            dash_index = raw_title.index('-')

            title_index = dash_index + 2
            artist_index = dash_index - 1

            self.title = raw_title[title_index:]
            self.artist = raw_title[:artist_index]
        else:
            self.title = raw_title
            self.artist = self.ytm_video_info['videoDetails']['author']

        self.date = get_date[:4]
        self.album = 'Videos'
        self.album_artist = self.artist

    # Find video cover url
    def find_cover_url(self):
        self.cover_url = self.ytm_video_info['microformat']['microformatDataRenderer'][
                                                'thumbnail']['thumbnails'][0]['url']

    # Crop video cover to a square
    def crop_cover(self):
        image = Image.open('cover.jpg')
        image_size = image.size
        width, height = image_size

        if image_size == (480, 360):  # Smaller YouTube thumbnails
            height -= 90  # Remove height of horizontal black bars

            top = 45
            bottom = int(top + height)
        else:
            top = 0
            bottom = int(height)

        left = int((width - height) / 2)
        right = int(left + height)

        crop_box = (left, top, right, bottom)

        cover = image.crop(crop_box)
        cover.save('cover.jpg')


class VideoToSong:
    """Handle video to song conversion"""

    def __init__(self, b_obj, title, artist):
        self.b = b_obj
        self.title = title
        self.artist = artist

        self.convert = True
        self.convertible = False

        self.search_title = ''

        self.song_id = ''

    # Prompt user to convert video to song (-p argument)
    def vts_prompt(self):
        while True:
            prompt = input(f'\033[1;34m{self.title}\033[0m is a video that contains music. Do you want to find a '
                           'YouTube Music song using the video title? [Y/n] ').lower()

            if prompt == 'y':
                break
            elif prompt == 'n':
                self.convert = False
                break
            else:
                print('Answer with [Y/n].')

    # Tell if video can be converted to song
    def find_is_convertible(self):
        if ' - ' not in self.title:
            self.search_title = f'{self.artist} - {self.title}'
        else:
            self.search_title = self.title

        self.b.find_content_type(search_string=self.search_title, strict_result=False)

        if self.b.content_type == 'song':
            self.convertible = True
            self.song_id = self.b.ytm_song_info[0]['videoId']


class Playlist:
    """Handle playlist related tasks"""

    def __init__(self, ytm, playlist_id):
        self.ytm = ytm
        self.playlist_id = playlist_id

        self.content_list = []
        self.ytm_playlist_info = None

    # Get info of each song in playlist
    def get_playlist_info(self):
        self.ytm_playlist_info = self.ytm.get_playlist(playlistId=self.playlist_id, limit=5000)

    # Add each content ids to content list
    def build_content_list(self):
        for content_info in self.ytm_playlist_info['tracks']:
            content_id = content_info['videoId']
            self.content_list.append(content_id)
