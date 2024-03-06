# https://github.com/QuirkyCort/pgzhelper


import math
import pygame
from pgzero.actor import Actor, POS_TOPLEFT, ANCHOR_CENTER, transform_anchor
from pgzero import game, loaders
from typing import Sequence, Tuple, Union
from pygame import Vector2

_Coordinate = Union[Tuple[float, float], Sequence[float], Vector2]


class Actor(Actor):
  def __init__(self, image:Union[str, pygame.Surface], pos=POS_TOPLEFT, anchor=ANCHOR_CENTER, **kwargs):
    self._flip_x = False
    self._flip_y = False
    self._scale = 1
    self._mask = None
    self._images = None
    self._image_idx = 0
    self._subrects = None
    self._transform_cnt = 0
    self._orig_surfs = {}
    self._surfs = {}
    self._animate_counter = 0
    self._animate_run = False
    self._radius = None
    self._collision_width = None
    self._collision_height = None
    self.fps = 5
    self.direction = 0
    self.velocityX = 0
    self.velocityY = 0


    subrect=kwargs.pop('subrect',None)
    image_str = None
    if isinstance(image,str):
      image_str = image
    super().__init__(image_str, pos, anchor, **kwargs)
    if isinstance(image,pygame.Surface):
        self._orig_surf = image
        self._update_pos()
    self._subrect=None
    if subrect is not None:
      self.subrect=subrect

  def distance_to(self, target):
    if isinstance(target, Actor):
      x, y = target.pos
    else:
      x, y = target
    return distance_to(self.x, self.y, x, y)

  def distance_toXY(self, x, y):
    return distance_to(self.x, self.y, x, y)

  def direction_to(self, target):
    if isinstance(target, Actor):
      x, y = target.pos
    else:
      x, y = target
    return direction_to(self.x, self.y, x, y)

  def direction_toXY(self, x, y):
    return direction_to(self.x, self.y, x, y)


  def move_towards(self, target:Union[int, float, Actor, _Coordinate], dist, stop_on_target=True):
    if isinstance(target, (int,float)):
      direction = target
    else:
      direction = self.direction_to(target)
      if stop_on_target:
          target_distance = self.distance_to(target)
          if (target_distance < dist) and dist>0:
            dist = target_distance
    self.x, self.y = move(self.x, self.y, direction, dist)

  def move_towardsXY(self, x, y, dist):
    direction = self.direction_toXY(x, y)
    self.x, self.y = move(self.x, self.y, direction, dist)

  def point_towards(self, actor, y=None):
    self.angle = self.direction_to(actor)

  def point_towardsXY(self, x, y):
    self.angle = direction_to(self.x, self.y, x, y)

  def move_in_direction(self, dist):
    self.x, self.y = move(self.x, self.y, self.direction, dist)

  def move_forward(self, dist):
    self.x, self.y = move(self.x, self.y, self.angle, dist)

  def move_left(self, dist):
    self.x, self.y = move(self.x, self.y, self.angle + 90, dist)

  def move_right(self, dist):
    self.x, self.y = move(self.x, self.y, self.angle - 90, dist)

  def move_back(self, dist):
    self.x, self.y = move(self.x, self.y, self.angle, -dist)

  @property
  def images(self):
    return self._images

  @images.setter
  def images(self, images):
    self._subrects = None
    self._images = images
    if len(self._images) != 0:
      self.image = self._images[0]

  def load_images(self, sheet_name:str, cols:int, rows:int, cnt:int=0, subrect:pygame.Rect=None):
    self._subrects=[None]*cols*rows
    self._image_idx=0
    sheet:pygame.Surface = loaders.images.load(sheet_name)
    if subrect is not None:
      sheet = sheet.subsurface(subrect)
    for col in range(0,cols):
      for row in range(0,rows):
          width=sheet.get_width()/cols
          height=sheet.get_height()/rows
          self._subrects[col+row*cols]=(int(col*width),int(row*height),int(width),int(height))
    if len(self._subrects) != 0:
      self.image = sheet_name
      self.subrect = self._subrects[0]

  def sel_image(self, newimage:Union[str, int])-> bool:
    try:
      if isinstance(newimage, int):
          if self._subrects is None and self._images is None:
            return False
          if self._subrects is not None:
            self.subrect = self._subrects[newimage]
          else:
            self.image = self._images[newimage]
          self._image_idx = newimage
          return True
      else:
        self._image_idx = self._images.index(newimage)
        self.image = newimage
    except:
      return False

  def next_image(self)-> int:
    if self._subrects is not None:
      next_image_idx = (self._image_idx+1) % len(self._subrects)
      self._image_idx = next_image_idx
      self.subrect = self._subrects[self._image_idx]
    elif (self._images is not None) :
      if (self.image in self._images):
        next_image_idx = (self._images.index(self.image)+1) % len(self._images)
        self._image_idx = next_image_idx
        self.image = self._images[self._image_idx]
      else:
        self._image_idx = 0
        self.image = self._images[0]
    else:
      self._image_idx = 0
    return self._image_idx

  def animate(self)-> int:
    now = int(time.time() * self.fps)
    if self._animate_counter == 0:
      self._animate_counter=now
    frames_elapsed = now-self._animate_counter

    if frames_elapsed!=0:
      self._animate_counter = now
      idx=self.next_image()
      return idx
    else:
      return -1

  @property
  def angle(self):
    return self._angle

  @angle.setter
  def angle(self, angle):
    self._angle = angle
    self._transform_surf()
    self._transform_cnt+=1

  @property
  def scale(self):
    return self._scale

  @scale.setter
  def scale(self, scale):
    self._scale = scale
    self._transform_surf()
    self._transform_cnt+=1

  @property
  def flip_x(self):
    return self._flip_x

  @flip_x.setter
  def flip_x(self, flip_x):
    self._flip_x = flip_x
    self._transform_surf()
    self._transform_cnt+=1

  @property
  def flip_y(self):
    return self._flip_y

  @flip_y.setter
  def flip_y(self, flip_y):
    self._flip_y = flip_y
    self._transform_surf()
    self._transform_cnt+=1

  @property
  def image(self):
    return self._image_name

  @image.setter
  def image(self, image):
    if image is not None:
      self._orig_surf = self._surf = loaders.images.load(image)
      self._image_name = image
      self._orig_surfs[image]=self._orig_surf
    else:
      self._orig_surf = self._surf = pygame.Surface((1,1),pygame.SRCALPHA)
      self._image_name = ''
    self._update_pos()
    if image is not None:
      if (image not in self._surfs) or (self._surfs[image][1]!=self._transform_cnt):
        self._transform_surf()
        self._surfs[image]=(self._surf,self._transform_cnt)

  @property
  def subrect(self):
    return self._subrect
  @subrect.setter
  def subrect(self, subrect:pygame.Rect):
    subr = subrect
    if subrect is not None:
      subr=pygame.Rect(subrect)
    if subr != self._subrect:
      self._subrect = subr
      if self._subrect is not None:
        hashv=hash((subr.x, subr.y,subr.width,subr.height))
        surf_name=self._image_name+str(hashv)
        if surf_name not in self._orig_surfs:
          self._orig_surfs[surf_name] = loaders.images.load(self.image).subsurface(subr)
        self._orig_surf=self._orig_surfs[surf_name]
        self._update_pos()
        if (surf_name not in self._surfs) or (self._surfs[surf_name][1]!=self._transform_cnt):
          self._transform_surf()
          self._surfs[surf_name]=(self._surf,self._transform_cnt)
        self._surf=self._surfs[surf_name][0]
      else:
        self._orig_surf = self._surf = loaders.images.load(self.image)
        self._update_pos()
        self._transform_surf()

  @property
  def orig_surf(self):
    return self._orig_surf

  @orig_surf.setter
  def orig_surf(self, surf:pygame.Surface):
    self._orig_surf = self._surf =surf
    self._update_pos()
    self._transform_surf()

  def recalc(self):
    self._surf = self._orig_surf
    self._update_pos()
    self._transform_surf()

  def _transform_surf(self):
    self._surf = self._orig_surf
    p = self.pos

    if self._scale != 1:
      size = self._orig_surf.get_size()
      self._surf = pygame.transform.scale(self._surf, (int(size[0] * self.scale), int(size[1] * self.scale)))
    if self._flip_x:
      self._surf = pygame.transform.flip(self._surf, True, False)
    if self._flip_y:
      self._surf = pygame.transform.flip(self._surf, False, True)

    self._surf = pygame.transform.rotate(self._surf, self._angle)

    self.width, self.height = self._surf.get_size()
    w, h = self._orig_surf.get_size()
    ax, ay = self._untransformed_anchor
    anchor = transform_anchor(ax, ay, w, h, self._angle)
    self._anchor = (anchor[0] * self.scale, anchor[1] * self.scale)

    self.pos = p
    self._mask = None

  def collidepoint_pixel(self, x, y=0):
    if isinstance(x, tuple):
      y = x[1]
      x = x[0]
    if self._mask == None:
      self._mask = pygame.mask.from_surface(self._surf)

    xoffset = int(x - self.left)
    yoffset = int(y - self.top)
    if xoffset < 0 or yoffset < 0:
      return 0

    width, height = self._mask.get_size()
    if xoffset >= width or yoffset >= height:
      return 0

    return self._mask.get_at((xoffset, yoffset))

  def collide_pixel(self, actor):
    for a in [self, actor]:
      if a._mask == None:
        a._mask = pygame.mask.from_surface(a._surf)

    xoffset = int(actor.left - self.left)
    yoffset = int(actor.top - self.top)

    return self._mask.overlap(actor._mask, (xoffset, yoffset))

  def collidelist_pixel(self, actors):
    for i in range(len(actors)):
      if self.collide_pixel(actors[i]):
        return i
    return -1

  def collidelistall_pixel(self, actors):
    collided = []
    for i in range(len(actors)):
      if self.collide_pixel(actors[i]):
        collided.append(i)
    return collided

  def _unrotated_size(self):
      w = self._orig_surf.get_width()*self.scale
      h = self._orig_surf.get_height()*self.scale
      return w, h

  @property
  def collision_width(self):
    if self._collision_width is None:
      w,_ = self._unrotated_size()
      return w
    return self._collision_width

  @collision_width.setter
  def collision_width(self, collision_width):
    self._collision_width = collision_width

  @property
  def collision_height(self):
    if self._collision_height is None:
      _,h = self._unrotated_size()
      return h
    return self._collision_height

  @collision_height.setter
  def collision_height(self, collision_height):
    self._collision_height = collision_height

  def obb_collidepoint(self, x, y):
    w,h = self._unrotated_size()
    return Collide.obb_point(self.centerx, self.centery, w, h, self._angle, x, y)

  def obb_collidepoints(self, points):
    w,h = self._unrotated_size()
    return Collide.obb_points(self.centerx, self.centery, w, h, self._angle, points)

  def obb_collideobb(self, actor):
    if self._collision_width is None and self._collision_height is None:
      x,y = self.centerx, self.centery
    else:
      x,y = self.x, self.y

    if actor._collision_width is None and actor._collision_height is None:
      x2,y2 = actor.centerx, actor.centery
    else:
      x2,y2 = actor.x, actor.y

    return Collide.obb_obb(x, y, self.collision_width, self.collision_height, self._angle,
                              x2, y2, actor.collision_width, actor.collision_height, actor._angle)

  @property
  def radius(self):
    if self._radius is None:
      w,h = self._unrotated_size()
      self._radius = min(w, h) * .5
    return self._radius

  @radius.setter
  def radius(self, radius):
    self._radius = radius

  def circle_collidepoints(self, points):
    return Collide.circle_points(self.centerx, self.centery, self._radius, points)

  def circle_collidepoint(self, x, y):
    return Collide.circle_point(self.centerx, self.centery, self._radius, x, y)

  def circle_collidecircle(self, actor):
    return Collide.circle_circle(self.centerx, self.centery, self._radius, actor.centerx, actor.centery, actor._radius)

  def circle_colliderect(self, actor):
    return Collide.circle_rect(self.centerx, self.centery, self._radius, actor.centerx, actor.centery, actor.width, actor.height)

  def circle_collideobb(self, actor):
    w2, h2 = actor._unrotated_size()
    return Collide.obb_circle(actor.centerx, actor.centery, w2, h2, actor.angle,
                              self.centerx, self.centery, self._radius)

  def draw(self):
    game.screen.blit(self._surf, self.topleft)

  def get_rect(self):
    return self._rect
