from collections import namedtuple
import struct
import numpy

class V3(object):
  def __init__(self, x, y=None, z=None):
    if (type(x) == numpy.matrix):
      self.x, self.y, self.z = x.tolist()[0]
    else:
      self.x = x
      self.y = y
      self.z = z
  
  def __repr__(self):
    return "V3(%s, %s, %s)" % (self.x, self.y, self.z)

class V2(object):
  def __init__(self, x, y=None):
    if (type(x) == numpy.matrix):
      self.x, self.y = x.tolist()[0]
    else:
      self.x = x
      self.y = y
  
  def __repr__(self):
    return "V2(%s, %s)" % (self.x, self.y)

def sum(v0, v1):
  return V3(v0.x + v1.x, v0.y + v1.y, v0.z + v1.z)

def sub(v0, v1):
  return V3(v0.x - v1.x, v0.y - v1.y, v0.z - v1.z)

def mul(v0, k):
  return V3(v0.x * k, v0.y * k, v0.z * k)

def dot(v0, v1):
  return v0.x * v1.x + v0.y * v1.y + v0.z * v1.z

def length(v0):
  return (v0.x**2 + v0.y**2 + v0.z**2)**0.5

def norm(v0):
  v0length = length(v0)
  if not v0length:
    return V3(0, 0, 0)

  return V3(v0.x/v0length, v0.y/v0length, v0.z/v0length)

def bbox(*vertices):
  xs = [vertex.x for vertex in vertices]
  ys = [vertex.y for vertex in vertices]

  return (max(xs), max(ys), min(xs), min(ys))

def cross(v1, v2):
  return V3(
    v1.y * v2.z - v1.z * v2.y,
    v1.z * v2.x - v1.x * v2.z,
    v1.x * v2.y - v1.y * v2.x
  )


def barycentric(A, B, C, P):
  bc = cross(
    V3(B.x - A.x, C.x - A.x, A.x - P.x),
    V3(B.y - A.y, C.y - A.y, A.y - P.y)
  )

  if abs(bc.z) < 1:
    return -1, -1, -1

  u = bc.x / bc.z
  v = bc.y / bc.z
  w = 1 - (bc.x + bc.y) / bc.z

  return w, v, u  

# def allbarycentric(A, B, C, bbox_min, bbox_max):
#   barytransform = numpy.linalg.inv([[A.x, B.x, C.x],
#   gr])

def multMatriz(a, b):
  c = []
  for i in range(0, len(a)):
    temp = []
    for j in range(0, len(b[0])):
      s = 0
      for k in range(0, len(a[0])):
        s += a[i][k]*b[k][j]
      temp.append(s)
    c.append(temp)
  return c

def reflect(I, N):
  Lm = mul(I, -1)
  n = mul(N, 2 * dot(Lm, N))
  return norm(sub(Lm, n))

def refract(I, N, refractive_index):  # Implementation of Snell's law
  cosi = -max(-1, min(1, dot(I, N)))
  etai = 1
  etat = refractive_index

  if cosi < 0:  # if the ray is inside the object, swap the indices and invert the normal to get the correct result
    cosi = -cosi
    etai, etat = etat, etai
    N = mul(N, -1)

  eta = etai/etat
  k = 1 - eta**2 * (1 - cosi**2)
  if k < 0:
    return V3(1, 0, 0)

  return norm(sum(
    mul(I, eta),
    mul(N, (eta * cosi - k**(1/2)))
  ))

def char(c):
  return struct.pack('=c', c.encode('ascii'))

def word(c):
  return struct.pack('=h', c)

def dword(c):
  return struct.pack('=l', c)

def color(r, g, b):
  return bytes([b, g, r])

class color(object):
  def __init__(self, r, g, b):
    self.r = r
    self.g = g
    self.b = b

  def __add__(self, other_color):
    r = self.r + other_color.r
    g = self.g + other_color.g
    b = self.b + other_color.b

    return color(r, g, b)

  def __mul__(self, other):
    r = self.r * other
    g = self.g * other
    b = self.b * other
    return color(r, g, b)

  def __repr__(self):
    return "color(%s, %s, %s)" % (self.r, self.g, self.b)

  def toBytes(self):
    self.r = int(max(min(self.r, 255), 0))
    self.g = int(max(min(self.g, 255), 0))
    self.b = int(max(min(self.b, 255), 0))
    return bytes([self.b, self.g, self.r])

  def __truediv__(self, other):
    r = self.r / other
    g = self.g / other
    b = self.b / other
    return color(r, g, b)
    
  def __eq__(self, other):
    if other is None or not isinstance(other, color):
      return False
    return (self.r, self.g, self.b) == (other.r, other.r, other.r)

  __rtruediv__ = __truediv__
  __rmul__ = __mul__

class Light(object):
  def __init__(self, position=V3(0, 0, 0), intensity=1):
    self.position = position
    self.intensity = intensity


class Intersect(object):
  def __init__(self, distance=0, point=None, normal=None):
    self.distance = distance
    self.point = point
    self.normal = normal
    
