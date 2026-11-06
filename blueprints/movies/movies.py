import re

from flask import Blueprint, request, make_response, jsonify
import jwt
from blueprints.movies import movie_validator as validator
from decorators import jwt_required, admin_required
from bson import ObjectId
import globals
import utils

movies_bp = Blueprint("movies_bp", __name__)

movies = globals.db.movies

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
        movie["_id"] = str(movie["_id"])
        for review in movie.get('reviews', []):
            review["_id"] = str(review["_id"])
            if review.get("user_id") is not None:
                review["user_id"] = str(review["user_id"])
        movies_data.append(movie)

    total_movies = movies.count_documents({})
    total_pages = utils.get_total_pages(total_movies, per_page)
        
    return make_response(jsonify({"results": movies_data,
                                  "total_pages": total_pages,
                                  "current_page": page_num,
                                  "total_items": total_movies,
                                  "per_page": per_page
                                  }), 200)


@movies_bp.route("/api/v1.0/movies/search", methods=['GET'])
def search_movies():
    pagination = utils.get_pagination(request.args)
    if pagination is None:
        return make_response(jsonify({
            "error": "page_num and per_page must be positive integers"
        }), 400)
    page_num, per_page = pagination

    keyword = request.args.get("keyword", "").strip()
    genre = request.args.get("genre", "").strip()

    if not keyword and not genre:
        return make_response(jsonify({"error": "No keyword or genre provided"}), 400)

    filters = {}
    if keyword:
        filters["keywords"] = re.compile(
            f"^{re.escape(keyword)}$",
            re.IGNORECASE
        )
    if genre:
        filters["genres"] = re.compile(
            f"^{re.escape(genre)}$",
            re.IGNORECASE
        )

    pipeline = [
        {"$match": filters},
        {"$skip": (page_num - 1) * per_page},
        {"$limit": per_page}
    ]

    movies_data = list(movies.aggregate(pipeline))
    for movie in movies_data:
        movie["_id"] = str(movie["_id"])
        for review in movie.get("reviews", []):
            review["_id"] = str(review["_id"])
            if review.get("user_id") is not None:
                review["user_id"] = str(review["user_id"])
    total_movies = movies.count_documents(filters)
    return make_response(jsonify({
        "results": movies_data,
        "total_pages": utils.get_total_pages(total_movies, per_page),
        "current_page": page_num,
        "total_items": total_movies,
        "per_page": per_page
    }), 200)


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
            if review.get("user_id") is not None:
                review["user_id"] = str(review["user_id"])
        movies_data.append(movie)

    total_movies = movies.count_documents({})
    return make_response(jsonify({
        "results": movies_data,
        "total_pages": utils.get_total_pages(total_movies, per_page),
        "current_page": page_num,
        "total_items": total_movies,
        "per_page": per_page
    }), 200)

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
    for movie in movies.find().sort("release_year", 1).skip(skip).limit(per_page):
        movie["_id"] = str(movie["_id"])
        for review in movie.get("reviews", []):
            review["_id"] = str(review["_id"])
            if review.get("user_id") is not None:
                review["user_id"] = str(review["user_id"])
        movies_data.append(movie)

    total_movies = movies.count_documents({})
    return make_response(jsonify({
        "results": movies_data,
        "total_pages": utils.get_total_pages(total_movies, per_page),
        "current_page": page_num,
        "total_items": total_movies,
        "per_page": per_page
    }), 200)

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
    filters = {"flags.is_popular": True}
    for movie in movies.find(filters).skip(skip).limit(per_page):
        movie["_id"] = str(movie["_id"])
        for review in movie.get("reviews", []):
            review["_id"] = str(review["_id"])
            if review.get("user_id") is not None:
                review["user_id"] = str(review["user_id"])
        movies_data.append(movie)

    total_movies = movies.count_documents(filters)
    return make_response(jsonify({
        "results": movies_data,
        "total_pages": utils.get_total_pages(total_movies, per_page),
        "current_page": page_num,
        "total_items": total_movies,
        "per_page": per_page
    }), 200)

