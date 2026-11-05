from flask import Blueprint, request, make_response,jsonify
from blueprints.reviews import review_validator as validator
from decorators import jwt_required, admin_required
from bson import ObjectId
import globals
import utils
import jwt


reviews_bp = Blueprint("reviews_bp", __name__)

movies = globals.db.movies

def can_manage_review(user, review_user_id):
   return user["admin"] or user["_id"] == review_user_id

@reviews_bp.route("/api/v1.0/movies/<string:id>/reviews", methods=["POST"])
@jwt_required
def add_review(id):
    data = request.get_json(silent=True)

    if not isinstance(data, dict) or not data:
        return make_response(jsonify({"error": "Request body must be a JSON object"}), 400)

    invalid_review_fields = validator.get_invalid_review_fields(data)
    if invalid_review_fields:
        return make_response(jsonify({"error": "Invalid review fields", "fields": invalid_review_fields}), 400)

    comment = data["comment"]
    stars = data["stars"]
    
    if utils.is_valid_object_id(id):

        token = request.headers.get('x-access-token')
        decoded_token = jwt.decode(token, globals.secret_key, algorithms=["HS256"])
        logged_in_user = decoded_token.get('user')

        user = globals.db.users.find_one({"username": logged_in_user})
        if user is None:
            return make_response(jsonify({"error": "Authenticated user not found"}), 401)

        new_review = {
              "_id" : ObjectId(),
              "user_id" : user["_id"],
              "username" : logged_in_user,
              "name" : user["name"],
              "comment" : comment.strip(),
              "stars" : stars
          }

        result = movies.update_one({"_id" : ObjectId(id)},
                               {"$push": {"reviews" : new_review}})
        if result.matched_count == 1:
            new_review_url = "http://localhost:5000/api/v1.0/movies/" + id + "/reviews/" + str(new_review["_id"])
            return make_response(jsonify({"url" : new_review_url, "message": "Review added successfully"}), 201)
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

    if not utils.is_valid_object_id(id):
        return make_response(jsonify({"error": "Invalid movie ID"}), 400)

    movie_id = ObjectId(id)
    movie = movies.find_one({"_id": movie_id}, {"reviews": 1})
    if movie is None:
        return make_response(jsonify({"error": "No movie found"}), 404)

    total_reviews = len(movie.get("reviews", []))

    skip = (page_num - 1) * per_page

    pipeline = [
           {"$match": {"_id": movie_id}},
           {"$project": {"reviews": 1}},
           {"$unwind": "$reviews"},
           {"$skip": skip},
           {"$limit": per_page},
           {
               "$project": {
                   "_id": {"$toString": "$reviews._id"},
                   "user_id": {"$toString": "$reviews.user_id"},
                   "username": "$reviews.username",
                   "name": "$reviews.name",
                   "comment": "$reviews.comment",
                   "stars": "$reviews.stars"
            }
        }
    ]

    review_data = list(movies.aggregate(pipeline))
    return make_response(jsonify({
        "results": review_data,
        "total_pages": utils.get_total_pages(total_reviews, per_page),
        "current_page": page_num,
        "total_items": total_reviews,
        "per_page": per_page
    }), 200)
        
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
          review["user_id"] = str(review["user_id"])
          return make_response(jsonify(review), 200)
        else:
            return make_response(jsonify({"error" : "Invalid review ID"}), 400)
    else:
        return make_response(jsonify({"error" : "Invalid movie ID"}), 400)

@reviews_bp.route("/api/v1.0/movies/<string:id>/reviews/stats", methods=["GET"])
def get_movie_review_stats(id):
    if not utils.is_valid_object_id(id):
        return make_response(jsonify({"error": "Invalid movie ID"}), 400)

    movie = movies.find_one({"_id": ObjectId(id)}, {"reviews": 1})
    if movie is None:
        return make_response(jsonify({"error": "No movie found"}), 404)

    pipeline = [
        {"$match": {"_id": ObjectId(id)}},
        {"$unwind": "$reviews"},
        {
            "$group": {
                "_id": "$_id",
                "total_reviews": {"$sum": 1},
                "average_stars": {"$avg": "$reviews.stars"},
                "minimum_stars": {"$min": "$reviews.stars"},
                "maximum_stars": {"$max": "$reviews.stars"}
            }
        },
        {
            "$project": {
                "_id": 0,
                "total_reviews": 1,
                "average_stars": {"$round": ["$average_stars", 1]},
                "minimum_stars": 1,
                "maximum_stars": 1
            }
        }
    ]

    stats = next(movies.aggregate(pipeline), None)
    if stats is None:
        return make_response(jsonify({
            "total_reviews": 0,
            "average_stars": None,
            "minimum_stars": None,
            "maximum_stars": None
        }), 200)
    return make_response(jsonify(stats), 200)

