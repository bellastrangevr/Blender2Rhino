"""
.3DM export operator using the rhino3dm library.
rhino3dm is installed on demand via the addon preferences (one-click install).
Objects are placed on named Rhino layers matching their jewelry type tag.
"""
import bpy
import os
from bpy.types import Operator
from ..properties.props import LAYER_MAP


def _import_rhino3dm():
    """Import rhino3dm (vendor path already in sys.path via __init__)."""
    try:
        import rhino3dm
        return rhino3dm
    except ImportError:
        return None


def _blender_mesh_to_rhino(obj, rhino3dm, scale):
    """
    Convert a Blender mesh object to a rhino3dm.Mesh.
    Applies scale and triangulates for safety.
    """
    import bmesh

    bm = bmesh.new()
    depsgraph = bpy.context.evaluated_depsgraph_get()
    eval_obj = obj.evaluated_get(depsgraph)
    bm.from_mesh(eval_obj.to_mesh())
    bmesh.ops.triangulate(bm, faces=bm.faces)

    r_mesh = rhino3dm.Mesh()

    for v in bm.verts:
        co = obj.matrix_world @ v.co
        r_mesh.Vertices.Add(co.x * scale, co.y * scale, co.z * scale)

    for f in bm.faces:
        verts = [v.index for v in f.verts]
        if len(verts) == 3:
            r_mesh.Faces.AddFace(verts[0], verts[1], verts[2])
        elif len(verts) == 4:
            r_mesh.Faces.AddFace(verts[0], verts[1], verts[2], verts[3])

    r_mesh.Normals.ComputeNormals()
    r_mesh.Compact()

    bm.free()
    eval_obj.to_mesh_clear()
    return r_mesh


class BRB_OT_Export3DM(Operator):
    """Export tagged objects as a .3DM file for Rhino (requires rhino3dm library)"""
    bl_idname = "brb.export_3dm"
    bl_label = "Export for Rhino (.3DM)"
    bl_options = {'REGISTER'}

    @classmethod
    def poll(cls, context):
        scene_props = context.scene.rhino_bridge
        return bool(scene_props.export.output_path)

    def execute(self, context):
        rhino3dm = _import_rhino3dm()
        if rhino3dm is None:
            self.report(
                {'ERROR'},
                "rhino3dm not installed. Go to Edit > Preferences > Add-ons > Blender2Rhino and click 'Install rhino3dm'."
            )
            return {'CANCELLED'}

        scene_props = context.scene.rhino_bridge
        export = scene_props.export

        output_dir = bpy.path.abspath(export.output_path)
        os.makedirs(output_dir, exist_ok=True)

        include_untagged = export.include_untagged
        targets = [
            o for o in context.scene.objects
            if o.type == 'MESH'
            and (include_untagged or o.rhino_bridge.jewelry_type != 'NONE')
        ]

        if not targets:
            self.report({'WARNING'}, "No tagged mesh objects found.")
            return {'CANCELLED'}

        # Scale factor
        scene = context.scene
        scale = 1000.0 if scene.unit_settings.length_unit in ('METERS', 'NONE') else 1.0

        model = rhino3dm.File3dm()

        # Build named layers for each jewelry type present
        layer_index = {}
        tags_present = {o.rhino_bridge.jewelry_type for o in targets}
        for tag in tags_present:
            layer_name = LAYER_MAP.get(tag, 'Untagged')
            layer = rhino3dm.Layer()
            layer.Name = layer_name
            idx = model.Layers.Add(layer)
            layer_index[tag] = idx

        # Add each object to its layer
        errors = []
        for obj in targets:
            tag = obj.rhino_bridge.jewelry_type
            try:
                r_mesh = _blender_mesh_to_rhino(obj, rhino3dm, scale)
                attr = rhino3dm.ObjectAttributes()
                attr.LayerIndex = layer_index[tag]
                attr.Name = obj.name
                model.Objects.AddMesh(r_mesh, attr)
            except Exception as e:
                errors.append(f"{obj.name}: {e}")

        export_name = export.export_name or "jewelry_export"
        out_path = os.path.join(output_dir, f"{export_name}.3dm")
        model.Write(out_path, 7)  # Version 7 = Rhino 7/8 compatible

        for err in errors:
            self.report({'WARNING'}, f"Skipped — {err}")

        self.report({'INFO'}, f"Exported {len(targets) - len(errors)} object(s) → {out_path}")
        return {'FINISHED'}


def register():
    bpy.utils.register_class(BRB_OT_Export3DM)


def unregister():
    bpy.utils.unregister_class(BRB_OT_Export3DM)
