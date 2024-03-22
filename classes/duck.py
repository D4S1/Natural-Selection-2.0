import pygame
import math
from random import randint, choice, random


class Duck(pygame.sprite.Sprite):

    def __init__(self, name, speed, sense, energy, x, y, group):
        super(Duck, self).__init__()

        # PARAMETRY ORGANIZMU
        self.name = name

        # target
        self.target = None

        self.speed = speed
        self.sense = sense

        self.energy = energy
        self.group = group

        # Koszt energii na 1 krok
        self.step_energy_cost = self.speed**2 / 4 + self.sense/50

        # Koszt energii na rozmnażanie
        self.reproduction_energy_cost = 1100

        # Prawdopodobieństwo, że zajdzie mutacja przy rozmnażaniu
        self.speed_mutation_probability = 0.7
        self.sense_mutation_probability = 0.8

        # Prawdopodobieńśtwo, że kaczucha zmieni kierunek
        self.change_dir_probability = 0.2

        # ustawienie stanu animacji
        self.dir = [0, -1]
        self.duck_frame_idx = 0

        self.images = [
            pygame.image.load('graphics/m1.png').convert_alpha(),
            pygame.image.load('graphics/m2.png').convert_alpha(),
            pygame.image.load('graphics/m3.png').convert_alpha(),
            pygame.image.load('graphics/m4.png').convert_alpha(),
            pygame.image.load('graphics/m5.png').convert_alpha(),
            pygame.image.load('graphics/m6.png').convert_alpha(),
            pygame.image.load('graphics/m5.png').convert_alpha(),
            pygame.image.load('graphics/m4.png').convert_alpha(),
            pygame.image.load('graphics/m3.png').convert_alpha(),
            pygame.image.load('graphics/m2.png').convert_alpha()

        ]
        # Pygame owe rzeczy
        self.image = self.images[0]
        self.rect = self.image.get_rect(midbottom=(x, y))

    def animation_state(self):
        """
        Funkcja ustawia, która z grafik animacji powinna zostać w danej klatce wyświetlona
        """
        # Chcemy, żeby nowa grafika się pojawiała co kilka klatek
        self.duck_frame_idx += 0.4
        if self.duck_frame_idx >= len(self.images): self.duck_frame_idx = 0

        self.image = self.images[int(self.duck_frame_idx)]

        if self.dir[1] != 0:
            self.image = pygame.transform.rotate(self.image, math.degrees(math.atan2(self.dir[0], self.dir[1])) + 180)
        else:
            if self.dir[0] >= 0:
                self.image = pygame.transform.rotate(self.image, -90)
            else:
                self.image = pygame.transform.rotate(self.image, 90)

    def i_see(self, vector_to_point, cone_min_vec, cone_max_vec, ):

        cross_1 = cone_min_vec[0] * vector_to_point[1] - cone_min_vec[1] * vector_to_point[0]
        cross_2 = cone_max_vec[0] * vector_to_point[1] - cone_max_vec[1] * vector_to_point[0]

        dot_1 = cone_min_vec[0] * vector_to_point[0] + cone_min_vec[1] * vector_to_point[1]

        if (cross_1 < 0 < cross_2 or cross_1 > 0 > cross_2) and dot_1 > 0:
            return True
        else:
            return False

    def find_target(self, targets):
        left_vec = [
            self.dir[0] * math.cos(math.pi / 6) - self.dir[1] * math.sin(math.pi / 6),
            self.dir[0] * math.sin(math.pi / 6) + self.dir[1] * math.cos(math.pi / 6)
        ]

        right_vec = [
            self.dir[0] * math.cos(-math.pi / 6) - self.dir[1] * math.sin(-math.pi / 6),
            self.dir[0] * math.sin(-math.pi / 6) + self.dir[1] * math.cos(-math.pi / 6)
        ]
        min_dis = self.sense
        c = False
        for target in targets:
            point = (target.rect.x, target.rect.y)
            vector_to_point = [point[0] - self.rect.x, point[1] - self.rect.y]
            dis = (vector_to_point[0] ** 2 + vector_to_point[1] ** 2) ** (1/2)
            if dis <= self.sense and self.i_see(vector_to_point, left_vec, right_vec) and dis < min_dis:
                self.target = point
                min_dis = dis
                c = True
        return c

    def move_to_target(self):
        dx = self.target[0] - self.rect.x
        dy = self.target[1] - self.rect.y
        dis = (dx ** 2 + dy ** 2) ** (1/2)
        self.dir = [dx/dis, dy/dis]

    def random_dir(self):
        # ustawienie nowego kierunku
        next_dir = self.dir
        lr = choice([1, -1])
        if random() < self.change_dir_probability:
            next_dir = [
                self.dir[0] * math.cos(math.pi / 12) - self.dir[1] * math.sin(lr * math.pi / 12),
                self.dir[0] * math.sin(lr * math.pi / 12) + self.dir[1] * math.cos(math.pi / 12)
            ]

        self.dir = next_dir

    def move(self, menu_width, screen_size):
        """
        funkcja modyfikująca współrzędne obiektu w nawiasie losowo
        """

        self.rect.x += self.dir[0] * self.speed

        if self.rect.left < menu_width: self.rect.right = screen_size[0]
        if self.rect.right > screen_size[0]: self.rect.left = menu_width

        # tak samo ja wyżej tylko, że dla y
        self.rect.y += self.dir[1] * self.speed

        if self.rect.top < 0: self.rect.bottom = screen_size[1]
        if self.rect.bottom > screen_size[1]: self.rect.top = 0

        self.animation_state()

    def energy_lost(self):
        '''
        Koszt energii w jednej jednostce czasu, jaki ponosi
        organizm. W przypadku jeśli spadnie to zera to
        kaczucha umiera.
        energy = enrgy - (speed^2 * sense)
        '''
        self.energy -= self.step_energy_cost

    def mutate(self):
        """
        Funkcja generuje zmutowane (lub nie) parametry dla potomstwa
        """
        speed = self.speed
        sense = self.sense

        if random() < self.speed_mutation_probability:
            if speed <= 3 or random() >= 0.5:
                speed += math.ceil(0.1 * speed)
            else:
                speed -= math.ceil(0.1 * speed)

        if random() < self.sense_mutation_probability:
            if sense == 1 or random() >= 0.5:
                sense += 25
            else:
                sense -= 25

        return speed, sense

    def reproduce(self):
        """
        funkcja rozmnażająca kaczki
        warto się zastanowić nad energią graniczną wymaganą do rozmnażania,
        energią zużywaną na rozmnażanie i energią nadawaną dzieciom
        """
        if self.energy >= 3 * self.reproduction_energy_cost:
            self.energy -= self.reproduction_energy_cost
            speed, sense = self.mutate()
            self.group.add(
                Duck(
                    name=f"Kaczucha",
                    speed=speed,
                    sense=sense,
                    energy=1000,
                    x=self.rect.x,
                    y=self.rect.y,
                    group=self.group
                )
            )

    def eat(self):
        self.energy += 500

    def alive(self):
        if self.energy <= 0:
            self.kill()

    def update(self, menu_width, screen_size, targets):
        if self.find_target(targets):
            self.move_to_target()
        else:
            self.random_dir()

        self.move(menu_width, screen_size)
        self.energy_lost()
        self.reproduce()
        self.alive()
