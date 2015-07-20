import media
import fresh_tomatoes

# add some movies
movies = []
movies.append(media.Movie("Matrix",
                          "http://ia.media-imdb.com/images/M/MV5BMTkxNDYxOTA4M15BMl5BanBnXkFtZTgwNTk0NzQxMTE@._V1_SX214_AL_.jpg",
                          "https://www.youtube.com/watch?v=m8e-FF8MsqU"))
                          
movies.append(media.Movie("Memento",
                          "http://ia.media-imdb.com/images/M/MV5BMTc4MjUxNDAwN15BMl5BanBnXkFtZTcwMDMwNDg3OA@@._V1_SY317_CR12,0,214,317_AL_.jpg",
                          "https://www.youtube.com/watch?v=UFuFFdK7i44"))

movies.append(media.Movie("The Terminator",
                          "http://ia.media-imdb.com/images/M/MV5BODE1MDczNTUxOV5BMl5BanBnXkFtZTcwMTA0NDQyNA@@._V1_SX214_AL_.jpg",
                          "https://www.youtube.com/watch?v=lHz95RYUbik"))

# produce the html file by using movies
fresh_tomatoes.open_movies_page(movies)
