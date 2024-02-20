# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTIBILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

# Plugin info for Blender
bl_info = {
    "name": "VMC4B",
    "author": "tonimono",
    "description": "VMC Protocol Marionette Addon for Blender",
    "blender": (2, 93, 5),
    "version": (1, 1, 2),
    "location": "View3D > Sidebar",
    "warning": "",
    "category": "Animation"
}


if "bpy" not in locals():
    import bpy
    from . import core
    from . import operators
    from . import panels
else:
    import importlib
    importlib.reload(core)
    importlib.reload(operators)
    importlib.reload(panels)

# register and unregister all classes


def register():
    bpy.types.Scene.vmc4b_performer_address = bpy.props.StringProperty(
        name="Address",
        description="VMC4B Performer Address",
        default="127.0.0.1"
    )
    bpy.types.Scene.vmc4b_performer_port = bpy.props.StringProperty(
        name="Port",
        description="VMC4B Performer Port",
        default="39539"
    )
    bpy.types.Scene.vmc4b_target_armature = bpy.props.StringProperty(
        name="Armature",
        description="Armature controlled by VMC"
    )
    bpy.types.Scene.vmc4b_receive_frame_rate = bpy.props.IntProperty(
        name="frame rate",
        description="Receive frame rate",
        default=120,
        min=0,
        max=120
    )
    bpy.utils.register_class(panels.main.MainPanel)
    bpy.utils.register_class(panels.bones.BonesPanel)
    bpy.utils.register_class(operators.connect.ConnectButton)
    bpy.utils.register_class(operators.connect.DisconnectButton)
    bpy.utils.register_class(operators.record.StartRecordingButton)
    bpy.utils.register_class(operators.record.StopRecordingButton)
    bpy.utils.register_class(operators.update.UpdateModal)
    core.config.register()


def unregister():
    if core.state.server.is_alive():
        core.state.server.stop()
    del bpy.types.Scene.vmc4b_performer_address
    del bpy.types.Scene.vmc4b_performer_port
    del bpy.types.Scene.vmc4b_target_armature
    del bpy.types.Scene.vmc4b_receive_frame_rate
    bpy.utils.unregister_class(panels.main.MainPanel)
    bpy.utils.unregister_class(panels.bones.BonesPanel)
    bpy.utils.unregister_class(operators.connect.ConnectButton)
    bpy.utils.unregister_class(operators.connect.DisconnectButton)
    bpy.utils.unregister_class(operators.record.StartRecordingButton)
    bpy.utils.unregister_class(operators.record.StopRecordingButton)
    bpy.utils.unregister_class(operators.update.UpdateModal)
    core.config.unregister()
