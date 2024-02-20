import bpy
from ..core import state
from ..core.config import Config


class ConnectButton(bpy.types.Operator):
    bl_idname = "vmc4b.connect"
    bl_label = "Connect"
    bl_description = "Connect with VMC Protocol Performer"

    @classmethod
    def poll(cls, context):
        if context.scene.vmc4b_performer_address == "":
            return False
        if context.scene.vmc4b_performer_port == "":
            return False
        if context.scene.vmc4b_target_armature == "":
            return False
        if state.server.is_alive():
            return False
        return True

    def invoke(self, context, event):
        state.config = Config()
        state.server.start(context.scene.vmc4b_performer_address,
                           int(context.scene.vmc4b_performer_port))
        bpy.ops.vmc4b.update()
        return {'FINISHED'}


class DisconnectButton(bpy.types.Operator):
    bl_idname = "vmc4b.disconnect"
    bl_label = "Disconnect"
    bl_description = "Disconnect with VMC Protocol Performer"

    @classmethod
    def poll(cls, context):
        if state.is_recording:
            return False
        return True

    def invoke(self, context, event):
        state.server.stop()
        state.is_recording = False
        return {'FINISHED'}