@reviews_bp.route("/api/v1.0/movies/<string:mid>/reviews/<string:rid>", methods=["PATCH"])
@jwt_required
def edit_review(mid, rid):
    if utils.is_valid_object_id(mid):
           movie_id = ObjectId(mid)

           movie = movies.find_one({"_id" : movie_id})

           if movie is None:
               return make_response(jsonify({"error" : "No movie found"}), 404)
           
           if utils.is_valid_object_id(rid):
               review_id = ObjectId(rid)

               review = next(
                   (review for review in movie["reviews"] if review["_id"] == review_id),
                   None
                )
               if review is None:
                    return make_response(jsonify({"error" : "No review found"}), 404)

               token = request.headers.get('x-access-token')
               decoded_token = jwt.decode(token, globals.secret_key, algorithms=["HS256"])
               logged_in_user = decoded_token.get('user')

               user = globals.db.users.find_one({"username": logged_in_user})
               
               if user is None:
                   return make_response(jsonify({"error" : "User not found"}), 404)
               
               if not can_manage_review(user, review["user_id"]):
                   return make_response(jsonify({"error" : "Unauthorized to edit this review"}), 403)

               data = request.get_json(silent=True)

               if not isinstance(data, dict) or not data:
                       return make_response(jsonify({"error": "Request body must be a JSON object"}), 400)

               invalid_review_fields = validator.get_invalid_review_fields(data)
               if invalid_review_fields:
                   return make_response(jsonify({"error": "Invalid review fields", "fields": invalid_review_fields}), 400)

               allowed_fields = [
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
               movies.update_one(
                   {"_id": movie_id, "reviews._id": review_id},
                   {"$set": update_fields}
               )

               edited_review_url = "http://localhost:5000/api/v1.0/movies/" + mid + "/reviews/" + rid
        
               return make_response(jsonify({"url" : edited_review_url, "message": "Review edited successfully"}), 200)
           else:
               return make_response(jsonify({"error" : "Invalid review ID"}), 400)
    else:
         return make_response(jsonify({"error" : "Invalid movie ID"}), 400)
    
@reviews_bp.route("/api/v1.0/movies/<string:mid>/reviews/<string:rid>", methods=["DELETE"])
@jwt_required
def delete_review(mid, rid):
    if utils.is_valid_object_id(mid):
       movie_id = ObjectId(mid)
       movie = movies.find_one({"_id" : movie_id})
       if movie is None:
           return make_response(jsonify({"error" : "No movie found"}), 404)
       
       if utils.is_valid_object_id(rid):
           review_id = ObjectId(rid)

           review = next(
                           (review for review in movie["reviews"] if review["_id"] == review_id),
                           None
                        )
           if review is None:
                return make_response(jsonify({"error" : "No review found"}), 404)
        
           token = request.headers.get('x-access-token')
           decoded_token = jwt.decode(token, globals.secret_key, algorithms=["HS256"])
           logged_in_user = decoded_token.get('user')
        
           user = globals.db.users.find_one({"username": logged_in_user})
                       
           if user is None:
                return make_response(jsonify({"error" : "User not found"}), 404)
                       
           if not can_manage_review(user, review["user_id"]):
                return make_response(jsonify({"error" : "Unauthorized to delete this review"}), 403)
         
           movies.update_one(
               {"_id" : movie_id, "reviews._id" : review_id},
               {"$pull" : {"reviews" : {"_id" : review_id}}}
           )
           return make_response(jsonify({"message" : "Review deleted successfully"}), 204)
       else:
           return make_response(jsonify({"error" : "Invalid review ID"}), 400)
    else:
        return make_response(jsonify({"error" : "Invalid movie ID"}), 400)


       
