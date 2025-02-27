import pygame
from math import sqrt
from sys import exit

class Vector2:
    def __init__(self, x: float, y: float):
        self.x = x
        self.y = y
        self.length = sqrt((x ** 2) + (y ** 2))

    def normalize(self):
        return Vector2(self.x / self.length, self.y / self.length) if self.length > 0 else Vector2(0, 0)
    
    def __iter__(self):
        yield self.x
        yield self.y
    
    def __mul__(self, num: float):
        return Vector2(self.x * num, self.y * num)
    
    def __add__(self, other):
        return Vector2(self.x + other.x, self.y + other.y)

    def __sub__(self, other):
        return Vector2(self.x - other.x, self.y - other.y)
    
    def __str__(self):
        return f"({self.x}, {self.y})"

    __rmul__ = __mul__

class GameObject:
    def __init__(self, sprite: str, position: tuple):
        self.sprite = sprite
        self.position = Vector2(position[0], position[1])
        self.surf = pygame.image.load(self.sprite)
        self.rect = self.surf.get_rect(topleft=tuple(self.position))
    
    def render(self, camera, screen):
        screen.blit(self.surf, (self.rect.x - camera.x, self.rect.y - camera.y))
    
    def scale(self, factor: tuple):
        self.surf = pygame.transform.scale(self.surf, (self.rect.width * factor[0], self.rect.height * factor[1]))
        self.rect.size = (self.surf.get_width(), self.surf.get_height())

    def size(self, size: tuple):
        self.surf = pygame.transform.scale(self.surf, size)
        self.rect.size = (self.surf.get_width(), self.surf.get_height())

class Building(GameObject):
    def __init__(self, sprite: str, position: tuple, max_health: int):
        super().__init__(sprite, position)
        self.max_health = max_health
        self.health = max_health

class Troop(GameObject):
    def __init__(self, sprite: str, position: tuple, max_health: int, speed: int, damage: int):
        super().__init__(sprite, position)
        self.max_health = max_health
        self.health = max_health
        self.speed = speed
        self.damage = damage
        self.velocity = Vector2(0, 0)
        self.target: Vector2 | None = None
    
    def stop(self):
        self.velocity = Vector2 (0, 0)

    def move(self):
        if self.target:
            self.goto(self.target)
            if self.speed >= (self.position - self.target).length >= -1 * self.speed:#self.position.x == self.target.x and self.position.y == self.target.y:
                self.target = None
                self.stop()

        self.position.x += self.velocity.x
        self.position.y += self.velocity.y
        self.rect.topleft = (self.position.x, self.position.y)

    def goto(self, position: Vector2):
        self.velocity = Vector2(position.x - self.position.x, position.y - self.position.y).normalize() * self.speed

    #def combat(self):


class Game:
    def __init__(self):
        self.game_objects: dict[str, list[GameObject]] = {}

def get_camera_position(camera: Vector2, world_size: tuple, screen_size: tuple) -> tuple:
    camera_x = max(0, min(camera.x, world_size[0] - screen_size[0]))
    camera_y = max(0, min(camera.y, world_size[1] - screen_size[1]))
    return Vector2(camera_x, camera_y)

def select_troop(mouse_pos: tuple, camera: Vector2, troops: list[Troop], selected_troop: Troop = None) -> Troop:
    cam_offset = Vector2(mouse_pos[0] + camera.x, mouse_pos[1] + camera.y)
    
    for troop in troops:
        if troop.rect.collidepoint(cam_offset.x, cam_offset.y):
            return troop  # Return the new selected troop
    
    return selected_troop

"""def select_building(mouse_pos: tuple, camera: Vector2, troops: list[Troop], selected_troop: Troop = None) -> Troop:
    cam_offset = Vector2(mouse_pos[0] + camera.x, mouse_pos[1] + camera.y)
    
    for troop in troops:
        if troop.rect.collidepoint(cam_offset.x, cam_offset.y):
            return troop  # Return the new selected troop
    
    return selected_troop"""

