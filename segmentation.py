def init(data):
    text_annotations = data.text_annotations[1::]

    simpler_annotations = []
    for annotation in text_annotations:
        simpler_annotations.append({
            "text": annotation.description,
            "vertices": annotation.bounding_poly.vertices
        })

    height_threshold = 8 # in percentage
    lines = []

    for annotation in simpler_annotations:
        vertices = annotation["vertices"]

        left_top, right_top, left_bottom, right_bottom = 3, 2, 0, 1

        avg_top_y = round((vertices[left_top].y + vertices[right_top].y) / 2)
        avg_bottom_y = round((vertices[left_bottom].y + vertices[right_bottom].y) / 2)
        y_min = round(avg_bottom_y * (1 - height_threshold / 100))
        y_max = round(avg_top_y * (1 + height_threshold / 100))

        line = None
        for l in lines:
            if avg_bottom_y >= l["yMin"] and avg_top_y <= l["yMax"]:
                line = l
        
        end_x = max([vertex.x for vertex in annotation["vertices"]])
        if line:
            line["words"].append({
                "text": annotation["text"],
                "x": end_x
            })
        
        else:
            lines.append({
                "yMin": y_min,
                "yMax": y_max,
                "words": [
                    {
                        "text": annotation["text"],
                        "x": end_x
                    }
                ]
            })

    final = [" ".join([word["text"] for word in line["words"]]) for line in lines]

    return final
