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
    bubble_bubble_dist = 10
    bubble_border_dist = 100
    max_higscore_entries = 5
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
        Media.default_cursor = pygame.image.load(os.path.join(Settings.images_path, 'cursor1.png')).convert_alpha()
        Media.pop_cursor = pygame.image.load(os.path.join(Settings.images_path, 'cursor2.png')).convert_alpha()
        Media.grayfilter = pygame.image.load(os.path.join(Settings.images_path, 'grayfilter.png')).convert_alpha()


class Background(pygame.sprite.Sprite):
    """
    Background for the game
    """
    def __init__(self, image):
        super().__init__()
        self.image = image
        self.rect = self.image.get_rect()
        self.image = pygame.transform.scale(self.image, Settings.get_dim())


class Cursor(pygame.sprite.Sprite):
    """
    Custom Cursor
    """
    def __init__(self, game,):
        super().__init__()
        self.game = game
        self.image = Media.default_cursor
        self.rect = self.image.get_rect()
        pygame.mouse.set_visible(False)
        self.update()
    
    def update(self):
        self.rect.left, self.rect.top = pygame.mouse.get_pos()
            
    def get_pos(self):
        return (self.rect.left, self.rect.top)
        
    def set_pop_cursor(self):
            self.image = Media.pop_cursor
        
    def set_default_cursor(self):
            self.image = Media.default_cursor


