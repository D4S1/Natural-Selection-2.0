import pygame
from sys import exit

from random import randint, randrange
from collections import Counter

import matplotlib.pyplot as plt
# import numpy as np

from classes.duck import Duck
from classes.food import Food
from classes.ui import UI, MainMenu, SideMenu, Button


class Simulation:

    def __init__(self, screen_size):
        pygame.init()
        self.screen = pygame.display.set_mode(screen_size)
        self.clock = pygame.time.Clock()

        UI.init(self.screen)

        self.running = False
        self.intro = True

        # Hyperparameters
        self.init_pop = 0
        self.init_food_den = 0

        # Time
        self.start_time = 0
        self.pause_start = 0
        self.pause_gap = 0
        self.time = 0

        # Simulation objects
        self.ducks = pygame.sprite.Group()
        self.food = pygame.sprite.Group()

        # UI
        self.simulation_space = pygame.Surface((self.get_size()[1], self.get_size()[1]))
        self.simulation_space.fill((107, 142, 35))

        self.main_menu = MainMenu(self.screen)
        self.side_menu = None

        # Buttons
        self.pause_img = pygame.image.load('graphics/pause.png').convert_alpha()
        self.play_img = pygame.image.load('graphics/play.png').convert_alpha()
        self.pause_button = Button(UI.side_menu_positions['Stop'], self.play_img)
        self.restart_button = Button(UI.side_menu_positions['Restart'], pygame.image.load('graphics/restart.png').convert_alpha())

        self.food_timer = pygame.USEREVENT + 1
        pygame.time.set_timer(self.food_timer, 4000)

    def get_size(self):
        return self.screen.get_size()

    def generate_food(self, size: int) -> object:
        # Funkcja generująca jedzenie
        width, height = self.get_size()  # screen
        x = randrange(UI.side_menu_size + 2 * size, width - size, size)
        y = randrange(1 + size, height - size, size)
        return Food(x, y)

    def new_food(self) -> None:
        # Funkcja dodaje jedzenie na planszę.
        # Im większe frequency, tym mniej jedzenia się pojawi.

        food_width = int(5)  # dla jedzenia o szerokości 5
        width, height = self.get_size()

        num = int((height/(food_width * 10)) ** 2 * self.init_food_den/100)
        for i in range(num):
            self.food.add(self.generate_food(food_width))
        # Szerokość jedzenia to 5, dlatego +/- 5, dzięki temu jedzenie na siebie nie na chodzi

    def initialize_ducks(self) -> None:
        # Funkcja dodaje init liczbę kaczek do symulacji.
        # W tym przypadku kaczki nachodzące na siebie nas nie dotyczy, bo ruch i tak
        # tego nie uwzględnia.
        width, height = self.get_size()

        for i in range(self.init_pop):
            self.ducks.add(
                Duck(
                    name=f"Kaczucha no {i}",
                    speed=randint(6, 10),
                    sense=100,
                    energy=1000,
                    x=randint(UI.side_menu_size, width),
                    y=randint(1, height),
                    group=self.ducks
                )
            )

    def collision_sprite(self):
        """
        Funkcja sprawdza kolizje pomiędzy obiektami (czyt. czy kaczka weszła na jedzenie).
        Jeżeli tak, to zwiększy energie kaczki i usunie obiekt jedzenie
        """
        for duck in self.ducks.sprites():
            target_exist = False
            for food in self.food.sprites():
                if pygame.sprite.collide_rect(duck, food):
                    duck.eat()
                    food.kill()
                if duck.target == (food.rect.x, food.rect.y):
                    target_exist = True
            if not target_exist:
                duck.target = None

    def pause(self):
        if self.running:
            self.pause_start = int(pygame.time.get_ticks() / 1000)
            self.time = int(pygame.time.get_ticks() / 1000) - self.pause_gap - self.start_time
            self.pause_button.image = self.pause_img
        else:
            self.pause_gap += int(pygame.time.get_ticks() / 1000) - self.pause_start
            self.pause_button.image = self.play_img

        self.running = not self.running

    def graph(self):

        # ax = plt.figure().add_subplot(projection='3d')

        x = [duck.speed for duck in self.ducks]  # np.array for 3d
        y = [duck.sense for duck in self.ducks]
        count = Counter(zip(x, y))
        # X, Y = np.meshgrid(x, y)
        # Z = np.array([[count[(xi, yi)] for xi in x] for yi in y])
        #
        # # Plot the 3D surface
        # ax.scatter(X, Y, Z, alpha=0.3)
        # ax.set(xlim=(0, 15), ylim=(0, 300), zlim=(0, 10), xlabel='speed', ylabel='sense', zlabel='counts')

        fig, ax = plt.subplots()
        size = [50 * count[(x1, y1)] for x1, y1 in zip(x, y)]
        ax.set(xlim=(0, 15), ylim=(0, 300), xlabel="speed", ylabel="sense")
        ax.scatter(x, y, s=size)

        plt.savefig('graphics/plot.png', dpi=60)

        img = pygame.image.load('graphics/plot.png')
        plt.close()
        self.screen.blit(img, UI.side_menu_positions['Plot'])

    def run(self):
        self.running = True

        while True:
            for event in pygame.event.get():
                # zamykanie okna
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()

                # space (pause)
                if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                    if not self.intro:
                        self.pause()
                        self.pause_button.action = not self.pause_button.action

                    else:
                        self.intro = False
                        self.init_pop, self.init_food_den = self.main_menu.get_settings()

                        self.side_menu = SideMenu(self)

                        self.initialize_ducks()
                        self.new_food()  # Początkowe jedzenie const = 20 ?

                        # deklaracja wykresu
                        # fig, ax = plt.subplots()

                        self.start_time = int(pygame.time.get_ticks() / 1000)
                        self.pause_gap = 0
                        self.pause_button.action = False
                        self.running = True

                # dostawianie jedzenia
                if self.running and event.type == self.food_timer:
                    self.new_food()

            if self.intro:
                self.main_menu.run()

            else:
                if self.running:
                    self.time = int(pygame.time.get_ticks() / 1000) - self.pause_gap - self.start_time

                self.screen.blit(self.simulation_space, (UI.side_menu_size, 0))
                self.side_menu.run()
                self.graph()

                paused = self.pause_button.draw(self.screen)
                if not (self.running ^ paused):
                    self.pause()

                if self.restart_button.draw(self.screen):
                    self.restart_button.action = False
                    self.ducks.empty()
                    self.food.empty()
                    self.intro = True
                    self.running = False

                self.food.draw(self.screen)
                self.ducks.draw(self.screen)

                if self.running:
                    self.ducks.update(UI.side_menu_size, self.get_size(), self.food)

                    # sprawdzanie kolizji
                    self.collision_sprite()

                if len(self.ducks.sprites()) == 0 and self.running:
                    self.running = False

            pygame.display.update()
            self.clock.tick(20)


if __name__ == "__main__":
    plt.rcParams.update({
        'axes.labelsize': 20,
        'axes.titlesize': 20,
    })
    simulation = Simulation((1000+400, 1000))
    simulation.run()
