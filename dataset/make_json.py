import pandas as pd
import json
import ast
import random
from bson import ObjectId
from pymongo import MongoClient


REVIEWER_NAMES = [
  "Alex Morgan",
  "Sam Taylor",
  "Jordan Lee",
  "Casey Brown",
  "Riley Wilson",
  "Jamie Patel",
  "Morgan Davis",
  "Avery Chen",
  "Taylor Kim",
  "Cameron Scott",
  "Drew Robinson",
  "Quinn Murphy",
  "Skyler Adams",
  "Reese Thompson",
  "Parker Nguyen",
  "Rowan Clark",
  "Emerson Wright",
  "Finley Brooks",
  "Hayden Rivera",
  "Kendall Price",
]

REVIEW_COMMENTS = {
  1: [
    "I found the story confusing and the characters hard to care about.",
    "This was a disappointing watch and I would not recommend it.",
    "The pacing dragged, and the film never really came together for me.",
    "The plot felt messy, and I struggled to stay interested.",
    "The characters and dialogue did not feel convincing to me.",
    "I kept waiting for the story to improve, but it never did.",
  ],
  2: [
    "There were a few good moments, but overall it did not hold my attention.",
    "An uneven film with some promise, though it missed the mark for me.",
    "The cast tried their best, but the story felt underdeveloped.",
    "It was watchable, but I probably would not choose to see it again.",
    "Some scenes worked well, while others felt slow and predictable.",
    "A couple of strong ideas were let down by the uneven pacing.",
  ],
  3: [
    "A decent film with an interesting idea and a few memorable scenes.",
    "I enjoyed parts of it, even if it was not especially original.",
    "A solid, entertaining watch, though it has a few rough edges.",
    "It kept me entertained, although I had mixed feelings by the end.",
    "There is plenty to like here, even if it does not fully stand out.",
    "A good choice for a casual movie night, with a few flaws.",
  ],
  4: [
    "A really enjoyable film with strong performances and a compelling story.",
    "I was drawn in from the start and would happily watch it again.",
    "Well made and entertaining, with plenty of moments that stayed with me.",
    "The story kept moving, and the cast made the characters feel real.",
    "A memorable film with great scenes and only a few minor issues.",
    "I had a great time watching this and would recommend it.",
  ],
  5: [
    "An outstanding film with a brilliant story and performances I will remember.",
    "One of my favorites: beautifully made, moving, and completely absorbing.",
    "Everything came together perfectly. I loved it from beginning to end.",
    "A remarkable film that had me thinking about it long after it ended.",
    "The writing, performances, and direction were all exceptional.",
    "I could not find a moment that did not work for me. Truly excellent.",
  ],
}


def create_reviews(count=20):
  reviews = []
  for _ in range(count):
    stars = random.randint(1, 5)
    reviews.append({
      "_id" : ObjectId(),
      "name": random.choice(REVIEWER_NAMES),
      "comment": random.choice(REVIEW_COMMENTS[stars]),
      "stars": stars,
    })
  return reviews


movies_df = pd.read_csv("tmdb_5000_movies.csv")
credits_df = pd.read_csv("tmdb_5000_credits.csv")

merged_df = pd.merge(
    movies_df,
    credits_df,
    left_on="id",
    right_on="movie_id",
    how="inner"
)

movies_list = []
limit = 200
for _, row in merged_df.iterrows():
  if len(movies_list) >= limit:
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

        "reviews": create_reviews(),

        "flags":{
             "has_reviews": True,
                   "is_popular": float(row["popularity"]) >= 100
        },
    }

  movies_list.append(movie)

client = MongoClient("mongodb://127.0.0.1:27017")
db = client.moviesDB
movies = db.movies

with open("movies.json", "w", encoding="utf-8") as f:
  json.dump(movies_list, f, indent=4, ensure_ascii=False, default=str)


movies.delete_many({})


movies.insert_many(movies_list)



 