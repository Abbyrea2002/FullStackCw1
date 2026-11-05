def get_invalid_review_fields(data):
    invalid_fields = []

    if not isinstance(data.get("comment"), str) or not data.get("comment").strip():
        invalid_fields.append("comment")

    stars = data.get("stars")
    if not isinstance(stars, int) or not 1 <= stars <= 5:
        invalid_fields.append("stars")

    return invalid_fields
