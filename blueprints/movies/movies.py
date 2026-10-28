from flask import Blueprint, request, make_response, jsonify
import re
from bson import ObjectId

movies_bp = Blueprint("movies_bp", __name__)

movies = globals.db.movies
#check http status coded
#can i extract and reuse any code?
#finish enpoints
#test

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
def show_one_movie(id):
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

# edit movie
@movies_bp.route("/api/v1.0/movies<string:id>", methods=['PATCH'])
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
    
    if re.fullmatch(r"[0-9a-fA-F]{24}", id):
        edited_movie = movies.update_one(
            {"_id": ObjectId(id)},
            {"$set": data}
        )

        if edited_movie.matched_count == 0:
            return make_response(jsonify({"error": "Movie not found"}), 404)
    else:
        return make_response(jsonify({"error": "Invalid movie ID"}), 404)
    edited_movie_url = "http://localhost:5000/api/v1.0/movies/" + id
    return make_response(jsonify({"url:": edited_movie_url}), 200)



# delete movie
@movies_bp.route("/api/v1.0/movies/<string:id>", methods=['DELETE'])
def delete_movie(id):
    if re.fullmatch(r"[0-9a-fA-F]{24}", id):
      movies.delete_one({"_id" : ObjectId(id)})

      return make_response(jsonify({}, 204))
    else:
      return make_response(jsonify({"error": "Invalid movie ID"}))

  

# get movies via keywords

# get movies via genres

#retrieve movies in decending order by year

#retrieve movies in decending order by year