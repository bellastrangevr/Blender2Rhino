Place the rhino3dm Python library here to enable .3DM export.

Install instructions:
  pip download rhino3dm --no-deps -d ./rhino3dm_wheels
  Unzip the appropriate .whl for your platform into this vendor/ folder
  so that `import rhino3dm` works from here.

Alternatively, install system-wide:
  pip install rhino3dm

The addon checks the vendor/ folder first, then falls back to the
system Python path. If rhino3dm is not found, .3DM export is disabled
but OBJ export continues to work normally.
