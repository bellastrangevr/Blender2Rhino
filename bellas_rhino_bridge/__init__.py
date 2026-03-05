bl_info = {
    "name": "Bella's Rhino Bridge",
    "author": "Bella",
    "version": (0, 1, 0),
    "blender": (4, 0, 0),
    "location": "View 3D > N-Panel > Rhino Tab",
    "description": "Tag and export jewelry shapes from Blender to Rhino Matrix Gold 8 with correct scale, axis, and layer organization.",
    "category": "Import-Export",
}

import bpy
from . import operators, panels, properties


def register():
    properties.register()
    operators.register()
    panels.register()


def unregister():
    panels.unregister()
    operators.unregister()
    properties.unregister()
