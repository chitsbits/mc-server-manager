def format_document_response(data: dict | list):
    formatted = {}
    if isinstance(data, dict):
        formatted = {
            "id": str(data["_id"]),  # Convert ObjectId to string
            **{key: value for key, value in data.items() if key != "_id"}
        }
    elif isinstance(data, list):
        formatted = []
        for item in data:
            formatted.append({
                "id": str(item["_id"]),  # Convert ObjectId to string
                **{key: value for key, value in item.items() if key != "_id"}
            })

    return formatted
