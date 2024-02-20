import bpy
from mathutils import Vector
from mathutils import Quaternion

from ..core import state


def convert_root(args):
    result_q = Quaternion((args[7], args[4], args[6], -args[5]))
    result_l = Vector((-args[1], -args[3], args[2]))
    return {"location": result_l, "rotation_quaternion": result_q}


def convert_pose(args):
    parent_quaternion = state.config.humanoid_to_bone[args[0]
                                                      ].parent_quaternion
    rotate_quat = Quaternion((args[7], args[4], args[6], -args[5]))
    result_l = Vector((0, 0, 0))

    if args[0] == "Hips":
        hips_location = state.config.humanoid_to_bone["Hips"].pose_bone.bone.head_local
        root_quaternion = state.config.humanoid_to_bone["root"].parent_quaternion
        result_l = root_quaternion.inverted(
        ) @ (Vector((-args[1], -args[3], args[2])) - hips_location)
    result_q: Quaternion = parent_quaternion.inverted() @ rotate_quat @ parent_quaternion
    return {"location": result_l, "rotation_quaternion": result_q}


def convert_blendshape_proxy(args):
    try:
        group = state.config.proxy_to_group[args[0]]
    except KeyError:
        return
    factor = args[1]
    if group["is_binary"]:
        factor = 1.0 if factor > 0.5 else 0.0
    for bind in group["binds"]:
        yield ((bind["mesh"], bind["index"]), bind["weight"] * factor)
