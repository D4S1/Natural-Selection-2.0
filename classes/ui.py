import pygame


class UI:
    @staticmethod
    def init(screen):
        path = 'font/Pixeltype.ttf'

        UI.font = pygame.font.Font(path, 30)
        UI.sfont = pygame.font.Font(path, 20)
        UI.lfont = pygame.font.Font(path, 40)
        UI.xlfont = pygame.font.Font(path, 50)

        UI.center = (screen.get_size()[0]//2, screen.get_size()[1]//2)
        UI.half_width = screen.get_size()[0]//2
        UI.half_height = screen.get_size()[1]//2

        UI.width, UI.height = screen.get_size()

        UI.fonts = {
            'sm': UI.sfont,
            'm': UI.font,
            'l': UI.lfont,
            'xl': UI.xlfont
        }

        UI.main_menu_positions = {
            'title': (UI.half_width, 200),
            'logo': (UI.half_width, 400),
            'subtitle': (UI.half_width, 600),
            'label_s1': (UI.half_width - 150, 660),
            'slider1': (UI.half_width + 100, 660),
            'label_s2': (UI.half_width - 150, 700),
            'slider2': (UI.half_width + 100, 700),
            'run': (UI.half_width, 780)
        }

        UI.side_menu_size = 400
        UI.side_menu_positions = {
            'time': (UI.side_menu_size//2, 100),
            'Population': (UI.side_menu_size//2, 150),
            'Stop': (UI.side_menu_size//2, 300),
            'Restart': (UI.side_menu_size//2, 380),
            'Plot': (UI.side_menu_size//2 - 200, 450),
            'Init population': (UI.side_menu_size//2, UI.height - 100),
            'Init food density': (UI.side_menu_size//2, UI.height - 50),
        }


class MainMenu:

    def __init__(self, screen, bg='White'):
        self.screen = screen
        self.bg = bg
        self.screen_width, self.screen_height = self.screen.get_size()

        self.game_name = UI.fonts['xl'].render('Natural selection simulation', False, 'Black')
        self.game_name_rect = self.game_name.get_rect(center=UI.main_menu_positions['title'])

        duck_logo = pygame.image.load('graphics/m_logo.png').convert_alpha()
        self.duck_logo = pygame.transform.rotozoom(duck_logo, 0, 0.7)
        self.duck_logo_rect = self.duck_logo.get_rect(center=UI.main_menu_positions['logo'])

        self.subtitle = UI.fonts['l'].render('Settings', False, 'Black')
        self.subtitle_rect = self.subtitle.get_rect(center=UI.main_menu_positions['subtitle'])

        self.slider1_label = UI.fonts['m'].render('Population', False, 'Black')
        self.slider1_rect = self.slider1_label.get_rect(center=UI.main_menu_positions['label_s1'])

        self.slider2_label = UI.fonts['m'].render('Food density %', False, 'Black')
        self.slider2_rect = self.slider2_label.get_rect(center=UI.main_menu_positions['label_s2'])

        self.sliders = {
            'Population': Slider(UI.main_menu_positions['slider1'], 250, init_val=20, min_val=0, max_val=250),
            'Food density': Slider(UI.main_menu_positions['slider2'], 250, init_val=20, min_val=1, max_val=100),
        }

        self.game_message = UI.fonts['l'].render('Press space to run', False, 'Black')
        self.game_message_rect = self.game_message.get_rect(center=UI.main_menu_positions['run'])

    def get_settings(self):
        population = self.sliders['Population'].get_value()
        food_density = self.sliders['Food density'].get_value()
        return population, food_density

    def run(self):
        self.screen.fill(self.bg)
        self.screen.blit(self.game_name, self.game_name_rect)
        self.screen.blit(self.duck_logo, self.duck_logo_rect)
        self.screen.blit(self.subtitle, self.subtitle_rect)
        self.screen.blit(self.slider1_label, self.slider1_rect)
        self.screen.blit(self.slider2_label, self.slider2_rect)
        self.screen.blit(self.game_message, self.game_message_rect)

        # Sliders
        mouse_pos = pygame.mouse.get_pos()
        mouse = pygame.mouse.get_pressed()

        for name, slider in self.sliders.items():
            grabbed = False
            if slider.dot.collidepoint(mouse_pos) or slider.line.collidepoint(mouse_pos):
                if mouse[0] and mouse:
                    grabbed = True

            if grabbed:
                slider.move_slider(mouse_pos)

            slider.draw(self.screen)


class SideMenu:

    def __init__(self, app):
        self.app = app
        self.screen = app.screen

        self.menu_surf = pygame.Surface((UI.side_menu_size, app.get_size()[1]))
        self.menu_surf.fill('White')

        self.time_text = UI.fonts['xl'].render(f'Time: {self.app.time}', False, (64, 64, 64))
        self.time_rect = self.time_text.get_rect(center=UI.side_menu_positions['time'])

        self.population_text = UI.fonts['xl'].render(f'Population: {len(self.app.ducks.sprites())}', False, (64, 64, 64))
        self.population_rect = self.population_text.get_rect(center=UI.side_menu_positions['Population'])

        self.init_population_text = UI.fonts['m'].render(f'Initial population: {self.app.init_pop}', False, (64, 64, 64))
        self.init_population_rect = self.init_population_text.get_rect(center=UI.side_menu_positions['Init population'])

        self.init_food_den_text = UI.fonts['m'].render(f'Initial food density: {self.app.init_food_den} %', False, (64, 64, 64))
        self.init_food_den_rect = self.init_food_den_text.get_rect(center=UI.side_menu_positions['Init food density'])

    def update(self):
        self.time_text = UI.fonts['xl'].render(f'Time: {self.app.time}', False, (64, 64, 64))
        self.population_text = UI.fonts['xl'].render(f'Population: {len(self.app.ducks.sprites())}', False, (64, 64, 64))

    def run(self):
        self.update()
        self.screen.blit(self.menu_surf, (0, 0))
        self.screen.blit(self.time_text, self.time_rect)
        self.screen.blit(self.population_text, self.population_rect)
        self.screen.blit(self.init_population_text, self.init_population_rect)
        self.screen.blit(self.init_food_den_text, self.init_food_den_rect)


class Button:

    def __init__(self, pos, image):
        self.image = image
        self.rect = self.image.get_rect(center=pos)
        self.pressed = False
        self.action = False  # False -> simulation is running, True --> simulation is paused

    def draw(self, screen):
        pos = pygame.mouse.get_pos()

        if self.rect.collidepoint(pos):
            if pygame.mouse.get_pressed()[0] == 1 and not self.pressed:
                self.pressed = True

        if pygame.mouse.get_pressed()[0] == 0 and self.pressed:
            self.pressed = False
            self.action = not self.action

        screen.blit(self.image, (self.rect.x, self.rect.y))
        return self.action


class Slider:

    def __init__(self, pos: tuple, size: int, init_val: int, min_val: int, max_val: int):
        self.pos = pos
        self.size = size
        self.min = min_val
        self.max = max_val
        self.slider_range = size
        self.init_val_pos = init_val/(self.max - self.min) * self.slider_range

        self.slider_left_pos = self.pos[0] - size // 2
        self.slider_right_pos = self.pos[0] + size // 2
        self.slider_top_pos = self.pos[1] + 1

        self.line = pygame.Rect(self.slider_left_pos, self.slider_top_pos, self.size, 5)
        self.dot = pygame.Rect(self.slider_left_pos + self.init_val_pos - 9, self.slider_top_pos - 9, 18, 18)

        # Labels
        self.min_label_mess = UI.fonts['m'].render(f'{self.min}', False, 'Black')
        self.max_label_mess = UI.fonts['m'].render(f'{self.max}', False, 'Black')
        self.dot_label_mess = UI.fonts['sm'].render(f'{init_val}', False, 'Black')

        self.min_label_rect = self.min_label_mess.get_rect(midright=(self.slider_left_pos - 10, self.slider_top_pos - 20))
        self.max_label_rect = self.max_label_mess.get_rect(midleft=(self.slider_right_pos + 10, self.slider_top_pos - 20))
        self.dot_label_rect = self.dot_label_mess.get_rect(center=(self.dot.centerx, self.slider_top_pos - 20))

    def move_slider(self, mouse_pos):
        pos = mouse_pos[0]
        if pos < self.slider_left_pos:
            pos = self.slider_left_pos
        if pos > self.slider_right_pos:
            pos = self.slider_right_pos
        self.dot.centerx = pos

        self.dot_label_mess = UI.fonts['sm'].render(f'{self.get_value()}', False, 'Black')
        self.dot_label_rect = self.dot_label_mess.get_rect(center=(self.dot.centerx, self.slider_top_pos - 20))

    def get_value(self):
        dot_val = self.dot.centerx - self.slider_left_pos
        return int((dot_val/self.slider_range) * (self.max - self.min) + self.min)

    def draw(self, screen):
        pygame.draw.rect(screen, 'Black', self.line)
        pygame.draw.rect(screen, 'Black', self.dot)

        screen.blit(self.min_label_mess, self.min_label_rect)
        screen.blit(self.max_label_mess, self.max_label_rect)
        screen.blit(self.dot_label_mess, self.dot_label_rect)

