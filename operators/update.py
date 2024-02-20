import bpy
from bpy.types import Timer
from typing import Union
from ..core import state
from ..core.applier import Applier
from ..core.recorder import Recorder


class UpdateModal(bpy.types.Operator):
    bl_idname = "vmc4b.update"
    bl_label = "Update"

    timer: Union[Timer, None] = None

    @classmethod
    def poll(cls, context):
        return True

    def modal(self, context, event):
        if event.type != "TIMER":
            return {"PASS_THROUGH"}

        while state.server.queue:
            item = state.server.queue.popleft()
            self.applier.update(item["address"], item["args"])
            if state.is_recording:
                self.recorder.store(item)

        if (not state.is_recording) and self.recorder.queue:
            self.recorder.bake()

        if not state.server.is_alive():
            context.window_manager.event_timer_remove(UpdateModal.timer)
            return {"FINISHED"}

        return {"RUNNING_MODAL"}

    def execute(self, context):
        return self.invoke(context, None)

    def invoke(self, context, event):
        self.applier = Applier()
        self.recorder = Recorder()
        context.window_manager.modal_handler_add(self)
        UpdateModal.timer = context.window_manager.event_timer_add(
            1 / context.scene.vmc4b_receive_frame_rate, window=context.window)
        return {"RUNNING_MODAL"}
