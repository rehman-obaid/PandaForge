from dataclasses import dataclass


@dataclass
class Mouse:
    # raw mouse pointer x and y (pixel co-ordinates)
    _x = 0.0
    _y = 0.0

    # mouse x and y (screen co-ordinates)
    _mx = 0.0
    _my = 0.0

    # mouse dx and dy (movement displacement from last frame)
    _dx = 0.0
    _dy = 0.0

    _zoom = 0

    _vertical_axis = 0.0
    _horizontal_axis  = 0.0

    _has_mouse = False

    _last_valid = False
    _force_relative_mode = False
    
    def _update(self,
        mouse_x,
        mouse_y,
        has_mouse,
        force_relative
    ):
        self._has_mouse = has_mouse
        
        if (self._has_mouse):
            if (force_relative):
                if (not self._force_relative_mode):
                    # entering relative mode — reset state
                    self._x = 0
                    self._y = 0
                    
                    self._dx = 0
                    self._dy = 0
                    
                    self._force_relative_mode = True
                    self._last_valid = False
                else:
                    # after recentering, watcher reports ~0,0
                    # so current position IS the delta
                    self._dx = mouse_x
                    self._dy = mouse_y
                    
                # MouseWatcher will report 0,0 next frame — but to be safe,
                # treat this frame's post-warp read as the new baseline
                self._last_valid = False;
            else:
                if (self._force_relative_mode or not self._last_valid):
                    self._dx = 0
                    self._dy = 0
                    
                    self._force_relative_mode = False;
                else:
                    self._dx = mouse_x - self._x
                    self._dy = mouse_y - self._y

                self._x = mouse_x
                self._y = mouse_y
                
                self._last_valid = True
                
            self._mx = mouse_x
            self._my = mouse_y
       
        else:
            self._dx = 0
            self._dy = 0
            
        self._horizontal_axis = 1 if self._dx > 0 else (-1 if self._dx < 0 else 0)
        self._vertical_axis = 1 if self._dy > 0 else (-1 if self._dy < 0 else 0)
