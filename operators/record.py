import bpy
from ..core import state
from . import update


class StartRecordingButton(bpy.types.Operator):
    bl_idname = "vmc4b.startrecording"
    bl_label = "Start Recording"

    @classmethod
    def poll(cls, context):
        return state.server.is_alive()

    def invoke(self, context, event):
        state.is_recording = True
        return {'FINISHED'}
    
    def execute(self, context):

        return self.invoke(context, None)


class StopRecordingButton(bpy.types.Operator):
    bl_idname = "vmc4b.stoprecording"
    bl_label = "Stop Recording"

    @classmethod
    def poll(cls, context):
        return state.server.is_alive()

    def invoke(self, context, event):
        state.is_recording = False
        return {'FINISHED'}
    
    def execute(self, context):

        return self.invoke(context, None)
