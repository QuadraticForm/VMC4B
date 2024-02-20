from collections import deque

import bpy

from . import state
from . import utility


class Applier:
    def __init__(self):
        self.shapekey_queue = {}
        self.used_shapekeys = deque([])

    def update(self, address, args):
        if address == "/VMC/Ext/Root/Pos":
            self.update_root(args)
        if address == "/VMC/Ext/Bone/Pos":
            self.update_pose(args)
        if address == "/VMC/Ext/Blend/Val":
            self.accumulate_blendshape_proxy(args)
        if address == "/VMC/Ext/Blend/Apply":
            self.update_blendshape_proxy()

    def update_root(self, args):
        pose = utility.convert_root(args)

        state.config.root.location = pose["location"]
        state.config.root.rotation_quaternion = pose["rotation_quaternion"]

    def update_pose(self, args):
        bone = None
        if state.config.humanoid_to_bone.get(args[0]):
            bone = state.config.humanoid_to_bone[args[0]]
        else:
            return
        pose = utility.convert_pose(args)
        if args[0] == "Hips":
            bone.pose_bone.rotation_quaternion = pose["rotation_quaternion"]
            if state.config.humanoid_to_bone.get("root"):
                state.config.humanoid_to_bone["root"].pose_bone.location = pose["location"]
        else:
            bone.pose_bone.location = pose["location"]
            bone.pose_bone.rotation_quaternion = pose["rotation_quaternion"]

    def accumulate_blendshape_proxy(self, args):
        if args[1] == 0.0:
            return
        for bind in utility.convert_blendshape_proxy(args):
            if not self.shapekey_queue.get(bind[0]):
                self.shapekey_queue[bind[0]] = 0.0
            self.shapekey_queue[bind[0]] += bind[1]

    def update_blendshape_proxy(self):
        while self.used_shapekeys:
            mesh, index = self.used_shapekeys.popleft()
            try:
                mesh: bpy.types.Mesh = state.config.mesh_name_to_mesh[mesh]
            except KeyError:
                continue
            try:
                mesh.shape_keys.key_blocks[index].value = 0.0
            except KeyError:
                continue
        for (mesh, index), value in self.shapekey_queue.items():
            self.used_shapekeys.append((mesh, index))
            try:
                mesh: bpy.types.Mesh = state.config.mesh_name_to_mesh[mesh]
            except KeyError:
                continue
            try:
                mesh.shape_keys.key_blocks[index].value = value
            except KeyError:
                continue
        self.shapekey_queue = {}
