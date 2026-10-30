from flask import Blueprint, request, make_response, jsonify
import re
from bson import ObjectId
import globals
import utils

movies_bp = Blueprint("movies_bp", __name__)

movies = globals.db.movies


#finish enpoints
#test


@movies_bp.route("/api/v1.0/movies", methods=['GET'])
def show_all_movies():
    pagination = utils.get_pagination(request.args)
    if pagination is None:
        return make_response(jsonify({
            "error": "page_num and per_page must be positive integers"
        }), 400)
    page_num, per_page = pagination

    skip = (page_num - 1) * per_page
    
    movies_data = []
    for movie in movies.find().skip(skip).limit(per_page):
        movie['_id'] = str(movie['_id'])
        for review in movie.get('reviews', []):
            review['_id'] = str(review['_id'])
        movies_data.append(movie)

    return make_response(jsonify(movies_data), 200)


@movies_bp.route("/api/v1.0/movies/keyword", methods=['GET'])
def get_movies_by_keyword():
    pagination = utils.get_pagination(request.args)
    if pagination is None:
        return make_response(jsonify({
            "error": "page_num and per_page must be positive integers"
        }), 400)
    page_num, per_page = pagination

    keyword = request.args.get("keyword", "").strip()
    if not keyword:
        return make_response(jsonify({"error": "Keyword is required"}), 400)

    skip = (page_num - 1) * per_page
    movies_data = []
    for movie in movies.find({"keywords": keyword}).skip(skip).limit(per_page):
        movie["_id"] = str(movie["_id"])
        for review in movie.get("reviews", []):
            review["_id"] = str(review["_id"])
        movies_data.append(movie)

    return make_response(jsonify(movies_data), 200)


@movies_bp.route("/api/v1.0/movies/genre", methods=['GET'])
def get_movies_by_genre():
    pagination = utils.get_pagination(request.args)
    if pagination is None:
        return make_response(jsonify({
            "error": "page_num and per_page must be positive integers"
        }), 400)
    page_num, per_page = pagination

    genre = request.args.get("genre", "").strip()
    if not genre:
        return make_response(jsonify({"error": "Genre is required"}), 400)

    skip = (page_num - 1) * per_page
    movies_data = []
    for movie in movies.find({"genres": genre}).skip(skip).limit(per_page):
        movie["_id"] = str(movie["_id"])
        for review in movie.get("reviews", []):
            review["_id"] = str(review["_id"])
        movies_data.append(movie)

    return make_response(jsonify(movies_data), 200)

@movies_bp.route("/api/v1.0/movies/descending", methods=['GET'])
def get_movies_by_year_decending():
    pagination = utils.get_pagination(request.args)
    if pagination is None:
        return make_response(jsonify({
            "error": "page_num and per_page must be positive integers"
        }), 400)
    page_num, per_page = pagination
       
       
    skip = (page_num - 1) * per_page
    movies_data = []
    for movie in movies.find().sort("release_year", -1).skip(skip).limit(per_page):
        movie["_id"] = str(movie["_id"])
        for review in movie.get("reviews", []):
            review["_id"] = str(review["_id"])
        movies_data.append(movie)
       
    return make_response(jsonify(movies_data), 200)

@movies_bp.route("/api/v1.0/movies/ascending", methods=['GET'])
def get_movies_by_year_ascending():
    pagination = utils.get_pagination(request.args)
    if pagination is None:
        return make_response(jsonify({
            "error": "page_num and per_page must be positive integers"
        }), 400)
    page_num, per_page = pagination
           
           
    skip = (page_num - 1) * per_page
    movies_data = []
    for movie in movies.find({"flags.is_popular" : True}).skip(skip).limit(per_page):
        movie["_id"] = str(movie["_id"])
        for review in movie.get("reviews", []):
            review["_id"] = str(review["_id"])
        movies_data.append(movie)
           
    return make_response(jsonify(movies_data), 200)

