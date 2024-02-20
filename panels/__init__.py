if "bpy" not in locals():
    import bpy
    from . import main
    from . import bones
else:
    import importlib
    importlib.reload(main)
    importlib.reload(bones)