def main():
    # Initialize pygame
    pygame.init()
    window = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
    screen = pygame.display.set_mode((1920, 1080))
    GLOBAL_SCALE = (.25, .25)

    # Camera setup
    camera = Vector2(0, 0)
    camera_speed = 30

    # Load background
    background = GameObject('imgs/background_grid.png', (0, 0))
    background.size((3000, 2000))

    # Define background tiling positions
    background_tiles = [
        (0, 0), (3000, 0),
        (0, 2000), (3000, 2000)
    ]

    # Load game objects
    starship_grey = Troop('imgs/black_ship.png', (600, 450), 700, 2, int(200-250))
    starship_grey.scale(GLOBAL_SCALE)

    starship_red = Troop('imgs/red_ship.png', (600, 1000), 700, 2, int(70-80))
    starship_red.scale(GLOBAL_SCALE)

    command_center = Building('imgs/command_center.png', (100, 100), 2000)
    command_center.scale((.5, .5))

    barracks = Building('imgs/barracks.png', (450, 185), 1000)
    barracks.scale((.29, .29))

    starport = Building('imgs/starport.png', (150, 450), 750)
    starport.scale((.65, .65))

    depot = Building('imgs/vehicle_depot.png', (445, 450), 1250)
    depot.scale((.3, .3))

    red_troop = Troop('imgs/red_soildger.png', (1200, 700), 150, 10, int(40-50))
    red_troop.scale(GLOBAL_SCALE)

    blue_troop = Troop('imgs/blue_soildger.png', (300, 200), 150, 10, int(40-50))
    blue_troop.scale(GLOBAL_SCALE)

    blue_tank = Troop('imgs/blue_tank.png', (1000, 400), 500, 10, int(150-180))
    blue_tank.scale((.2, .2))

    selected_troop = None
    troops = [red_troop, blue_troop, starship_grey, starship_red, blue_tank]
    buildings = [command_center, barracks, starport, depot]

    # Game loop
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()

            mouse_pos = pygame.mouse.get_pos()
            world_size = (background.rect.width * 2, background.rect.height * 2)
            screen_size = screen.get_size()

            

            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    selected_troop = select_troop(pygame.mouse.get_pos(), camera, troops, selected_troop)

                elif event.button == 3:
                    if selected_troop == red_troop:
                        cam_pos = get_camera_position(camera, world_size, screen_size)
                        red_troop.target = Vector2(mouse_pos[0], mouse_pos[1]) + cam_pos

                    elif selected_troop == blue_troop:
                        cam_pos = get_camera_position(camera, world_size, screen_size)
                        blue_troop.target = Vector2(mouse_pos[0], mouse_pos[1]) + cam_pos

                    elif selected_troop == blue_tank:
                        cam_pos = get_camera_position(camera, world_size, screen_size)
                        blue_tank.target = Vector2(mouse_pos[0], mouse_pos[1]) + cam_pos

                    elif selected_troop == starship_red:
                        cam_pos = get_camera_position(camera, world_size, screen_size)
                        starship_red.target = Vector2(mouse_pos[0], mouse_pos[1]) + cam_pos

                    elif selected_troop == starship_grey:
                        cam_pos = get_camera_position(camera, world_size, screen_size)
                        starship_grey.target = Vector2(mouse_pos[0], mouse_pos[1]) + cam_pos

            # Camera movement
            keys = pygame.key.get_pressed()
            if keys[pygame.K_w]:  # Move up
                camera.y = max(camera.y - camera_speed, 0)
            if keys[pygame.K_s]:  # Move down
                camera.y = min(camera.y + camera_speed, (background.rect.height * 2) - screen.get_height())
            if keys[pygame.K_a]:  # Move left
                camera.x = max(camera.x - camera_speed, 0)
            if keys[pygame.K_d]:  # Move right
                camera.x = min(camera.x + camera_speed, (background.rect.width * 2) - screen.get_width())
            if keys[pygame.K_u]:
                selected_troop = None
            if keys[pygame.K_ESCAPE]:
                pygame.quit()
                exit()


        # Render background tiles
        for pos in background_tiles:
            screen.blit(background.surf, (pos[0] - camera.x, pos[1] - camera.y))

        red_troop.move()
        blue_troop.move()
        starship_grey.move()
        starship_red.move()
        blue_tank.move()

        # Render objects
        command_center.render(camera, screen)
        barracks.render(camera, screen)
        starport.render(camera, screen)
        depot.render(camera, screen)
        red_troop.render(camera, screen)
        blue_troop.render(camera, screen)
        blue_tank.render(camera, screen)
        starship_grey.render(camera, screen)
        starship_red.render(camera, screen)
        
        resized_screen = pygame.transform.scale(screen, (window.get_width(), window.get_height()))
        window.blit(resized_screen, (0, 0))

        # Update the display
        pygame.display.update()

if __name__ == "__main__":
    main()