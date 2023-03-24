import base64
import hashlib


def rgb_float_to_hex(r, g, b):
    return f"#{int(r*255):02x}{int(g*255):02x}{int(b*255):02x}"


array_types_mapping = [
    " ",  # VTK_VOID                   0
    " ",  # VTK_BIT                    1
    "b",  # VTK_CHAR                   2
    "B",  # VTK_UNSIGNED_CHAR          3
    "h",  # VTK_SHORT                  4
    "H",  # VTK_UNSIGNED_SHORT         5
    "i",  # VTK_INT                    6
    "I",  # VTK_UNSIGNED_INT           7
    "l",  # VTK_LONG                   8
    "L",  # VTK_UNSIGNED_LONG          9
    "f",  # VTK_FLOAT                 10
    "d",  # VTK_DOUBLE                11
    "L",  # VTK_ID_TYPE               12
    " ",  # unspecified               13
    " ",  # unspecified               14
    "b",  # signed_char               15
    "ll",  # VTK_LONG_LONG            16
    "LL",  # VTK_UNSIGNED_LONG_LONG   17
]

javascript_mapping = {
    "b": "Int8Array",
    "B": "Uint8Array",
    "h": "Int16Array",
    "H": "Int16Array",
    "i": "Int32Array",
    "I": "Uint32Array",
    "l": "Int32Array",
    "L": "Uint32Array",
    "f": "Float32Array",
    "d": "Float64Array",
    "ll": "BigInt64Array",
    "LL": "BigUint64Array",
}


def base64_encode(x):
    return base64.b64encode(x).decode("utf-8")


def hash_data_array(data_array):
    hashed_bit = hashlib.md5(memoryview(data_array)).hexdigest()
    type_code = array_types_mapping[data_array.GetDataType()]
    return "%s_%d%s" % (hashed_bit, data_array.GetSize(), type_code)


def get_js_array_type(data_array):
    return javascript_mapping[array_types_mapping[data_array.GetDataType()]]


def wrap_id(id_str):
    return "instance:${%s}" % id_str


def reference_id(ref):
    if ref:
        try:
            return ref.__this__[1:17]
        except Exception:
            id_str = str(ref)[-12:-1]
            # print('====> fallback ID %s for %s' % (id_str, ref))
            return id_str
    return "0x0"
