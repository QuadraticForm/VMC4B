if "bpy" not in locals():
    import bpy
    from . import connect
    from . import update
    from . import record
else:
    import importlib
    importlib.reload(connect)
    importlib.reload(update)
    importlib.reload(record)
