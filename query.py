from argparse import ArgumentParser


class Query:
    """Handle user input related tasks"""

    def __init__(self):
        self.url = ''

        self.video_to_song = False
        self.vts_prompt = False

        self.ytm_setup = False
        self.id_filename = False

    # Parse arguments entered by user
    def query_args(self):
        parser = ArgumentParser(prog='synthesis', usage='%(prog)s [options] url')
        vts_args = parser.add_mutually_exclusive_group()

        parser.add_argument('url', type=str, action='store', help='YouTube url')

        vts_args.add_argument('-s', '--song', action='store_true', help='find a YouTube Music song using the video'
                                                                        'title for all processed videos')
        vts_args.add_argument('-p', '--prompt', action='store_true', help='prompt the user to find a YouTube Music song'
                                                                          ' using the video title for each processed '
                                                                          'video')

        parser.add_argument('-a', '--auth', action='store_true', help='setup authenticated ytmusicapi requests')
        parser.add_argument('-i', '--id', action='store_true', help='use content id as filename')

        args = parser.parse_args()

        self.url = args.url
        self.video_to_song = args.song
        self.vts_prompt = args.prompt
        self.ytm_setup = args.auth
        self.id_filename = args.id
