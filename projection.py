from __future__ import annotations
from dataclasses import dataclass
from typing import Callable
import math as m

@dataclass
class Vec3:
    x:float = 0.0
    y:float = 0.0
    z:float = 0.0

    def __repr__(self) -> str:
        return f"Vec3< {self.x}, {self.y}, {self.z} >"

    def project(self, camera:Camera, screen:Screen):
        screen = screen
        camera = camera
        z_prime = camera.view_distance
        y_prime = self.y*z_prime / self.z
        x_prime = self.x*z_prime / self.z

        x = x_prime * camera.view_width / screen.width
        y = y_prime * camera.view_height / screen.height

        return x, y
    
    def tuple(self):
        return (self.x, self.y, self.z)
    
    def tuple2d(self):
        return (self.x, self.y)
    
    def get_magnitude(self):
        return m.sqrt(self.x**2 + self.y**2 + self.z**2)
    
    def get_normalized(self):
        mag = self.get_magnitude()
        return Vec3(self.x/mag, self.y/mag, self.z/mag)
    
    def get_rotation_matrix(self, rotation:Vec3):
        rot = rotation
        return (
            [ # X ROTATION
                Vec3(1, 0, 0),
                Vec3(0, m.cos(rot.x), -m.sin(rot.x)),
                Vec3(0, m.sin(rot.x), m.cos(rot.x))
            ],
            [ # Y ROTATION
                Vec3(m.cos(rot.y), 0, m.sin(rot.y)),
                Vec3(0, 1, 0),
                Vec3(-m.sin(rot.y), 0, m.cos(rot.y))
            ],
            [ # Z ROTATION
                Vec3(m.cos(rot.z), -m.sin(rot.z), 0),
                Vec3(m.sin(rot.z), m.cos(rot.z), 0),
                Vec3(0, 0, 1)
            ],
        )
    
    def rotate(self, rotation:Vec3):
        ret_rotation = Vec3(0, 0, 0)
        for rot in self.get_rotation_matrix(rotation):
            vec_buffer = []
            for vec in rot:
                vec_buffer.append(
                    vec.x*self.x + vec.y*self.y + vec.z*self.z
                )
            
            ret_rotation += Vec3(*vec_buffer)
        return ret_rotation

    
    def __add__(self, other):
        if isinstance(other, Vec3):
            return Vec3(self.x + other.x,
            self.y + other.y,
            self.z + other.z)
        else:
            return Vec3(self.x + other,
            self.y + other,
            self.z + other)

    def __sub__(self, other:Vec3):
        if isinstance(other, Vec3):
            return Vec3(self.x - other.x,
            self.y - other.y,
            self.z - other.z)
        else:
            return Vec3(self.x - other,
            self.y - other,
            self.z - other)

    def __mul__(self, other:Vec3):
        if isinstance(other, Vec3):
            return Vec3(self.x * other.x,
            self.y * other.y,
            self.z * other.z)
        else:
            return Vec3(self.x * other,
            self.y * other,
            self.z * other)

    def __div__(self, other):
        if isinstance(other, Vec3):
            return Vec3(self.x / other.x,
            self.y / other.y,
            self.z / other.z)
        else:
            return Vec3(self.x / other,
            self.y / other,
            self.z / other)

    def __pow__(self, other):
        if isinstance(other, Vec3):
            return Vec3(self.x ** other.x,
            self.y ** other.y,
            self.z ** other.z)
        else:
            return Vec3(self.x ** other,
            self.y ** other,
            self.z ** other)

    def __neg__(self,):
        return Vec3(-self.x,
        -self.y,
        -self.z)

class Screen:
    def __init__(self, width:int, height:int) -> None:
        self.width = width
        self.height = height
    
class Camera:
    def __init__(self, position:Vec3, view_width:int, view_height:int, view_distance:int) -> None:
        self.position = position
        self.view_width = view_width
        self.view_height = view_height
        self.view_distance = view_distance

