import numpy as np
import random

from .framework import *
from .cam_render import CamRender


class ColorRender(CamRender):
    def __init__(self, width=1600, height=1200, name='Color Renderer'):
        program_files = ['color.vs', 'color.fs']
        CamRender.__init__(self, width, height, name, program_files=program_files)

        # WARNING: this differs from vertex_buffer and vertex_data in Render
        self.vert_buffer = {}
        self.vert_data = {}

        self.color_buffer = {}
        self.color_data = {}

        self.vertex_dim = {}
        self.n_vertices = {}

    def set_mesh(self, vertices, faces, color, faces_clr, mat_name='all'):
        self.vert_data[mat_name] = vertices[faces.reshape([-1])]
        self.n_vertices[mat_name] = self.vert_data[mat_name].shape[0]
        self.vertex_dim[mat_name] = self.vert_data[mat_name].shape[1]

        if mat_name not in self.vert_buffer.keys():
            self.vert_buffer[mat_name] = glGenBuffers(1)
        glBindBuffer(GL_ARRAY_BUFFER, self.vert_buffer[mat_name])
        glBufferData(GL_ARRAY_BUFFER, self.vert_data[mat_name], GL_STATIC_DRAW)

        self.color_data[mat_name] = color[faces_clr.reshape([-1])]
        if mat_name not in self.color_buffer.keys():
            self.color_buffer[mat_name] = glGenBuffers(1)
        glBindBuffer(GL_ARRAY_BUFFER, self.color_buffer[mat_name])
        glBufferData(GL_ARRAY_BUFFER, self.color_data[mat_name], GL_STATIC_DRAW)

        glBindBuffer(GL_ARRAY_BUFFER, 0)

    def cleanup(self):
        
        glBindBuffer(GL_ARRAY_BUFFER, 0)
        for key in self.vert_data:
            glDeleteBuffers(1, [self.vert_buffer[key]])
            glDeleteBuffers(1, [self.color_buffer[key]])

        self.vert_buffer = {}
        self.vert_data = {}
    
        self.color_buffer = {}
        self.color_data = {}

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
            glBindBuffer(GL_ARRAY_BUFFER, self.color_buffer[mat])
            glEnableVertexAttribArray(1)
            glVertexAttribPointer(1, 3, GL_DOUBLE, GL_FALSE, 0, None)

            glDrawArrays(GL_TRIANGLES, 0, self.n_vertices[mat])

            glDisableVertexAttribArray(1)
            glDisableVertexAttribArray(0)

        glBindBuffer(GL_ARRAY_BUFFER, 0)

        glUseProgram(0)

        glDisable(GL_MULTISAMPLE)

        self.draw_end()
