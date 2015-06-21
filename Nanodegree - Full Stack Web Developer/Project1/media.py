class Movie:
    """Holds info for the movies"""
    
    def __init__(self, title,poster_image_url,trailer_youtube_url):
        """"sets necessary fields"""
        self.title = title
        self.poster_image_url = poster_image_url
        self.trailer_youtube_url = trailer_youtube_url
