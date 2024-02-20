from collections import deque
from typing import Dict
from math import floor

import bpy
from . import state
from . import utility


class Recorder():
    def __init__(self):
        self.queue = deque([])

    def store(self, packet):
        self.queue.append(packet)

    def bake(self):
        target = bpy.data.objects[bpy.context.scene.vmc4b_target_armature]

        armature_action = bpy.data.actions.new(name="Recorded: " + target.name)
        armature_action.use_fake_user = True
        target.animation_data_create().action = armature_action

        mesh_actions = {}
        for mesh_name, mesh in state.config.mesh_name_to_mesh.items():
            mesh_action = bpy.data.actions.new(name="Recorded: " + mesh_name)
            mesh_action.use_fake_user = True
            mesh.shape_keys.animation_data_create().action = mesh_action
            mesh_actions[mesh_name] = mesh_action

        data_root = deque([])
        data_bone = deque([])
        data_shapekey = deque([])

        firsttime = self.queue[0]["timestamp"]
        while self.queue:
            item = self.queue.popleft()
            item["frame_number"] = floor(
                (item["timestamp"] - firsttime).total_seconds() * bpy.context.scene.render.fps) + 1

            if item["address"] == "/VMC/Ext/Root/Pos":
                data_root.append(item)
            if item["address"] == "/VMC/Ext/Bone/Pos":
                data_bone.append(item)
            if item["address"] == "/VMC/Ext/Blend/Val":
                data_shapekey.append(item)
            if item["address"] == "/VMC/Ext/Blend/Apply":
                data_shapekey.append(item)

        self.bake_root(armature_action, data_root)
        self.bake_bone(armature_action, data_bone)
        self.bake_shapekeys(mesh_actions, data_shapekey)

    def bake_root(self, action: bpy.types.Action, data: deque):
        action.groups.new("Object Transforms")
        data_paths = {}
        while data:
            item = data.popleft()
            pose = utility.convert_root(item["args"])

            for path, values in pose.items():
                if not data_paths.get(path):
                    data_paths[path] = []
                for i, value in enumerate(values):
                    if len(data_paths[path]) < i + 1:
                        data_paths[path].append([])
                    frame = {
                        "frame_number": item["frame_number"],
                        "value": value
                    }
                    if len(data_paths[path][i]) == 0:
                        data_paths[path][i].append(frame)
                    if data_paths[path][i][len(data_paths[path][i]) - 1]["frame_number"] == item["frame_number"]:
                        data_paths[path][i][len(
                            data_paths[path][i]) - 1] = frame
                    else:
                        data_paths[path][i].append(frame)

        for data_path, component_lists in data_paths.items():
            for i, component_list in enumerate(component_lists):
                curve = action.fcurves.new(
                    data_path=data_path,
                    index=i,
                    action_group="Object Transforms"
                )
                curve.color_mode = "AUTO_RGB" if len(
                    component_lists) == 3 else "AUTO_YRGB"
                keyframe_points = curve.keyframe_points
                keyframe_points.add(len(component_list))
                for j, component in enumerate(component_list):
                    keyframe_points[j].co = (
                        component["frame_number"],
                        component["value"]
                    )
                    keyframe_points[j].interpolation = "LINEAR"

    def bake_bone(self, action: bpy.types.Action, data: deque):
        data_paths = {}
        while data:
            item = data.popleft()
            bone = state.config.humanoid_to_bone.get(item["args"][0])
            if bone is None:
                continue
            pose = utility.convert_pose(item["args"])

            for path, values in pose.items():
                bone_name = bone.pose_bone.name

                if (path == "location") and (item["args"][0] == "Hips"):
                    bone_name = state.config.humanoid_to_bone["root"].pose_bone.name

                if not data_paths.get(bone_name):
                    data_paths[bone_name] = {}
                if not data_paths[bone_name].get(path):
                    data_paths[bone_name][path] = []
                for i, value in enumerate(values):
                    if len(data_paths[bone_name][path]) < i + 1:
                        data_paths[bone_name][path].append([])
                    frame = {
                        "frame_number": item["frame_number"],
                        "value": value
                    }
                    if len(data_paths[bone_name][path][i]) == 0:
                        data_paths[bone_name][path][i].append(frame)
                    if data_paths[bone_name][path][i][len(data_paths[bone_name][path][i]) - 1]["frame_number"] == item["frame_number"]:
                        data_paths[bone_name][path][i][len(
                            data_paths[bone_name][path][i]) - 1] = frame
                    else:
                        data_paths[bone_name][path][i].append(frame)

        for bone_name, paths in data_paths.items():
            action.groups.new(bone_name)
            for path, component_lists in paths.items():
                for i, component_list in enumerate(component_lists):
                    data_path = "pose.bones[\"" + bone_name + "\"]." + path
                    curve = action.fcurves.new(
                        data_path=data_path,
                        index=i,
                        action_group=bone_name
                    )
                    curve.color_mode = "AUTO_RGB" if len(
                        component_lists) == 3 else "AUTO_YRGB"
                    keyframe_points = curve.keyframe_points
                    keyframe_points.add(len(component_list))
                    for j, component in enumerate(component_list):
                        keyframe_points[j].co = (
                            component["frame_number"],
                            component["value"]
                        )
                        keyframe_points[j].interpolation = "LINEAR"

    def bake_shapekeys(self, actions: Dict[str, bpy.types.Action], data: deque):
        self.shapekey_queue = {}
        self.meshes_data_paths = {}
        while data:
            item = data.popleft()
            if item["address"] == "/VMC/Ext/Blend/Apply":
                self.apply_shapekey(actions, item["frame_number"])
            else:
                self.accumulate_shapekey(item["args"])
        for mesh_name, shapekeys in self.meshes_data_paths.items():
            for shapekey_name, frames in shapekeys.items():
                action: bpy.types.Action = actions[mesh_name]
                data_path = "key_blocks[\"" + shapekey_name + "\"].value"
                curve = action.fcurves.new(data_path=data_path)
                keyframe_points = curve.keyframe_points
                keyframe_points.add(len(frames))
                for i, frame in enumerate(frames):
                    keyframe_points[i].co = (
                        frame["frame_number"],
                        frame["value"]
                    )
                    keyframe_points[i].interpolation = "LINEAR"

    def apply_shapekey(self, actions, frame_number):
        for mesh_name, mesh_id in state.config.mesh_name_to_mesh.items():
            mesh_id: bpy.types.Mesh
            for key_name in mesh_id.shape_keys.key_blocks.keys():
                value = 0.0
                if self.shapekey_queue.get(mesh_name):
                    if self.shapekey_queue[mesh_name].get(key_name):
                        value = self.shapekey_queue[mesh_name][key_name]

                if not self.meshes_data_paths.get(mesh_name):
                    self.meshes_data_paths[mesh_name] = {}
                if not self.meshes_data_paths[mesh_name].get(key_name):
                    self.meshes_data_paths[mesh_name][key_name] = []

                key_sequence = self.meshes_data_paths[mesh_name][key_name]
                frame = {
                    "frame_number": frame_number,
                    "value": value
                }

                if len(key_sequence) == 0:
                    key_sequence.append(frame)
                if key_sequence[len(key_sequence) - 1]["frame_number"] == frame["frame_number"]:
                    key_sequence[len(key_sequence) - 1] = frame
                else:
                    key_sequence.append(frame)

        self.shapekey_queue = {}

    def accumulate_shapekey(self, args):
        if args[1] == 0.0:
            return
        for (mesh_name, index_name), factor in utility.convert_blendshape_proxy(args):
            if not self.shapekey_queue.get(mesh_name):
                self.shapekey_queue[mesh_name] = {}
            if not self.shapekey_queue[mesh_name].get(index_name):
                self.shapekey_queue[mesh_name][index_name] = 0.0
            self.shapekey_queue[mesh_name][index_name] += factor
