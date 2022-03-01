
from asyncio import events
import pygame_widgets
import pygame
import math
import os
from utils import blit_text_centre
from pygame_widgets.slider import Slider
from pygame_widgets.textbox import TextBox
import time

pygame.init()

WIDTH, HEIGHT = 1920, 1080
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Planet Simulation")

WHITE = (255, 255, 255)
YELLOW = (255, 255, 0)
BLUE = (100, 149, 237)
RED = (188, 39, 50)
DARK_GREY = (80, 78, 81)
BROWN = (205, 127, 50)

MAIN_FONT = pygame.font.SysFont("comicsans", 44)

timeFont = pygame.font.SysFont("comicsans", 25)
FONT = pygame.font.SysFont("comicsans", 17)

#loading images
bg = pygame.image.load(os.path.join("images\space1.png")).convert()
bg = pygame.transform.scale(bg,(WIDTH,HEIGHT))
e_button = pygame.image.load(os.path.join("images\exit_btn.png")).convert()






class Button():

    def __init__(self, x, y, image, scale):
        width = image.get_width()
        height = image.get_height()
        self.image = pygame.transform.scale(image, (int(width*scale), int(height*scale)))
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)
        self.clicked = False
        self.action = False
    

    def draw(self):
        pos = pygame.mouse.get_pos()
        

        

        if self.rect.collidepoint(pos):
            if pygame.mouse.get_pressed()[0] == 1 and self.clicked == False:
                print("clicked")
                self.clicked = True
                self.action = True

    
        WIN.blit(self.image , (self.rect.x, self.rect.y))

        


class gameInfo:

    def __init__(self):
        self.started = False
        self.simulation_start_time = 0

    def reset(self):
        self.started = False

    def start_simulation(self):
        self.started = True
        self.simulation_start_time = time.time()

    def get_simulation_time(self):
        if not self.started:
            return 0
        return round(time.time() - self.simulation_start_time)
   



class Planet:
    AU = 149.6e6 * 1000
    G = 6.67428e-11
    SCALE = 250 / AU  # 1AU = 100 pixels
    TIMESTEP = 3600*24 # 1 day

    def __init__(self, x, y, radius, color, mass):
        self.x = x
        self.y = y
        self.radius = radius
        self.color = color
        self.mass = mass

        self.orbit = []
        self.sun = False
        self.distance_to_sun = 0

        self.x_vel = 0
        self.y_vel = 0
        
        


    def draw(self, win):
        x = self.x * self.SCALE + WIDTH / 2
        y = self.y * self.SCALE + HEIGHT / 2

        if len(self.orbit) > 2:
            updated_points = []
            for point in self.orbit:
                x, y = point
                x = x * self.SCALE + WIDTH / 2
                y = y * self.SCALE + HEIGHT / 2
                updated_points.append((x, y))

            pygame.draw.lines(win, self.color, False, updated_points, 2)
        pygame.draw.circle(win, self.color, (x, y), self.radius)

        if not self.sun:
            distance_text = FONT.render(
                f"{round(self.distance_to_sun/1000000)}GM", 1, WHITE)
            win.blit(distance_text, (x - distance_text.get_width() /
                     2, y - distance_text.get_height()/2))

    def attraction(self, other):
        other_x, other_y = other.x, other.y
        distance_x = other_x - self.x
        distance_y = other_y - self.y
        distance = math.sqrt(distance_x ** 2 + distance_y ** 2)

        if other.sun:
            self.distance_to_sun = distance

        force = self.G * self.mass * other.mass / distance**2
        theta = math.atan2(distance_y, distance_x)
        force_x = math.cos(theta) * force
        force_y = math.sin(theta) * force
        return force_x, force_y

    def update_position(self, planets):
        total_fx = total_fy = 0
        for planet in planets:
            if self == planet:
                continue
            fx, fy = self.attraction(planet)
            total_fx += fx
            total_fy += fy

        self.x_vel += total_fx / self.mass * self.TIMESTEP
        self.y_vel += total_fy / self.mass * self.TIMESTEP

        self.x += self.x_vel * self.TIMESTEP
        self.y += self.y_vel * self.TIMESTEP
        self.orbit.append((self.x, self.y))

#creating objects 

game_info = gameInfo()
exit_button = Button(1680, 10, e_button, 1)



def main():
    run = True
    clock = pygame.time.Clock()

    mass_sun = Slider(WIN, 100, 100, 400, 40, min=0, max=99, step=1, intial = 100)
    sun_output = TextBox(WIN, 300, 200, 50, 50, fontsize = 30)
    sun_output.disable()



    sun = Planet(0, 0, 60, YELLOW, 1.98892 * 10**30)
    sun.sun = True

    earth = Planet(-1 * Planet.AU, 0, 32, BLUE, 5.9742 * 10**24)
    earth.y_vel = 29.783 * 1000

    mars = Planet(-1.524 * Planet.AU, 0, 24, RED, 6.39 * 10**23)
    mars.y_vel = 24.077 * 1000

    mercury = Planet(0.387 * Planet.AU, 0, 16, DARK_GREY, 3.30 * 10**23)
    mercury.y_vel = -47.4 * 1000

    venus = Planet(0.723 * Planet.AU, 0, 28, BROWN, 4.8685 * 10**24)
    venus.y_vel = -35.02 * 1000



    planets = [sun, earth, mars, mercury, venus]

    slider_settings = [(mass_sun, sun_output)]
   

    while run:
        clock.tick(60)
        WIN.fill((0, 0, 0))
        WIN.blit(bg, (0,0))
        

        while game_info.started == False:
            blit_text_centre(WIN, MAIN_FONT, f"Pess any key to start the simulation")
            
            pygame.display.update()

            events = pygame.event.get()
            for event in events:
                if event.type == pygame.QUIT:
                    pygame.quit()
                    break

                if event.type == pygame.KEYDOWN:
                    game_info.start_simulation()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
        

        
    

        
        exit_button.draw()
        if exit_button.action == True:
            game_info.started = False
            break

        
        


      
        for planet in planets:
            planet.update_position(planets)
            planet.draw(WIN)

        #pygame_widgets.update(events)
        pygame.display.update()

    pygame.quit()


main()
