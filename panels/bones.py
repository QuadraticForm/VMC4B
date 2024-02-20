import bpy
from bpy import context
from ..core import state
from ..core import config


class BonesPanel(bpy.types.Panel):
    bl_label = "Bind (override)"
    bl_idname = "OBJECT_PT_VMC4B_BONES"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = 'VMC4B'
    bl_options = {'DEFAULT_CLOSED'}

    @classmethod
    def poll(cls, context: context):
        return True

    def draw_header(self, context):
        try:
            layout = self.layout
        except Exception as exc:
            print(str(exc) + " | Error in VMC4B panel header")

    def draw(self, context):
        layout = self.layout

        if context.scene.vmc4b_target_armature == "":
            layout.label(text="Select the armature")
            return
        if context.scene.objects[context.scene.vmc4b_target_armature].type != "ARMATURE":
            layout.label(text="Select the armature")
            return

        box_torso = layout.box()
        box_right_hand = layout.box()
        box_left_hand = layout.box()

        if state.server.is_alive():
            box_torso.active = False
            box_right_hand.active = False
            box_left_hand.active = False

        armature_name = context.scene.vmc4b_target_armature

        for bone in config.human_body_bones_torso:
            box_torso.prop_search(
                context.scene,
                "vmc4b_bones_" + bone,
                bpy.data.objects[armature_name].pose,
                "bones"
            )
        for bone in config.human_body_bones_right_hand:
            box_right_hand.prop_search(
                context.scene,
                "vmc4b_bones_" + bone,
                bpy.data.objects[armature_name].pose,
                "bones"
            )
        for bone in config.human_body_bones_left_hand:
            box_left_hand.prop_search(
                context.scene,
                "vmc4b_bones_" + bone,
                bpy.data.objects[armature_name].pose,
                "bones"
            )
