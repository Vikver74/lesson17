# app.py

from flask import Flask, request
from flask_restx import Api, Resource
from setup_db import db
from schemas import MovieSchema, DirectorSchema, GenreSchema
from models import Movie, Director, Genre


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['RESTX_JSON'] = {'ensure_ascii': False, 'indent': 2}

db.init_app(app)
app.app_context().push()

movie_schema = MovieSchema()
movies_schema = MovieSchema(many=True)
director_schema = DirectorSchema()
directors_schema = DirectorSchema(many=True)
genre_schema = GenreSchema()
genres_schema = GenreSchema(many=True)


api = Api(app)

movie_ns = api.namespace('movies')
director_ns = api.namespace('directors')
genre_ns = api.namespace('genre')


@movie_ns.route('/')
class MovieView(Resource):
    def get(self):
        director_id = request.args.get('director_id')
        genre_id = request.args.get('genre_id')
        movies = db.session.query(Movie)

        if director_id:
            movies = movies.filter(Movie.director_id == director_id)
        if genre_id:
            movies = movies.filter(Movie.genre_id == genre_id)
        movies = movies.all()

        if len(movies) > 0:
            movies_json = movies_schema.dump(movies)
            return movies_json, 200
        else:
            return "Фильмов, удовлетворяющих заданным параметрам, не найдено", 200


@movie_ns.route('/<int:id>')
class MoviesView(Resource):
    def get(self, id):
        try:
            movie = db.session.query(Movie).filter(Movie.id == id).one()
            movie_json = movie_schema.dump(movie)
            return movie_json, 200

        except Exception as e:
            return str(e), 404


@director_ns.route('')
class DirectorsView(Resource):
    def post(self):
        req_json = request.json
        director = Director(**req_json)
        db.session.add(director)
        db.session.commit()

        return "Запись успешно добавлена", 201

@director_ns.route('/<int:id>')
class DirectorView(Resource):
    def put(self, id):
        director = db.session.query(Director).get(id)
        if not director:
            return "Режиссер с заданным ID не найден", 404
        req_json = request.json
        director.name = req_json['name']
        db.session.add(director)
        db.session.commit()
        return "Изменения в запись о режиссере внесены", 204

    def delete(self, id):
        director = Director.query.get(id)
        if not director:
            return "Режиссер с заданным ID не найден", 404
        db.session.delete(director)
        db.session.commit()

        return "Запись о режиссере успешно удалена", 204


@genre_ns.route('')
class GenresView(Resource):
    def post(self):
        req_json = request.json
        genre = Genre(**req_json)
        db.session.add(genre)
        db.session.commit()

        return "Запись о жанре успешно добавлена", 201

@genre_ns.route('/<int:id>')
class GenreView(Resource):
    def put(self, id):
        genre = db.session.query(Genre).get(id)
        if not genre:
            return "Жанр с заданным ID не найден", 404
        req_json = request.json
        genre.name = req_json['name']
        db.session.add(genre)
        db.session.commit()
        return "Изменения в запись о жанре внесены", 204

    def delete(self, id):
        genre = Genre.query.get(id)
        if not genre:
            return "Жанр с заданным ID не найден", 404
        db.session.delete(genre)
        db.session.commit()

        return "Запись о жанре успешно удалена", 204


if __name__ == '__main__':
    app.run(debug=True)
