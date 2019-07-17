"""
author: Ines Schnabl
email: horstjens@gmail.com
contact: see http://spielend-programmieren.at/de:kontakt
license: gpl, see http://www.gnu.org/licenses/gpl-3.0.de.html
download: 
idea: clean python3/pygame template using pygame.math.vector2

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
        self._overwrite_parameters()
        pygame.sprite.Sprite.__init__(self, self.groups) #call parent class. NEVER FORGET !
        self.number = VectorSprite.number # unique number for each sprite
        VectorSprite.number += 1
        VectorSprite.numbers[self.number] = self
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
        
    def create_image(self):
        self.image = Viewer.images[self.fluffball_color]
        self.image0 = self.image.copy()
        self.rect = self.image.get_rect()
        
class Babycat(VectorSprite):
    
    def _overwrite_parameters(self):
        self._layer = 1
    
    def create_image(self):        
        self.image = Viewer.images["baby cat"]
        self.image0 = self.image.copy()
        self.rect = self.image.get_rect()
    
    def ai(self):
        if random.random() < 0.01:
            self.move = pygame.math.Vector2(random.randint(-50,50),random.randint(-50,50))
            
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

class Explosion():
    
    def __init__(self, pos, what="Spark", maxspeed=150, minspeed=20, color=(255,255,0),maxduration=2.5,gravityy=3.7,sparksmin=5,sparksmax=20):

        for s in range(random.randint(sparksmin,sparksmax)):
            v = pygame.math.Vector2(1,0) # vector aiming right (0°)
            a = random.randint(0,360)
            v.rotate_ip(a)
            g = pygame.math.Vector2(0, - gravityy)
            speed = random.randint(minspeed, maxspeed)     #150
            duration = random.random() * maxduration
            if what == "Spark":     
                Spark(pos=pygame.math.Vector2(pos.x, pos.y), angle= a, move=v*speed,
                  max_age = duration, color=color, gravity = g)
            elif what == "Crumb":
                
                Crumb(pos=pygame.math.Vector2(pos.x, pos.y), angle= a, move=v*speed,
                  max_age = duration, color=color, gravity = g)
                  
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


                  
class Crumb(VectorSprite):

    def __init__(self, **kwargs):
        VectorSprite.__init__(self, **kwargs)
        #print("i am a new Crumb")
        if "gravity" not in kwargs:
            self.gravity = pygame.math.Vector2(0, -3.7)
    
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


class Viewer(object):
    width = 0
    height = 0
    images={}
    
    menu =  {"main":      ["Resume", "Help", "Credits", "Settings","Fluffballs"],
            "Help":       ["back", "Fluffball", "Donut", "Cookie", "Car wheel", "Cat"],
            "Credits":    ["back", "Ines Schnabl", "Martin Schnabl", ],
            "Settings":   ["back", "Screenresolution", "Fullscreen", "Difficulty"],
            "Resolution": ["back"],
            "Fullscreen": ["back", "True", "False"],
            "Difficulty": ["back", "Easy", "Medium", "Hard", "Impossible"],
            "Fluffballs": ["back", "Players", "Colors"],
            "Players":     ["back", "1 Player", "2 Player","3 Player", "4 Player"],
            "Colors":     ["back", "Fluffball 1", "Fluffball 2","Fluffball 3", "Fluffball 4"],
            "Fluffball 1":["back", "red", "yellow", "green", "turquoise", "blue", "purple"],
            "Fluffball 2":["back", "red", "yellow", "green", "turquoise", "blue", "purple"],
            "Fluffball 3":["back", "red", "yellow", "green", "turquoise", "blue", "purple"],
            "Fluffball 4":["back", "red", "yellow", "green", "turquoise", "blue", "purple"]
            }
            
            
            
    descr = {"Resume" :           ["Resume to the", "game"],                                           #resume
             "Martin schnabl" :   ["Ines' sixteen year", "old brother", "who helps her,", "when she is again", "confused by python"],
             "Ines schnabl":      ["A fourteen year old girl", "who programmed the game.", "But she is very often", "confused by python"],
             "Settings" :         ["Change the", "screenresolution", "only in the", "beginning!"],
             "Fluffball" :        ["A fluffy Ball", "who trys to eat", "as much donuts and cookies", "as possible"],
             "Donut" :            ["A delicious Donut,", "one of the favourite", "foods of Fluffballs"],
             "Cookie" :           ["A yummy Cookie.", "Fluffballs and", "Pummeleinhörner love it", "because it has so much", "sugar in it"],
             "Car wheel" :        ["A not so tasty car wheel.", "If Fluffballs take", "accidently a bite", "of a car wheel", "they will roll away", "in the other direction"],
             "Cat"  :             ["A cute Cat", "who whants to play", "with the fluffballs"],
             "Players":           ["Change the amount of", "Fluffballs in the game."],
             "Colors":            ["Change the color of the Fluffballs."]
             }
    menu_images = {"Fluffball" : "fluffball_menu",
                   "Donut"     : "donut_menu",
                   "Cookie"    : "cookie_menu",
                   "Car wheel" : "car wheel_menu",
                   "Cat"       : "baby cat_menu",
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
        li = ["back"]
        for i in pygame.display.list_modes():
            # li is something like "(800, 600)"
            pair = str(i)
            comma = pair.find(",")
            x = pair[1:comma]
            y = pair[comma+2:-1]
            li.append(str(x)+"x"+str(y))
        Viewer.menu["Screenresolution"] = li
        self.set_screenresolution()

    def loadbackground(self):
        
        #try:
        #    self.background = pygame.image.load(os.path.join("data",
        #         self.backgroundfilenames[Viewer.wave %
        #         len(self.backgroundfilenames)]))
        #except:
        #    self.background = pygame.Surface(self.screen.get_size()).convert()
        #    self.background.fill((255,255,255)) # fill background white
        self.background = pygame.Surface(self.screen.get_size()).convert()
        self.background.fill((255,255,255))
        self.background = pygame.transform.scale(self.background,
                          (Viewer.width,Viewer.height))
        self.background.convert()
        
    def set_screenresolution(self):
        print(self.width, self.height)
        if Viewer.fullscreen:
             self.screen = pygame.display.set_mode((self.width, self.height), pygame.DOUBLEBUF|pygame.FULLSCREEN)
        else:
             self.screen = pygame.display.set_mode((self.width, self.height), pygame.DOUBLEBUF)
        self.loadbackground()
        
    def load_sprites(self):
        Viewer.images["fluffballb."] = pygame.image.load(os.path.join("data", "Fluffballlöwenzahnb.png")).convert_alpha()
        Viewer.images["fluffballb."] = pygame.transform.scale(Viewer.images["fluffballb."], (100,100))
        Viewer.images["fluffballgb."] = pygame.image.load(os.path.join("data", "Fluffballlöwenzahngb.png")).convert_alpha()
        Viewer.images["fluffballgb."] = pygame.transform.scale(Viewer.images["fluffballgb."], (100,100))
        Viewer.images["fluffballgn."] = pygame.image.load(os.path.join("data", "Fluffballlöwenzahngn.png")).convert_alpha()
        Viewer.images["fluffballgn."] = pygame.transform.scale(Viewer.images["fluffballgn."], (100,100))
        Viewer.images["fluffballp."] = pygame.image.load(os.path.join("data", "Fluffballlöwenzahnp.png")).convert_alpha()
        Viewer.images["fluffballp."] = pygame.transform.scale(Viewer.images["fluffballp."], (100,100))
        Viewer.images["fluffballt."] = pygame.image.load(os.path.join("data", "Fluffballlöwenzahnt.png")).convert_alpha()
        Viewer.images["fluffballt."] = pygame.transform.scale(Viewer.images["fluffballt."], (100,100))
        Viewer.images["fluffball_menu"] = pygame.image.load(os.path.join("data", "Fluffballlöwenzahn.png")).convert_alpha()
        Viewer.images["fluffball_menu"] = pygame.transform.scale(Viewer.images["fluffball_menu"], (300, 300))
        Viewer.images["fluffballr."] = pygame.image.load(os.path.join("data", "Fluffballlöwenzahnr.png")).convert_alpha()
        Viewer.images["fluffballr."] = pygame.transform.scale(Viewer.images["fluffballr."], (100,100))
        Viewer.images["donut_menu"] = pygame.image.load(os.path.join("data", "donut.png")).convert_alpha()
        Viewer.images["donut_menu"] = pygame.transform.scale(Viewer.images["donut_menu"], (300, 300))
        Viewer.images["cookie_menu"] = pygame.image.load(os.path.join("data", "cookie.png")).convert_alpha()
        Viewer.images["cookie_menu"] = pygame.transform.scale(Viewer.images["cookie_menu"], (275, 275))
        Viewer.images["car wheel_menu"] = pygame.image.load(os.path.join("data", "car_wheel.png")).convert_alpha()
        Viewer.images["car wheel_menu"] = pygame.transform.scale(Viewer.images["car wheel_menu"], (300, 300))
        Viewer.images["baby cat"] = pygame.image.load(os.path.join("data", "baby cat.png")).convert_alpha()
        Viewer.images["baby cat_menu"] = pygame.transform.scale(Viewer.images["baby cat"], (300, 300))
        Viewer.images["baby cat"] = pygame.transform.scale(Viewer.images["baby cat"], (125, 175))
        Viewer.images["donut"] = pygame.image.load(os.path.join("data", "donut.png")).convert_alpha()
        Viewer.images["donut"] = pygame.transform.scale(Viewer.images["donut"], (100,100))
        Viewer.images["cookie"] = pygame.image.load(os.path.join("data", "cookie.png")).convert_alpha()
        Viewer.images["cookie"] = pygame.transform.scale(Viewer.images["cookie"], (80,80))
        Viewer.images["car wheel"] = pygame.image.load(os.path.join("data", "car_wheel.png")).convert_alpha()
        Viewer.images["car wheel"] = pygame.transform.scale(Viewer.images["car wheel"], (100,100))
    
    
    def prepare_sprites(self):
        """painting on the surface and create sprites"""
        self.load_sprites()
        self.allgroup =  pygame.sprite.LayeredUpdates() # for drawing
        self.explosiongroup = pygame.sprite.Group()
        self.foodgroup = pygame.sprite.Group()
        self.fluffgroup = pygame.sprite.Group()
        self.car_wheelgroup = pygame.sprite.Group()
        self.flytextgroup = pygame.sprite.Group()
        self.babycatgroup = pygame.sprite.Group()
        self.collisiongroup = pygame.sprite.Group()
        
        VectorSprite.groups = self.allgroup
        Flytext.groups = self.allgroup
        Explosion.groups = self.allgroup, self.explosiongroup
        Donut.groups = self.allgroup, self.foodgroup, self.collisiongroup
        Fluffball.groups = self.allgroup, self.fluffgroup, self.collisiongroup
        Cookie.groups = self.allgroup, self.foodgroup, self.collisiongroup
        Autoreifen.groups = self.allgroup, self.car_wheelgroup, self.collisiongroup
        Flytext.groups = self.allgroup, self.flytextgroup
        Babycat.groups = self.allgroup, self.babycatgroup, self.collisiongroup
        Spark.groups = self.allgroup 
        Crumb.groups = self.allgroup

        self.fluffs.clear()
        self.fluff = Fluffball(bounce_on_edge=True, pos=pygame.math.Vector2(Viewer.width//4,-Viewer.height//4),fluffball_color="fluffballb.")
        self.fluffs.append(self.fluff)
        if Game.players >= 2:
            self.fluff2 = Fluffball(bounce_on_edge=True, pos=pygame.math.Vector2(Viewer.width//1.33,-Viewer.height//4))
            self.fluffs.append(self.fluff2)
        if Game.players >= 3:
            self.fluff3 = Fluffball(bounce_on_edge=True, pos=pygame.math.Vector2(Viewer.width//4,-Viewer.height//1.33))
            self.fluffs.append(self.fluff3)
        if Game.players >= 4:
            self.fluff3 = Fluffball(bounce_on_edge=True, pos=pygame.math.Vector2(Viewer.width//1.33,-Viewer.height//1.33))
            self.fluffs.append(self.fluff4)
            
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
                self.babycat = Babycat(warp_on_edge=True, pos=pygame.math.Vector2(random.randint(0,Viewer.width),-random.randint(0,Viewer.height)))
        else:
            for x in range(Game.difficulty*3):
                self.babycat = Babycat(warp_on_edge=True, pos=pygame.math.Vector2(random.randint(0,Viewer.width),-random.randint(0,Viewer.height)))
    
    def menu_run(self):
        """Not The mainloop"""
        running = True
        pygame.mouse.set_visible(False)
        self.menu = True
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
                        elif text == "back":
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
                            if text == "blue":
                                self.fluff.fluffball_color = "fluffballb."
                                self.fluff.create_image()
                                self.fluff.rect.center  = (int(self.fluff.pos.x), -int(self.fluff.pos.y))
                            elif text == "purple":
                                self.fluff.fluffball_color = "fluffballp."
                                self.fluff.create_image()
                                self.fluff.rect.center  = (int(self.fluff.pos.x), -int(self.fluff.pos.y))
                            elif text == "turquoise":
                                self.fluff.fluffball_color = "fluffballt."
                                self.fluff.create_image()
                                self.fluff.rect.center  = (int(self.fluff.pos.x), -int(self.fluff.pos.y))
                            elif text == "red":
                                self.fluff.fluffball_color = "fluffballr."
                                self.fluff.create_image()
                                self.fluff.rect.center  = (int(self.fluff.pos.x), -int(self.fluff.pos.y)) 
                            elif text == "yellow":
                                self.fluff.fluffball_color = "fluffballgb."
                                self.fluff.create_image()
                                self.fluff.rect.center  = (int(self.fluff.pos.x), -int(self.fluff.pos.y))
                            elif text == "green":
                                self.fluff.fluffball_color = "fluffballgn."
                                self.fluff.create_image()
                                self.fluff.rect.center  = (int(self.fluff.pos.x), -int(self.fluff.pos.y))   
                        elif Viewer.name == "Fluffball 2":
                            if len(self.fluffgroup) >= 2:
                                if text == "blue":
                                    self.fluff2.fluffball_color = "fluffballb."
                                    self.fluff2.create_image()
                                    self.fluff2.rect.center  = (int(self.fluff2.pos.x), -int(self.fluff2.pos.y))
                                elif text == "purple":
                                    self.fluff2.fluffball_color = "fluffballp."
                                    self.fluff2.create_image()
                                    self.fluff2.rect.center  = (int(self.fluff2.pos.x), -int(self.fluff2.pos.y))
                                elif text == "turquoise":
                                    self.fluff2.fluffball_color = "fluffballt."
                                    self.fluff2.create_image()
                                    self.fluff2.rect.center  = (int(self.fluff2.pos.x), -int(self.fluff2.pos.y))
                                elif text == "red":
                                    self.fluff2.fluffball_color = "fluffballr."
                                    self.fluff2.create_image()
                                    self.fluff2.rect.center  = (int(self.fluff2.pos.x), -int(self.fluff2.pos.y))
                                elif text == "yellow":
                                    self.fluff2.fluffball_color = "fluffballgb."
                                    self.fluff2.create_image()
                                    self.fluff2.rect.center  = (int(self.fluff.pos.x), -int(self.fluff.pos.y))
                                elif text == "green":
                                    self.fluff2.fluffball_color = "fluffballgn."
                                    self.fluff2.create_image()
                                    self.fluff2.rect.center  = (int(self.fluff.pos.x), -int(self.fluff.pos.y))
                        elif Viewer.name == "Fluffball 3":
                            if len(self.fluffgroup) >= 3:
                                if text == "blue":
                                    self.fluff3.fluffball_color = "fluffballb."
                                    self.fluff3.create_image()
                                    self.fluff3.rect.center  = (int(self.fluff.pos.x), -int(self.fluff.pos.y))
                                elif text == "purple":
                                    self.fluff3.fluffball_color = "fluffballp."
                                    self.fluff3.create_image()
                                    self.fluff3.rect.center  = (int(self.fluff.pos.x), -int(self.fluff.pos.y))
                                elif text == "turquoise":
                                    self.fluff3.fluffball_color = "fluffballt."
                                    self.fluff3.create_image()
                                    self.fluff3.rect.center  = (int(self.fluff.pos.x), -int(self.fluff.pos.y))
                                elif text == "red":
                                    self.fluff3.fluffball_color = "fluffballr."
                                    self.fluff3.create_image()
                                    self.fluff3.rect.center  = (int(self.fluff.pos.x), -int(self.fluff.pos.y)) 
                                elif text == "yellow":
                                    self.fluff3.fluffball_color = "fluffballgb."
                                    self.fluff3.create_image()
                                    self.fluff3.rect.center  = (int(self.fluff.pos.x), -int(self.fluff.pos.y))
                                elif text == "green":
                                    self.fluff3.fluffball_color = "fluffballgn."
                                    self.fluff3.create_image()
                                    self.fluff3.rect.center  = (int(self.fluff.pos.x), -int(self.fluff.pos.y))
                        elif Viewer.name == "Fluffball 4":
                            if len(self.fluffgroup) >= 4:
                                if text == "blue":
                                    self.fluff4.fluffball_color = "fluffballb."
                                    self.fluff4.create_image()
                                    self.fluff4.rect.center  = (int(self.fluff.pos.x), -int(self.fluff.pos.y))
                                elif text == "purple":
                                    self.fluff4.fluffball_color = "fluffballp."
                                    self.fluff4.create_image()
                                    self.fluff4.rect.center  = (int(self.fluff.pos.x), -int(self.fluff.pos.y))
                                elif text == "turquoise":
                                    self.fluff4.fluffball_color = "fluffballt."
                                    self.fluff4.create_image()
                                    self.fluff4.rect.center  = (int(self.fluff.pos.x), -int(self.fluff.pos.y))
                                elif text == "red":
                                    self.fluff4.fluffball_color = "fluffballr."
                                    self.fluff4.create_image()
                                    self.fluff4.rect.center  = (int(self.fluff.pos.x), -int(self.fluff.pos.y)) 
                                elif text == "yellow":
                                    self.fluff4.fluffball_color = "fluffballgb."
                                    self.fluff4.create_image()
                                    self.fluff4.rect.center  = (int(self.fluff.pos.x), -int(self.fluff.pos.y))
                                elif text == "green":
                                    self.fluff4.fluffball_color = "fluffballgn."
                                    self.fluff4.create_image()
                                    self.fluff4.rect.center  = (int(self.fluff.pos.x), -int(self.fluff.pos.y))  
                        elif text == "2 Player":
                            Game.players = 2
                            if len(self.fluffgroup) > 2:
                                self.fluff3.kill()
                            if len(self.fluffgroup) > 3:
                                self.fluff4.kill()
                            if len(self.fluffgroup) < 2:
                                self.fluff2 = Fluffball(bounce_on_edge=True, pos=pygame.math.Vector2(Viewer.width//1.33,-Viewer.height//4),fluffball_color="fluffballp.")
                                if len(self.fluffs) < 2:
                                    self.fluffs.append(self.fluff2)
                                Flytext(Viewer.width//2,Viewer.height//4,text="2 Fluffballs in the Game",color=(0,255,255),duration=5,fontsize=50)
                        elif text == "1 Player":
                            Game.players = 1
                            if len(self.fluffgroup) > 1:
                                self.fluff2.kill()
                            if len(self.fluffgroup) > 2:
                                self.fluff3.kill()
                            if len(self.fluffgroup) > 3:
                                self.fluff4.kill()
                            Flytext(Viewer.width//2,Viewer.height//4,text="1 Fluffball in the Game",color=(0,255,255),duration=5,fontsize=50) 
                        elif text == "3 Player":
                            Game.players = 3
                            if len(self.fluffgroup) == 1:
                                self.fluff2 = Fluffball(bounce_on_edge=True, pos=pygame.math.Vector2(Viewer.width//1.33,-Viewer.height//4),fluffball_color="fluffballt.")
                                if len(self.fluffs) < 2:
                                    self.fluffs.append(self.fluff2)
                            if len(self.fluffgroup) == 2:
                                self.fluff3 = Fluffball(bounce_on_edge=True, pos=pygame.math.Vector2(Viewer.width//4,-Viewer.height//1.33),fluffball_color="fluffballp.")
                                if len(self.fluffs) < 3:
                                    self.fluffs.append(self.fluff3)
                            if len(self.fluffgroup) > 3:
                                self.fluff4.kill()
                            Flytext(Viewer.width//2,Viewer.height//4,text="3 Fluffball in the Game",color=(0,255,255),duration=5,fontsize=50)
                        elif text == "4 Player":    
                            Game.players = 4
                            if len(self.fluffgroup) == 1:
                                self.fluff2 = Fluffball(bounce_on_edge=True, pos=pygame.math.Vector2(Viewer.width//4,-Viewer.height//1.33),fluffball_color="fluffballt.")
                                if len(self.fluffs) < 2:
                                    self.fluffs.append(self.fluff2)
                            if len(self.fluffgroup) == 2:
                                self.fluff3 = Fluffball(bounce_on_edge=True, pos=pygame.math.Vector2(Viewer.width//1.33,-Viewer.height//4),fluffball_color="fluffballp.")
                                if len(self.fluffs) < 3:
                                    self.fluffs.append(self.fluff3)
                            if len(self.fluffgroup) == 3:
                                self.fluff4 = Fluffball(bounce_on_edge=True, pos=pygame.math.Vector2(Viewer.width//1.33,-Viewer.height//1.33),fluffball_color="fluffballr.")
                                if len(self.fluffs) < 4:
                                    self.fluffs.append(self.fluff4)
                            Flytext(Viewer.width//2,Viewer.height//4,text="4 Fluffball in the Game",color=(0,255,255),duration=5,fontsize=50)
                        elif Viewer.name == "Difficulty":
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
                            if text == "True":
                                #Viewer.menucommandsound.play()
                                Viewer.fullscreen = True
                                self.set_screenresolution()
                            elif text == "False":
                                #Viewer.menucommandsound.play()
                                Viewer.fullscreen = False
                                self.set_screenresolution()
                            
                        
            # ------delete everything on screen-------
            self.screen.blit(self.background, (0, 0))
            
            # -------------- UPDATE all sprites -------             
            self.flytextgroup.update(seconds)

            # ----------- clear, draw , update, flip -----------------
            self.allgroup.draw(self.screen)
            
            
            pygame.draw.rect(self.screen,(170,170,170),(200,90,350,350))
            pygame.draw.rect(self.screen,(200,200,200),(600,90,350,350))
            pygame.draw.rect(self.screen,(230,230,230),(1000,90,350,350))
            
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
        Flytext(Viewer.width/2,Viewer.height/4,"Eat all Donuts and Cookies", (0,0,255), duration=10, fontsize=100)
        Flytext(Viewer.width/2,Viewer.height/2,"and stay under 50 collisions", (0,0,255), duration=10, fontsize=100)
        Flytext(Viewer.width/2,Viewer.height/1.33,"with the car wheels", (0,0,255), duration=10, fontsize=100)
        
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
                # ------- pressed and released key ------
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False
                #   if event.key == pygame.K_l:
                #       self.fluff.move = pygame.math.Vector2(0,0)
                #       self.fluff.pos = pygame.math.Vector2(Viewer.width/1.33,-Viewer.height/2)
                #   elif event.key == pygame.K_k:
                #       self.fluff2.move = pygame.math.Vector2(0,0)
                #       self.fluff2.pos = pygame.math.Vector2(Viewer.width/4,-Viewer.height/2)
                    elif event.key == pygame.K_m:
                        self.menu_run() 
            # delete everything on screen
            self.screen.blit(self.background, (0, 0))
            # ------------ pressed keys ------
            pressed_keys = pygame.key.get_pressed()

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
            # ------ mouse handler ------
            #left,middle,right = pygame.mouse.get_pressed()
            #if oldleft and not left:
            #    self.launchRocket(pygame.mouse.get_pos())
            #if right:
            #    self.launchRocket(pygame.mouse.get_pos())
            #oldleft, oldmiddle, oldright = left, middle, right

            # ------ joystick handler -------
            print(self.fluffs)
            print(len(self.joysticks))
            for number, j in enumerate(self.joysticks):
                if number == 0 :
                    x = j.get_axis(0)
                    y = j.get_axis(1)
                    self.fluffs[0].move.x += x * 10 # *2 
                    self.fluffs[0].move.y -= y * 10 # *2 
                if len(self.fluffs) > 1 and number == 1:
                    x = j.get_axis(0)
                    y = j.get_axis(1)
                    self.fluffs[1].move.x += x * 10 # *2 
                    self.fluffs[1].move.y -= y * 10 # *2
                if len(self.fluffs) > 2 and number == 2:
                    x = j.get_axis(0)
                    y = j.get_axis(1)
                    self.fluffs[2].move.x += x * 10 # *2 
                    self.fluffs[2].move.y -= y * 10 # *2
                if len(self.fluffs) > 3 and number == 3:
                    x = j.get_axis(0)
                    y = j.get_axis(1)
                    self.fluffs[3].move.x += x * 10 # *2 
                    self.fluffs[3].move.y -= y * 10 # *2
            #       buttons = j.get_numbuttons()
            #       for b in range(buttons):
            #           pushed = j.get_button( b )
                       #if b == 0 and pushed:
                       #        self.launchRocket((mouses[number].x, mouses[number].y))
                       #elif b == 1 and pushed:
                       #    if not self.mouse4.pushed: 
                       #        self.launchRocket((mouses[number].x, mouses[number].y))
                       #        mouses[number] = True
                       #elif b == 1 and not pushed:
                       #    mouses[number] = False
            
            
            #pos1 = pygame.math.Vector2(pygame.mouse.get_pos())
            #pos2 = self.mouse2.rec#t.center
            #pos3 = self.mouse3.rect.center
            
            # write text below sprites
            write(self.screen, "FPS: {:8.3}".format(
                self.clock.get_fps() ), x=10, y=10)
            write(self.screen, "Collisions:{}".format(self.collisions), x=Viewer.width-200, y=10)
            self.allgroup.update(seconds)
            
            #if len(self.foodgroup) == 0:
            #    Flytext(Viewer.width/2,Viewer.width/2,"Alles gemumpft... Päuschen!", (0,0,255), duration=10, fontsize=100)
            #if self.collisions > 100:
            #    break
            
            # -----------collision detection between fluffballs and food -----
            for f in self.fluffgroup:
                crashgroup = pygame.sprite.spritecollide(f, self.foodgroup,
                             False,pygame.sprite.collide_mask)
                for e in crashgroup:
                    if e.__class__.__name__=="Donut":
                        Flytext(f.pos.x,-f.pos.y,text="Mjam",color=(240,80,190),duration=5,fontsize=30)
                        Explosion(pos=e.pos, what ="Crumb", maxspeed=150, minspeed=50, color=(210,110,210), maxduration=1.5, gravityy=0, sparksmin=100, sparksmax=300)
                    elif e.__class__.__name__=="Cookie":
                        Flytext(f.pos.x,-f.pos.y,text="Knusper, Knusper!",color=(210,110,10),duration=5,fontsize=30)
                        Explosion(pos=e.pos, what ="Crumb", maxspeed=150, minspeed=50, color=(220,160,40), maxduration=1.5, gravityy=0, sparksmin=100, sparksmax=300)
                    e.kill()
                    #Explosion(pos=e.pos, what ="Crumb", maxspeed=100, minspeed=50, color=(220,160,40), maxduration=1.5, gravityy=0, sparksmin=20, sparksmax=50)
                    if len(self.foodgroup) == 0 and not gameOver:
                        Flytext(Viewer.width/2,Viewer.height/2,"Alles gemampft... Päuschen!", (0,0,255), duration=10, fontsize=100)
                        #endtime = self.playtime + 5 # in 5 sekunden ist alles aus
                        gameOver = True
                        exittime = self.playtime + 3
            # ----------collision detection between fluffballs and badfood----
            for f in self.fluffgroup:
                crashgroup = pygame.sprite.spritecollide(f, self.car_wheelgroup,
                             False,pygame.sprite.collide_mask)
                for z in crashgroup:
                    if z.__class__.__name__=="Autoreifen":
                        Flytext(f.pos.x,-f.pos.y,text="Uargh, ein Autoreifen!",color=(1,1,1),duration=5,fontsize=40)
                        #Fluffball makes a little jump if bouncing against a car wheel
                        f.move = f.move*-0.8
                        j = f.move.normalize()*25
                        f.pos += j
                        if len(self.foodgroup):
                            self.collisions += 1
                        if self.collisions == 50:
                            Flytext(Viewer.width/2,Viewer.height/2,"Game over", (0,0,0), duration=10, fontsize=350)
                            gameOver = True
                            exittime = self.playtime + 3
                        #(self, pos, maxspeed=150, minspeed=20, color=(255,255,0),maxduration=2.5,gravity=3.7,sparksmin=5,sparksmax=20):
                        dist = f.pos-z.pos
                        point = z.pos + dist * 0.5
                        
                        Explosion(pos=point, what ="Spark", maxspeed=100, minspeed=50, color=(0,0,0), maxduration=1.5, gravityy=0, sparksmin=20, sparksmax=50)
            #------------collision detection between fluffball and other fluffball-----           
            for f in self.fluffgroup:
                crashgroup = pygame.sprite.spritecollide(f, self.fluffgroup, False, pygame.sprite.collide_mask)
                for otherf in crashgroup:
                    if f.number > otherf.number:
                        elastic_collision(f, otherf)   
            #-----------collision detection between babycat and other stuff------
            for b in self.babycatgroup:
                crashgroup = pygame.sprite.spritecollide(b, self.fluffgroup, False, pygame.sprite.collide_mask)
                for c in crashgroup:
                    m = pygame.math.Vector2(random.randint(150,350),0)
                    m = m.rotate(random.randint(0,360))
                    c.move = m
            # ----------- clear, draw , update, flip -----------------
            self.allgroup.draw(self.screen)            
            # -------- next frame -------------
            pygame.display.flip()
        #-----------------------------------------------------
        pygame.mouse.set_visible(True)    
        pygame.quit()

if __name__ == '__main__':
    Viewer(1430,800).run() # try Viewer(800,600).run()
