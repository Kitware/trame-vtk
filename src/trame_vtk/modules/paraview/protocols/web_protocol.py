import os

from paraview import simple
from paraview.servermanager import vtkSMTransferFunctionManager

from trame_vtk.modules.vtk.protocols.web_protocol import vtkWebProtocol


class ParaViewWebProtocol(vtkWebProtocol):
    def __init__(self):
        self.core_server = None
        self.multi_root = False
        self.base_directory = ""
        self.base_directory_map = {}

    def map_id_to_proxy(self, id):
        """
        Maps global-id for a proxy to the proxy instance. May return None if the
        id is not valid.
        """
        try:
            id = int(id)
        except ValueError:
            return None
        if id <= 0:
            return None
        return simple.servermanager._getPyProxy(
            simple.servermanager.ActiveConnection.Session.GetRemoteObject(id)
        )

    def get_view(self, vid):
        """
        Returns the view for a given view ID, if vid is None then return the
        current active view.
        :param vid: The view ID
        :type vid: str
        """
        view = self.map_id_to_proxy(vid)
        if not view:
            # Use active view is none provided.
            view = simple.GetActiveView()

        if not view:
            raise Exception(f"no view provided: {vid}")

        return view

    def debug(self, msg):
        if self.debug_mode:
            print(msg)

    def set_base_directory(self, base_path):
        self.override_data_dir_key = None
        self.base_directory = ""
        self.base_directory_map = {}
        self.multi_root = False

        if base_path.find("|") < 0:
            if base_path.find("=") >= 0:
                base_pair = base_path.split("=")
                if os.path.exists(base_pair[1]):
                    self.base_directory = base_pair[1]
                    self.override_data_dir_key = base_pair[0]
            else:
                self.base_directory = base_path
            self.base_directory = os.path.normpath(self.base_directory)
        else:
            base_dirs = base_path.split("|")
            for base_dir in base_dirs:
                base_pair = base_dir.split("=")
                if os.path.exists(base_pair[1]):
                    self.base_directory_map[base_pair[0]] = os.path.normpath(
                        base_pair[1]
                    )

            # Check if we ended up with just a single directory
            bd_keys = list(self.base_directory_map)
            if len(bd_keys) == 1:
                self.base_directory = os.path.normpath(
                    self.base_directory_map[bd_keys[0]]
                )
                self.override_data_dir_key = bd_keys[0]
                self.base_directory_map = {}
            elif len(bd_keys) > 1:
                self.multi_root = True

    def get_absolute_path(self, relative_path):
        absolute_path = None

        if self.multi_root:
            rel_path_parts = relative_path.replace("\\", "/").split("/")
            real_base_path = self.base_directory_map[rel_path_parts[0]]
            absolute_path = os.path.join(real_base_path, *rel_path_parts[1:])
        else:
            absolute_path = os.path.join(self.base_directory, relative_path)

        cleaned_path = os.path.normpath(absolute_path)

        # Make sure the cleaned_path is part of the allowed ones
        if self.multi_root:
            for key, value in self.base_directory_map.items():
                if cleaned_path.startswith(value):
                    return cleaned_path
        elif cleaned_path.startswith(self.base_directory):
            return cleaned_path

        return None

    def update_scalar_bars(self, view=None, mode=1):
        """
        Manage scalarbar state

            view:
                A view proxy or the current active view will be used.

            mode:
                HIDE_UNUSED_SCALAR_BARS = 0x01,
                SHOW_USED_SCALAR_BARS = 0x02
        """
        v = view or self.get_view(-1)
        lut_mgr = vtkSMTransferFunctionManager()
        lut_mgr.UpdateScalarBars(v.SMProxy, mode)

    def publish(self, topic, event):
        if self.core_server:
            self.core_server.publish(topic, event)
