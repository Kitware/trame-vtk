from wslink import register as exportRpc

from .web_protocol import vtkWebProtocol


class vtkWebViewPortGeometryDelivery(vtkWebProtocol):
    """Provide Geometry delivery mechanism (WebGL)

    (deprecated - will be removed in VTK 10+)
    """

    @exportRpc("viewport.webgl.metadata")
    def getSceneMetaData(self, view_id):
        view = self.getView(view_id)
        data = self.getApplication().GetWebGLSceneMetaData(view)
        return data

    @exportRpc("viewport.webgl.data")
    def getWebGLData(self, view_id, object_id, part):
        view = self.getView(view_id)
        data = self.getApplication().GetWebGLBinaryData(view, str(object_id), part - 1)
        return data
