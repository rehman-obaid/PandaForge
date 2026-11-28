import os
import panda3d.core as p3d

from pathlib import PureWindowsPath

from direct.showbase.ShowBase import ShowBase

from .mouse import Mouse
from .scene_cam import SceneCamera
from .geom_utils import GeomUtils
from .game_view import (
    GameViewStyle,
    GameViewSettings,
    GameViewDefaultSize
)


# constants
EDITOR_MASK = p3d.BitMask32.bit(0)
GAME_MASK = p3d.BitMask32.bit(1)


# utility methods
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


# PandaForge
class Forge(ShowBase):
    def __init__(self, game):
        ShowBase.__init__(self)
        self.disableMouse()
        
        print(f"\nPandaForge Started...")
        print(f"--Editor Resources path: {ed_res_path}")
        print(f"--Game Resources path: {game_res_path}")
        
        # add game resources search path to Panda3D's
        # models search path, otherwise Panda3D won't
        # be load resources from game resources path
        model_path = p3d.getModelPath()
        model_path.prependDirectory(ed_res_path)
        model_path.prependDirectory(game_res_path)
        
        # =========== tasks and event handling ===========
        # event handling
        self.buttonThrowers[0].node().setButtonDownEvent("btn_down")
        self.buttonThrowers[0].node().setButtonRepeatEvent("btn_repeat")
        self.buttonThrowers[0].node().setButtonUpEvent("btn_up")
        
        self.accept("window-event", self._on_win_evt)
        self.accept("btn_down", self._on_button_down)
        self.accept("btn_repeat", self._on_button_repeat)
        self.accept("btn_up", self._on_button_up)
        
        # update task
        self.taskMgr.add(self._on_update, "update_task")
   
        # =========== editor view rendering ===========
        # pixel2d
        # This special root, pixel2d, uses units in pixels that are relative
        # to the window. The upperleft corner of the window is (0, 0),
        # the lowerleft corner is (xsize, -ysize), in this coordinate system.
        self._pixel2d = self.render2d.attach_new_node("Pixel2D")
        self._pixel2d.set_pos(-1, 0, 1) 

        # editor display region
        display_region = self.cam.node().getDisplayRegion(0)
        display_region.set_clear_color_active(True)
        display_region.set_clear_color(p3d.LVecBase4(0, 0, 0, 1.0))

        # scene-camera
        cam_np = Forge.create_cam(
            "SceneCam",
            Forge.create_prespective_lens(),
            self.render,
            display_region
        )
        
        self._scene_cam = SceneCamera(cam_np)
        
        # infinite grid
        self._grid_np = GeomUtils.create_square()
        self._grid_np.reparent_to(self._scene_cam.np)
        self._grid_np.set_transparency(p3d.TransparencyAttrib.M_alpha)

        grid_shader = p3d.Shader.load(
            p3d.Shader.SL_GLSL, "shaders/grid.vert", "shaders/grid.frag"
        )

        self._grid_np.set_two_sided(True)
        self._grid_np.set_shader(grid_shader)
        self._grid_np.set_shader_input("camPos", self._scene_cam.np.get_pos())
        self._grid_np.set_shader_input("majorScale", 1)
        self._grid_np.set_shader_input("minorScale", 10)
 
        # init direction reference axis
        self._view_axes = GeomUtils.create_3lines_axes(1, 1)
        self._view_axes.set_scale(25)
        self._view_axes.reparent_to(self._pixel2d)
        
        # =========== gameview rendering ===========
        # create a top level scene node.
        # all scene-nodes should be parented to this
        self._gameview_settings = GameViewSettings()
        
        self._scene_np = p3d.NodePath("SceneNP")
        self._scene_np.reparent_to(self.render)

        self._game_dr = Forge.create_dr(
            self.win,
            p3d.LColor(0.2, 0.2, 0.2, 1.0),
            p3d.LVecBase4f(0, 0.3, 0, 0.3)
        )
        
        self._player_cam = Forge.create_cam(
            "SceneCam",
            Forge.create_prespective_lens(),
            self._scene_np,
            self._game_dr
        )
        
        self._scene_cam.np.node().set_camera_mask(EDITOR_MASK)
        self._player_cam.node().set_camera_mask(GAME_MASK)
        
        # =========== init other classes ===========
        self._mouse = Mouse()
        self._game = game(self)

    def _on_button_down(self, evt):
        # print(f"Pressed: {evt}")
        
        # increment/decrement gameview size
        if (evt == "control-i"):
            self.increase_gameview_size()
        elif (evt == "control-d"):
            self.decrease_game_view_size()
            
        # change gameview style
        if (evt == "control-1"): self.set_gameview_style(GameViewStyle.BOTTOM_LEFT)
        elif (evt == "control-2"): self.set_gameview_style(GameViewStyle.BOTTOM_RIGHT)
        elif (evt == "control-3"): self.set_gameview_style(GameViewStyle.TOP_LEFT)
        elif (evt == "control-4"): self.set_gameview_style(GameViewStyle.TOP_RIGHT)
        elif (evt == "control-0"): self.set_gameview_style(GameViewStyle.CENTER)
        
        # show/hide grid
        if (evt == "control-g"): self.show_grid()
        elif (evt == "control-h"): self.hide_grid()
        
        # send event to game
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
        self._player_cam.node().get_lens().set_aspect_ratio(aspect_ratio)
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
        camera_quat = self._scene_cam.np.get_quat()
        camera_quat.invert_in_place()
        self._view_axes.set_quat(camera_quat)
        
        # update direction reference axis
        self._grid_np.set_shader_input("camPos", self._scene_cam.np.get_pos())
        
        # update game
        self._game.on_update(task)
        
        # continue
        return task.cont

    def hide_grid(self):
        self._grid_np.hide()
        
    def show_grid(self):
        self._grid_np.show()

    def increase_gameview_size(self):
        increment = (1.0 - GameViewDefaultSize) / 4.0
        min_size = GameViewDefaultSize
        
        self._gameview_settings.size = clamp(
            self._gameview_settings.size + increment, min_size, 1.0
        )
        
        self.update_game_view(self._gameview_settings, self._game_dr)

    def decrease_game_view_size(self):
        decrement = (1.0 - GameViewDefaultSize) / 4.0
        min_size = GameViewDefaultSize
        
        self._gameview_settings.size = clamp(
            self._gameview_settings.size - decrement, min_size, 1.0
        )
 
        self.update_game_view(self._gameview_settings, self._game_dr)

    def update_game_view(self, gameview_settings, dr3d):
        width = gameview_settings.size
        height = gameview_settings.size
        style = gameview_settings.style
        
        left_anchor = (style == GameViewStyle.BOTTOM_LEFT or style == GameViewStyle.TOP_LEFT)
        right_anchor = (style == GameViewStyle.BOTTOM_RIGHT or style == GameViewStyle.TOP_RIGHT)
        bottom_anchor = (style == GameViewStyle.BOTTOM_LEFT or style == GameViewStyle.BOTTOM_RIGHT)
        top_anchor = (style == GameViewStyle.TOP_LEFT or style == GameViewStyle.TOP_RIGHT)
        center = (style == GameViewStyle.CENTER)

        if (center):
            left = 0.5 - width / 2.0
            right = 0.5 + width / 2.0
            bottom = 0.5 - height / 2.0
            top = 0.5 + height / 2.0
        else:
            left = 0.0 if left_anchor else 1.0 - width
            right = width if left_anchor else 1.0
            
            bottom = 0.0 if bottom_anchor else 1.0 - height
            top = height if bottom_anchor else 1.0

        # Update 3d and 2d display-regions
        dr3d.set_dimensions(left, right, bottom, top)
        
    def set_gameview_style(self, style: GameViewStyle):
        self._gameview_settings.style = style
        self.update_game_view(self._gameview_settings, self._game_dr)
        
    def is_btn_down(self, btn):
        return self.mouseWatcherNode.is_button_down(btn)

    @property
    def scene_np(self):
        return self._scene_np

    def create_cam(name, lens, render, dr):
        cam = p3d.Camera(name)
        cam.set_lens(lens)
        cam_np = p3d.NodePath(cam)
        
        if render is not None: cam_np.reparent_to(render)
        if dr is not None: dr.set_camera(cam_np)
        
        return cam_np

    def create_prespective_lens(near=0.05, far=1000, fov=60):
        lens = p3d.PerspectiveLens()
        lens.set_fov(fov)
        lens.set_near_far(near, far)
        return lens
        
    def create_ortho_lens(nnear=0.05, far=1000, film_size=p3d.LVecBase2i(2, 2)):
        lens = p3d.OrthographicLens()
        lens.set_film_size(film_size)
        lens.set_near_far(near, far)
        return lens

    def create_dr(win, clear_color: p3d.LColor, size: p3d.LVecBase4f, cam=None):
        dr = win.make_display_region(size)
        dr.set_clear_color_active(True)
        dr.set_clear_depth_active(True)
        dr.set_clear_color(clear_color)
        if cam: dr.set_camera(cam)
        return dr
