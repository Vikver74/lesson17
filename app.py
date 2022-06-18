# app.py

from flask import Flask, request
from flask_restx import Api, Resource
from flask_sqlalchemy import SQLAlchemy
from marshmallow import Schema, fields

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JSON_AS_ASCII'] = False
app.config['RESTX_JSON'] = {'ensure_ascii': False, 'indent': 2}
db = SQLAlchemy(app)


class Movie(db.Model):
    __tablename__ = 'movie'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255))
    description = db.Column(db.String(255))
    trailer = db.Column(db.String(255))
    year = db.Column(db.Integer)
    rating = db.Column(db.Float)
    genre_id = db.Column(db.Integer, db.ForeignKey("genre.id"))
    genre = db.relationship("Genre")
    director_id = db.Column(db.Integer, db.ForeignKey("director.id"))
    director = db.relationship("Director")

class Director(db.Model):
    __tablename__ = 'director'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))


class Genre(db.Model):
    __tablename__ = 'genre'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))


class MovieSchema(Schema):
    id = fields.Int()
    title = fields.Str()
    description = fields.Str()
    trailer = fields.Str()
    year = fields.Int()
    rating = fields.Int()
    genre_id = fields.Int()
    director_id = fields.Int()


class DirectorSchema(Schema):
    id = fields.Int()
    name = fields.Str()


class GenreSchema(Schema):
    id = fields.Int()
    name = fields.Str()


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
        if director_id and genre_id:
            movies = db.session.query(Movie).filter(Movie.director_id == director_id, Movie.genre_id == genre_id).all()
        elif director_id:
            movies = db.session.query(Movie).filter(Movie.director_id == director_id).all()
        elif genre_id:
            movies = db.session.query(Movie).filter(Movie.genre_id == genre_id).all()
        else:
            movies = db.session.query(Movie).all()

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
        # req_dict = director_schema.loads(req_json)
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
        # dict_genre = genre_schema.load(req_json)
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