@movies_bp.route("/api/v1.0/movies/ascending", methods=['GET'])
def get_movies_by_year_ascending():
    pagination = utils.get_pagination(request.args)
    if pagination is None:
        return make_response(jsonify({
            "error": "page_num and per_page must be positive integers"
        }), 400)
    page_num, per_page = pagination
           
           
    skip = (page_num - 1) * per_page
    movies_data = []
    for movie in movies.find({"flags.has_reviews" : True}).skip(skip).limit(per_page):
        movie["_id"] = str(movie["_id"])
        for review in movie.get("reviews", []):
            review["_id"] = str(review["_id"])
        movies_data.append(movie)
           
    return make_response(jsonify(movies_data), 200)

@movies_bp.route("/api/v1.0/movies/popular", methods=['GET'])
def get_popular_movies():
    pagination = utils.get_pagination(request.args)
    if pagination is None:
        return make_response(jsonify({
            "error": "page_num and per_page must be positive integers"
        }), 400)
    page_num, per_page = pagination
           
           
    skip = (page_num - 1) * per_page
    movies_data = []
    for movie in movies.find().sort("release_year", 1).skip(skip).limit(per_page):
        movie["_id"] = str(movie["_id"])
        for review in movie.get("reviews", []):
            review["_id"] = str(review["_id"])
        movies_data.append(movie)
           
    return make_response(jsonify(movies_data), 200)



@movies_bp.route("/api/v1.0/movies/<string:id>", methods=['GET'])
def show_one_movie(id):
    if utils.is_valid_object_id(id):
        movie = movies.find_one({'_id': ObjectId(id)})
        if movie is not None:
            movie['_id'] = str(movie['_id'])
            for review in movie['reviews']:
                review['_id'] = str(movie['_id'])
            return make_response(jsonify(movie), 200)
        else: 
            return make_response(jsonify({"error" : "No movie found"}), 404)
    else:
        return make_response(jsonify({"error" : "Invalid ID"}), 400)


@movies_bp.route("/api/v1.0/movies", methods=['POST'])
def add_movie():
    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return make_response(jsonify({"error": "Request body must be a JSON object"}), 400)

    required_fields = [
        "title",
        "overview", 
        "release_year",
        "production_companies",
        "runtime",
        "genres",
        "keywords",
        "director",
        "cast",
        "statistics",
        "flags"
    ]

    missing_fields = []

    for field in required_fields:
        if field not in data:
            missing_fields.append(field)
  
    if missing_fields:
        return make_response(jsonify({"error": "Missing fields", "fields": missing_fields}), 400)

    new_movie_id = movies.insert_one(data)
    new_movie_url = "http://localhost:5000/api/v1.0/movies/" \
    + str(new_movie_id.inserted_id)
    return make_response(jsonify({"url": new_movie_url}), 201)


@movies_bp.route("/api/v1.0/movies/<string:id>", methods=['PATCH'])
def edit_movie(id):
    data = request.get_json(silent=True)
         
    if not isinstance(data, dict) or not data:
        return make_response(jsonify({"error": "Send fields to update as a JSON object"}), 400)

    allowed_fields = [
            "title",
            "overview", 
            "release_year",
            "production_companies",
            "runtime",
            "genres",
            "keywords",
            "director",
            "cast",
            "statistics",
            "flags"
    ]

    invalid_fields = []

    for field in data:
        if field not in allowed_fields:
            invalid_fields.append(field)

        if invalid_fields:
            return make_response(jsonify({"error": "Fields can not be updated: " + invalid_fields}), 400)
    
    if utils.is_valid_object_id(id):
        edited_movie = movies.update_one(
            {"_id": ObjectId(id)},
            {"$set": data}
        )
    
        if edited_movie.matched_count == 0:
            return make_response(jsonify({"error": "Movie not found"}), 404)
        else:
            edited_movie_url = "http://localhost:5000/api/v1.0/movies/" + id
            return make_response(jsonify({"url:": edited_movie_url}), 200)
    else:
        return make_response(jsonify({"error": "Invalid movie ID"}), 404)


@movies_bp.route("/api/v1.0/movies/<string:id>", methods=['DELETE'])
def delete_movie(id):
    if utils.is_valid_object_id(id):
       deleted_movie = movies.delete_one({"_id" : ObjectId(id)})

       if deleted_movie.deleted_count == 0:
             return make_response(jsonify({"error": "No movie found"}), 404)

       else:
             return "", 204

    else:
       return make_response(jsonify({"error": "Invalid movie ID"}), 400)



#retrive movies based on popularity

#retrieve movies based on having reviews