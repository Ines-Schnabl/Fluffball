"""
author: Ines Schnabl
email: ines@schnabl.sc
contact: ines@schnabl.sc
license: gpl, see http://www.gnu.org/licenses/gpl-3.0.de.html
download: 
idea: A game for up to 4 players with fluffy balls, donuts, cookies and cats
"""

import pygame
import random
import os
import time
import math

def randomize_color(color, delta=50):
    d=random.randint(-delta, delta)
    color = color + d
    color = min(255,color)
    color = max(0, color)
    return color

def make_text(msg="pygame is cool", fontcolor=(255, 0, 255), fontsize=42, font=None):
    """returns pygame surface with text. You still need to blit the surface."""
    myfont = pygame.font.SysFont(font, fontsize)
    mytext = myfont.render(msg, True, fontcolor)
    mytext = mytext.convert_alpha()
    return mytext

def write(background, text, x=50, y=150, color=(0,0,0),
          fontsize=None, center=False):
        """write text on pygame surface. """
        if fontsize is None:
            fontsize = 24
        font = pygame.font.SysFont('mono', fontsize, bold=True)
        fw, fh = font.size(text)
        surface = font.render(text, True, color)
        if center: # center text around x,y
            background.blit(surface, (x-fw//2, y-fh//2))
        else:      # topleft corner is x,y
            background.blit(surface, (x,y))
            
def distance(point_1=(0, 0), point_2=(0, 0)):
    """Returns the distance between two points"""
    return math.sqrt((point_1[0] - point_2[0]) ** 2 + (point_1[1] - point_2[1]) ** 2)

def elastic_collision(sprite1, sprite2):
        """elasitc collision between 2 VectorSprites (calculated as disc's).
           The function alters the dx and dy movement vectors of both sprites.
           The sprites need the property .mass, .radius, pos.x pos.y, move.x, move.y
           by Leonard Michlmayr"""
        if sprite1.static and sprite2.static:
            return 
        dirx = sprite1.pos.x - sprite2.pos.x
        diry = sprite1.pos.y - sprite2.pos.y
        sumofmasses = sprite1.mass + sprite2.mass
        sx = (sprite1.move.x * sprite1.mass + sprite2.move.x * sprite2.mass) / sumofmasses
        sy = (sprite1.move.y * sprite1.mass + sprite2.move.y * sprite2.mass) / sumofmasses
        bdxs = sprite2.move.x - sx
        bdys = sprite2.move.y - sy
        cbdxs = sprite1.move.x - sx
        cbdys = sprite1.move.y - sy
        distancesquare = dirx * dirx + diry * diry
        if distancesquare == 0:
            dirx = random.randint(0,11) - 5.5
            diry = random.randint(0,11) - 5.5
            distancesquare = dirx * dirx + diry * diry
        dp = (bdxs * dirx + bdys * diry) # scalar product
        dp /= distancesquare # divide by distance * distance.
        cdp = (cbdxs * dirx + cbdys * diry)
        cdp /= distancesquare
        if dp > 0:
            if not sprite2.static:
                sprite2.move.x -= 2 * dirx * dp
                sprite2.move.y -= 2 * diry * dp
            if not sprite1.static:
                sprite1.move.x -= 2 * dirx * cdp
                sprite1.move.y -= 2 * diry * cdp

class Game():
    difficulty = 1
    players = 1
    
class Flytext(pygame.sprite.Sprite):
    def __init__(self, x, y, text="hallo", color=(255, 0, 0),
                 dx=0, dy=-50, duration=2, acceleration_factor = 1.0, delay = 0, fontsize=22):
        """a text flying upward and for a short time and disappearing"""
        self._layer = 7  # order of sprite layers (before / behind other sprites)
        pygame.sprite.Sprite.__init__(self, self.groups)  # THIS LINE IS IMPORTANT !!
        self.text = text
        self.r, self.g, self.b = color[0], color[1], color[2]
        self.dx = dx
        self.dy = dy
        self.x, self.y = x, y
        self.duration = duration  # duration of flight in seconds
        self.acc = acceleration_factor  # if < 1, Text moves slower. if > 1, text moves faster.
        self.image = make_text(self.text, (self.r, self.g, self.b), fontsize)  # font 22
        self.rect = self.image.get_rect()
        self.rect.center = (self.x, self.y)
        self.time = 0 - delay

    def update(self, seconds):
        self.time += seconds
        if self.time < 0:
            self.rect.center = (-100,-100)
        else:
            self.y += self.dy * seconds
            self.x += self.dx * seconds
            self.dy *= self.acc  # slower and slower
            self.dx *= self.acc
            self.rect.center = (self.x, self.y)
            if self.time > self.duration:
                self.kill()      # remove Sprite from screen and from groups
                

class VectorSprite(pygame.sprite.Sprite):
    """base class for sprites. this class inherits from pygames sprite class"""
    number = 0
    numbers = {} # { number, Sprite }

    def __init__(self, **kwargs):
        self._default_parameters(**kwargs)
        pygame.sprite.Sprite.__init__(self, self.groups) #call parent class. NEVER FORGET !
        self.number = VectorSprite.number # unique number for each sprite
        VectorSprite.number += 1
        VectorSprite.numbers[self.number] = self
        self._overwrite_parameters()
        self.create_image()
        self.distance_traveled = 0 # in pixel
        self.rect.center = (int(self.pos.x), -int(self.pos.y))
        if self.angle != 0:
            self.set_angle(self.angle)
        self.start()
        
    def start(self):
        pass

    def _overwrite_parameters(self):
        """change parameters before create_image is called""" 
        pass

    def _default_parameters(self, **kwargs):    
        """get unlimited named arguments and turn them into attributes
           default values for missing keywords"""

        for key, arg in kwargs.items():
            setattr(self, key, arg)
        if "layer" not in kwargs:
            self._layer = 4
        else:
            self._layer = self.layer
        if "static" not in kwargs:
            self.static = False
        if "pos" not in kwargs:
            self.pos = pygame.math.Vector2(random.randint(0, Viewer.width),-50)
        if "move" not in kwargs:
            self.move = pygame.math.Vector2(0,0)
        if "radius" not in kwargs:
            self.radius = 5
        if "width" not in kwargs:
            self.width = self.radius * 2
        if "height" not in kwargs:
            self.height = self.radius * 2
        if "color" not in kwargs:       #self.color = None
            self.color = (random.randint(0,255), random.randint(0,255), random.randint(0,255))
        if "hitpoints" not in kwargs:
            self.hitpoints = 100
        self.hitpointsfull = self.hitpoints # makes a copy
        if "mass" not in kwargs:
            self.mass = 10
        if "damage" not in kwargs:
            self.damage = 10
        if "bounce_on_edge" not in kwargs:
            self.bounce_on_edge = False
        if "kill_on_edge" not in kwargs:
            self.kill_on_edge = False
        if "angle" not in kwargs:
            self.angle = 0 # facing right?
        if "max_age" not in kwargs:
            self.max_age = None
        if "max_distance" not in kwargs:
            self.max_distance = None
        if "picture" not in kwargs:
            self.picture = None
        if "bossnumber" not in kwargs:
            self.bossnumber = None
        if "kill_with_boss" not in kwargs:
            self.kill_with_boss = False
        if "sticky_with_boss" not in kwargs:
            self.sticky_with_boss = False
        if "mass" not in kwargs:
            self.mass = 15
        if "upkey" not in kwargs:
            self.upkey = None
        if "downkey" not in kwargs:
            self.downkey = None
        if "rightkey" not in kwargs:
            self.rightkey = None
        if "leftkey" not in kwargs:
            self.leftkey = None
        if "speed" not in kwargs:
            self.speed = None
        if "age" not in kwargs:
            self.age = 0 # age in seconds
        if "warp_on_edge" not in kwargs:
            self.warp_on_edge = False
        if "dangerhigh" not in kwargs:
            self.dangerhigh = False
        if "fluffball_color" not in kwargs:
            self.fluffball_color = random.choice(["fluffballb.", "fluffballp.", "fluffballt.", "fluffballr."])

    def kill(self):
        if self.number in self.numbers:
           del VectorSprite.numbers[self.number] # remove Sprite from numbers dict
        pygame.sprite.Sprite.kill(self)

    def create_image(self):
        if self.picture is not None:
            self.image = self.picture.copy()
        else:
            self.image = pygame.Surface((self.width,self.height))
            self.image.fill((self.color))
        self.image = self.image.convert_alpha()
        self.image0 = self.image.copy()
        self.rect= self.image.get_rect()
        self.width = self.rect.width
        self.height = self.rect.height

    def rotate(self, by_degree):
        """rotates a sprite and changes it's angle by by_degree"""
        self.angle += by_degree
        oldcenter = self.rect.center
        self.image = pygame.transform.rotate(self.image0, self.angle)
        self.image.convert_alpha()
        self.rect = self.image.get_rect()
        self.rect.center = oldcenter

    def set_angle(self, degree):
        """rotates a sprite and changes it's angle to degree"""
        self.angle = degree
        oldcenter = self.rect.center
        self.image = pygame.transform.rotate(self.image0, self.angle)
        self.image.convert_alpha()
        self.rect = self.image.get_rect()
        self.rect.center = oldcenter
        
    def ai(self):
        pass

    def update(self, seconds):
        """calculate movement, position and bouncing on edge"""
        self.ai()
        # ----- kill because... ------
        if self.hitpoints <= 0:
            self.kill()
        if self.max_age is not None and self.age > self.max_age:
            self.kill()
        if self.max_distance is not None and self.distance_traveled > self.max_distance:
            self.kill()
        # ---- movement with/without boss ----
        if self.bossnumber is not None:
            if self.kill_with_boss:
                if self.bossnumber not in VectorSprite.numbers:
                    self.kill()
            if self.sticky_with_boss:
                boss = VectorSprite.numbers[self.bossnumber]
                #self.pos = v.Vec2d(boss.pos.x, boss.pos.y)
                self.pos = pygame.math.Vector2(boss.pos.x, boss.pos.y)
        self.pos += self.move * seconds
        self.distance_traveled += self.move.length() * seconds
        self.age += seconds
        self.wallbounce()
        self.rect.center = ( round(self.pos.x, 0), -round(self.pos.y, 0) )

    def wallbounce(self):
        # ---- bounce / kill on screen edge ----
        # ------- left edge ----
        if self.pos.x < 0:
            if self.kill_on_edge:
                self.kill()
            elif self.bounce_on_edge:
                self.pos.x = 0
                self.move.x *= -1
            elif self.warp_on_edge:
                self.pos.x = Viewer.width 
        # -------- upper edge -----
        if self.pos.y  > 0:
            if self.kill_on_edge:
                self.kill()
            elif self.bounce_on_edge:
                self.pos.y = 0
                self.move.y *= -1
            elif self.warp_on_edge:
                self.pos.y = -Viewer.height
        # -------- right edge -----                
        if self.pos.x  > Viewer.width:
            if self.kill_on_edge:
                self.kill()
            elif self.bounce_on_edge:
                self.pos.x = Viewer.width
                self.move.x *= -1
            elif self.warp_on_edge:
                self.pos.x = 0
        # --------- lower edge ------------
        if self.dangerhigh:
            y = self.dangerhigh
        else:
            y = Viewer.height
        if self.pos.y   < -y:
            if self.kill_on_edge:
                self.hitpoints = 0
                self.kill()
            elif self.bounce_on_edge:
                self.pos.y = -y
                self.move.y *= -1
            elif self.warp_on_edge:
                self.pos.y = 0
                
class Fluffball(VectorSprite):
    
    def _overwrite_parameters(self):
        self._layer = 2
        self.reifendamage = 0
        
    def update(self, seconds):
        VectorSprite.update(self, seconds)
        if self.reifendamage > 0:
            self.reifendamage -= 5
        #print("reifendamage", self.reifendamage)
        
    def create_image(self):
        self.image = Viewer.images[self.fluffball_color]
        self.image0 = self.image.copy()
        self.rect = self.image.get_rect()

class Kitty(VectorSprite):
    
    def _overwrite_parameters(self):
        Paw(bossnumber = self.number, side="right",sticky_with_boss=True)
        Paw(bossnumber = self.number, side="left",sticky_with_boss=True)
        self.chance_to_flap = 0.005
        self.chance_to_sit = 0.01
        self.state="sit"
        self.bounce_on_edge=True
        self.glow = False
        self.glow2 = False
        self.sleep = False
        self.sleep_time =0
        self.glow_time = 0
        self.glow2_time = 0
        self.i = 0
        
    def start_glowing(self):
        self.glow = True
        self.glow_time = self.age + 0.25
        
        
    def end_glowing(self):
        self.glow2 = True
        self.glow2_time = self.age + 0.25    
        
    def next_image(self):
        if self.i < 14:
            self.i += 1
            self.handle_image(self.images[self.i])
        
    def previous_image(self):
        if self.i > 0:
            self.i -= 1
            self.handle_image(self.images[self.i])
            
    def start_sleeping(self):
        self.sleep = True
        self.sleep_time = self.age + random.randint(3,20)
        #self.sleep_image = ("kittys")
        self.image = self.sleep_image
        self.rect = self.image.get_rect()
        self.rect.center = (self.pos.x, -self.pos.y)
        
        
        
    def update(self,seconds):
        VectorSprite.update(self,seconds)
        # will ich glühende Augen haben?
        
           
        if self.sleep:
              self.image = self.sleep_image
              #return
              self.move = pygame.math.Vector2(0,0)
              
              # zzzzz
              if random.random() < 0.03:     #0,01
                  Flytext(x = self.pos.x, y =  -self.pos.y-50, text="Z", color=(random.randint(0,255), random.randint(0,255), random.randint(0,255)),
                          dx = random.random(),dy = -10,
                          duration=3, fontsize=random.randint(10,50))
              
              if self.age > self.sleep_time:
                  self.image = self.notsleep_image
                  self.rect = self.image.get_rect()
                  self.rect.center = (self.pos.x, -self.pos.y)
        
                  self.sleep = False
              else:
                  return    
        
        
        if random.random()<0.0007: #0.0007:
            self.start_sleeping()
                
        
        if random.random()<0.001:      # 30 x pro sekunde
            self.start_glowing()
        if self.glow:
            if self.age > self.glow_time:
                self.next_image()
                self.glow_time = self.age + 0.25
                if self.i == 14:
                    self.glow = False
                    self.end_glowing()
        
        
        
        if self.glow2:
            if self.age > self.glow2_time:
                self.previous_image()
                self.glow2_time = self.age + 0.25
                if self.i == 0:
                    self.glow2 = False
        
        if self.state == "sit":
            if random.random() < self.chance_to_flap:
                self.state="flap"
                v=pygame.math.Vector2(150,0)
                v.rotate_ip(random.randint(0,360))
                self.move=v 
        elif self.state == "flap":
            if random.random() < self.chance_to_sit:
                self.state="sit"
                self.move=pygame.math.Vector2(0,0)
                
        elif random.random() <= 0.05:
                self.kitty.start_gowing
    
    def create_image(self):
        self.images = ["kitty0","kitty1", "kitty2", "kitty3", "kitty4", "kitty5", "kitty6", "kitty7", "kitty8", "kitty9", "kitty10", "kitty11", "kitty12", "kitty13", "kitty14"]
       
        self.sleep_image = Viewer.images["kittys"]
        self.notsleep_image = Viewer.images["kitty0"]
        self.handle_image(self.images[0])
            
            
    def handle_image(self, i):
            self.image = Viewer.images[i]
            self.image.convert_alpha()
            self.image0 = self.image.copy()
            
            self.rect = self.image.get_rect()
            self.rect.center = (self.pos.x, -self.pos.y)
        

class Paw(VectorSprite):
    
    def _overwrite_parameters(self):
        self.pos = pygame.math.Vector2(0,0)
        self.boss = VectorSprite.numbers[self.bossnumber]
        self.angle = 270
        #self.correction()
    
    def correction(self):    
        if self.side == "right":
            self.rect.centerx = self.boss.rect.centerx + 15
            #self.pos.x = self.boss.pos.x + 5
            self.rect.centery = self.boss.rect.centery + 10
            #self.pos.y = self.boss.pos.y - 10
        elif self.side == "left":
            self.rect.centerx = self.boss.rect.centerx - 15
            #self.pos.x = self.boss.pos.x - 25
            self.rect.centery = self.boss.rect.centery + 10
            #self.pos.y = self.boss.pos.y - 10
        
    def flap(self):
        self.boss.chance_to_flap = 0.001
        #self.correction()
        a=random.randint(240,300) #240, 300
        #("flapwinkel", a)
        if self.side == "right":
            self.set_angle(a)
        else:
            self.set_angle(a-180)    
        
    def play(self,angle=0):
        self.boss.chance_to_flap += 0.005
        
        if angle < 90 and angle > -90:
            if self.side == "right":
                self.set_angle(angle + random.randint(-5,5))
        #elif angle >= 90 and angle <= 270: 
        else:
            if self.side == "left":
                self.set_angle(angle + random.randint(-5,5))
        
    def update(self, seconds):
        VectorSprite.update(self,seconds)
        self.correction()  
        if self.boss.sleep:
        
            self.rect.center = (0,-400) #  = pygame.math.Vector2(0, 100)
        
       
    
    def stop_play(self):
       # self.boss.chance_to_flap = 0.005
    
        self.set_angle(180)
        
    def create_image(self):
        self.image = Viewer.images["paw"]
        self.image.convert_alpha()
        self.image0 = self.image.copy()
        self.rect = self.image.get_rect()
        
class Crumb(VectorSprite):

    def __init__(self, **kwargs):
        VectorSprite.__init__(self, **kwargs)
        #print("i am a new Crumb")
        if "gravity" not in kwargs:
            self.gravity = pygame.math.Vector2(0, -3.7)
        if "acc" not in kwargs:
            self.acc = 1.0
    
    def _overwrite_parameters(self):
        self._layer = 2
        self.kill_on_edge = True
    
    def create_image(self):
        r,g,b = self.color
        r = randomize_color(r,20)
        g = randomize_color(g,20)
        b = randomize_color(b,20)
        self.image = pygame.Surface((10,10))
        pygame.draw.circle(self.image, (r,g,b), (5,5), 5)
        if self.color == (220,160,40):
            pygame.draw.circle(self.image, (90,50,0), (random.randint(2,7), random.randint(2,7)), random.randint(0,2))
        pygame.draw.circle(self.image, (0,0,0), (random.randint(2,7), random.randint(2,7)), random.randint(0,4))
        self.image.set_colorkey((0,0,0))
        self.rect= self.image.get_rect()
        self.image0 = self.image.copy()

    def update(self, seconds):
        VectorSprite.update(self, seconds)
        self.move += self.gravity
        self.move *= self.acc

class Explosion():
    
    def __init__(self, pos, what="Spark", maxspeed=150, minspeed=20, color=(255,255,0),maxduration=2.5,gravityy=3.7,sparksmin=5,sparksmax=20,acc=1.0, min_angle=0, max_angle=360):

        for s in range(random.randint(sparksmin,sparksmax)):
            v = pygame.math.Vector2(1,0) # vector aiming right (0°)
            a = random.randint(int(min_angle),int(max_angle))
            v.rotate_ip(a)
            g = pygame.math.Vector2(0, - gravityy)
            speed = random.randint(minspeed, maxspeed)     #150
            duration = random.random() * maxduration
            if what == "Spark":     
                Spark(pos=pygame.math.Vector2(pos.x, pos.y), angle= a, move=v*speed,
                  max_age = duration, color=color, gravity = g)
            elif what == "Crumb":
                
                Crumb(pos=pygame.math.Vector2(pos.x, pos.y), angle= a, move=v*speed,
                  max_age = duration, color=color, gravity = g, acc=acc)
                  
class Donut(VectorSprite):
    
    def create_image(self):
        self.image = Viewer.images["donut"]
        self.image0 = self.image.copy()
        self.rect = self.image.get_rect()
        
class Cookie(VectorSprite):
    
    def create_image(self):
        self.image = Viewer.images["cookie"]
        self.image0 = self.image.copy()
        self.rect = self.image.get_rect()
        
class Autoreifen(VectorSprite):
    
    def create_image(self):
        self.image = Viewer.images["car wheel"]
        self.image0 = self.image.copy()
        self.rect = self.image.get_rect()
        
class Spark(VectorSprite):

    def __init__(self, **kwargs):
        VectorSprite.__init__(self, **kwargs)
        if "gravity" not in kwargs:
            self.gravity = pygame.math.Vector2(0, -3.7)
    
    def _overwrite_parameters(self):
        self._layer = 2
        self.kill_on_edge = True
    
    def create_image(self):
        r,g,b = self.color
        r = randomize_color(r,50)
        g = randomize_color(g,50)
        b = randomize_color(b,50)
        self.image = pygame.Surface((10,10))
        pygame.draw.line(self.image, (r,g,b), 
                         (10,5), (5,5), 3)
        pygame.draw.line(self.image, (r,g,b),
                          (5,5), (2,5), 1)
        self.image.set_colorkey((0,0,0))
        self.rect= self.image.get_rect()
        self.image0 = self.image.copy()

    def update(self, seconds):
        VectorSprite.update(self, seconds)
        self.move += self.gravity




class Viewer(object):
    width = 0
    height = 0
    images={}
    
    menu =  {"main":         ["Resume", "Hilfe", "Credits", "Settings","Fluffbälle", "Steuerung"],
            "Hilfe":         ["zurück", "Fluffball", "Donut", "Cookie", "Autoreifen", "Katze", "Spielziel"],
            "Credits":       ["zurück", "Ines Schnabl", "Martin Schnabl","Bilder","Musik" ],
            "Settings":      ["zurück", 
                              #"Screenresolution", 
                              "Fullscreen", "Schwierigkeit"],
            "Resolution":    ["zurück", ],
            "Fullscreen":    ["zurück", "Fullscreen Ein", "Fullscreen Aus"],
            "Schwierigkeit": ["zurück", "Easy", "Medium", "Hard", "Impossible"],
            "Fluffbälle":    ["zurück", "Spieler", "Farbe"],
            "Spieler":       ["zurück", "1 Spieler", "2 Spieler","3 Spieler", "4 Spieler"],
            "Farbe":         ["zurück", "Fluffball 1", "Fluffball 2","Fluffball 3", "Fluffball 4"],
            "Fluffball 1":   ["zurück", "rot", "gelb", "grün", "türkis", "blau", "violett"],
            "Fluffball 2":   ["zurück", "rot", "gelb", "grün", "türkis", "blau", "violett"],
            "Fluffball 3":   ["zurück", "rot", "gelb", "grün", "türkis", "blau", "violett"],
            "Fluffball 4":   ["zurück", "rot", "gelb", "grün", "türkis", "blau", "violett"]
            }
            
            
            
    descr = {"Resume" :           ["Zurück zum Spiel"],                                           #resume
             "Martin Schnabl" :   ["Mein großer Bruder hat","mich zum Programmieren","inspiriert und","mir Python erklärt.","","(Für einen großen Bruder","ist er voll in Ordnung.)"],
             "Ines Schnabl":      ["Mein Ziel ist es mehr","Flauschigkeit in die Welt","zu bringen.","","Das ist mein erstes Spiel,","das ich selber program-","miert habe."],
             "Bilder":            ["Katzen gezeichnet von","Ines Schnabl.","","Andere Bilder:","Lizenzfrei","von www.pixabay.com"],
             "Musik":             ["Fountain of Diana","gespielt","von Ines Schnabl","am Klavier"],
             "Screensolution" :   ["Ändere die", "screenresolution", "nur am Anfang"],
             "Fluffball" :        ["Ein flauschiger Ball der", "versucht so viele Donuts", "und Cookies wie möglich zu","essen. Doch leider hat er",
                                   "seine Brille verlegt. Weil", "der Fluffball nicht unter-","scheiden kann, was essbar","und was ein Autoreifen ist,",
                                   "musst du ihm helfen. Wenn","der Fluffball 100-mal auf", "Autoreifen trifft hast du", "verloren."],
             "Donut" :            ["Ein super leckerer Donut,", "einer der Lieblingssnacks", "von Fluffbällen."],
             "Cookie" :           ["Ein knuspriger Cookie.", "Fluffbälle lieben ihn,", "weil er so  viel Zucker", "und Schokolade enthält."],
             "Autoreifen" :       ["Ein nicht so gut", "schmeckender Autoreifen.", "Wenn ein Fluffball ihn", "versehentlich anknabbert", 
                                   "rollt der Fluffball in ", "die andere Richtung davon.","Wenn der Fluffball den", "Autoreifen 100-mal an-",
                                   "knabbert wird dem Fluff-", "ball schlecht und du","hast verloren."],
             "Katze"  :           ["Ein niedliches Kätzchen,", "das gerne mit Fluffbällen", "spielt.", "Es denkt es könnte fliegen,", "aber es ist nicht so", 
                                   "süß wie es aussieht,", "denn es hat einen Laserblick.", "(der Fluffbälle zum Glück", "nicht verletzt).", "Manchmal schläft das", "Kätzchen auch ein."],
             "Spieler":           ["Ändere die Anzahl von", "Fluffbällen im Spiel, damit", "deine Freunde und deine", "Verwandten mitspielen können."],
             "1 Spieler":         ["Steuerung:", "Fluffball 1, mit Pfeiltasten"],
             "2 Spieler":         ["Steuerung:", "Fluffball 1, mit Pfeiltasten", "Fluffball 2, mit w a s d"],
             "3 Spieler":         ["Steuerung:", "Fluffball 1, mit Pfeiltasten", "Fluffball 2, mit w a s d", "Fluffball 3, mit i j k l"],
             "4 Spieler":         ["Steuerung:", "Fluffball 1, mit Pfeiltasten", "Fluffball 2, mit w a s d", "Fluffball 3, mit i j k l", "Fluffball 4, mit g v b n"],
             "Farbe":             ["Ändere die Farbe",  "der Fluffbälle."],
             "Steuerung":         ["Fluffball 1, mit Pfeiltasten", "Fluffball 2, mit w a s d", "Fluffball 3, mit i j k l", "Fluffball 4, mit g v b n", "", "mit m öffnet man das Menü"],
             "Spielziel":         ["Gewinnen: Alle Cookies und", "Donuts gegessen.","", "Verlieren: Fluffball trifft", "100-mal oder öfter auf", "einen Autoreifen."]
             }
    menu_images = {"Fluffball"  : "fluffball_menu",
                   "Donut"      : "donut_menu",
                   "Cookie"     : "cookie_menu",
                   "Autoreifen" : "car wheel_menu",
                   "Katze"      : "baby cat_menu",
                   "rot"        : "fluffballr.",
                   "gelb"       : "fluffballgb.",
                   "grün"       : "fluffballgn.",
                   "blau"       : "fluffballb.",
                   "türkis"     : "fluffballt.",
                   "violett"    : "fluffballp.",
                   }
 
    history = ["main"]
    cursor = 0
    name = "main"
    fullscreen = False

    def __init__(self, width=640, height=400, fps=30):
        """Initialize pygame, window, background, font,...
           default arguments """
        pygame.init()
        Viewer.width = width    # make global readable
        Viewer.height = height
        self.screen = pygame.display.set_mode((self.width, self.height), pygame.DOUBLEBUF)
        self.background = pygame.Surface(self.screen.get_size()).convert()
        self.background.fill((255,255,255)) # fill background white
        self.clock = pygame.time.Clock()
        self.fps = fps
        self.playtime = 0.0
        self.collisions = 0
        self.fluffs = []
        # ------ background images ------
        self.backgroundfilenames = [] # every .jpg file in folder 'data'
        try:
            for root, dirs, files in os.walk("data"):
                for file in files:
                    if file[-4:] == ".jpg" or file[-5:] == ".jpeg":
                        self.backgroundfilenames.append(file)
            random.shuffle(self.backgroundfilenames) # remix sort order
        except:
            print("no folder 'data' or no jpg files in it")
        # ------ joysticks ----
        pygame.joystick.init()
        self.joysticks = [pygame.joystick.Joystick(x) for x in range(pygame.joystick.get_count())]
        for j in self.joysticks:
            j.init()
        self.prepare_sprites()
        self.loadbackground()
        # --- create screen resolution list ---
        li = ["zurück"]
        for i in pygame.display.list_modes():
            # li is something like "(800, 600)"
            pair = str(i)
            comma = pair.find(",")
            x = pair[1:comma]
            y = pair[comma+2:-1]
            #print(" Screen "+str(x)+"  "+str(y))
            li.append(str(x)+"x"+str(y))
        Viewer.menu["Screenresolution"] = li
        #Viewer.menu["Screenresolution"] = ["zurück","1430x800","800x600"]
        self.set_screenresolution()
        #print("Spiele meine Musik")
        pygame.mixer.init()
        pygame.mixer.music.load(os.path.join("data", "FOUNTAIN.wav"))
        pygame.mixer.music.play(loops=-1)



    def getFluffFarbe():
        return Viewer.FluffFarbList[random.randint(0,len(Viewer.FluffFarbList)-1)]
        
    def loadbackground(self):
        
        self.background = pygame.Surface(self.screen.get_size()).convert()
        self.background.fill((255,255,255))
        self.background = pygame.transform.scale(self.background,
                          (Viewer.width,Viewer.height))
        self.background.convert()
        
    def set_screenresolution(self):
       # print(self.width, self.height)
        if Viewer.fullscreen:
             self.screen = pygame.display.set_mode((self.width, self.height), pygame.DOUBLEBUF|pygame.FULLSCREEN)
        else:
             self.screen = pygame.display.set_mode((self.width, self.height), pygame.DOUBLEBUF)
        self.loadbackground()
        
    def load_sprites(self):
        Viewer.images["kitty0"] = pygame.image.load(os.path.join("data", "kitty0.png")).convert_alpha()
        Viewer.images["kitty0"] = pygame.transform.scale(Viewer.images["kitty0"], (250,175))
        Viewer.images["kitty1"] = pygame.image.load(os.path.join("data", "kitty1.png")).convert_alpha()
        Viewer.images["kitty1"] = pygame.transform.scale(Viewer.images["kitty1"], (250,175))
        Viewer.images["kitty2"] = pygame.image.load(os.path.join("data", "kitty2.png")).convert_alpha()
        Viewer.images["kitty2"] = pygame.transform.scale(Viewer.images["kitty2"], (250,175))
        Viewer.images["kitty3"] = pygame.image.load(os.path.join("data", "kitty3.png")).convert_alpha()
        Viewer.images["kitty3"] = pygame.transform.scale(Viewer.images["kitty3"], (250,175))
        Viewer.images["kitty4"] = pygame.image.load(os.path.join("data", "kitty4.png")).convert_alpha()
        Viewer.images["kitty4"] = pygame.transform.scale(Viewer.images["kitty4"], (250,175))
        Viewer.images["kitty5"] = pygame.image.load(os.path.join("data", "kitty5.png")).convert_alpha()
        Viewer.images["kitty5"] = pygame.transform.scale(Viewer.images["kitty5"], (250,175))
        Viewer.images["kitty6"] = pygame.image.load(os.path.join("data", "kitty6.png")).convert_alpha()
        Viewer.images["kitty6"] = pygame.transform.scale(Viewer.images["kitty6"], (250,175))
        Viewer.images["kitty7"] = pygame.image.load(os.path.join("data", "kitty7.png")).convert_alpha()
        Viewer.images["kitty7"] = pygame.transform.scale(Viewer.images["kitty7"], (250,175))
        Viewer.images["kitty8"] = pygame.image.load(os.path.join("data", "kitty8.png")).convert_alpha()
        Viewer.images["kitty8"] = pygame.transform.scale(Viewer.images["kitty8"], (250,175))
        Viewer.images["kitty9"] = pygame.image.load(os.path.join("data", "kitty9.png")).convert_alpha()
        Viewer.images["kitty9"] = pygame.transform.scale(Viewer.images["kitty9"], (250,175))
        Viewer.images["kitty10"] = pygame.image.load(os.path.join("data", "kitty10.png")).convert_alpha()
        Viewer.images["kitty10"] = pygame.transform.scale(Viewer.images["kitty10"], (250,175))
        Viewer.images["kitty11"] = pygame.image.load(os.path.join("data", "kitty11.png")).convert_alpha()
        Viewer.images["kitty11"] = pygame.transform.scale(Viewer.images["kitty11"], (250,175))
        Viewer.images["kitty12"] = pygame.image.load(os.path.join("data", "kitty12.png")).convert_alpha()
        Viewer.images["kitty12"] = pygame.transform.scale(Viewer.images["kitty12"], (250,175))
        Viewer.images["kitty13"] = pygame.image.load(os.path.join("data", "kitty13.png")).convert_alpha()
        Viewer.images["kitty13"] = pygame.transform.scale(Viewer.images["kitty13"], (250,175))
        Viewer.images["kitty14"] = pygame.image.load(os.path.join("data", "kitty14.png")).convert_alpha()
        Viewer.images["kitty14"] = pygame.transform.scale(Viewer.images["kitty14"], (250,175))
        
        Viewer.images["kittys"] = pygame.image.load(os.path.join("data", "kittys.png")).convert_alpha()
        Viewer.images["kittys"] = pygame.transform.scale(Viewer.images["kittys"], (170,150))
        #Viewer.images["kittys"].set_colorkey((255,255,255))
        #Viewer.images["kittys"].convert_alpha()
        Viewer.images["paw"] = pygame.image.load(os.path.join("data", "paw1.png")).convert_alpha()
        Viewer.images["paw"] = pygame.transform.scale(Viewer.images["paw"], (50,150))
        
        Viewer.images["fluffballb."] = pygame.image.load(os.path.join("data", "Fluffballlöwenzahnb.png")).convert_alpha()
        Viewer.images["fluffballb."] = pygame.transform.scale(Viewer.images["fluffballb."], (90,90))
        Viewer.images["fluffballgb."] = pygame.image.load(os.path.join("data", "Fluffballlöwenzahngb.png")).convert_alpha()
        Viewer.images["fluffballgb."] = pygame.transform.scale(Viewer.images["fluffballgb."], (90,90))
        Viewer.images["fluffballgn."] = pygame.image.load(os.path.join("data", "Fluffballlöwenzahngn.png")).convert_alpha()
        Viewer.images["fluffballgn."] = pygame.transform.scale(Viewer.images["fluffballgn."], (90,90))
        Viewer.images["fluffballp."] = pygame.image.load(os.path.join("data", "Fluffballlöwenzahnp.png")).convert_alpha()
        Viewer.images["fluffballp."] = pygame.transform.scale(Viewer.images["fluffballp."], (90,90))
        Viewer.images["fluffballt."] = pygame.image.load(os.path.join("data", "Fluffballlöwenzahnt.png")).convert_alpha()
        Viewer.images["fluffballt."] = pygame.transform.scale(Viewer.images["fluffballt."], (90,90))
        Viewer.images["fluffball_menu"] = pygame.image.load(os.path.join("data", "Fluffballlöwenzahn.png")).convert_alpha()
        Viewer.images["fluffball_menu"] = pygame.transform.scale(Viewer.images["fluffball_menu"], (300, 300))
        Viewer.images["fluffballr."] = pygame.image.load(os.path.join("data", "Fluffballlöwenzahnr.png")).convert_alpha()
        Viewer.images["fluffballr."] = pygame.transform.scale(Viewer.images["fluffballr."], (90,90))
        Viewer.images["donut_menu"] = pygame.image.load(os.path.join("data", "donut.png")).convert_alpha()
        Viewer.images["donut_menu"] = pygame.transform.scale(Viewer.images["donut_menu"], (300, 300))
        Viewer.images["cookie_menu"] = pygame.image.load(os.path.join("data", "cookie.png")).convert_alpha()
        Viewer.images["cookie_menu"] = pygame.transform.scale(Viewer.images["cookie_menu"], (275, 275))
        Viewer.images["car wheel_menu"] = pygame.image.load(os.path.join("data", "car_wheel.png")).convert_alpha()
        Viewer.images["car wheel_menu"] = pygame.transform.scale(Viewer.images["car wheel_menu"], (300, 300))
        Viewer.images["baby cat"] = pygame.image.load(os.path.join("data", "kitty0.png")).convert_alpha()
        Viewer.images["baby cat_menu"] = pygame.transform.scale(Viewer.images["baby cat"], (400, 300))
        Viewer.images["baby cat"] = pygame.transform.scale(Viewer.images["baby cat"], (125, 175))
        Viewer.images["donut"] = pygame.image.load(os.path.join("data", "donut.png")).convert_alpha()
        Viewer.images["donut"] = pygame.transform.scale(Viewer.images["donut"], (100,100))
        Viewer.images["cookie"] = pygame.image.load(os.path.join("data", "cookie.png")).convert_alpha()
        Viewer.images["cookie"] = pygame.transform.scale(Viewer.images["cookie"], (80,80))
        Viewer.images["car wheel"] = pygame.image.load(os.path.join("data", "car_wheel.png")).convert_alpha()
        Viewer.images["car wheel"] = pygame.transform.scale(Viewer.images["car wheel"], (100,100))
        
        Viewer.FluffFarbList=["fluffballb.","fluffballgb.","fluffballgn.","fluffballp.","fluffballt.","fluffballr."]
        
    def prepare_sprites(self):
        """painting on the surface and create sprites"""
        self.load_sprites()
        self.allgroup =  pygame.sprite.LayeredUpdates() # for drawing
        self.explosiongroup = pygame.sprite.Group()
        self.foodgroup = pygame.sprite.Group()
        self.fluffgroup = pygame.sprite.Group()
        self.car_wheelgroup = pygame.sprite.Group()
        self.flytextgroup = pygame.sprite.Group()
        self.kittygroup = pygame.sprite.Group()
        self.collisiongroup = pygame.sprite.Group()
        self.pawgroup = pygame.sprite.Group()
        
        Kitty.groups = self.allgroup, self.kittygroup
        Paw.groups = self.allgroup, self.pawgroup
        VectorSprite.groups = self.allgroup
        Flytext.groups = self.allgroup
        Explosion.groups = self.allgroup, self.explosiongroup
        Donut.groups = self.allgroup, self.foodgroup, self.collisiongroup
        Fluffball.groups = self.allgroup, self.fluffgroup, self.collisiongroup
        Cookie.groups = self.allgroup, self.foodgroup, self.collisiongroup
        Autoreifen.groups = self.allgroup, self.car_wheelgroup, self.collisiongroup
        Flytext.groups = self.allgroup, self.flytextgroup
        #Babycat.groups = self.allgroup, self.babycatgroup, self.collisiongroup
        Spark.groups = self.allgroup 
        Crumb.groups = self.allgroup
   

        self.fluffs.clear()
        
        self.kitty1 = Kitty(pos=pygame.math.Vector2(200,-100))
        self.kitty2 = Kitty(pos=pygame.math.Vector2(900,-300))
        self.kitty3 = Kitty(pos=pygame.math.Vector2(900,-600))
        
        
        
        self.fluff = Fluffball(bounce_on_edge=True, pos=pygame.math.Vector2(Viewer.width//4,-Viewer.height//4),
        fluffball_color=Viewer.getFluffFarbe())
       
            
        for x in range(Game.difficulty*6-1):
            while True:
                autoreifen_x = random.randint(0, Viewer.width)
                autoreifen_y = -random.randint(0, Viewer.height)
                if distance((autoreifen_x, autoreifen_y), self.fluff.pos) < 100:
                    continue
                elif distance((autoreifen_x, autoreifen_y), (Viewer.width//1.33,-Viewer.height//4)) < 100:
                    continue
                elif distance((autoreifen_x, autoreifen_y), (Viewer.width//4,-Viewer.height//1.33)) < 100:
                    continue
                elif distance((autoreifen_x, autoreifen_y), (Viewer.width//1.33,-Viewer.height//1.33)) < 100:
                    continue
                    
                for w in self.car_wheelgroup:
                    if distance((autoreifen_x, autoreifen_y),w.pos) < 200:
                        break
                else:
                    Autoreifen(pos=pygame.math.Vector2(autoreifen_x, autoreifen_y))
                    break
        for x in range(10):
            while True:
                donut_x = random.randint(0, Viewer.width)
                donut_y = -random.randint(0, Viewer.height)
                for w in self.car_wheelgroup:
                    if distance((donut_x, donut_y), w.pos) < 50:
                        break
                else:
                    Donut(pos=pygame.math.Vector2(random.randint(0,Viewer.width),-random.randint(0,Viewer.height)))
                    break
        for x in range(10):
            while True:
                cookie_x = random.randint(0, Viewer.width)
                cookie_y = -random.randint(0, Viewer.height)
                for w in self.car_wheelgroup:
                    if distance((cookie_x, cookie_y), w.pos) < 50:
                        break
                else:
                    Cookie(pos=pygame.math.Vector2(random.randint(0,Viewer.width),-random.randint(0,Viewer.height)))
                    break
        
        if Game.difficulty == 4:
            for x in range(25):
                Kitty(warp_on_edge=True, pos=pygame.math.Vector2(random.randint(0,Viewer.width),-random.randint(0,Viewer.height)))
        else:
            for x in range(Game.difficulty*3):
                Kitty(warp_on_edge=True, pos=pygame.math.Vector2(random.randint(0,Viewer.width),-random.randint(0,Viewer.height)))
    
    def menu_run(self):
        """Not The mainloop"""
        running = True
        pygame.mouse.set_visible(False)
        self.menu = True  #self.menu_run()
        while running:
            #pygame.mixer.music.pause()
            milliseconds = self.clock.tick(self.fps) #
            seconds = milliseconds / 1000
            text = Viewer.menu[Viewer.name][Viewer.cursor]
            # -------- events ------
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return -1 # running = False
                # ------- pressed and released key ------
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        return -1 # running = False
                    if event.key == pygame.K_UP:
                        Viewer.cursor -= 1
                        Viewer.cursor = max(0, Viewer.cursor) # not < 0
                        #Viewer.menusound.play()
                    if event.key == pygame.K_DOWN:
                        Viewer.cursor += 1
                        Viewer.cursor = min(len(Viewer.menu[Viewer.name])-1,Viewer.cursor) # not > menu entries
                        #Viewer.menusound.play()
                    if event.key == pygame.K_RETURN:
                        if text == "quit":
                            return -1
                            Viewer.menucommandsound.play()
                        elif text in Viewer.menu:
                            # changing to another menu
                            Viewer.history.append(text) 
                            Viewer.name = text
                            Viewer.cursor = 0
                        elif text == "Resume":
                            return
                        elif text == "zurück":
                            Viewer.history = Viewer.history[:-1] # remove last entry
                            Viewer.cursor = 0
                            Viewer.name = Viewer.history[-1] # get last entry
                        elif Viewer.name == "Screenresolution":
                            # text is something like 800x600
                            t = text.find("x")
                            if t != -1:
                                x = int(text[:t])
                                y = int(text[t+1:])
                                Viewer.width = x
                                Viewer.height = y
                                self.set_screenresolution()
                                self.prepare_sprites()
                        elif Viewer.name == "Fluffball 1":
                            if text == "blau":
                                self.fluff.fluffball_color = "fluffballb."
                                self.fluff.create_image()
                                self.fluff.rect.center  = (int(self.fluff.pos.x), -int(self.fluff.pos.y))
                            elif text == "violett":
                                self.fluff.fluffball_color = "fluffballp."
                                self.fluff.create_image()
                                self.fluff.rect.center  = (int(self.fluff.pos.x), -int(self.fluff.pos.y))
                            elif text == "türkis":
                                self.fluff.fluffball_color = "fluffballt."
                                self.fluff.create_image()
                                self.fluff.rect.center  = (int(self.fluff.pos.x), -int(self.fluff.pos.y))
                            elif text == "rot":
                                self.fluff.fluffball_color = "fluffballr."
                                self.fluff.create_image()
                                self.fluff.rect.center  = (int(self.fluff.pos.x), -int(self.fluff.pos.y)) 
                            elif text == "gelb":
                                self.fluff.fluffball_color = "fluffballgb."
                                self.fluff.create_image()
                                self.fluff.rect.center  = (int(self.fluff.pos.x), -int(self.fluff.pos.y))
                            elif text == "grün":
                                self.fluff.fluffball_color = "fluffballgn."
                                self.fluff.create_image()
                                self.fluff.rect.center  = (int(self.fluff.pos.x), -int(self.fluff.pos.y))   
                        elif Viewer.name == "Fluffball 2":
                            if len(self.fluffgroup) >= 2:
                                if text == "blau":
                                    self.fluff2.fluffball_color = "fluffballb."
                                    self.fluff2.create_image()
                                    self.fluff2.rect.center  = (int(self.fluff2.pos.x), -int(self.fluff2.pos.y))
                                elif text == "violett":
                                    self.fluff2.fluffball_color = "fluffballp."
                                    self.fluff2.create_image()
                                    self.fluff2.rect.center  = (int(self.fluff2.pos.x), -int(self.fluff2.pos.y))
                                elif text == "türkis":
                                    self.fluff2.fluffball_color = "fluffballt."
                                    self.fluff2.create_image()
                                    self.fluff2.rect.center  = (int(self.fluff2.pos.x), -int(self.fluff2.pos.y))
                                elif text == "rot":
                                    self.fluff2.fluffball_color = "fluffballr."
                                    self.fluff2.create_image()
                                    self.fluff2.rect.center  = (int(self.fluff2.pos.x), -int(self.fluff2.pos.y))
                                elif text == "gelb":
                                    self.fluff2.fluffball_color = "fluffballgb."
                                    self.fluff2.create_image()
                                    self.fluff2.rect.center  = (int(self.fluff.pos.x), -int(self.fluff.pos.y))
                                elif text == "grün":
                                    self.fluff2.fluffball_color = "fluffballgn."
                                    self.fluff2.create_image()
                                    self.fluff2.rect.center  = (int(self.fluff.pos.x), -int(self.fluff.pos.y))
                        elif Viewer.name == "Fluffball 3":
                            if len(self.fluffgroup) >= 3:
                                if text == "blau":
                                    self.fluff3.fluffball_color = "fluffballb."
                                    self.fluff3.create_image()
                                    self.fluff3.rect.center  = (int(self.fluff.pos.x), -int(self.fluff.pos.y))
                                elif text == "violett":
                                    self.fluff3.fluffball_color = "fluffballp."
                                    self.fluff3.create_image()
                                    self.fluff3.rect.center  = (int(self.fluff.pos.x), -int(self.fluff.pos.y))
                                elif text == "türkis":
                                    self.fluff3.fluffball_color = "fluffballt."
                                    self.fluff3.create_image()
                                    self.fluff3.rect.center  = (int(self.fluff.pos.x), -int(self.fluff.pos.y))
                                elif text == "rot":
                                    self.fluff3.fluffball_color = "fluffballr."
                                    self.fluff3.create_image()
                                    self.fluff3.rect.center  = (int(self.fluff.pos.x), -int(self.fluff.pos.y)) 
                                elif text == "gelb":
                                    self.fluff3.fluffball_color = "fluffballgb."
                                    self.fluff3.create_image()
                                    self.fluff3.rect.center  = (int(self.fluff.pos.x), -int(self.fluff.pos.y))
                                elif text == "grün":
                                    self.fluff3.fluffball_color = "fluffballgn."
                                    self.fluff3.create_image()
                                    self.fluff3.rect.center  = (int(self.fluff.pos.x), -int(self.fluff.pos.y))
                        elif Viewer.name == "Fluffball 4":
                            if len(self.fluffgroup) >= 4:
                                if text == "blau":
                                    self.fluff4.fluffball_color = "fluffballb."
                                    self.fluff4.create_image()
                                    self.fluff4.rect.center  = (int(self.fluff.pos.x), -int(self.fluff.pos.y))
                                elif text == "violett":
                                    self.fluff4.fluffball_color = "fluffballp."
                                    self.fluff4.create_image()
                                    self.fluff4.rect.center  = (int(self.fluff.pos.x), -int(self.fluff.pos.y))
                                elif text == "türkis":
                                    self.fluff4.fluffball_color = "fluffballt."
                                    self.fluff4.create_image()
                                    self.fluff4.rect.center  = (int(self.fluff.pos.x), -int(self.fluff.pos.y))
                                elif text == "rot":
                                    self.fluff4.fluffball_color = "fluffballr."
                                    self.fluff4.create_image()
                                    self.fluff4.rect.center  = (int(self.fluff.pos.x), -int(self.fluff.pos.y)) 
                                elif text == "gelb":
                                    self.fluff4.fluffball_color = "fluffballgb."
                                    self.fluff4.create_image()
                                    self.fluff4.rect.center  = (int(self.fluff.pos.x), -int(self.fluff.pos.y))
                                elif text == "grün":
                                    self.fluff4.fluffball_color = "fluffballgn."
                                    self.fluff4.create_image()
                                    self.fluff4.rect.center  = (int(self.fluff.pos.x), -int(self.fluff.pos.y))  
                        elif text == "2 Spieler":
                            Game.players = 2
                            if len(self.fluffgroup) > 2:
                                self.fluff3.kill()
                            if len(self.fluffgroup) > 3:
                                self.fluff4.kill()
                            if len(self.fluffgroup) < 2:
                                self.fluff2 = Fluffball(bounce_on_edge=True, pos=pygame.math.Vector2(Viewer.width//1.33,-Viewer.height//4),fluffball_color=Viewer.getFluffFarbe())
                                if len(self.fluffs) < 2:
                                    self.fluffs.append(self.fluff2)
                                Flytext(Viewer.width//2,Viewer.height//4,text="2 Fluffbälle im Spiel",color=(0,255,255),duration=5,fontsize=50)
                        elif text == "1 Spieler":
                            Game.players = 1
                            if len(self.fluffgroup) > 3:
                                self.fluff2.kill()
                                self.fluff3.kill()
                                self.fluff4.kill()
                            if len(self.fluffgroup) > 2:
                                self.fluff2.kill()
                                self.fluff3.kill()
                            if len(self.fluffgroup) > 1:
                                self.fluff2.kill()
                            
                            
                            Flytext(Viewer.width//2,Viewer.height//4,text="1 Fluffball im Spiel",color=(0,255,255),duration=5,fontsize=50) 
                        elif text == "3 Spieler":
                            Game.players = 3
                            if len(self.fluffgroup) == 1:
                                self.fluff2 = Fluffball(bounce_on_edge=True, pos=pygame.math.Vector2(Viewer.width//1.33,-Viewer.height//4),fluffball_color=Viewer.getFluffFarbe())
                                if len(self.fluffs) < 2:
                                    self.fluffs.append(self.fluff2)
                            if len(self.fluffgroup) == 2:
                                self.fluff3 = Fluffball(bounce_on_edge=True, pos=pygame.math.Vector2(Viewer.width//4,-Viewer.height//1.33),fluffball_color=Viewer.getFluffFarbe())
                                if len(self.fluffs) < 3:
                                    self.fluffs.append(self.fluff3)
                            if len(self.fluffgroup) > 3:
                                self.fluff4.kill()
                            Flytext(Viewer.width//2,Viewer.height//4,text="3 Fluffbälle im Spiel",color=(0,255,255),duration=5,fontsize=50)
                        elif text == "4 Spieler":    
                            Game.players = 4
                            if len(self.fluffgroup) == 1:
                                self.fluff2 = Fluffball(bounce_on_edge=True, pos=pygame.math.Vector2(Viewer.width//4,-Viewer.height//1.33),fluffball_color=Viewer.getFluffFarbe())
                                if len(self.fluffs) < 2:
                                    self.fluffs.append(self.fluff2)
                            if len(self.fluffgroup) == 2:
                                self.fluff3 = Fluffball(bounce_on_edge=True, pos=pygame.math.Vector2(Viewer.width//1.33,-Viewer.height//4),fluffball_color=Viewer.getFluffFarbe())
                                if len(self.fluffs) < 3:
                                    self.fluffs.append(self.fluff3)
                            if len(self.fluffgroup) == 3:
                                self.fluff4 = Fluffball(bounce_on_edge=True, pos=pygame.math.Vector2(Viewer.width//1.33,-Viewer.height//1.33),fluffball_color=Viewer.getFluffFarbe())
                                if len(self.fluffs) < 4:
                                    self.fluffs.append(self.fluff4)
                            Flytext(Viewer.width//2,Viewer.height//4,text="4 Fluffbälle im Spiel",color=(0,255,255),duration=5,fontsize=50)
                        elif Viewer.name == "Schwierigkeit":
                            if text == "Easy":
                                Game.difficulty = 1
                                self.collisions = 0
                            elif text == "Medium":
                                Game.difficulty = 2
                                self.collisions = 0
                            elif text == "Hard":
                                Game.difficulty = 3
                                self.collisions = 0
                            elif text == "Impossible":
                                Game.difficulty = 4
                                self.collisions = 0
                            self.prepare_sprites()
                        elif Viewer.name == "Fullscreen":
                            if text == "Fullscreen Ein":
                                #Viewer.menucommandsound.play()
                                Viewer.fullscreen = True
                                self.set_screenresolution()
                            elif text == "Fullscreen Aus":
                                #Viewer.menucommandsound.play()
                                Viewer.fullscreen = False
                                self.set_screenresolution()
                            
                        
            # ------delete everything on screen-------
            self.screen.blit(self.background, (0, 0))
            
            # -------------- UPDATE all sprites -------             
            self.flytextgroup.update(seconds)

            # ----------- clear, draw , update, flip -----------------
            self.allgroup.draw(self.screen)
            
            
            
            pygame.draw.rect(self.screen,(170,170,170),(200,90,350,370))
            pygame.draw.rect(self.screen,(200,200,200),(600,90,350,370))
            pygame.draw.rect(self.screen,(230,230,230),(1000,90,350,370))
            
            self.flytextgroup.draw(self.screen)

            # --- paint menu ----
            # ---- name of active menu and history ---
            write(self.screen, text="you are here:", x=200, y=50, color=(0,255,255), fontsize=15)
            
            t = "main"
            for nr, i in enumerate(Viewer.history[1:]):
                #if nr > 0:
                t+=(" > ")
                t+=(i)
            write(self.screen, text=t, x=200,y=70,color=(0,255,255), fontsize=15)
            # --- menu items ---
            menu = Viewer.menu[Viewer.name]
            for y, item in enumerate(menu):
                write(self.screen, text=item, x=Viewer.width//2-500, y=100+y*50, color=(255,255,255), fontsize=30)
            # --- cursor ---
            write(self.screen, text="-->", x=Viewer.width//2-600, y=100+ Viewer.cursor * 50, color=(0,0,0), fontsize=30)
            # ---- descr ------
            if text in Viewer.descr:
                lines = Viewer.descr[text]
                for y, line in enumerate(lines):
                    write(self.screen, text=line, x=Viewer.width//2-100, y=100+y*30, color=(255,0,255), fontsize=20)
           # ---- menu_images -----
            if text in Viewer.menu_images:
                self.screen.blit(Viewer.images[Viewer.menu_images[text]], (1020,100))
                
            # -------- next frame -------------
            pygame.display.flip()
    
    def run(self):
        """The mainloop"""
        running = True
        Viewer.fullscreen = True
        self.set_screenresolution()
        #pygame.mouse.set_visible(False)
        oldleft, oldmiddle, oldright  = False, False, False
        self.snipertarget = None
        gameOver = False
        exittime = 0
        self.menu_run()
       
        crazytime = 0
        crazytime_cooldown = 0
        while running:
            
            milliseconds = self.clock.tick(self.fps) #
            seconds = milliseconds / 1000
            self.playtime += seconds
            
            if gameOver:
                if self.playtime > exittime:
                    running = False
                    
            # -------- events ------
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYUP:
                    if event.key == pygame.K_t:
                        for p in self.pawgroup:
                            if p.bossnumber == self.kitty1.number:
                                p.stop_play()
                
                        
                        
                
                # ------- pressed and released key ------
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False
                    #if event.key == pygame.K_1:
                     
                    elif event.key == pygame.K_m:
                        self.menu_run()
                        
                    elif event.key == pygame.K_1:
                        for w in self.kittygroup:
                            w.next_image()
                    elif event.key == pygame.K_2:
                        for q in self.kittygroup:
                            q.previous_image()
                            
                    elif event.key == pygame.K_3:
                        self.kitty1.start_glowing()
            # delete everything on screen
            self.screen.blit(self.background, (0, 0))  # macht alles weiß
            if self.playtime < crazytime :
                self.screen.fill((random.randint(0,255), random.randint(0,255), random.randint(0,255)))
                
            # ------------ pressed keys ------
            pressed_keys = pygame.key.get_pressed()

            if pressed_keys[pygame.K_t]:
                # alle pfoten von kitty1 suchen
                for p in self.pawgroup:
                    if p.bossnumber == self.kitty1.number:
                        p.play(angle=100)
            
            
            
            if pressed_keys[pygame.K_RIGHT]:
                self.fluff.move += pygame.math.Vector2(10,0)
            if pressed_keys[pygame.K_LEFT]:
                self.fluff.move += pygame.math.Vector2(-10,0)
            if pressed_keys[pygame.K_UP]:
                self.fluff.move += pygame.math.Vector2(0,10)
            if pressed_keys[pygame.K_DOWN]:
                self.fluff.move += pygame.math.Vector2(0,-10)
                
            if len(self.fluffgroup) >= 2:
                if pressed_keys[pygame.K_d]:
                    self.fluff2.move += pygame.math.Vector2(10,0)
                if pressed_keys[pygame.K_a]:
                    self.fluff2.move += pygame.math.Vector2(-10,0)
                if pressed_keys[pygame.K_w]:
                    self.fluff2.move += pygame.math.Vector2(0,10)
                if pressed_keys[pygame.K_s]:
                    self.fluff2.move += pygame.math.Vector2(0,-10)
                    
            if len(self.fluffgroup) >= 3:
                if pressed_keys[pygame.K_l]:
                    self.fluff3.move += pygame.math.Vector2(10,0)
                if pressed_keys[pygame.K_j]:
                    self.fluff3.move += pygame.math.Vector2(-10,0)
                if pressed_keys[pygame.K_i]:
                    self.fluff3.move += pygame.math.Vector2(0,10)
                if pressed_keys[pygame.K_k]:
                    self.fluff3.move += pygame.math.Vector2(0,-10)
                    
                    
            if len(self.fluffgroup) == 4:
                if pressed_keys[pygame.K_n]:
                    self.fluff4.move += pygame.math.Vector2(10,0)
                if pressed_keys[pygame.K_v]:
                    self.fluff4.move += pygame.math.Vector2(-10,0)
                if pressed_keys[pygame.K_g]:
                    self.fluff4.move += pygame.math.Vector2(0,10)
                if pressed_keys[pygame.K_b]:
                    self.fluff4.move += pygame.math.Vector2(0,-10)       
           
            
            # write text below sprites
            write(self.screen, "FPS: {:8.3}".format(
                self.clock.get_fps() ), x=10, y=10)
            write(self.screen, "Collisions:{}".format(self.collisions), x=Viewer.width-200, y=10)
            self.allgroup.update(seconds)
            
            
            # -----------collision detection between fluffballs and food -----
            for f in self.fluffgroup:
                crashgroup = pygame.sprite.spritecollide(f, self.foodgroup,
                             False,pygame.sprite.collide_mask)
                for e in crashgroup:
                    if e.__class__.__name__=="Donut":
                        Flytext(f.pos.x,-f.pos.y,text="Mjam",color=(240,80,190),duration=5,fontsize=30)
                        Explosion(pos=e.pos, what ="Crumb", maxspeed=900, minspeed=500, color=(210,110,210), maxduration=1.5, gravityy=0, sparksmin=100, sparksmax=300, acc=0.9)
                    elif e.__class__.__name__=="Cookie":
                        Flytext(f.pos.x,-f.pos.y,text="Knusper, Knusper!",color=(210,110,10),duration=5,fontsize=30)
                        Explosion(pos=e.pos, what ="Crumb", maxspeed=150, minspeed=50, color=(220,160,40), maxduration=1.5, gravityy=0, sparksmin=100, sparksmax=300, acc=1.05)
                    e.kill()
                    #Explosion(pos=e.pos, what ="Crumb", maxspeed=100, minspeed=50, color=(220,160,40), maxduration=1.5, gravityy=0, sparksmin=20, sparksmax=50)
                    if len(self.foodgroup) == 0 and not gameOver:
                        Flytext(Viewer.width/2,Viewer.height/2,"Alles gemampft... Päuschen!", (0,0,255), duration=10, fontsize=145)
                        #endtime = self.playtime + 5 # in 5 sekunden ist alles aus
                        gameOver = True
                        exittime = self.playtime + 3
            # ----------collision detection between fluffballs and car wheel----
            for f in self.fluffgroup:
                crashgroup = pygame.sprite.spritecollide(f, self.car_wheelgroup,
                             False,pygame.sprite.collide_mask)
                for z in crashgroup:
                    if z.__class__.__name__=="Autoreifen":
                        if crazytime_cooldown <= self.playtime:
                            crazytime = self.playtime + 0.1
                            crazytime_cooldown = self.playtime + 0.75
                            Flytext(f.pos.x,-f.pos.y,text="Uargh, ein Autoreifen!",color=(1,1,1),duration=5,fontsize=40)
                       
                        f.reifendamage +=100
                        #Fluffball makes a little jump if bouncing against a car wheel
                        f.move = f.move*-0.8
                        j = f.move.normalize()*25
                        f.pos += j
                        if len(self.foodgroup):
                            self.collisions += 1
                        if self.collisions == 100:
                            Flytext(Viewer.width/2,Viewer.height/2,"Game over", (0,0,0), duration=10, fontsize=350)
                            gameOver = True
                            exittime = self.playtime + 3
                        #(self, pos, maxspeed=150, minspeed=20, color=(255,255,0),maxduration=2.5,gravity=3.7,sparksmin=5,sparksmax=20):
                        dist = f.pos-z.pos
                        point = z.pos + dist * 0.5
                        a = -dist.angle_to(pygame.math.Vector2(1,0))
                        a1 = a -15
                        a2 = a + 15
                        Explosion(pos=point, min_angle=a1, max_angle=a2, what ="Spark", maxspeed=100, minspeed=50, color=(0,0,0), maxduration=2.5, gravityy=0, sparksmin=10, sparksmax=30)
            #------------collision detection between fluffball and other fluffball-----           
            for f in self.fluffgroup:
                crashgroup = pygame.sprite.spritecollide(f, self.fluffgroup, False, pygame.sprite.collide_mask)
                for otherf in crashgroup:
                    if f.number > otherf.number:
                        elastic_collision(f, otherf)   
       
            
            # ----- all paws in idle position ----- 
            for k in self.kittygroup:
                for p in self.pawgroup:
                    if p.bossnumber == k.number:
                        p.stop_play()

            #------ flapping ? -------
            #if pressed_keys[pygame.K_1]:              
            for k in self.kittygroup:
                if k.state == "flap":
                    # todo: kitty bewegen
                    for p in self.pawgroup:
                        if p.bossnumber == k.number:
                            p.flap()

                for f in self.fluffgroup:
                    # --------- kitty plays with ball -------
                    
                    diff= f.pos - (k.pos - pygame.math.Vector2(0,0))
                    diff.y *= -1
                    #print ("Test " + str(diff.length()))
                    if diff.length()<100:

                        a=diff.angle_to(pygame.math.Vector2(1,0))
                        # alle pfoten von kitty1 suchen
                        for p in self.pawgroup:
                            if p.bossnumber == k.number:
                                #print("Pfote gefunden")
                                p.play(angle=a)
                        
                        f.move = pygame.math.Vector2(0,0)
                        rv = pygame.math.Vector2(random.random()*150+150,0)
                        rv=rv.rotate(random.randint(0,360))
                        f.move+=rv
                        
                    
                            # ----------- clear, draw , update, flip -----------------
            self.allgroup.draw(self.screen)
           
                        
            # -------- next frame -------------
            pygame.display.flip()
        #-----------------------------------------------------
        pygame.mouse.set_visible(True)    
        pygame.quit()

if __name__ == '__main__':
    Viewer(1430,800).run() # try Viewer(800,600).run()
#© 2019 GitHub, Inc.
#Terms
#Privacy
#Security
#Status
#Help
#Contact GitHub
#Pricing
#API
#Training
#Blog
#About
