import bpy
from ..core import state


class MainPanel(bpy.types.Panel):
    bl_label = "VMC4B"
    bl_idname = "OBJECT_PT_VMC4B_MENU"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = 'VMC4B'

    @classmethod
    def poll(cls, context):
        return True

    def draw_header(self, context):
        try:
            layout = self.layout
        except Exception as exc:
            print(str(exc) + " | Error in VMC4B panel header")

    def draw(self, context):
        layout = self.layout

        config = layout.column()
        config.enabled = not state.server.is_alive()
        config.prop(context.scene, "vmc4b_performer_address")
        config.prop(context.scene, "vmc4b_performer_port")
        config.prop_search(
            context.scene, "vmc4b_target_armature", bpy.data, "objects")
        config.prop(context.scene, "vmc4b_receive_frame_rate")

        row = layout.row(align=True)
        row.scale_y = 1.3
        if not state.server.is_alive():
            row.operator("vmc4b.connect", icon="PLAY")
        else:
            row.operator("vmc4b.disconnect", icon="PAUSE")

        row = layout.row(align=True)
        row.scale_y = 1.3
        if not state.is_recording:
            row.operator("vmc4b.startrecording", icon="RADIOBUT_ON")
        else:
            row.operator("vmc4b.stoprecording", icon="RADIOBUT_OFF")
