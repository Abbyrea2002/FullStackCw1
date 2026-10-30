from bson import ObjectId


def is_valid_object_id(value):
    return ObjectId.is_valid(value)


def get_pagination(args):
    try:
        page_num = int(args.get("page_num", "1"))
        per_page = int(args.get("per_page", "10"))
    except (TypeError, ValueError):
        return None

    if page_num < 1 or per_page < 1:
        return None

    return page_num, per_page