import math as math
import panda3d.core as p3d


class SceneCamera:
    # references
    _cam_np = None
    _target = None
    
    # variables
    _move_speed = 30.0

    # cache
    _yaw = 0.0
    _pitch = 0.0
    _is_ortho = False
    
    def __init__(self, cam_np):
        self._cam_np = cam_np
        self._target = p3d.NodePath("TargetNode")
        
        self.reset()
        
    def reset(self):
        self._yaw = self._pitch = 0.0
        
        self._target.set_pos(p3d.LVecBase3f(0.0, 0.0, 0.0))
        self._cam_np.set_pos(p3d.LVecBase3f(0.0, 100.0, 0.0))

        self.move(p3d.LVecBase3f(0.0, 0.0))
        self.orbit(p3d.LVecBase2f(155.0, 35.0))

    def update(self, dx, dy, alt, ctrl, mouse_left, mouse_middle, mouse_right):
        if (not alt):
            return;

        orbit_sensitivity = 200.0
        pan_sensitivity = 200.0
        dist = (self._cam_np.get_pos() - self._target.get_pos()).length()

        if (mouse_left):
            if (abs(dx) > abs(dy)):
                self.orbit(p3d.LVecBase2f(-dx, 0) * orbit_sensitivity)
            else:
                self.orbit(p3d.LVecBase2f(0, -dy) * orbit_sensitivity)
        elif (mouse_middle):
            self.move(p3d.LVecBase3f(-dx, 0, -dy) * pan_sensitivity)
        elif (mouse_right):
            self.zoom(dx * pan_sensitivity)
    	
    def on_win_event(self, aspect_ratio):
        self._cam_np.node().get_lens().set_aspect_ratio(aspect_ratio)

    def move(self, move_vec):
        dist = (self._cam_np.get_pos() - self._target.get_pos()).length()
        scale = dist / 300.0

        # get camera orientation vectors
        right = self._cam_np.get_quat().get_right()
        up = self._cam_np.get_quat().get_up()

        # convert input into world movement
        world_move = (
            right * move_vec.get_x() + up * move_vec.get_z()
        ) * scale;

        # move both camera and _target in same space
        self._cam_np.set_pos(self._cam_np.get_pos() + world_move);
        self._target.set_pos(self._target.get_pos() + world_move)
    
    def zoom(self, delta):
        forward = self._cam_np.get_quat().get_forward()

        dist = (self._cam_np.get_pos() - self._target.get_pos()).length()
        scale = dist / 300.0

        move_vec = forward * delta * scale

        # move camera only (not _target)
        self._cam_np.set_pos(self._cam_np.get_pos() + move_vec)
    
    def orbit(self, delta):
        self._yaw += delta.get_x()
        self._pitch += delta.get_y()

        self._pitch = clamp(self._pitch, -89.5, 89.5)
        
        ry = self._yaw * 0.0174533  # yaw * deg_to_rad conversion factor
        rp = self._pitch * 0.0174533

        dist = (self._cam_np.get_pos() - self._target.get_pos()).length()

        pos = p3d.LPoint3f(0, 0, 0)
        pos.set_x(dist * math.sin(ry) * math.cos(rp))
        pos.set_y(-dist * math.cos(ry) * math.cos(rp))
        pos.set_z(dist * math.sin(rp))

        self._cam_np.set_pos(self._target.get_pos() + pos)

        # always look at target
        self._cam_np.look_at(self._target, p3d.LVecBase3f(0, 0, 1))
        
    def cam_np(self):
        return self._cam_np
