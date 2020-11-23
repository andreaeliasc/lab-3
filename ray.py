#Andrea Estefania Elias Cobar
from lib import *
from sphere import *
from math import pi, tan
import random

class Material(object):
  def __init__(self, diffuse, albedo, spec):
    self.diffuse = diffuse
    self.albedo = albedo
    self.spec = spec



esferas = Material(diffuse=color(255, 0, 0), albedo=(0.6, 0.3, 0.1, 0), spec=5)



BLACK = color(0, 0, 0)
WHITE = color(255, 255, 255)
BACKGROUND = color(200, 200, 190)
MAX_RECURSION_DEPTH = 3

class Raycaster(object):
  def __init__(self, width, height):
    self.width = width
    self.height = height
    self.background_color = BLACK
    self.scene = []
    self.glClear()

  def glClear(self):
    self.pixels = [
      [self.background_color for x in range(self.width)]
      for y in range(self.height)
    ]

  def finish(self, filename):
    f = open(filename, 'bw')

    #file header
    f.write(char('B'))
    f.write(char('M'))
    f.write(dword(14 + 40 + self.width * self.height * 3))
    f.write(dword(0))
    f.write(dword(14 + 40))


    # image loader
    f.write(dword(40))
    f.write(dword(self.width))
    f.write(dword(self.height))
    f.write(word(1))
    f.write(word(24))
    f.write(dword(0))
    f.write(dword(self.width * self.height * 3))
    f.write(dword(0))
    f.write(dword(0))
    f.write(dword(0))
    f.write(dword(0))


    # pixel data
    for x in range(self.width):
      for y in range(self.height):
        f.write(self.pixels[x][y].toBytes())


    f.close()

  
  def point(self, x, y, color = None):
    try: 
      self.pixels[y][x] = color or self.background_color
    except:
      pass

  def scene_intersect(self, orig, direction):
    zbuffer = float('inf')

    material = None
    intersect = None

    for obj in self.scene:
      hit = obj.ray_intersect(orig, direction)
      if hit is not None:
        if hit.distance < zbuffer:
          zbuffer = hit.distance
          material = obj.material
          intersect = hit

    return material, intersect

  def cast_ray(self, orig, direction, recursion=0):
    material, intersect = self.scene_intersect(orig, direction)

    if material is None or recursion >= MAX_RECURSION_DEPTH:   # break recursion of reflections after n iterations
      return self.background_color

    offset_normal = mul(intersect.normal, 1.1)

    if material.albedo[2] > 0:
      reverse_direction = mul(direction, -1)
      reflect_dir = reflect(reverse_direction, intersect.normal)
      reflect_orig = sub(intersect.point, offset_normal) if dot(reflect_dir, intersect.normal) < 0 else sum(intersect.point, offset_normal)
      reflect_color = self.cast_ray(reflect_orig, reflect_dir, recursion + 1)
    else:
      reflect_color = color(0, 0, 0)

    if material.albedo[3] > 0:
      refract_dir = refract(direction, intersect.normal, material.refractive_index)
      refract_orig = sub(intersect.point, offset_normal) if dot(refract_dir, intersect.normal) < 0 else sum(intersect.point, offset_normal)
      refract_color = self.cast_ray(refract_orig, refract_dir, recursion + 1)
    else:
      refract_color = color(0, 0, 0)

    light_dir = norm(sub(self.light.position, intersect.point))
    light_distance = length(sub(self.light.position, intersect.point))

    shadow_orig = sub(intersect.point, offset_normal) if dot(light_dir, intersect.normal) < 0 else sum(intersect.point, offset_normal)
    shadow_material, shadow_intersect = self.scene_intersect(shadow_orig, light_dir)
    shadow_intensity = 0

    if shadow_material and length(sub(shadow_intersect.point, shadow_orig)) < light_distance:
      shadow_intensity = 0.9

    intensity = self.light.intensity * max(0, dot(light_dir, intersect.normal)) * (1 - shadow_intensity)

    reflection = reflect(light_dir, intersect.normal)
    specular_intensity = self.light.intensity * (
      max(0, -dot(reflection, direction))**material.spec
    )

    diffuse = material.diffuse * intensity * material.albedo[0]
    specular = color(255, 255, 255) * specular_intensity * material.albedo[1]
    reflection = reflect_color * material.albedo[2]
    refraction = refract_color * material.albedo[3]
    return diffuse + specular + reflection + refraction

  def render(self):
    fov = int(pi/2)
    for y in range(self.height):
      for x in range(self.width):
        i =  (2 * (x + 0.5)/self.width - 1) * tan(fov/2) * self.width/self.height
        j =  (2 * (y + 0.5)/self.height - 1) * tan(fov/2)
        direction = norm(V3(i, j, -1))
        
        ver_rojo = self.cast_ray(V3(0.3, 0, 0), direction)
        luz_roja = (ver_rojo * 0.5 + color(100, 0, 0)) if ver_rojo != self.background_color else ver_rojo

       
        ver_azul = self.cast_ray(V3(-0.3, 0, 0), direction)
        luz_azul = (ver_azul * 0.5 + color(0, 0, 100)) if ver_azul != self.background_color else ver_azul

        luz_total = luz_roja + luz_azul
        self.pixels[y][x] = luz_total

r = Raycaster(2000, 2000)

r.light = Light(
  position=V3(40, 20, 20),
  intensity=1.5
)

r.scene = [
  
  Sphere(V3(0, -1, -10), 2, esferas),
  
]


r.render()
r.finish('holaPandai.bmp')



