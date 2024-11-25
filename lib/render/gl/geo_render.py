import numpy as np
import random

from .framework import *
from .cam_render import CamRender


class GeoRender(CamRender):
    def __init__(self, width=1600, height=1200, name='Geo Renderer'):
        program_files = ['geo.vs', 'geo.fs']
        CamRender.__init__(self, width, height, name, program_files=program_files)

        # WARNING: this differs from vertex_buffer and vertex_data in Render
        self.vert_buffer = {}
        self.vert_data = {}

        self.norm_buffer = {}
        self.norm_data = {}

        self.vertex_dim = {}
        self.n_vertices = {}

    def set_mesh(self, vertices, faces, norms, faces_nml, mat_name='all'):
        self.vert_data[mat_name] = vertices[faces.reshape([-1])]
        self.n_vertices[mat_name] = self.vert_data[mat_name].shape[0]
        self.vertex_dim[mat_name] = self.vert_data[mat_name].shape[1]

        if mat_name not in self.vert_buffer.keys():
            self.vert_buffer[mat_name] = glGenBuffers(1)
        glBindBuffer(GL_ARRAY_BUFFER, self.vert_buffer[mat_name])
        glBufferData(GL_ARRAY_BUFFER, self.vert_data[mat_name], GL_STATIC_DRAW)

        self.norm_data[mat_name] = norms[faces_nml.reshape([-1])]
        if mat_name not in self.norm_buffer.keys():
            self.norm_buffer[mat_name] = glGenBuffers(1)
        glBindBuffer(GL_ARRAY_BUFFER, self.norm_buffer[mat_name])
        glBufferData(GL_ARRAY_BUFFER, self.norm_data[mat_name], GL_STATIC_DRAW)

        glBindBuffer(GL_ARRAY_BUFFER, 0)

    def cleanup(self):
        
        glBindBuffer(GL_ARRAY_BUFFER, 0)
        for key in self.vert_data:
            glDeleteBuffers(1, [self.vert_buffer[key]])
            glDeleteBuffers(1, [self.norm_buffer[key]])

        self.vert_buffer = {}
        self.vert_data = {}
    
        self.norm_buffer = {}
        self.norm_data = {}

        self.render_texture_mat = {}

        self.vertex_dim = {}
        self.n_vertices = {}

    def draw(self):
        self.draw_init()

        glEnable(GL_MULTISAMPLE)

        glUseProgram(self.program)
        glUniformMatrix4fv(self.model_mat_unif, 1, GL_FALSE, self.model_view_matrix.transpose())
        glUniformMatrix4fv(self.persp_mat_unif, 1, GL_FALSE, self.projection_matrix.transpose())

        for mat in self.vert_buffer:
            # Handle vertex buffer
            glBindBuffer(GL_ARRAY_BUFFER, self.vert_buffer[mat])
            glEnableVertexAttribArray(0)
            glVertexAttribPointer(0, self.vertex_dim[mat], GL_DOUBLE, GL_FALSE, 0, None)

            # Handle normal buffer
            glBindBuffer(GL_ARRAY_BUFFER, self.norm_buffer[mat])
            glEnableVertexAttribArray(1)
            glVertexAttribPointer(1, 3, GL_DOUBLE, GL_FALSE, 0, None)

            glDrawArrays(GL_TRIANGLES, 0, self.n_vertices[mat])

            glDisableVertexAttribArray(1)
            glDisableVertexAttribArray(0)

        glBindBuffer(GL_ARRAY_BUFFER, 0)

        glUseProgram(0)

        glDisable(GL_MULTISAMPLE)

        self.draw_end()
