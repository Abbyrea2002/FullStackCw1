
def get_movie_invalid_fields(data):
    invalid_fields = []

    if "title" in data and not isinstance(data["title"], str):
        invalid_fields.append("title")
    if "overview" in data and not isinstance(data["overview"], str):
        invalid_fields.append("overview")
    if "release_year" in data and not isinstance(data["release_year"], int):
        invalid_fields.append("release_year")
    if "production_companies" in data:
        if not isinstance(data["production_companies"], list):
            invalid_fields.append("production_companies")
        else:
            for index, company in enumerate(data["production_companies"]):
                if not isinstance(company.get("name"), str) or not company["name"].strip():
                    invalid_fields.append(f"name {index + 1}")
    if "runtime" in data and not isinstance(data["runtime"], float) and not isinstance(data["runtime"], int):
        invalid_fields.append("runtime")

    for field in ("genres", "keywords"):
        if field in data and (
            not isinstance(data[field], list)
            or any(not isinstance(value, str) or not value.strip() for value in data[field])
        ):
            invalid_fields.append(field)

    if "directors" in data:
        if not isinstance(data["directors"], list):
            invalid_fields.append("directors")
        else:
            for index, director in enumerate(data["directors"]):
                if not isinstance(director.get("name"), str) or not director["name"].strip():
                    invalid_fields.append(f"directors name {index + 1}")
    if "cast" in data:
        if not isinstance(data["cast"], list):
            invalid_fields.append("cast")
        else:
            for index, actor in enumerate(data["cast"]):
                if not isinstance(actor.get("name"), str) or not actor["name"].strip():
                    invalid_fields.append(f"cast name {index + 1}")
                if not isinstance(actor.get("character"), str) or not actor["character"].strip():
                    invalid_fields.append(f"cast character {index + 1}")
    if "statistics" in data:
        if not isinstance(data["statistics"], dict):
            invalid_fields.append("statistics")
        else:
            for stat in ("budget", "revenue", "popularity", "tmdb_rating", "vote_count"):
                if stat in data["statistics"] and not isinstance(data["statistics"][stat], (int, float)):
                    invalid_fields.append(stat)
    if "flags" in data:
        if not isinstance(data["flags"], dict):
            invalid_fields.append("flags")
        else:
            for flag in ("has_reviews", "is_popular"):
                if flag in data["flags"] and not isinstance(data["flags"][flag], bool):
                    invalid_fields.append(flag)
    return invalid_fields
    
