SERIALIZERS = {}
JS_CLASS_MAPPING = {}
context = None


def registerInstanceSerializer(name, method):
    SERIALIZERS[name] = method


def registerJSClass(vtk_class, js_class):
    JS_CLASS_MAPPING[vtk_class] = js_class


def class_name(vtk_obj):
    vtk_class = vtk_obj.GetClassName()
    if vtk_class in JS_CLASS_MAPPING:
        return JS_CLASS_MAPPING[vtk_class]

    return vtk_class
