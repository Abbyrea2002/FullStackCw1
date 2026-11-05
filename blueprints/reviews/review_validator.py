def get_invalid_review_fields(data):
    invalid_fields = []
   
    if "comment" in data:
      comment = data.get("comment")
      if not isinstance(comment, str) or not comment.strip():
        invalid_fields.append("comment")

    if "stars" in data:
       stars = data.get("stars")
       if not isinstance(stars, int) or not 1 <= stars <= 5:
        invalid_fields.append("stars")

    return invalid_fields
