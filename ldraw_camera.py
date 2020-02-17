import bpy
import mathutils
import math

from . import options


class LDrawCamera:
    """Data about a camera"""

    cameras = []

    def __init__(self):
        self.hidden = False
        self.orthographic = False
        self.fov = options.camera_fov
        self.z_near = options.camera_near
        self.z_far = options.camera_far
        self.position = mathutils.Vector((0.0, 0.0, 0.0))
        self.target_position = mathutils.Vector((1.0, 0.0, 0.0))
        self.up_vector = mathutils.Vector((0.0, 1.0, 0.0))
        self.name = "Camera"

    @classmethod
    def reset(cls):
        cls.cameras = []

    @staticmethod
    def get_cameras():
        return LDrawCamera.cameras

    def create_camera_node(self, empty=None, collection=None):
        camera = bpy.data.cameras.new(self.name)

        obj = bpy.data.objects.new(self.name, camera)

        obj.name = self.name
        obj.location = self.position
        obj.hide_viewport = self.hidden
        obj.hide_render = self.hidden

        camera.sensor_fit = 'VERTICAL'
        # camera.sensor_height = self.fov
        camera.lens_unit = 'FOV'
        camera.angle = math.radians(self.fov)  # self.fov * 3.1415926 / 180.0
        camera.clip_start = self.z_near
        camera.clip_end = self.z_far

        if self.orthographic:
            dist_target_to_camera = (self.position - self.target_position).length
            camera.ortho_scale = dist_target_to_camera / 1.92
            camera.type = 'ORTHO'
        else:
            camera.type = 'PERSP'

        camera.clip_start = camera.clip_start * options.scale
        camera.clip_end = camera.clip_end * options.scale

        location = obj.location.copy()
        location.x = location.x * options.scale
        location.y = location.y * options.scale
        location.z = location.z * options.scale
        obj.location = location
        # bpy.context.view_layer.update()

        self.target_position.x = self.target_position.x * options.scale
        self.target_position.y = self.target_position.y * options.scale
        self.target_position.z = self.target_position.z * options.scale

        self.up_vector.x = self.up_vector.x * options.scale
        self.up_vector.y = self.up_vector.y * options.scale
        self.up_vector.z = self.up_vector.z * options.scale

        if collection is None:
            collection = bpy.context.scene.collection
        if obj.name not in collection:
            collection.objects.link(obj)

        # https://blender.stackexchange.com/a/72899
        # https://blender.stackexchange.com/a/154926
        # https://blender.stackexchange.com/a/29148
        # when parenting the location of the parented obj is affected by the transform of the empty
        # this undoes the transform of the empty
        obj.parent = empty
        if obj.parent is not None:
            obj.matrix_parent_inverse = obj.parent.matrix_world.inverted()

        # https://docs.blender.org/api/current/info_gotcha.html#stale-data
        # https://blenderartists.org/t/how-to-avoid-bpy-context-scene-update/579222/6
        # https://blenderartists.org/t/where-do-matrix-changes-get-stored-before-view-layer-update/1182838
        bpy.context.view_layer.update()

        LDrawCamera.look_at(obj, self.target_position, self.up_vector)

        return obj

    @staticmethod
    def look_at(obj, target_location, up_vector):
        # back vector is a vector pointing from the target to the camera
        back = obj.location - target_location
        back.normalize()

        # If our back and up vectors are very close to pointing the same way (or opposite), choose a different up_vector
        if abs(back.dot(up_vector)) > 0.9999:
            up_vector = mathutils.Vector((0.0, 0.0, 1.0))
            if abs(back.dot(up_vector)) > 0.9999:
                up_vector = mathutils.Vector((1.0, 0.0, 0.0))

        right = up_vector.cross(back)
        right.normalize()

        up = back.cross(right)
        up.normalize()

        row1 = [right.x, up.x, back.x, obj.location.x]
        row2 = [right.y, up.y, back.y, obj.location.y]
        row3 = [right.z, up.z, back.z, obj.location.z]
        row4 = [0.0, 0.0, 0.0, 1.0]

        obj.matrix_world = mathutils.Matrix((row1, row2, row3, row4))

    @staticmethod
    def add_camera(ldraw_camera):
        LDrawCamera.cameras.append(ldraw_camera)