@movies_bp.route("/api/v1.0/movies/has-reviews", methods=['GET'])
def get_movies_with_reviews():
    pagination = utils.get_pagination(request.args)
    if pagination is None:
        return make_response(jsonify({
            "error": "page_num and per_page must be positive integers"
        }), 400)
    page_num, per_page = pagination
           
           
    skip = (page_num - 1) * per_page
    movies_data = []
    filters = {"flags.has_reviews": True}
    for movie in movies.find(filters).skip(skip).limit(per_page):
        movie["_id"] = str(movie["_id"])
        for review in movie.get("reviews", []):
            review["_id"] = str(review["_id"])
            if review.get("user_id") is not None:
                review["user_id"] = str(review["user_id"])
        movies_data.append(movie)

    total_movies = movies.count_documents(filters)
    return make_response(jsonify({
        "results": movies_data,
        "total_pages": utils.get_total_pages(total_movies, per_page),
        "current_page": page_num,
        "total_items": total_movies,
        "per_page": per_page
    }), 200)

@movies_bp.route("/api/v1.0/movies/title", methods=['GET'])
def show_one_movie():
    title = request.args.get("title", "").strip()

    if not title:
        return make_response(jsonify({"error": "Title cannot be empty"}), 400)
    
    title_pattern = re.compile(
        f"^{re.escape(title)}$",
        re.IGNORECASE
    ) 
    movie = movies.find_one({'title': title_pattern})

    if movie is None:
        return make_response(jsonify({"error": "No movie found"}), 404)

    movie['_id'] = str(movie['_id'])
    for review in movie['reviews']:
         review['_id'] = str(review['_id'])
         if review.get("user_id") is not None:
             review["user_id"] = str(review["user_id"])

    return make_response(jsonify(movie), 200)



@movies_bp.route("/api/v1.0/movies", methods=['POST'])
@jwt_required
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
        "directors",
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

    invalid_fields = validator.get_invalid_movie_fields(data)
    if invalid_fields:
        return make_response(jsonify({
            "error": "Invalid values for movie fields",
            "fields": invalid_fields
        }), 400)

    new_movie_id = movies.insert_one(data)
    new_movie_url = "http://localhost:5000/api/v1.0/movies/" \
    + str(new_movie_id.inserted_id)
    return make_response(jsonify({"url": new_movie_url, 
                                  "message": "Movie added successfully"}), 201)


@movies_bp.route("/api/v1.0/movies/<string:id>", methods=['PATCH'])
@jwt_required
@admin_required
def edit_movie(id):

    data = request.get_json(silent=True)
         
    if not isinstance(data, dict) or not data:
                       return make_response(jsonify({"error": "Request body must be a JSON object"}), 400)

    allowed_fields = [
            "title",
            "overview", 
            "release_year",
            "production_companies",
            "runtime",
            "genres",
            "keywords",
            "directors",
            "cast",
            "statistics",
            "flags"
    ]

    invalid_fields = []

    for field in data:
        if field not in allowed_fields:
            invalid_fields.append(field)

    if invalid_fields:
        return make_response(jsonify({"error": "Fields cannot be updated", "fields": invalid_fields}), 400)

    invalid_values = validator.get_invalid_movie_fields(data)
    if invalid_values:
        return make_response(jsonify({
            "error": "Invalid values for movie fields",
            "fields": invalid_values
        }), 400)
    
    if utils.is_valid_object_id(id):
        edited_movie = movies.update_one(
            {"_id": ObjectId(id)},
            {"$set": data}
        )
    
        if edited_movie.matched_count == 0:
            return make_response(jsonify({"error": "Movie not found"}), 404)
        else:
            edited_movie_url = "http://localhost:5000/api/v1.0/movies/" + id
            return make_response(jsonify({"url:": edited_movie_url, "message": "Movie edited successfully"}), 200)
    else:
        return make_response(jsonify({"error": "Invalid movie ID"}), 400)


@movies_bp.route("/api/v1.0/movies/<string:id>", methods=['DELETE'])
@jwt_required
@admin_required
def delete_movie(id):
    if utils.is_valid_object_id(id):
       deleted_movie = movies.delete_one({"_id" : ObjectId(id)})

       if deleted_movie.deleted_count == 0:
             return make_response(jsonify({"error": "No movie found"}), 404)
       else:
             return make_response(jsonify({"message": "Movie deleted successfully"}), 204)

    else:
       return make_response(jsonify({"error": "Invalid movie ID"}), 400)