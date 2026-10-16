import pandas as pd
import json
import ast
from pymongo import MongoClient

movies_df = pd.read_csv("tmdb_5000_movies.csv")
credits_df = pd.read_csv("tmdb_5000_credits.csv")

merged_df = pd.merge(
    movies_df,
    credits_df,
    left_on="id",
    right_on="movie_id",
    how="inner"
)

movies = []
limit = 100
for _, row in merged_df.iterrows():
  if len(movies) >= limit:
    break
  try:
     production_companies_data = ast.literal_eval(row["production_companies"])
     production_companies = [
        {"name": company["name"]}
        for company in production_companies_data
     ]
  except:
     production_companies = [] 

  try:
     genres = ast.literal_eval(row["genres"])
     genres = [g["name"] for g in genres]
  except:
        genres = []

  try:
    keywords = ast.literal_eval(row["keywords"])
    keywords = [k["name"] for k in keywords]
  except:
        keywords = []

  try:
    cast_data = ast.literal_eval(row["cast"])
    cast = [
         {"name": actor["name"],
          "character": actor["character"]}
          for actor in cast_data[:5]
        ]
  except:
    cast = []

  director = {}
  try:
     crew_data = ast.literal_eval(row["crew"])

     for crew_member in crew_data:
         if crew_member["job"] == "Director":
           director = {
               "name": crew_member["name"]
           }
           break    
  except:
        pass

    
  movie = {

        "_id": f"m{int(row['id'])}",

        "title": row["title_x"],

        "overview": row["overview"],

        "release_year":
            int(str(row["release_date"])[:4])
            if pd.notna(row["release_date"])
            else None,
        "production_companies": production_companies,

        "runtime": row["runtime"],

        "genres": genres,

        "keywords": keywords,

        "director": director,

        "cast": cast,

        "statistics": {

            "budget": int(row["budget"]),

            "revenue": int(row["revenue"]),

            "popularity": float(row["popularity"]),

            "tmdb_rating": float(row["vote_average"]),

            "vote_count": int(row["vote_count"])
        },

        "reviews": [],

        "flags":{
                   "has_reviews": False,
                   "is_popular": float(row["popularity"]) >= 100
        },
    }

  movies.append(movie)

client = MongoClient("mongodb://127.0.0.1:27017")
db = client.moviesDB
movies_collection = db.movies

with open("movies.json", "w", encoding="utf-8") as f:
    json.dump(movies, f, indent=4, ensure_ascii=False)


movies_collection.delete_many({})


movies_collection.insert_many(movies)



 