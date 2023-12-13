import io
import logging
import time
import zipfile

from vtkmodules.vtkCommonCore import vtkTypeUInt32Array, vtkFloatArray, vtkDoubleArray

from .utils import base64_encode, wrap_id

logger = logging.getLogger(__name__)

JS_VTK_ARRAY = {
    "Float32Array": vtkFloatArray,
    "Float64Array": vtkDoubleArray,
}


class SynchronizationContext:
    """Convenience class for caching data arrays, storing computed sha sums, keeping
    track of valid actors, etc..
    """

    def __init__(self):
        self.data_array_cache = {}
        self.last_dependencies_mapping = {}
        self.ignore_last_dependencies = False

    def set_ignore_last_dependencies(self, force):
        self.ignore_last_dependencies = force

    def cache_data_array(self, p_md5, data):
        self.data_array_cache[p_md5] = data

    def get_cached_data_array(self, p_md5, binary=False, compression=False):
        cache_obj = self.data_array_cache[p_md5]
        array = cache_obj["array"]
        cache_time = cache_obj["mTime"]
        array_js_datatype = cache_obj.get("dataType")

        if cache_time != array.GetMTime():
            logger.debug(" ***** ERROR: you asked for an old cache key! ***** ")

        if array_js_datatype and array_js_datatype in JS_VTK_ARRAY:
            logger.debug(
                "Convert Array %s to %s", array.GetClassName(), array_js_datatype
            )
            new_array = JS_VTK_ARRAY[array_js_datatype]()
            new_array.DeepCopy(array)
            p_buffer = memoryview(new_array)
        elif array.GetDataType() == 12:
            # IdType need to be converted to Uint32
            array_size = array.GetNumberOfTuples() * array.GetNumberOfComponents()
            new_array = vtkTypeUInt32Array()
            new_array.SetNumberOfTuples(array_size)
            for i in range(array_size):
                new_array.SetValue(
                    i, -1 if array.GetValue(i) < 0 else array.GetValue(i)
                )
            p_buffer = memoryview(new_array)
        else:
            p_buffer = memoryview(array)

        if binary:
            # Convert the vtkUnsignedCharArray into a bytes object, required by
            # Autobahn websockets
            return (
                p_buffer.tobytes()
                if not compression
                else zip_compression(p_md5, p_buffer.tobytes())
            )

        return base64_encode(
            p_buffer if not compression else zip_compression(p_md5, p_buffer.tobytes())
        )

    def check_for_arrays_to_release(self, time_window=20):
        cut_off_time = time.time() - time_window
        shas_to_delete = []
        for sha in self.data_array_cache:
            record = self.data_array_cache[sha]
            array = record["array"]
            count = array.GetReferenceCount()

            if count == 1 and record["ts"] < cut_off_time:
                shas_to_delete.append(sha)

        for sha in shas_to_delete:
            del self.data_array_cache[sha]

    def get_last_dependency_list(self, idstr):
        last_deps = []
        if (
            idstr in self.last_dependencies_mapping
            and not self.ignore_last_dependencies
        ):
            last_deps = self.last_dependencies_mapping[idstr]
        return last_deps

    def set_new_dependency_list(self, idstr, dep_list):
        self.last_dependencies_mapping[idstr] = dep_list

    def build_dependency_call_list(self, idstr, new_list, add_method, remove_method):
        old_list = self.get_last_dependency_list(idstr)

        calls = []
        calls += [[add_method, [wrap_id(x)]] for x in new_list if x not in old_list]
        calls += [[remove_method, [wrap_id(x)]] for x in old_list if x not in new_list]

        self.set_new_dependency_list(idstr, new_list)
        return calls


def zip_compression(name, data):
    with io.BytesIO() as in_memory:
        with zipfile.ZipFile(in_memory, mode="w") as zf:
            zf.writestr("data/%s" % name, data, zipfile.ZIP_DEFLATED)
        in_memory.seek(0)
        return in_memory.read()
