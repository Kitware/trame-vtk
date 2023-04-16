def handle_property(hash_list, prop_value):
    if isinstance(prop_value, list):
        for item in prop_value:
            handle_property(hash_list, item)
        return

    if not isinstance(prop_value, dict):
        return

    if "vtkClass" in prop_value and "hash" in prop_value:
        hash_list.append(
            dict(
                hash=prop_value.get("hash"),
                type=prop_value.get("dataType"),
                vtk=prop_value.get("vtkClass"),
            )
        )


def handle_instance(hash_list, instance):
    if "dependencies" in instance:
        for child in instance.get("dependencies"):
            handle_instance(hash_list, child)
    if "properties" in instance:
        for prop in instance.get("properties").values():
            handle_property(hash_list, prop)
    return hash_list


def extract_array_hash(scene_description):
    return handle_instance([], scene_description)
