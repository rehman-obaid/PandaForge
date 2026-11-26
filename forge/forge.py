import os
import panda3d.core as p3d

from pathlib import PureWindowsPath
from direct.showbase.ShowBase import ShowBase

from .mouse import Mouse
from .scene_cam import SceneCamera
from .geom_utils import GeomUtils


def get_ed_resources_path():
    path = r"{0}/forge/resources".format(os.getcwd())
    win_path = PureWindowsPath(path)
    drive = win_path.drive.rstrip(':').lower()
    return f"/{drive}/" + "/".join(win_path.parts[1:])

def get_game_resources_path():
    path = r"{0}/resources".format(os.getcwd())
    win_path = PureWindowsPath(path)
    drive = win_path.drive.rstrip(':').lower()
    return f"/{drive}/" + "/".join(win_path.parts[1:])


ed_res_path = get_ed_resources_path()
game_res_path = get_game_resources_path()


class Forge(ShowBase):
    def __init__(self, game):
        ShowBase.__init__(self)
        
        print(f"\nPandaForge Started...")
        print(f"--Editor Resources path: {ed_res_path}")
        print(f"--Game Resources path: {game_res_path}")
        
        # add game resources search path to Panda3D's
        # models search path, otherwise Panda3D won't
        # be load resources from game resources path
        model_path = p3d.getModelPath()
        model_path.prependDirectory(ed_res_path)
        model_path.prependDirectory(game_res_path)

        # =========== setup defaults ===========
        self.disableMouse()
        
        display_region = self.cam.node().getDisplayRegion(0)
        display_region.set_clear_color_active(True)
        display_region.set_clear_color(p3d.LVecBase4(0, 0, 0, 1.0))
        
        # create pixel2d
        # This special root, pixel2d, uses units in pixels that are relative
        # to the window. The upperleft corner of the window is (0, 0),
        # the lowerleft corner is (xsize, -ysize), in this coordinate system.
        self._pixel2d = self.render2d.attach_new_node("Pixel2D")
        self._pixel2d.set_pos(-1, 0, 1)
        
        # create a game camera and a game display region
        self._player_cam = None
        
        # event handling
        self.buttonThrowers[0].node().setButtonDownEvent("btn_down")
        self.buttonThrowers[0].node().setButtonRepeatEvent("btn_repeat")
        self.buttonThrowers[0].node().setButtonUpEvent("btn_up")
        
        self.accept("window-event", self._on_win_evt)
        self.accept('btn_down', self._on_button_down)
        self.accept('btn_repeat', self._on_button_repeat)
        self.accept('btn_up', self._on_button_up)
        
        # update task
        self.taskMgr.add(self._on_update, "update_task")
        
        # =========== init mouse ===========
        self._mouse = Mouse()
        
        # =========== init SceneCamera ===========
        lens = p3d.PerspectiveLens()
        lens.set_fov(60)
        lens.set_near_far(0.1, 1000)
        
        cam = p3d.Camera("PlayerCam")
        cam.set_lens(lens)
        
        cam_np = p3d.NodePath(cam)
        
        cam_np.reparent_to(render)
        display_region.set_camera(cam_np)
        
        self._scene_cam = SceneCamera(cam_np)
        
        # =========== create a world grid ===========
        self._grid_np = GeomUtils.create_square()
        self._grid_np.reparent_to(self._scene_cam.cam_np())
        self._grid_np.set_transparency(p3d.TransparencyAttrib.M_alpha)

        grid_shader = p3d.Shader.load(
            p3d.Shader.SL_GLSL, "shaders/grid.vert", "shaders/grid.frag"
        )
        
        self._grid_np.set_two_sided(True)
        self._grid_np.set_shader(grid_shader)
        self._grid_np.set_shader_input("camPos", self._scene_cam.cam_np().get_pos())
        self._grid_np.set_shader_input("majorScale", 1)
        self._grid_np.set_shader_input("minorScale", 10)
        
        # =========== init direction reference axis ===========
        self._view_axes = GeomUtils.create_3lines_axes(1, 1)
        self._view_axes.set_scale(25)
        self._view_axes.reparent_to(self._pixel2d)
        
        # =========== init game ===========
        self._game = game(self)

    def _on_button_down(self, evt):
        # print(f"Pressed: {evt}")
        self._game.on_event(evt, down=True)

    def _on_button_repeat(self, evt):
        # print(f"Pressed: {evt}-repeat")
        self._game.on_event(evt, down=True, repeat=True)

    def _on_button_up(self, evt):
        # print(f"Pressed: {evt}-up")
        self._game.on_event(evt, up=True)

    def _on_win_evt(self, win):
        self.windowEvent(win)  # defined in showbase
        
        if win == None or win != self.win or win.is_closed():
            return

        aspect_ratio = self.getAspectRatio(win)

        self._pixel2d.set_scale(2.0 / win.get_x_size(), 1.0, 2.0 / win.get_y_size())

        self._scene_cam.on_win_event(aspect_ratio)
        self._view_axes.set_pos(win.get_x_size() - 50, 0, -50)
        self._game.on_win_event(win, aspect_ratio)

    def _on_update(self, task):
        # update mouse
        if self.mouseWatcherNode.hasMouse():
            self._mouse._update(
                self.mouseWatcherNode.get_mouse_x(),
                self.mouseWatcherNode.get_mouse_y(),
                True,
                False
            )
        else:
            self._mouse._update(0, 0, False, False)

        # update camera
        self._scene_cam.update(
            self._mouse._dx,
            self._mouse._dy,
            self.is_btn_down("alt"),
            self.is_btn_down("control"),
            self.is_btn_down(p3d.MouseButton.one().get_index()),
            self.is_btn_down(p3d.MouseButton.two().get_index()),
            self.is_btn_down(p3d.MouseButton.three().get_index())
        )
        
        # update direction reference axis
        camera_quat = self._scene_cam.cam_np().get_quat()
        camera_quat.invert_in_place()
        self._view_axes.set_quat(camera_quat)
        
        # update direction reference axis
        self._grid_np.set_shader_input("camPos", self._scene_cam.cam_np().get_pos())
        
        # update game
        self._game.on_update(task)
        
        # continue
        return task.cont

    def hide_grid(self):
        pass
        
    def show_grid(self):
        pass

    def is_btn_down(self, btn):
        return self.mouseWatcherNode.is_button_down(btn)
