from flask import Blueprint, request, make_response,jsonify
import re
from bson import ObjectId
import globals
import utils

reviews_bp = Blueprint("reviews_bp", __name__)

movies = globals.db.movies

#add authenication
#test

@reviews_bp.route("/api/v1.0/movies/<string:id>/reviews", methods=["POST"])
def add_review(id):
    data = request.get_json(silent=True)

    if not isinstance(data, dict) or not data:
        return make_response(jsonify({"error": "Request body must be a JSON object"}), 400)

    required_fields = [
        "name",
        "comment",
        "stars"
    ]

    if set(data) != set(required_fields):
        return make_response(jsonify({"error": "JSON fields do not match fields required",
                                      "missing": list(set(required_fields) - set(data)),
                                      "unexpected": list(set(data) - set(required_fields))}), 400)
    
    if utils.is_valid_object_id(id):

      new_review = {
              "_id" : ObjectId(),
              "name" : data["name"],
              "comment" : data["comment"],
              "stars" : data["stars"]
          }

      result = movies.update_one({"_id" : ObjectId(id)},
                               {"$push": {"reviews" : new_review}})
      if result.matched_count == 1:
          new_review_url = "/api/v1.0/movies/" + id + "/reviews/" + str(new_review["_id"])
          return make_response(jsonify({"url" : new_review_url}), 201)
      else:
          return make_response(jsonify({"error" : "No movie found"}), 404)
    else: 
        return make_response(jsonify({"error" : "Invalid movie ID"}), 400)

@reviews_bp.route("/api/v1.0/movies/<string:id>/reviews", methods=["GET"])
def get_all_reviews(id):
    pagination = utils.get_pagination(request.args)
    if pagination is None:
        return make_response(jsonify({
            "error": "page_num and per_page must be positive integers"
        }), 400)
    page_num, per_page = pagination

    if utils.is_valid_object_id(id):
        movie = movies.find_one(
            {"_id" : ObjectId(id)},
            {"reviews" : 1, "_id" : 0}
        )
        if movie is None:
            return make_response(jsonify({"error" : "No movie found"}), 404)
        start = (page_num - 1) * per_page
        page_reviews = movie.get("reviews", [])[start:start + per_page]
        review_data = []
        for review in page_reviews:
            review["_id"] = str(review["_id"])
            review_data.append(review)
        return make_response(jsonify(review_data), 200)
    else:
        return make_response(jsonify({"error" : "Invalid movie ID"}), 400)
    
@reviews_bp.route("/api/v1.0/movies/<string:mid>/reviews/<string:rid>", methods=["GET"])
def get_review(mid, rid):
    if utils.is_valid_object_id(mid):
        movie = movies.find_one(
            {"_id" : ObjectId(mid)},
            {"reviews" : 1}
        )
        if movie is None:
            return make_response(jsonify({"error" : "No movie found"}), 404)
        
        if utils.is_valid_object_id(rid):

          review_id = ObjectId(rid)
          review = None
          for item in movie["reviews"]:
              if item["_id"] == review_id:
                  review = item
                  break
          if review is None:
              return make_response(jsonify({"error" : "No review found"}), 404)
          review["_id"] = str(review["_id"])
          return make_response(jsonify(review), 200)
        else:
            return make_response(jsonify({"error" : "Invalid review ID"}), 400)
    else:
        return make_response(jsonify({"error" : "Invalid movie ID"}), 400)


@reviews_bp.route("/api/v1.0/movies/<string:mid>/reviews/<string:rid>", methods=["PATCH"])
def edit_review(mid, rid):
    if utils.is_valid_object_id(mid):
           movie_id = ObjectId(mid)
           movie = movies.find_one({"_id" : movie_id})
           if movie is None:
               return make_response(jsonify({"error" : "No movie found"}), 404)
           
           if utils.is_valid_object_id(rid):
               review_id = ObjectId(rid)
               if not any(review["_id"] == review_id for review in movie["reviews"]):
                   return make_response(jsonify({"error" : "No review found"}), 404)

               data = request.get_json(silent=True)
               
               if not isinstance(data, dict) or not data:
                       return make_response(jsonify({"error": "Request body must be a JSON object"}), 400)
               
               allowed_fields = [
                       "name",
                       "comment",
                       "stars"
                   ]
               invalid_fields = []

               for field in data:
                   if field not in allowed_fields:
                       invalid_fields.append(field)

               if invalid_fields:
                   return make_response(jsonify({
                       "error": "Fields cannot be updated",
                       "fields": invalid_fields
                   }), 400)
                       
               update_fields = {
                   f"reviews.$.{field}": value
                   for field, value in data.items()
               }
               result = movies.update_one(
                   {"_id": movie_id, "reviews._id": review_id},
                   {"$set": update_fields}
               )
               if result.matched_count == 0:
                   return make_response(jsonify({"error": "No review found"}), 404)

               edited_review_url = "http://localhost:5000/api/v1.0/movies/" + mid + "/reviews/" + rid
        
               return make_response(jsonify({"url" : edited_review_url}), 200)
           else:
               return make_response(jsonify({"error" : "Invalid review ID"}), 400)
    else:
         return make_response(jsonify({"error" : "Invalid movie ID"}), 400)

#delete review
@reviews_bp.route("/api/v1.0/movies/<string:mid>/reviews/<string:rid>", methods=["DELETE"])
def delete_review(mid, rid):
    if utils.is_valid_object_id(mid):
       movie_id = ObjectId(mid)
       movie = movies.find_one({"_id" : movie_id})
       if movie is None:
           return make_response(jsonify({"error" : "No movie found"}), 404)
       
       if utils.is_valid_object_id(rid):
           review_id = ObjectId(rid)
           if not any(review["_id"] == review_id for review in movie["reviews"]):
               return make_response(jsonify({"error" : "No review found"}), 404)
           result = movies.update_one(
               {"_id" : movie_id, "reviews._id" : review_id},
               {"$pull" : {"reviews" : {"_id" : review_id}}}
           )
           if result.modified_count == 0:
               return make_response(jsonify({"error": "No review found"}), 404)
           return make_response(jsonify({}), 204)
       else:
           return make_response(jsonify({"error" : "Invalid review ID"}), 400)
    else:
        return make_response(jsonify({"error" : "Invalid movie ID"}), 400)


       
