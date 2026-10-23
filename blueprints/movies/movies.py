from flask import Blueprint, request, make_response, jsonify
import re
from bson import ObjectId

movies_bp = Blueprint("movies_bp", __name__)

movies = globals.db.movies

# get movies
@movies_bp.route("/api/v1.0/movies", methods=['GET'])
def show_all_movies():
    page_num = request.args.get("page_num", default=1, type=int)
    per_page = request.args.get("per_page", default=10, type=int)

    skip = (page_num - 1) * per_page
    
    movies_data = []
    for movie in movies.find().skip(skip).limit(per_page):
        movie['_id'] = str(movie['_id'])
        for review in movie['reviews']:
            review['_id'] = str(review['_id'])
        movies_data.append(movie)

    return make_response(jsonify(movies_data), 200)



# get movie
@movies_bp.route("/api/v1.0/movie/<string:id>", methods=['GET'])
def show_one_movie():
    if re.fullmatch(r"[0-9a-fA-F]{24}", id):
        movie = movies.find_one({'_id': ObjectId(id)})
        if movie is not None:
            movie['_id'] = str(movie['_id'])
            for review in movie['reviews']:
                review['_id'] = str(movie['_id'])
        else: 
            return make_response(jsonify({"error" : "Invalid movie ID"}), 404)
    else:
        return make_response(jsonify({"error" : "Invalid ID"}), 404)


# add movie
@movies_bp.route("/api/v1.0/movies", methods=['POST'])


# edit movie
@movies_bp.route("/api/v1.0/movies<string:id>", methods=['PUT'])

# delete movie
@movies_bp.route("/api/v1.0/movies/<string:id>", methods=['DELETE'])

# get movies via keywords

# get movies via genres
