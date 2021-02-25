import pygame
import os
import random
import math

class Settings(object):
    """
    Settings for the game
    the entire class is static
    """
    width = 700
    height = 600
    fps = 60
    title = "Bubbles"
    font = pygame.font.match_font("RockwellExtra")
    font_color = [255,255,255]
    file_path = os.path.dirname(os.path.abspath(__file__))
    images_path = os.path.join(file_path, "assets", "images")
    sounds_path = os.path.join(file_path, "assets", "sounds")
    nof_bubbles = width * height // 50000
    min_bubble_dist = 100
    #time values in ms
    base_time_units = 1000


    @staticmethod
    def get_dim():
        """
        returns a tuple of the window width and height
        """
        return (Settings.width, Settings.height)

    @staticmethod
    def get_border_rect():
        return pygame.rect.Rect(0, 0, Settings.width, Settings.height)


class Media:
    @staticmethod
    def load_media():
        Media.bubble_sprite = pygame.image.load(os.path.join(Settings.images_path, "bubble.png")).convert_alpha()
        Media.background = pygame.image.load(os.path.join(Settings.images_path, 'background.png')).convert()


class Background(pygame.sprite.Sprite):
    """
    Background for the game
    """
    def __init__(self):
        super().__init__()
        self.image = Media.background
        self.rect = self.image.get_rect()
        self.image = pygame.transform.scale(self.image, Settings.get_dim())

    def draw(self, screen):
        screen.blit(self.image, self.rect)


class Bubble(pygame.sprite.Sprite):
    """
    Bubble sprite
    """
    def __init__(self, game):
        super().__init__()
        self.game = game
        self.x = random.randint(Settings.min_bubble_dist, Settings.width - Settings.min_bubble_dist)
        self.y = random.randint(Settings.min_bubble_dist, Settings.height - Settings.min_bubble_dist)
        self.growth_rate = random.randint(1,4)
        self.radius = 5
        self.update()

    def update(self):
        self.radius += self.growth_rate
        self.image = Media.bubble_sprite
        self.image = pygame.transform.scale(self.image, [self.radius*2, self.radius*2])
        self.rect = self.image.get_rect()
        self.rect.centerx = self.x
        self.rect.centery = self.y
     
    def point_is_inside(self, point):
        return math.sqrt( (self.x - point[0])**2 + (self.y - point[1])**2 ) <= self.radius

    def get_value(self):
        return self.radius

    def coll_with_wall(self):
        return not Settings.get_border_rect().contains(self.rect)

    def dist_to_bubble(self, other_bubble):
        return math.sqrt( (self.x - other_bubble.x)**2 + (self.y - other_bubble.y)**2 )

    def coll_with_bubble(self, other_bubble):
        return math.sqrt( (self.x - other_bubble.x)**2 + (self.y - other_bubble.y)**2 ) <= (self.radius + other_bubble.radius)


class Text(pygame.sprite.Sprite):
    """
    A pygame.sprite.Sprite child class used to display text
    """
    def __init__(self, fontPath, fontSize, fontColor, top, left):
        super().__init__()
        self.font = pygame.font.Font(fontPath, fontSize)
        self.font_color = fontColor
        self.str = ""
        self.image = self.font.render(self.str, True, self.font_color)
        self.rect = self.image.get_rect()
        self.rect.top = top
        self.rect.left = left

    def set_text(self, text):
        """
        sets and renders the string that this object will display
        """
        self.str = text
        self.image = self.font.render(self.str, True, self.font_color)
        self.rect.width = self.image.get_width()
        self.rect.height = self.image.get_height()


class Game(object):
    """
    Main game object
    """
    def __init__(self):
        self.screen = pygame.display.set_mode(Settings.get_dim())
        Media.load_media()
        self.clock = pygame.time.Clock()
        self.done = False
        pygame.display.set_caption(Settings.title)

        #game variables
        self.last_bubble_time = pygame.time.get_ticks()
        self.time_units = Settings.base_time_units
        self.score = 0

        #sprites
        self.background = Background()
        self.all_bubbles = pygame.sprite.Group()

        #texts
        self.all_texts = pygame.sprite.Group()
        self.texts_by_name = {
            "score" : Text(Settings.font, 24, Settings.font_color, 5, 5),
            #"debug" : Text(Settings.font, 24, Settings.font_color, 5, 50),
        }
        for t in self.texts_by_name:
            self.all_texts.add(self.texts_by_name[t])

    def run(self):
        """
        Main game loop
        """
        while not self.done:
            self.clock.tick(Settings.fps)
            self.handle_events()
            self.add_bubble()
            if self.bubble_wall_collide():
                self.done = True
            if self.bubble_bubble_collide():
                self.done = True
            self.update()
            self.draw()
    
    def handle_events(self):
        for event in pygame.event.get():
            #Quit on window closed
            if event.type == pygame.QUIT:
                self.done = True

            if event.type == pygame.KEYUP:
                #"Quit on ESC
                if event.key == pygame.K_ESCAPE:
                    self.done = True 
            if event.type == pygame.MOUSEBUTTONDOWN:
                self.pop_bubble_at(pygame.mouse.get_pos())

    def update(self):
            self.all_bubbles.update()

    def draw(self):
            self.background.draw(self.screen)
            self.all_bubbles.draw(self.screen)
            self.all_texts.draw(self.screen)
            pygame.display.flip()

    def increase_score(self, value):
        """
        Increases the score
        """
        self.score += value
        self.texts_by_name["score"].set_text(f"{self.score} points")

    def add_bubble(self):
        if (len(self.all_bubbles) <= Settings.nof_bubbles and 
        pygame.time.get_ticks() > self.last_bubble_time + self.time_units):
            def new_bubble():
                new_b = Bubble(self)
                for b in self.all_bubbles:
                    if new_b.dist_to_bubble(b) <= new_b.radius + b.radius + Settings.min_bubble_dist:
                        return False
                return new_b
            
            new_b = new_bubble()
            while not new_b: new_b = new_bubble()

            self.all_bubbles.add(new_b)
            self.last_bubble_time = pygame.time.get_ticks()

    def pop_bubble_at(self, pos):
        for b in self.all_bubbles:
            if b.point_is_inside(pos):
                b.kill()
                self.increase_score(b.get_value())

    def bubble_wall_collide(self):
        for b in self.all_bubbles:
            if b.coll_with_wall():
                return True

    def bubble_bubble_collide(self):
        for i1, b1 in enumerate(self.all_bubbles):
            for i2, b2 in enumerate(self.all_bubbles):
                if b1.coll_with_bubble(b2) and i2 > i1:
                    return True


if __name__ == '__main__':
    pygame.init()
    game = Game()
    game.run()
  
    pygame.quit()