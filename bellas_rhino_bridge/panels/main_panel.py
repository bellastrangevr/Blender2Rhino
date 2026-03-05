"""
Main N-panel: jewelry type tagger, export settings, and Rhino pipeline guide.
"""
import bpy
from bpy.types import Panel
from ..properties.props import JEWELRY_TYPE_ITEMS, LAYER_MAP

# Icon per jewelry type (index matches JEWELRY_TYPE_ITEMS order)
TYPE_ICONS = {
    'RING_SHANK': 'MESH_TORUS',
    'GEMSTONE':   'MESH_ICOSPHERE',
    'BEZEL':      'MESH_CYLINDER',
    'PRONG':      'MESH_CONE',
    'GALLERY':    'MESH_GRID',
    'FINDING':    'LINKED',
    'REFERENCE':  'OBJECT_DATA',
    'NONE':       'QUESTION',
}


class BRB_PT_Main(Panel):
    bl_label = "Bella's Rhino Bridge"
    bl_idname = "BRB_PT_Main"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Rhino"

    def draw(self, context):
        layout = self.layout
        scene_props = context.scene.rhino_bridge
        export = scene_props.export
        obj = context.active_object

        # ── Unit warning ────────────────────────────────────────────
        scene = context.scene
        if scene.unit_settings.length_unit in ('METERS', 'NONE'):
            box = layout.box()
            col = box.column(align=True)
            row = col.row()
            row.label(text="Scene units: Meters", icon='ERROR')
            col.label(text="Export will scale ×1000 → Rhino mm", icon='INFO')
            col.operator("brb.set_scene_mm", text="Set Scene to Millimeters", icon='DRIVER_DISTANCE')
            layout.separator()

        # ── Active object tagger ─────────────────────────────────────
        box = layout.box()
        if obj and obj.type == 'MESH':
            obj_props = obj.rhino_bridge
            current_type = obj_props.jewelry_type
            icon = TYPE_ICONS.get(current_type, 'QUESTION')
            row = box.row()
            row.label(text=f"Active: {obj.name}", icon='OBJECT_DATA')
            row = box.row(align=True)
            row.prop(obj_props, "jewelry_type", text="", icon=icon)
            if current_type != 'NONE':
                row.label(text=f"→ Layer: {LAYER_MAP[current_type]}")
        else:
            box.label(text="Select a mesh object to tag", icon='INFO')

        layout.separator()

        # ── Tagged objects summary ───────────────────────────────────
        tagged = [
            o for o in context.scene.objects
            if o.type == 'MESH' and o.rhino_bridge.jewelry_type != 'NONE'
        ]
        untagged = [
            o for o in context.scene.objects
            if o.type == 'MESH' and o.rhino_bridge.jewelry_type == 'NONE'
        ]
        row = layout.row()
        row.label(text=f"Tagged: {len(tagged)}  |  Untagged meshes: {len(untagged)}", icon='CHECKMARK')

        layout.separator()

        # ── Export settings ──────────────────────────────────────────
        box = layout.box()
        box.label(text="Export Settings", icon='EXPORT')
        box.prop(export, "export_name", text="Name")
        box.prop(export, "output_path", text="Output")
        box.prop(export, "export_format", text="Format")
        row = box.row()
        row.prop(export, "include_rhino_script", text="Generate Rhino Script")
        row = box.row()
        row.prop(export, "include_untagged", text="Include Untagged")

        layout.separator()

        # ── Export button ────────────────────────────────────────────
        col = layout.column(align=True)
        col.scale_y = 1.4
        if export.export_format == 'OBJ':
            col.operator("brb.export_obj", text="Export for Rhino (OBJ)", icon='EXPORT')
        else:
            col.operator("brb.export_3dm", text="Export for Rhino (.3DM)", icon='EXPORT')

        layout.separator()

        # ── Rhino Pipeline Guide (collapsible) ───────────────────────
        row = layout.row()
        row.prop(scene_props, "show_guide",
                 icon='TRIA_DOWN' if scene_props.show_guide else 'TRIA_RIGHT',
                 text="Rhino Pipeline Guide", emboss=False)
        if scene_props.show_guide:
            box = layout.box()
            col = box.column(align=True)
            col.label(text="After importing OBJ into Rhino:", icon='INFO')
            col.separator()
            col.label(text="1.  Select objects on each layer")
            col.label(text="2.  Run: _QuadRemesh")
            col.label(text="3.  Run: _ToSubD")
            col.label(text="4.  Run: _ToNURBS")
            col.separator()
            col.label(text="Or run the generated _rhino_setup.py")
            col.label(text="via: Tools > PythonScript > Run")


class BRB_OT_SetSceneMM(bpy.types.Operator):
    """Set scene unit system to Millimeters for jewelry scale compatibility"""
    bl_idname = "brb.set_scene_mm"
    bl_label = "Set Scene to Millimeters"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        scene = context.scene
        scene.unit_settings.system = 'METRIC'
        scene.unit_settings.length_unit = 'MILLIMETERS'
        scene.unit_settings.scale_length = 0.001
        self.report({'INFO'}, "Scene units set to Millimeters.")
        return {'FINISHED'}


def register():
    bpy.utils.register_class(BRB_OT_SetSceneMM)
    bpy.utils.register_class(BRB_PT_Main)


def unregister():
    bpy.utils.unregister_class(BRB_PT_Main)
    bpy.utils.unregister_class(BRB_OT_SetSceneMM)
