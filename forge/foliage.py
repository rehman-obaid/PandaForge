import struct
import random
import panda3d.core as p3d

p3d.load_prc_file_data('', '''framebuffer-srgb 1
    sync-video 0
    show-frame-rate-meter 1
    multisamples 0'''
)

from operator import itemgetter
from direct.showbase.ShowBase import ShowBase


FT_LINEAR = p3d.SamplerState.FT_linear
FT_MIPMAP = p3d.SamplerState.FT_linear_mipmap_linear
GLSL = p3d.Shader.SLGLSL
F_SRGB = p3d.Texture.F_srgb
F_SRGBA = p3d.Texture.F_srgb_alpha


class App(ShowBase):
    def __init__(self):
        super().__init__(self)

        # make the grass map more gpu friendly:
        grass_map = p3d.PNMImage()
        grass_map.read('../../models/texture/terrain/terrain_grass.png')
        
        grass_list=[]
        
        x_size = grass_map.get_read_x_size()
        y_size = grass_map.get_read_y_size()
        
        # Compute grid spacing so the grid covers the same world area as before
        # (scale 512, offset -256)
        grid_spacing_x = 512.0 / x_size
        grid_spacing_y = 512.0 / y_size
        
        for x in range(x_size):
            for y in range(y_size):
                if grass_map.get_bright(x,y) > 0.1:
                    # Map grid indices to world coordinates
                    # Add a bit of random jitter to avoid 'grass grid' appearance
                    pos_x = -256.0 + (x + 0.5) * grid_spacing_x + random.uniform(-0.5, 0.5) * grid_spacing_x
                    pos_y = -256.0 + (y + 0.5) * grid_spacing_y + random.uniform(-0.5, 0.5) * grid_spacing_y
                    pos_z = 0.0  # flat ground
                    grass_list.append(p3d.LPoint3(pos_x, pos_y, pos_z))
                    
        print(f"Grass count: {len(grass_list)}")

        # pack the grass_list into a buffer_texture
        grass_buf_tex = p3d.Texture('texbuffer')
        grass_buf_tex.setup_buffer_texture(
            len(grass_list) + 1,
            p3d.Texture.T_float,
            p3d.Texture.F_rgb32,
            p3d.GeomEnums.UH_static
        )
        
        image = memoryview(grass_buf_tex.modify_ram_image())
        for i, pos in enumerate(grass_list):
            off = i * 12
            image[off:off+12] = struct.pack('fff', pos[0], pos[1], pos[2])
            
        # load the grass model
        grass_model=self.loader.load_model('../../models/grass')
        grass_model.flatten_strong()
        
        # fix texture for srgb
        if  p3d.ConfigVariableBool('framebuffer-srgb').get_value():
            for tex_stage in grass_model.find_all_texture_stages():
                tex = grass_model.find_texture(tex_stage)
                if tex:
                    tex.set_format(F_SRGBA)
                    grass_model.set_texture(tex_stage, tex, 1)

        grass_model.set_shader(p3d.Shader.load(GLSL, 'shaders/grass_v.glsl', 'shaders/grass_f.glsl'), 1)
        grass_model.set_shader_input('grass_buf_tex', grass_buf_tex)
        grass_model.set_shader_input('clip_distance', 125.0)
        grass_model.set_instance_count(len(grass_list))
        grass_model.reparent_to(self.render)
        
        # alpha testing will be done in the shader
        grass_model.set_transparency(p3d.TransparencyAttrib.M_multisample, 1)
        
        # set the bounds so it stays visible
        grass_model.node().set_bounds(p3d.BoundingBox((-256,-256, 0), (256, 256, 10)))
        grass_model.node().set_final(1)

        # make skybox
        self.sky_box=self.loader.load_model('../../models//box')
        self.sky_box.reparent_to(self.render)
        self.sky_box.set_scale(10)
        self.sky_box.set_shader(p3d.Shader.load(GLSL, 'shaders/skybox_v.glsl', 'shaders/skybox_f.glsl'), 1)
        self.sky_box.set_shader_input('blur', 0.0)
        self.sky_box.set_bin('background', 100)
        self.sky_box.set_depth_test(False)
        self.sky_box.set_depth_write(False)
        
        self.render.set_shader_input("camera", self.cam)
        self.render.set_shader_input('env_map', self.loader.load_texture('../../models/texture/cubemap/qwantani.txo'))

        # add a task to update the skybox
        self.taskMgr.add(self.update, 'update')

    def update(self, task):
        ''' Per frame update task'''
        self.sky_box.set_pos(self.cam.get_pos(self.render))
        return task.cont


app=App()
app.run()