class Vertex:
    def __init__(self, position:Vec3, connections:list[Vertex] | None = None) -> None:
        self.connections:list[Vertex] = connections if connections else []
        self.position:Vec3 = position

    def connect(self, vertex:Vertex):
        self.connections.append(vertex)

    def render(self, render_func:Callable[[Vec3, Vec3],None]):
        for con in self.connections:
            render_func(self.position, con.position)

class Mesh:
    def __init__(self, vertexes:list[Vertex], connection_indexes:list[tuple[int, int]]):
        self.vertexes = vertexes
        self.connection_indexes = connection_indexes
        self.connect_verts(vertexes, connection_indexes)

    @classmethod
    def connect_verts(cls, vertexes:list[Vertex], connection_indexes:list[tuple[int, int]]):
        """Connects vertexes together based on vertex index pairs in `connection_indexes` """
        for v_ind1, v_ind2 in connection_indexes:
            vertexes[v_ind1].connect(vertexes[v_ind2])

    def get_translation(self, vec3:Vec3) -> list[Vertex]:
        ret_verts:list[Vertex] = []
        for vert in self.vertexes:
            ret_verts.append(Vertex(vert.position + vec3))

        self.connect_verts(ret_verts, self.connection_indexes)

        return ret_verts

    def get_rotation(self, rotation:Vec3):
        ret_verts:list[Vertex] = []
        for vert in self.vertexes:
            ret_verts.append(Vertex(vert.position.rotate(rotation)))

        self.connect_verts(ret_verts, self.connection_indexes)
        return ret_verts
            


class Object:
    def __init__(self, mesh:Mesh, position:Vec3 | None = None, rotation:Vec3 | None = None) -> None:
        self.mesh = mesh
        self.position = position if position else Vec3(0,0,0)
        self.rotation = rotation if rotation else Vec3(0,0,0)
    
    def render(self, render_func:Callable[[Vec3, Vec3],None]):
        for vert in self.mesh.get_translation(self.position):
            vert.position += vert.position.rotate(self.rotation)
            vert.render(render_func)




if __name__ == "__main__":
    from PIL import Image, ImageDraw
    import time
    img = Image.new("RGB", (500,500), "white")
    img_draw = ImageDraw.Draw(img)
    screen = Screen(img.width, img.height)
    camera = Camera(Vec3(0.0,0.0,0.0), img.width, img.height, 200)
    cube = Mesh(
        [
            #front face
            Vertex(Vec3(-2, -0.5, 5)),
            Vertex(Vec3(-2,  0.5, 5)),
            Vertex(Vec3(-1,  0.5, 5)),
            Vertex(Vec3(-1, -0.5, 5)),
            #back face
            Vertex(Vec3(-2, -0.5, 6)),
            Vertex(Vec3(-2,  0.5, 6)),
            Vertex(Vec3(-1,  0.5, 6)),
            Vertex(Vec3(-1, -0.5, 6))
        ],
        [
            # FRONT
            (0,1),
            (1,2),
            (2,3),
            (3,0),
            # SIDES
            (0,4),
            (1,5),
            (2,6),
            (3,7),
            # BACK
            (4,5),
            (5,6),
            (6,7),
            (7,4)
        ]
    )

    cube_obj = Object(cube, Vec3(0,0,0))

    half_w = img.width/2
    half_h = img.height/2
    
    def render_func(pos_1:Vec3, pos_2:Vec3):
        (x1, y1),(x2, y2)= pos_1.project(camera, screen), pos_2.project(camera, screen)
        img_draw.line((half_w+x1, half_h+y1, half_w+x2, half_h+y2), "black", 0)
    

    cube_obj.position.x = x = 10
    cube_obj.position.y = y = 8

    for _ in range(0,25):
        cube_obj.position.y -= 2
        cube_obj.position.x = x
        cube_obj.rotation.z = 0
        for _ in range(0,25):
            cube_obj.position.x -= 2
            cube_obj.rotation.z = 0.3
            cube_obj.render(render_func)


    img.save("result.png")