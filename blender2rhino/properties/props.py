"""
Property groups: per-object jewelry type tag and scene-level export settings.
"""
import bpy
from bpy.props import (
    EnumProperty, StringProperty, BoolProperty, PointerProperty
)
from bpy.types import PropertyGroup


JEWELRY_TYPE_ITEMS = [
    ('RING_SHANK', "Ring Shank / Band",  "Main ring band or rail",          'MESH_TORUS',    0),
    ('GEMSTONE',   "Gemstone",           "Cut gem or placeholder stone",    'MESH_ICOSPHERE',1),
    ('BEZEL',      "Bezel Setting",      "Bezel wall or cup",               'MESH_CYLINDER', 2),
    ('PRONG',      "Prong Setting",      "Individual or shared prong",      'MESH_CONE',     3),
    ('GALLERY',    "Gallery / Base",     "Decorative underside structure",  'MESH_GRID',     4),
    ('FINDING',    "Finding",            "Bail, clasp, jump ring, etc.",    'LINKED',        5),
    ('REFERENCE',  "Reference / Guide",  "Non-manufacturing guide shape",   'OBJECT_DATA',   6),
    ('NONE',       "Untagged",           "No jewelry type assigned",        'QUESTION',      7),
]

# Maps enum value → Rhino layer name
LAYER_MAP = {
    'RING_SHANK': 'RingShank',
    'GEMSTONE':   'Gems',
    'BEZEL':      'Bezel',
    'PRONG':      'Prongs',
    'GALLERY':    'Gallery',
    'FINDING':    'Finding',
    'REFERENCE':  'Reference',
    'NONE':       'Untagged',
}

# These types should NOT go through QuadRemesh→ToSubD→ToNURBS in Rhino
# (gem placeholders are typically kept as mesh reference)
SKIP_NURBS_CONVERSION = {'REFERENCE', 'NONE'}


class JewelryObjectProps(PropertyGroup):
    jewelry_type: EnumProperty(
        name="Jewelry Type",
        description="Assigns this object to a named layer in Rhino for correct categorization",
        items=JEWELRY_TYPE_ITEMS,
        default='NONE',
    )


FORMAT_ITEMS = [
    ('OBJ', "OBJ",  "Wavefront OBJ — universal, works with any Rhino version"),
    ('3DM', ".3DM", "Rhino native — opens directly with pre-named layers (requires rhino3dm library)"),
]


class RhinoBridgeExportSettings(PropertyGroup):
    output_path: StringProperty(
        name="Output Folder",
        description="Folder where exported files will be saved",
        subtype='DIR_PATH',
        default="//",
    )
    export_format: EnumProperty(
        name="Format",
        items=FORMAT_ITEMS,
        default='OBJ',
    )
    include_rhino_script: BoolProperty(
        name="Generate Rhino Setup Script",
        description="Write a companion .py RhinoScript that runs QuadRemesh → ToSubD → ToNURBS on each layer automatically",
        default=True,
    )
    include_untagged: BoolProperty(
        name="Include Untagged Objects",
        description="Also export objects with no jewelry type assigned",
        default=False,
    )
    export_name: StringProperty(
        name="Export Name",
        description="Base filename for the exported files (no extension)",
        default="jewelry_export",
    )


class RhinoBridgeSceneProps(PropertyGroup):
    export: PointerProperty(type=RhinoBridgeExportSettings)
    show_guide: BoolProperty(name="Show Rhino Pipeline Guide", default=False)


classes = (
    JewelryObjectProps,
    RhinoBridgeExportSettings,
    RhinoBridgeSceneProps,
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.Object.rhino_bridge = PointerProperty(type=JewelryObjectProps)
    bpy.types.Scene.rhino_bridge = PointerProperty(type=RhinoBridgeSceneProps)


def unregister():
    del bpy.types.Scene.rhino_bridge
    del bpy.types.Object.rhino_bridge
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