class Bubble(pygame.sprite.Sprite):
    """
    Bubble sprite
    """
    def __init__(self, game):
        super().__init__()
        self.game = game
        self.image_base = Media.bubble_sprite
        self.x = random.randint(Settings.bubble_border_dist, Settings.width - Settings.bubble_border_dist)
        self.y = random.randint(Settings.bubble_border_dist, Settings.height - Settings.bubble_border_dist)
        self.growth_rate = random.randint(1,4)
        self.radius = 5
        self.update()

    def update(self):
        self.radius += self.growth_rate
        self.image = pygame.transform.scale(self.image_base, [self.radius*2, self.radius*2])
        self.rect = self.image.get_rect()
        self.rect.centerx = self.x
        self.rect.centery = self.y
     
    def get_value(self):
        return self.radius
        
    def point_is_inside(self, point):
        dist = math.sqrt( (self.x - point[0])**2 + (self.y - point[1])**2 )
        return dist <= self.radius

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
    def __init__(self, fontPath, fontSize, fontColor, left, top):
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
        
    def set_pos(self, left, top):
        self.rect.top = top
        self.rect.left = left
        
    def center(self):
        w, h = Settings.get_dim()
        self.set_pos((w - self.rect.width) // 2, (h - self.rect.height) // 2)
        
    def center_x(self):
        self.set_left((Settings.width - self.rect.width) // 2 )
        
    def center_y(self):
        self.set_top((Settings.height - self.rect.height) // 2 )
        
    def set_left(self, left):
        self.rect.left = left
    
    def set_top(self, top):
        self.rect.top = top
        
    def get_rect(self):
        return self.rect


class Scene(object):
    def __init__(self, screen, clock, main):
        self.screen = screen
        self.main = main
        self.clock = clock
        self.done = False
        self.all_sprite_groups = []
        
    def run(self):
        self.done = False
        while not self.done:
            self.clock.tick(Settings.fps)
            self.update()
            self.handle_events()
            self.draw()
        
    def handle_events(self):
        pass
        
    def update(self):
        for sg in self.all_sprite_groups:
            sg.update()
        
    def draw(self):
        for sg in self.all_sprite_groups:
            sg.draw(self.screen)
        pygame.display.flip()
        
    def end(self):
        self.done = True
        self.main.end()


class Main_Game(Scene):
    def __init__(self, screen, clock, main):
        super().__init__(screen, clock, main)
        self.last_bubble_time = pygame.time.get_ticks()
        self.time_units = Settings.base_time_units
        self.score = 0
        
        #sprites
        self.background = pygame.sprite.GroupSingle(Background(Media.background))
        self.all_bubbles = pygame.sprite.Group()
        self.cursor = pygame.sprite.GroupSingle(Cursor(self))
        
        #texts
        self.all_texts = pygame.sprite.Group()
        self.texts_by_name = {
            "score" : Text(Settings.font, 24, Settings.font_color, 5, 5),
            #"debug" : Text(Settings.font, 24, Settings.font_color, 5, 50),
        }
        for t in self.texts_by_name:
            self.all_texts.add(self.texts_by_name[t])
            
        self.all_sprite_groups = [
            self.background,
            self.all_bubbles,
            self.all_texts,
            self.cursor
        ]

    def run(self):
        while not self.done:
            self.clock.tick(Settings.fps)
            self.handle_events()
            self.add_bubble()
            if self.bubble_wall_collide():
                self.done = True
            if self.bubble_bubble_collide():
                self.done = True
            self.handle_cursor_icon()
            self.update()
            self.draw()

    def handle_events(self):
        for event in pygame.event.get():
            #Quit on window closed
            if event.type == pygame.QUIT:
                self.end()

            if event.type == pygame.KEYUP:
                #"Quit on ESC
                if event.key == pygame.K_ESCAPE:
                    self.end()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    self.pop_bubble()
                elif event.button == 3:
                    self.main.pause()

    def increase_score(self, value):
        """
        Increases the score
        """
        self.score += value
        self.texts_by_name["score"].set_text(f"{self.score} points")

    def add_bubble(self):
        """
        Adds a bubble with a minimum distance to the Border and other Bubbles
        """
        if (len(self.all_bubbles) <= Settings.nof_bubbles and 
        pygame.time.get_ticks() > self.last_bubble_time + self.time_units):
            def new_bubble():
                new_b = Bubble(self)
                for b in self.all_bubbles:
                    if new_b.dist_to_bubble(b) <= new_b.radius + b.radius + Settings.bubble_bubble_dist:
                        return False
                return new_b
            
            new_b = new_bubble()
            while not new_b: new_b = new_bubble()

            self.all_bubbles.add(new_b)
            self.last_bubble_time = pygame.time.get_ticks()

    def pop_bubble(self):
        """
        pops the bubble in contact with the cursor
        """
        i = self.cursor_bubble_collide()
        if i != -1:
            bubble = self.all_bubbles.sprites()[i]
            bubble.kill()
            self.increase_score(bubble.get_value())

    def bubble_wall_collide(self):
        for b in self.all_bubbles:
            if b.coll_with_wall():
                return True
        return False

    def bubble_bubble_collide(self):
        for i1, b1 in enumerate(self.all_bubbles):
            for i2, b2 in enumerate(self.all_bubbles):
                if b1.coll_with_bubble(b2) and i2 > i1:
                    return True
        return False

    def screenshot(self):
        self.cursor.sprite.kill()
        self.draw()
        self.cursor.sprite = Cursor(self)
        return self.screen.copy()
    
    def cursor_bubble_collide(self):
        pos = self.cursor.sprite.get_pos()
        for i, bubble in enumerate(self.all_bubbles.sprites()):
            if bubble.point_is_inside(pos):
                return i
        return -1

    def handle_cursor_icon(self):
        if self.cursor_bubble_collide() != -1:
            self.cursor.sprite.set_pop_cursor()
        else:
            self.cursor.sprite.set_default_cursor()

    def get_score(self):
        return self.score


class Pause(Scene):
    def __init__(self, screen, clock, main):
        super().__init__(screen, clock, main)
        self.background = pygame.sprite.GroupSingle(Background(self.main.screenshot()))
        self.grayfilter = pygame.sprite.GroupSingle(Background(Media.grayfilter))
        self.cursor = pygame.sprite.GroupSingle(Cursor(self))
            
        self.all_sprite_groups = [
            self.background,
            self.grayfilter,
            self.cursor
        ]
        
    def run(self):
        self.done = False
        self.background.sprite = Background(self.main.screenshot())
        while not self.done:
            self.clock.tick(Settings.fps)
            self.update()
            self.handle_events()
            self.draw()
            
    def handle_events(self):
        for event in pygame.event.get():
            #Quit on window closed
            if event.type == pygame.QUIT:
                self.end()

            if event.type == pygame.KEYUP:
                #"Quit on ESC
                if event.key == pygame.K_ESCAPE:
                    self.end()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 3:
                    self.done = True
    

class Game_Over(Scene):
    def __init__(self, screen, clock, main):
        super().__init__(screen, clock, main)
        #sprites and text
        self.main_text = pygame.sprite.GroupSingle(Text(Settings.font, 36, Settings.font_color, 5, 5))
        self.main_text.sprite.set_text("Game Over!")
        self.main_text.sprite.center()
        
        self.highscore_text = pygame.sprite.GroupSingle(Text(Settings.font, 24, Settings.font_color, 5, 5))
        
        self.restart_button = pygame.sprite.GroupSingle(Text(Settings.font, 24, Settings.font_color, 5, 5))
        self.restart_button.sprite.set_text("Try Again")
        self.restart_button.sprite.center_x()
        self.restart_button.sprite.get_rect().bottom = 0
        
        self.cursor = pygame.sprite.GroupSingle(Cursor(self))
        self.background = pygame.sprite.GroupSingle(Background(main.screenshot()))
        
        self.all_sprite_groups = [
            self.background,
            self.main_text,
            self.highscore_text,
            self.restart_button,
            self.cursor
        ]
        
    def run(self):
        self.done = False
        self.background.sprite = Background(self.main.screenshot())
        self.highscore_text.sprite.set_text("Highscores: " + ", ".join(map(str, self.main.get_highscores())))
        self.highscore_text.sprite.center_x()
        self.highscore_text.sprite.set_top(self.main_text.sprite.get_rect().bottom)
        while not self.done:
            self.clock.tick(Settings.fps)
            self.update()
            self.handle_events()
            self.draw()
            
    def handle_events(self):
        for event in pygame.event.get():
            #Quit on window closed
            if event.type == pygame.QUIT:
                self.end()

            if event.type == pygame.KEYUP:
                #"Quit on ESC
                if event.key == pygame.K_ESCAPE:
                    self.end()


class Game_Controller(object):
    """
    Main game object
    """
    def __init__(self):
        self.screen = pygame.display.set_mode(Settings.get_dim())
        self.clock = pygame.time.Clock()
        Media.load_media()
        pygame.display.set_caption(Settings.title)
        self.main_game_scene = Main_Game(self.screen, self.clock, self)
        self.game_over_scene = Game_Over(self.screen, self.clock, self)
        self.pause_scene = Pause(self.screen, self.clock, self)
        self.done = False

    def run(self):
        """
        Main game loop
        """
        while not self.done:
            self.main_game_scene = Main_Game(self.screen, self.clock, self)
            self.main_game_scene.run()
            if not self.done: 
                self.save_highscores()
                self.game_over_scene.run()
            
    def pause(self):
        self.pause_scene.run()
            
    def end(self):
        self.done = True
       
    def screenshot(self):
        return self.main_game_scene.screenshot()
        
    def save_highscores(self):
        highscores = self.get_highscores() + [self.get_score()]
        highscores = sorted(highscores,reverse=True)[:Settings.max_higscore_entries]
        score_file = open(os.path.join(Settings.file_path, "score.txt"), "w")
        score_file.write("\n".join(map(str,highscores)))
        
    def get_score(self):
        return self.main_game_scene.get_score()
        
    def get_highscores(self):
        score_file = open(os.path.join(Settings.file_path, "score.txt"), "r")
        highscores = sorted(map(int, score_file.readlines()),reverse=True)[:Settings.max_higscore_entries]
        return highscores
    

if __name__ == '__main__':
    pygame.init()
    game = Game_Controller()
    game.run()
  
    pygame.quit()