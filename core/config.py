from json import JSONDecoder
from typing import Dict

import bpy
from bpy import context
from bpy.props import StringProperty
from mathutils import Quaternion


class Config:
    decorder = JSONDecoder()

    def __init__(self):
        self.init_root()
        self.init_pose()
        self.init_blendshape_proxy()

    def init_root(self):
        self.root = bpy.data.objects[bpy.context.scene.vmc4b_target_armature]

    def init_pose(self):
        self.humanoid_to_bone = {}
        result = {}
        armature = bpy.data.objects[bpy.context.scene.vmc4b_target_armature]
        if hasattr(armature.data, "vrm_addon_extension"):
            human_bones = getattr(
                armature.data.vrm_addon_extension.vrm0.humanoid, "human_bones", [])
            for human_bone in human_bones:
                node_name = human_bone.node.value
                bone_name = human_bone.bone[0].upper(
                ) + human_bone.bone[1:]
                # If bone isn't exist, it will be ignored(ad hoc spec)
                if node_name in armature.pose.bones:
                    result[bone_name] = HumanoidBone(
                        armature.pose.bones[node_name])
        human_body_bones = [
            *human_body_bones_torso,
            *human_body_bones_right_hand,
            *human_body_bones_left_hand
        ]
        for bone_name in human_body_bones:
            binded_bone_name = getattr(
                bpy.context.scene,
                "vmc4b_bones_" + bone_name
            )
            if binded_bone_name != "":
                result[bone_name] = HumanoidBone(
                    armature.pose.bones[binded_bone_name])
        if result.get("Hips"):
            root_bone = result["Hips"].pose_bone
            while root_bone.parent:
                root_bone = root_bone.parent
            result["root"] = HumanoidBone(root_bone)

        self.humanoid_to_bone: Dict[str, HumanoidBone] = result

    def init_blendshape_proxy(self):
        armature = bpy.data.objects[bpy.context.scene.vmc4b_target_armature]
        self.proxy_to_group = {}
        self.mesh_name_to_mesh = {}

        if not hasattr(armature.data, "vrm_addon_extension"):
            return

        blend_shape_groups = getattr(
            armature.data.vrm_addon_extension.vrm0.blend_shape_master, "blend_shape_groups", [])

        proxy_to_group = {}
        mesh_name_to_mesh = {}
        for blend_shape_group in blend_shape_groups:
            proxy_to_group[blend_shape_group.name] = {
                "binds": [],
                "is_binary": getattr(blend_shape_group, "is_binary", False)
            }
            for bind in blend_shape_group.binds:
                proxy_to_group[blend_shape_group.name]["binds"].append({
                    "mesh": bind.mesh.value,
                    "index": bind.index,
                    "weight": bind.weight
                })

                if not mesh_name_to_mesh.get(bind.mesh.value):
                    try:
                        mesh_name_to_mesh[bind.mesh.value
                                          ] = bpy.data.meshes[bind.mesh.value]
                    except KeyError:
                        try:
                            mesh_name_to_mesh[bind.mesh.value] = bpy.data.objects[bind.mesh.value].data
                        except KeyError:
                            continue
                        continue

        self.proxy_to_group = proxy_to_group
        self.mesh_name_to_mesh = mesh_name_to_mesh


class HumanoidBone:
    def __init__(self, pose_bone: bpy.types.PoseBone):
        self.pose_bone: bpy.types.PoseBone = pose_bone
        quat = pose_bone.bone.matrix.to_quaternion()
        if not pose_bone.bone.use_inherit_rotation:
            self.parent_quaternion: Quaternion = quat
            return
        for parent in pose_bone.bone.parent_recursive:
            quat = parent.matrix.to_quaternion() @ quat
            if not parent.use_inherit_rotation:
                break
        self.parent_quaternion: Quaternion = quat


human_body_bones_torso = [
    "Hips",
    "Spine",
    "Chest",
    "UpperChest",
    "Neck",
    "Head",
    "LeftShoulder",
    "LeftUpperArm",
    "LeftLowerArm",
    "LeftHand",
    "LeftUpperLeg",
    "LeftLowerLeg",
    "LeftFoot",
    "LeftToes",
    "RightShoulder",
    "RightUpperArm",
    "RightLowerArm",
    "RightHand",
    "RightUpperLeg",
    "RightLowerLeg",
    "RightFoot",
    "RightToes",
    "LeftEye",
    "RightEye",
    "Jaw"
]

human_body_bones_left_hand = [
    "LeftThumbProximal",
    "LeftThumbIntermediate",
    "LeftThumbDistal",
    "LeftIndexProximal",
    "LeftIndexIntermediate",
    "LeftIndexDistal",
    "LeftMiddleProximal",
    "LeftMiddleIntermediate",
    "LeftMiddleDistal",
    "LeftRingProximal",
    "LeftRingIntermediate",
    "LeftRingDistal",
    "LeftLittleProximal",
    "LeftLittleIntermediate",
    "LeftLittleDistal"
]

human_body_bones_right_hand = [
    "RightThumbProximal",
    "RightThumbIntermediate",
    "RightThumbDistal",
    "RightIndexProximal",
    "RightIndexIntermediate",
    "RightIndexDistal",
    "RightMiddleProximal",
    "RightMiddleIntermediate",
    "RightMiddleDistal",
    "RightRingProximal",
    "RightRingIntermediate",
    "RightRingDistal",
    "RightLittleProximal",
    "RightLittleIntermediate",
    "RightLittleDistal"
]


def register():
    for bone in human_body_bones_torso:
        setattr(bpy.types.Scene, "vmc4b_bones_" + bone, StringProperty(
            name=bone,
            description="Select the bone that corresponds to the humanoids bone"
        ))
    for bone in human_body_bones_left_hand:
        setattr(bpy.types.Scene, "vmc4b_bones_" + bone, StringProperty(
            name=bone,
            description="Select the bone that corresponds to the humanoids bone"
        ))
    for bone in human_body_bones_right_hand:
        setattr(bpy.types.Scene, "vmc4b_bones_" + bone, StringProperty(
            name=bone,
            description="Select the bone that corresponds to the humanoids bone"
        ))


def unregister():
    for bone in human_body_bones_torso:
        delattr(bpy.types.Scene, "vmc4b_bones_" + bone)
    for bone in human_body_bones_left_hand:
        delattr(bpy.types.Scene, "vmc4b_bones_" + bone)
    for bone in human_body_bones_right_hand:
        delattr(bpy.types.Scene, "vmc4b_bones_" + bone)
