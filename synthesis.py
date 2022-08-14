import query
import metadata
import download


class Synthesis:
    """Main program class. Links all program components together."""

    def __init__(self):
        self.q = None
        self.b = None

        self.m = None
        self.d = None

        self.p = None

        self.vts = None
        self.vts_converted = False

        self.link_type = ''

        self.content_id = ''
        self.playlist_id = ''

        self.content_num = 1
        self.current_pos = 1

    # Gather user input and initialize program
    def process_query(self):
        self.q = query.Query()

        self.q.query_args()

        self.b = metadata.BasicInfo(url=self.q.url, ytm_setup=self.q.ytm_setup)

        self.b.initialize_ytm()
        self.b.find_link_type()
        self.link_type = self.b.link_type
        self.b.find_url_id()

        if self.link_type == 'playlist':
            self.playlist_id = self.b.url_id
        else:
            self.content_id = self.b.url_id

    # Handle all content related tasks
    def dl_content(self, auto_content_type: bool = True):
        print(f'\033[0;32mPreparing download \033[1;32m{self.current_pos}/{self.content_num}\033[0m')

        crop_cover = False

        if auto_content_type:
            self.b.find_content_type(search_string=self.content_id)

        if self.b.content_type == 'song':
            self.m = metadata.Song(ytm=self.b.ytm, ytm_song_info=self.b.ytm_song_info)
        elif self.b.content_type == 'video':
            self.m = metadata.Video(ytm=self.b.ytm, content_id=self.content_id)

            if self.q.video_to_song and not self.vts_converted or self.q.vts_prompt and not self.vts_converted:
                self.m.find_metadata()
                self.convert_vts()
                return

            crop_cover = True
        elif self.b.content_type is None:
            return

        self.m.find_metadata()
        self.m.find_cover_url()

        print(f'\033[0;32mDownloading \033[1;32m{self.m.title}\033[0m')

        self.d = download.Download(content_id=self.content_id, title=self.m.title, artist=self.m.artist,
                                   date=self.m.date, album=self.m.album, album_artist=self.m.album_artist,
                                   cover_url=self.m.cover_url, id_filename=self.q.id_filename)

        self.d.dl_content()
        self.d.dl_cover()

        if crop_cover:
            self.m.crop_cover()

        self.d.apply_cover()

    # Download every song or video in playlist
    def dl_playlist(self):
        self.p = metadata.Playlist(ytm=self.b.ytm, playlist_id=self.playlist_id)
        self.p.get_playlist_info()
        self.p.build_content_list()

        self.content_num = len(self.p.content_list)

        for self.content_id in self.p.content_list:
            self.dl_content()
            self.current_pos += 1

        self.content_num = 1
        self.current_pos = 1

    # Convert content from video to song
    def convert_vts(self):
        print(f'\033[0;34mConverting \033[1;34m{self.m.title}\033[0;34m to a song\033[0m')

        self.vts = metadata.VideoToSong(b_obj=self.b, title=self.m.title, artist=self.m.artist)

        if self.q.vts_prompt:
            self.vts.vts_prompt()

        if self.vts.convert:
            self.vts.find_is_convertible()

        if self.vts.convertible:
            self.content_id = self.vts.song_id
        elif not self.vts.convert:
            print('\033[0;34mDownloading video...\033[0m')
        elif not self.vts.convertible:
            print('\033[0;34mNo song found. Downloading video...\033[0m')

        self.vts_converted = True
        self.dl_content(auto_content_type=False)
        self.vts_converted = False


# Main program function. Executes main program components.
def main():
    s = Synthesis()
    s.process_query()

    if s.link_type == 'long_url' or s.link_type == 'short_url':
        s.dl_content()
    elif s.link_type == 'playlist':
        s.dl_playlist()
    else:
        print('\033[0;31mError: Wrong link type\033[0m')


# Entry point
if __name__ == '__main__':
    main()
