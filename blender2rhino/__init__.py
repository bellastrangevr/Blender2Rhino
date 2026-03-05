bl_info = {
    "name": "Blender2Rhino",
    "author": "Bella",
    "version": (0, 1, 0),
    "blender": (4, 0, 0),
    "location": "View 3D > N-Panel > Rhino Tab",
    "description": "Tag and export jewelry shapes from Blender to Rhino Matrix Gold 8 with correct scale, axis, and layer organization.",
    "category": "Import-Export",
}

import bpy
import os
import sys

# rhino3dm installs here — never touches Blender's own Python environment
VENDOR_PATH = os.path.join(os.path.dirname(__file__), "vendor")


def rhino3dm_available():
    """Return True if rhino3dm can be imported from vendor or system Python."""
    if VENDOR_PATH not in sys.path:
        sys.path.insert(0, VENDOR_PATH)
    try:
        import rhino3dm  # noqa: F401
        return True
    except ImportError:
        return False


from . import operators, panels, properties


class BRB_OT_InstallRhino3dm(bpy.types.Operator):
    """Download and install rhino3dm into the addon vendor folder (requires internet)"""
    bl_idname = "brb.install_rhino3dm"
    bl_label = "Install rhino3dm"

    def execute(self, context):
        import subprocess
        os.makedirs(VENDOR_PATH, exist_ok=True)
        try:
            subprocess.check_call([
                sys.executable, "-m", "pip", "install",
                "rhino3dm",
                "--target", VENDOR_PATH,
                "--upgrade",
                "--quiet",
            ])
        except subprocess.CalledProcessError as e:
            self.report({'ERROR'}, f"Install failed: {e}")
            return {'CANCELLED'}

        if rhino3dm_available():
            self.report({'INFO'}, "rhino3dm installed. .3DM export is now available.")
        else:
            self.report({'WARNING'}, "Installed but not yet importable — try restarting Blender.")
        return {'FINISHED'}


class BRB_AddonPreferences(bpy.types.AddonPreferences):
    bl_idname = __name__

    def draw(self, context):
        layout = self.layout
        if rhino3dm_available():
            layout.label(text="rhino3dm: installed", icon='CHECKMARK')
        else:
            col = layout.column(align=True)
            col.label(text="rhino3dm not found — .3DM export unavailable.", icon='ERROR')
            col.operator("brb.install_rhino3dm", icon='IMPORT',
                         text="Install rhino3dm  (one click, requires internet)")


def register():
    bpy.utils.register_class(BRB_OT_InstallRhino3dm)
    bpy.utils.register_class(BRB_AddonPreferences)
    properties.register()
    operators.register()
    panels.register()


def unregister():
    panels.unregister()
    operators.unregister()
    properties.unregister()
    bpy.utils.unregister_class(BRB_AddonPreferences)
    bpy.utils.unregister_class(BRB_OT_InstallRhino3dm)
