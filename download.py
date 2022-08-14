import mutagen
from yt_dlp import YoutubeDL
from requests import get
from base64 import b64encode
from mutagen.oggopus import OggOpus
from mutagen.flac import Picture


class Download:
    """Download content and apply metadata"""

    def __init__(self, content_id, cover_url, id_filename, title, artist, date, album, album_artist):
        self.content_id = content_id
        self.cover_url = cover_url

        self.id_filename = id_filename

        self.title = title
        self.artist = artist
        self.date = date
        self.album = album
        self.album_artist = album_artist

        if id_filename:
            self.filename = self.content_id
        else:
            self.filename = f'{self.artist} - {self.title}'

    # Download content using yt-dlp and apply text metadata
    def dl_content(self):
        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': f'{self.filename}.%(ext)s',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'opus',
            }],
            'postprocessor_args': [
                '-metadata', f'title={self.title}',
                '-metadata', f'album={self.album}',
                '-metadata', f'artist={self.artist}',
                '-metadata', f'album_artist={self.album_artist}',
                '-metadata', f'date={self.date}'
            ]
        }
        with YoutubeDL(ydl_opts) as ydl:
            ydl.download(self.content_id)

    # Download cover using cover url
    def dl_cover(self):
        get_cover = get(self.cover_url)
        open('cover.jpg', 'wb').write(get_cover.content)

    # Apply cover to output file
    def apply_cover(self):
        try:
            content_file = OggOpus(f'{self.filename}.opus')
        except mutagen.MutagenError:
            print('\033[0;31mError: Invalid characters in filename. Consider using -i argument\033[0m')
            return

        cover = Picture()

        with open('cover.jpg', 'rb') as cover_file:
            raw_data = cover_file.read()

        cover.data = raw_data
        cover_data = cover.write()
        encoded_data = b64encode(cover_data)
        vcomment_value = encoded_data.decode('ascii')

        content_file['metadata_block_picture'] = [vcomment_value]
        content_file.save()
