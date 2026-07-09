import pygame
import random
import sys
import os
import math

# ============ CONSTANTS ============
CELL_SIZE = 80
GRID_COLS = 11
GRID_ROWS = 5
HOUSE_COL = 0
SPAWN_COL = GRID_COLS - 1
STATUS_H = 60
CARD_H = 80
GRID_W = GRID_COLS * CELL_SIZE
GRID_H = GRID_ROWS * CELL_SIZE
SCREEN_W = GRID_W
SCREEN_H = STATUS_H + GRID_H + CARD_H
MAX_DT = 1.0 / 30.0
CARD_SHAKE_DURATION = 0.2
CARD_SHAKE_AMPLITUDE = 4

STATE_MENU = "menu"
STATE_DIFFICULTY_SELECT = "difficulty_select"
STATE_PLAYING = "playing"
STATE_PAUSED = "paused"
STATE_WIN = "win"
STATE_LOSE = "lose"
ASSET_DIR = os.path.join(os.path.dirname(__file__), "assets")
ASSET_FILES = {
    "sunflower": "sunflower_cut.png",
    "peashooter": "peashooter_right_cut.png",
    "wallnut": "wallnut_cut.png",
    "cherry_bomb": "cherry_bomb_cut.png",
    "cherry_bomb_warn": "cherry_bomb_warn.png",
    "explosion": "explosion.png",
    "zombie": "zombie_cut.png",
    "cone_accessory": "cone_accessory.png",
    "bucket_accessory": "bucket_accessory.png",
    "shovel": "shovel_cut.png",
    "sun": "sun_cut.png",
    "lawn_checker": "lawn_checker_mild.png",
}
FLIPPED_ASSETS = {"wallnut"}

# Colors
BG_COLOR = (55, 65, 55)
GRID_A = (70, 95, 65)
GRID_B = (80, 105, 75)
GRID_LINE = (55, 75, 50)
HOUSE_COLOR = (105, 105, 105)
SPAWN_COLOR = (120, 80, 45)
STATUS_BG = (30, 30, 30)
CARD_BG = (40, 35, 30)
SUNFLOWER_COLOR = (255, 230, 40)
PEASHOOTER_COLOR = (70, 210, 55)
WALLNUT_COLOR = (165, 115, 55)
CHERRY_BOMB_COLOR = (230, 45, 35)
ZOMBIE_COLOR = (145, 130, 110)
ZOMBIE_EYE = (220, 40, 40)
PEA_COLOR = (50, 230, 50)
SUN_COLOR = (255, 245, 60)
TEXT_COLOR = (255, 255, 255)
SHADOW_COLOR = (0, 0, 0)
WIN_BG = (0, 180, 0, 120)
LOSE_BG = (200, 0, 0, 120)
WIN_TEXT = (80, 255, 80)
LOSE_TEXT = (255, 60, 60)
SELECT_BORDER = (255, 255, 200)
HP_BAR_BG = (50, 50, 50)
HP_BAR_GREEN = (80, 200, 60)
HP_BAR_RED = (210, 60, 60)
SHOVEL_BG = (75, 75, 75)
SHOVEL_ACTIVE_BG = (120, 120, 120)
SHOVEL_METAL = (210, 210, 210)
SHOVEL_HANDLE = (120, 75, 35)

# Plant costs
COST_SUNFLOWER = 50
COST_PEASHOOTER = 100
COST_WALLNUT = 50
COST_CHERRY_BOMB = 150

# Plant HP
HP_SUNFLOWER = 100
HP_PEASHOOTER = 100
HP_WALLNUT = 400
HP_CHERRY_BOMB = 9999

# Plant timings
SUNFLOWER_INTERVAL = 10.0
PEASHOOTER_INTERVAL = 1.5
COOLDOWN_SUNFLOWER = 7.5
COOLDOWN_PEASHOOTER = 7.5
COOLDOWN_WALLNUT = 30.0
COOLDOWN_CHERRY_BOMB = 50.0
CHERRY_BOMB_IDLE_TIME = 1.2
CHERRY_BOMB_WARNING_TIME = 0.3
CHERRY_BOMB_EXPLODING_TIME = 0.5
CHERRY_BOMB_RADIUS_CELLS = 1

# Pea
PEA_DAMAGE = 20
PEA_SPEED = 300.0

# Sun
SUN_INITIAL = 50
SUN_VALUE = 25
SUN_LIFETIME = 8.0
SKY_SUN_INTERVAL = 8.0
SUN_FALL_SPEED = 45.0
SUN_CLICK_RADIUS = 30
SUN_MAX_Y = STATUS_H + GRID_H - SUN_CLICK_RADIUS

# Zombie
ZOMBIE_HP = 100
ZOMBIE_CONEHEAD_ARMOR = 180
ZOMBIE_BUCKETHEAD_ARMOR = 550
ZOMBIE_ATTACK_CD = 1.0
ZOMBIE_ATTACK_DMG = 20
ZOMBIE_WIDTH = 46
ZOMBIE_HEIGHT = 62
ZOMBIE_IMAGE_MAX_W = 58
ZOMBIE_IMAGE_MAX_H = CELL_SIZE - 4
ACCESSORY_ASSET_KEYS = {"cone_accessory", "bucket_accessory"}

# Wave system
TOTAL_WAVES = 5
WAVE_COOLDOWN = 20.0
SPAWN_INTERVAL_W1 = 8.0
SPAWN_INTERVAL_W5 = 3.0
SPEED_W1 = 20.0
SPEED_W5 = 35.0
ZOMBIES_PER_WAVE_BASE = 3
ZOMBIES_PER_WAVE_INC = 2
ZOMBIE_SPAWN_TABLE = {
    1: (("normal", None, 1.0),),
    2: (("normal", None, 0.75), ("normal", "cone", 0.25)),
    3: (("normal", None, 0.55), ("normal", "cone", 0.35), ("normal", "bucket", 0.10)),
    4: (("normal", None, 0.40), ("normal", "cone", 0.40), ("normal", "bucket", 0.20)),
    5: (("normal", None, 0.30), ("normal", "cone", 0.40), ("normal", "bucket", 0.30)),
}
ZOMBIE_WAVE_GUARANTEED_ACCESSORIES = {
    2: ("cone",),
    3: ("cone", "bucket"),
    4: ("cone", "bucket"),
    5: ("cone", "bucket"),
}

DIFFICULTY_CONFIG = {
    "easy": {
        "name": "Easy",
        "zombie_count_multiplier": 0.75,
        "wave_cooldown_multiplier": 1.25,
        "zombie_hp_multiplier": 0.8,
    },
    "normal": {
        "name": "Normal",
        "zombie_count_multiplier": 1.0,
        "wave_cooldown_multiplier": 1.0,
        "zombie_hp_multiplier": 1.0,
    },
    "hard": {
        "name": "Hard",
        "zombie_count_multiplier": 1.35,
        "wave_cooldown_multiplier": 0.7,
        "zombie_hp_multiplier": 1.5,
    },
}

# ============ ENTITIES ============

class Plant:
    def __init__(self, row, col, hp, cost, color, letter, asset_key=None):
        self.row = row
        self.col = col
        self.hp = hp
        self.max_hp = hp
        self.cost = cost
        self.color = color
        self.letter = letter
        self.asset_key = asset_key

    def take_damage(self, amount):
        self.hp -= amount
        return self.hp <= 0

    def update(self, dt, game):
        pass

    def draw(self, screen, image=None):
        x = self.col * CELL_SIZE
        y = STATUS_H + self.row * CELL_SIZE
        if image is not None:
            ix = x + (CELL_SIZE - image.get_width()) // 2
            iy = y + (CELL_SIZE - image.get_height()) // 2
            screen.blit(image, (ix, iy))
        else:
            pad = 5
            rect = pygame.Rect(x + pad, y + pad, CELL_SIZE - pad*2, CELL_SIZE - pad*2)
            pygame.draw.rect(screen, self.color, rect, border_radius=10)
            pygame.draw.rect(screen, (0, 0, 0, 40), rect, 2, border_radius=10)
            font = pygame.font.Font(None, 38)
            text = font.render(self.letter, True, (0, 0, 0))
            tx = x + (CELL_SIZE - text.get_width()) // 2
            ty = y + (CELL_SIZE - text.get_height()) // 2 - 6
            screen.blit(text, (tx, ty))
        if self.hp < self.max_hp:
            bw = CELL_SIZE - 14; bh = 6
            bx = x + 7; by = y + CELL_SIZE - 14
            pygame.draw.rect(screen, HP_BAR_BG, (bx, by, bw, bh))
            r = max(0, self.hp / self.max_hp)
            hc = HP_BAR_GREEN if r > 0.3 else HP_BAR_RED
            pygame.draw.rect(screen, hc, (bx, by, int(bw * r), bh))

class Sunflower(Plant):
    def __init__(self, row, col):
        super().__init__(row, col, HP_SUNFLOWER, COST_SUNFLOWER, SUNFLOWER_COLOR, "S", "sunflower")
        self.sun_timer = 0.0
    def update(self, dt, game):
        self.sun_timer += dt
        if self.sun_timer >= SUNFLOWER_INTERVAL:
            self.sun_timer = 0.0
            sx = self.col * CELL_SIZE + CELL_SIZE//2 + random.randint(-15, 15)
            sy = STATUS_H + self.row * CELL_SIZE + CELL_SIZE//2 + random.randint(-15, 15)
            game.add_sun(sx, sy, SUN_VALUE)

class Peashooter(Plant):
    def __init__(self, row, col):
        super().__init__(row, col, HP_PEASHOOTER, COST_PEASHOOTER, PEASHOOTER_COLOR, "P", "peashooter")
        self.shoot_timer = 0.0
    def update(self, dt, game):
        self.shoot_timer += dt
        if self.shoot_timer >= PEASHOOTER_INTERVAL:
            self.shoot_timer = 0.0
            if game.has_zombie_ahead(self.row, (self.col + 1) * CELL_SIZE):
                px = (self.col + 1) * CELL_SIZE + 4
                game.add_pea(self.row, px)

class Wallnut(Plant):
    def __init__(self, row, col):
        super().__init__(row, col, HP_WALLNUT, COST_WALLNUT, WALLNUT_COLOR, "W", "wallnut")

class CherryBomb(Plant):
    def __init__(self, row, col):
        super().__init__(row, col, HP_CHERRY_BOMB, COST_CHERRY_BOMB, CHERRY_BOMB_COLOR, "C", "cherry_bomb")
        self.state = "idle"
        self.state_timer = CHERRY_BOMB_IDLE_TIME
        self._damage_dealt = False

    def update(self, dt, game):
        self.state_timer -= dt
        while self.state_timer <= 0.0:
            overflow = -self.state_timer
            if self.state == "idle":
                self.state = "warning"
                self.state_timer = CHERRY_BOMB_WARNING_TIME - overflow
            elif self.state == "warning":
                self._enter_exploding(game)
                self.state_timer = CHERRY_BOMB_EXPLODING_TIME - overflow
            elif self.state == "exploding":
                game.remove_plant(self.row, self.col)
                return
            else:
                return

    def take_damage(self, amount):
        return False

    def _enter_exploding(self, game):
        self.state = "exploding"
        if self._damage_dealt:
            return
        self._damage_dealt = True
        game.shake_time = 0.2
        game.shake_intensity = 5
        min_row = max(0, self.row - CHERRY_BOMB_RADIUS_CELLS)
        max_row = min(GRID_ROWS - 1, self.row + CHERRY_BOMB_RADIUS_CELLS)
        min_col = max(0, self.col - CHERRY_BOMB_RADIUS_CELLS)
        max_col = min(GRID_COLS - 1, self.col + CHERRY_BOMB_RADIUS_CELLS)
        for zombie in game.zombies:
            if zombie.hp <= 0 or not (min_row <= zombie.row <= max_row):
                continue
            zombie_center_col = int((zombie.x + zombie.width / 2) // CELL_SIZE)
            if min_col <= zombie_center_col <= max_col:
                zombie.accessory_hp = 0
                zombie.accessory_key = None
                zombie.accessory_asset_key = None
                zombie.hp = 0

    def draw(self, screen, images=None):
        center = (
            self.col * CELL_SIZE + CELL_SIZE // 2,
            STATUS_H + self.row * CELL_SIZE + CELL_SIZE // 2,
        )
        if self.state == "exploding":
            image = None if images is None else images.get("explosion", {}).get("explosion")
            if image is not None:
                screen.blit(image, (center[0] - image.get_width() // 2, center[1] - image.get_height() // 2))
            else:
                rect = pygame.Rect(0, 0, CELL_SIZE * 3, CELL_SIZE * 3)
                rect.center = center
                pygame.draw.ellipse(screen, (255, 120, 20), rect)
                pygame.draw.ellipse(screen, (255, 235, 80), rect.inflate(-60, -60))
            return
        image_key = "cherry_bomb_warn" if self.state == "warning" else "cherry_bomb"
        image = None if images is None else images.get(image_key, {}).get("grid")
        super().draw(screen, image)

PLANT_REGISTRY = {
    "sunflower": {
        "name": "Sunflower",
        "cost": COST_SUNFLOWER,
        "color": SUNFLOWER_COLOR,
        "letter": "S",
        "asset_key": "sunflower",
        "class": Sunflower,
        "cooldown": COOLDOWN_SUNFLOWER,
        "initial_cooldown": 0.0,
    },
    "peashooter": {
        "name": "Peashooter",
        "cost": COST_PEASHOOTER,
        "color": PEASHOOTER_COLOR,
        "letter": "P",
        "asset_key": "peashooter",
        "class": Peashooter,
        "cooldown": COOLDOWN_PEASHOOTER,
        "initial_cooldown": 0.0,
    },
    "wallnut": {
        "name": "Wallnut",
        "cost": COST_WALLNUT,
        "color": WALLNUT_COLOR,
        "letter": "W",
        "asset_key": "wallnut",
        "class": Wallnut,
        "cooldown": COOLDOWN_WALLNUT,
        "initial_cooldown": 0.0,
    },
    "cherry_bomb": {
        "name": "Cherry Bomb",
        "cost": COST_CHERRY_BOMB,
        "hp": HP_CHERRY_BOMB,
        "color": CHERRY_BOMB_COLOR,
        "letter": "C",
        "asset_key": "cherry_bomb",
        "class": CherryBomb,
        "recharge": COOLDOWN_CHERRY_BOMB,
        "initial_cooldown": 0.0,
        "is_consumable": True,
    },
}

# --------------------

class Zombie:
    def __init__(self, row, speed, hp=ZOMBIE_HP, width=ZOMBIE_WIDTH, height=ZOMBIE_HEIGHT, asset_key="zombie", accessory_key=None, accessory_hp=0, accessory_asset_key=None):
        self.row = row
        self.width = width
        self.height = height
        self.asset_key = asset_key
        self.accessory_key = accessory_key
        self.accessory_asset_key = accessory_asset_key
        self.x = float(GRID_W) - self.width
        self.hp = hp
        self.max_hp = hp
        self.accessory_hp = accessory_hp
        self.max_accessory_hp = accessory_hp
        self.max_total_hp = hp + accessory_hp
        self.speed = speed
        self.attack_timer = 0.0
    def take_damage(self, amount):
        if self.accessory_hp > 0:
            self.accessory_hp = max(0, self.accessory_hp - amount)
            if self.accessory_hp <= 0:
                self.accessory_key = None
                self.accessory_asset_key = None
            return self.hp <= 0
        self.hp -= amount
        return self.hp <= 0
    def current_asset_key(self):
        return self.asset_key
    def current_accessory_asset_key(self):
        if self.accessory_hp > 0:
            return self.accessory_asset_key
        return None
    def _get_blocker(self, game):
        return game.get_zombie_blocker(self.row, self.x)
    def update(self, dt, game):
        blocker = self._get_blocker(game)
        if blocker is not None:
            self.attack_timer += dt
            if self.attack_timer >= ZOMBIE_ATTACK_CD:
                self.attack_timer = 0.0
                dead = blocker.take_damage(ZOMBIE_ATTACK_DMG)
                if dead:
                    game.remove_plant(blocker.row, blocker.col)
        else:
            self.attack_timer = 0.0
            self.x -= self.speed * dt
            if self.x <= -self.width:
                game.trigger_lost()
    def draw(self, screen, image=None):
        y = STATUS_H + self.row * CELL_SIZE + (CELL_SIZE-self.height)//2
        if image is not None:
            ix = int(self.x) + (self.width - image.get_width()) // 2
            iy = STATUS_H + self.row * CELL_SIZE + (CELL_SIZE - image.get_height()) // 2
            screen.blit(image, (ix, iy))
        else:
            rect = pygame.Rect(int(self.x), y, self.width, self.height)
            pygame.draw.rect(screen, ZOMBIE_COLOR, rect, border_radius=6)
            ey = y + 16
            pygame.draw.circle(screen, ZOMBIE_EYE, (int(self.x)+14, ey), 4)
            pygame.draw.circle(screen, ZOMBIE_EYE, (int(self.x)+32, ey), 4)
            font = pygame.font.Font(None, 26)
            txt = font.render("Z", True, (20, 20, 20))
            tx = int(self.x) + (self.width - txt.get_width())//2
            ty = y + self.height//2 - 2
            screen.blit(txt, (tx, ty))
        self.draw_health(screen)
    def draw_health(self, screen):
        y = STATUS_H + self.row * CELL_SIZE + (CELL_SIZE-self.height)//2
        bw = self.width; bh = 5
        by = y - 7
        pygame.draw.rect(screen, HP_BAR_BG, (int(self.x), by, bw, bh))
        total_hp = max(0, self.hp) + max(0, self.accessory_hp)
        r = max(0, total_hp/self.max_total_hp)
        hc = HP_BAR_GREEN if r > 0.3 else HP_BAR_RED
        pygame.draw.rect(screen, hc, (int(self.x), by, int(bw*r), bh))
    def draw_accessory(self, screen, base_image, accessory_image, offset):
        if base_image is None or accessory_image is None:
            return
        bx = int(self.x) + (self.width - base_image.get_width()) // 2
        by = STATUS_H + self.row * CELL_SIZE + (CELL_SIZE - base_image.get_height()) // 2
        screen.blit(accessory_image, (bx + offset[0], by + offset[1]))

ZOMBIE_REGISTRY = {
    "normal": {
        "name": "Normal Zombie",
        "class": Zombie,
        "hp": ZOMBIE_HP,
        "width": ZOMBIE_WIDTH,
        "height": ZOMBIE_HEIGHT,
        "asset_key": "zombie",
    },
}

ACCESSORY_REGISTRY = {
    "cone": {
        "name": "Traffic Cone",
        "hp": ZOMBIE_CONEHEAD_ARMOR,
        "asset_key": "cone_accessory",
        "max_size": (32, 36),
        "offset": (3, -18),
    },
    "bucket": {
        "name": "Bucket",
        "hp": ZOMBIE_BUCKETHEAD_ARMOR,
        "asset_key": "bucket_accessory",
        "max_size": (34, 30),
        "offset": (2, -11),
    },
}

class Pea:
    def __init__(self, row, x, damage):
        self.row = row; self.x = x; self.damage = damage
    def update(self, dt):
        self.x += PEA_SPEED * dt
    def draw(self, screen):
        cx, cy = int(self.x), STATUS_H + self.row*CELL_SIZE + CELL_SIZE//2
        pygame.draw.circle(screen, PEA_COLOR, (cx, cy), 7)
        pygame.draw.circle(screen, (180, 255, 180), (cx, cy), 4)

class Sun:
    def __init__(self, x, y, value, lifetime):
        self.x = max(SUN_CLICK_RADIUS, min(x, GRID_W - SUN_CLICK_RADIUS))
        self.y = min(y, SUN_MAX_Y)
        self.value = value
        self.lifetime = lifetime; self.age = 0.0
        self.dead = False
        self.target_y = min(self.y + random.randint(40, 100), SUN_MAX_Y)
    def update(self, dt):
        self.age += dt
        if self.age >= self.lifetime: self.dead = True; return
        if self.y < self.target_y:
            self.y += SUN_FALL_SPEED * dt
            if self.y > self.target_y: self.y = self.target_y
    def draw(self, screen, image=None):
        if self.dead: return
        cx, cy = int(self.x), int(self.y)
        if image is not None:
            screen.blit(image, (cx - image.get_width()//2, cy - image.get_height()//2))
        else:
            pygame.draw.circle(screen, SUN_COLOR, (cx, cy), 22)
            pygame.draw.circle(screen, (255, 255, 200), (cx, cy), 15)
            font = pygame.font.Font(None, 20)
            txt = font.render(str(self.value), True, (160, 120, 0))
            tx = cx - txt.get_width()//2; ty = cy - txt.get_height()//2
            screen.blit(txt, (tx, ty))
    def contains(self, mx, my):
        dx = self.x - mx; dy = self.y - my
        return dx*dx + dy*dy <= SUN_CLICK_RADIUS*SUN_CLICK_RADIUS

# ============ WAVE MANAGER ============

class WaveManager:
    def __init__(self):
        self.current_wave = 0
        self.zombies_spawned = 0
        self.zombies_in_wave = 0
        self.spawn_plan = []
        self.spawn_timer = 0.0
        self.wave_timer = 0.0
        self.in_wave = False
        self.all_done = False
    def _lerp(self, a, b, t):
        return a + (b - a) * max(0, min(1, t))
    def _spawn_interval(self):
        if TOTAL_WAVES <= 1: return SPAWN_INTERVAL_W1
        t = (self.current_wave - 1) / (TOTAL_WAVES - 1)
        return self._lerp(SPAWN_INTERVAL_W1, SPAWN_INTERVAL_W5, t)
    def _zombie_speed(self):
        if TOTAL_WAVES <= 1: return SPEED_W1
        t = (self.current_wave - 1) / (TOTAL_WAVES - 1)
        return self._lerp(SPEED_W1, SPEED_W5, t)
    def _wave_cooldown(self, game):
        return WAVE_COOLDOWN * game.difficulty_config["wave_cooldown_multiplier"]
    def _zombies_in_wave(self, game):
        base_count = ZOMBIES_PER_WAVE_BASE + (self.current_wave - 1) * ZOMBIES_PER_WAVE_INC
        return max(1, int(round(base_count * game.difficulty_config["zombie_count_multiplier"])))
    def _spawn_choice(self):
        table = ZOMBIE_SPAWN_TABLE.get(self.current_wave, ZOMBIE_SPAWN_TABLE[max(ZOMBIE_SPAWN_TABLE)])
        roll = random.random() * sum(weight for _, _, weight in table)
        upto = 0.0
        for zombie_key, accessory_key, weight in table:
            upto += weight
            if roll <= upto:
                return zombie_key, accessory_key
        return table[-1][0], table[-1][1]
    def _build_spawn_plan(self):
        plan = [
            ("normal", accessory_key)
            for accessory_key in ZOMBIE_WAVE_GUARANTEED_ACCESSORIES.get(self.current_wave, ())
        ][:self.zombies_in_wave]
        while len(plan) < self.zombies_in_wave:
            plan.append(self._spawn_choice())
        random.shuffle(plan)
        return plan
    def _start_wave(self, game):
        self.current_wave += 1
        self.zombies_spawned = 0
        self.zombies_in_wave = self._zombies_in_wave(game)
        self.spawn_plan = self._build_spawn_plan()
        self.spawn_timer = 0.0
        self.in_wave = True
    def try_spawn(self, dt, game):
        if self.all_done or game.state != STATE_PLAYING:
            return
        if not self.in_wave:
            self.wave_timer += dt
            if self.wave_timer >= self._wave_cooldown(game):
                self._start_wave(game)
            return
        if self.zombies_spawned >= self.zombies_in_wave:
            if not game.has_zombies():
                self.in_wave = False
                self.wave_timer = 0.0
                if self.current_wave >= TOTAL_WAVES:
                    self.all_done = True
                    game.trigger_won()
            return
        self.spawn_timer += dt
        interval = self._spawn_interval()
        if self.spawn_timer >= interval:
            self.spawn_timer -= interval
            row = random.randint(0, GRID_ROWS - 1)
            if self.zombies_spawned < len(self.spawn_plan):
                zombie_key, accessory_key = self.spawn_plan[self.zombies_spawned]
            else:
                zombie_key, accessory_key = self._spawn_choice()
            self.zombies_spawned += 1
            game.spawn_zombie(row, self._zombie_speed(), zombie_key, accessory_key)

# ============ GAME ============

class Game:
    CARD_KEYS = tuple(PLANT_REGISTRY.keys())
    def __init__(self):
        self.images = self._load_images()
        self.difficulty_key = "normal"
        self.difficulty_config = DIFFICULTY_CONFIG[self.difficulty_key]
        self.state = STATE_MENU
        self._reset_game()

    def _fit_image(self, image, max_width, max_height):
        width, height = image.get_size()
        scale = min(max_width / width, max_height / height)
        size = (max(1, int(width * scale)), max(1, int(height * scale)))
        return pygame.transform.smoothscale(image, size)

    def _trim_alpha(self, image):
        bbox = image.get_bounding_rect(min_alpha=8)
        if bbox.width <= 0 or bbox.height <= 0:
            return image
        return image.subsurface(bbox).copy()

    def _is_edge_background_pixel(self, color):
        r, g, b, a = color
        if a < 8:
            return True
        spread = max(r, g, b) - min(r, g, b)
        bright_neutral = (r + g + b) / 3 > 205 and spread < 75
        beige_shadow = r > 120 and g > 95 and b > 65 and r >= g >= b and spread < 95
        return bright_neutral or beige_shadow

    def _remove_edge_background(self, image):
        result = image.copy()
        width, height = result.get_size()
        bbox = result.get_bounding_rect(min_alpha=8)
        if bbox.width <= 0 or bbox.height <= 0:
            return result

        seeds = []
        for x in range(bbox.left, bbox.right):
            seeds.append((x, bbox.top))
            seeds.append((x, bbox.bottom - 1))
        for y in range(bbox.top, bbox.bottom):
            seeds.append((bbox.left, y))
            seeds.append((bbox.right - 1, y))

        queue = []
        visited = set()
        for point in seeds:
            if point in visited:
                continue
            visited.add(point)
            if self._is_edge_background_pixel(result.get_at(point)):
                queue.append(point)

        while queue:
            x, y = queue.pop()
            result.set_at((x, y), (0, 0, 0, 0))
            for nx, ny in ((x - 1, y), (x + 1, y), (x, y - 1), (x, y + 1)):
                if nx < 0 or ny < 0 or nx >= width or ny >= height or (nx, ny) in visited:
                    continue
                visited.add((nx, ny))
                if self._is_edge_background_pixel(result.get_at((nx, ny))):
                    queue.append((nx, ny))
        return result

    def _load_images(self):
        images = {}
        raw_images = {}
        for key, filename in ASSET_FILES.items():
            path = os.path.join(ASSET_DIR, filename)
            if not os.path.exists(path):
                continue
            try:
                raw = pygame.image.load(path).convert_alpha()
            except pygame.error:
                continue
            if key in FLIPPED_ASSETS:
                raw = pygame.transform.flip(raw, True, False)
            if key in ACCESSORY_ASSET_KEYS:
                raw = self._remove_edge_background(raw)
                raw = self._trim_alpha(raw)
            raw_images[key] = raw

        accessory_sizes = {
            data["asset_key"]: data["max_size"]
            for data in ACCESSORY_REGISTRY.values()
        }

        for key, raw in raw_images.items():
            if key == "lawn_checker":
                images[key] = {
                    "lawn": pygame.transform.smoothscale(raw, (GRID_W, GRID_H)),
                }
                continue
            zombie_image = self._fit_image(raw, ZOMBIE_IMAGE_MAX_W, ZOMBIE_IMAGE_MAX_H)
            accessory_image = None
            if key in accessory_sizes:
                accessory_image = self._fit_image(raw, *accessory_sizes[key])
            images[key] = {
                "grid": self._fit_image(raw, CELL_SIZE - 6, CELL_SIZE - 6),
                "card": self._fit_image(raw, 42, 36),
                "button": self._fit_image(raw, 44, 38),
                "zombie": zombie_image,
                "accessory": accessory_image,
                "explosion": pygame.transform.smoothscale(raw, (CELL_SIZE * 3, CELL_SIZE * 3)),
                "sun": self._fit_image(raw, 48, 48),
                "status": self._fit_image(raw, 30, 30),
            }
        return images

    def reset(self):
        self.state = STATE_MENU
        self._reset_game()

    def _reset_game(self):
        self.grid = [[None]*GRID_COLS for _ in range(GRID_ROWS)]
        self.zombies = []; self.peas = []; self.suns = []
        self.sun_count = SUN_INITIAL
        self.selected_card = None
        self.card_cooldowns = {
            key: float(data.get("initial_cooldown", 0.0))
            for key, data in PLANT_REGISTRY.items()
        }
        self.card_shake = {key: 0.0 for key in PLANT_REGISTRY}
        self.shovel_selected = False
        self.kills = 0
        self.wave_manager = WaveManager()
        self.sky_sun_timer = 0.0
        self.shake_time = 0.0
        self.shake_intensity = 0

    def start_game(self, difficulty_key="normal"):
        self.difficulty_key = difficulty_key if difficulty_key in DIFFICULTY_CONFIG else "normal"
        self.difficulty_config = DIFFICULTY_CONFIG[self.difficulty_key]
        self._reset_game()
        self.state = STATE_PLAYING

    def restart_game(self):
        self._reset_game()
        self.state = STATE_PLAYING

    def trigger_won(self):
        if self.state == STATE_PLAYING:
            self.state = STATE_WIN

    def trigger_lost(self):
        if self.state == STATE_PLAYING:
            self.state = STATE_LOSE

    def add_sun(self, x, y, value, lifetime=SUN_LIFETIME):
        self.suns.append(Sun(x, y, value, lifetime))

    def add_pea(self, row, x, damage=PEA_DAMAGE):
        self.peas.append(Pea(row, x, damage))

    def spawn_zombie(self, row, speed, zombie_key="normal", accessory_key=None):
        zombie_data = ZOMBIE_REGISTRY[zombie_key]
        zombie_class = zombie_data["class"]
        hp_multiplier = self.difficulty_config["zombie_hp_multiplier"]
        hp = max(1, int(round(zombie_data["hp"] * hp_multiplier)))
        accessory_data = None if accessory_key is None else ACCESSORY_REGISTRY[accessory_key]
        accessory_hp = 0
        accessory_asset_key = None
        if accessory_data is not None:
            accessory_hp = max(1, int(round(accessory_data["hp"] * hp_multiplier)))
            accessory_asset_key = accessory_data["asset_key"]
        self.zombies.append(zombie_class(
            row,
            speed,
            hp=hp,
            width=zombie_data["width"],
            height=zombie_data["height"],
            asset_key=zombie_data["asset_key"],
            accessory_key=accessory_key,
            accessory_hp=accessory_hp,
            accessory_asset_key=accessory_asset_key,
        ))

    def has_zombies(self):
        return len(self.zombies) > 0

    def has_zombie_ahead(self, row, min_x):
        return any(z.row == row and z.x >= min_x for z in self.zombies)

    def get_zombie_blocker(self, row, x):
        for col in range(GRID_COLS-1, -1, -1):
            plant = self.grid[row][col]
            if plant is not None and plant.hp > 0:
                if x <= (col+1)*CELL_SIZE - 8:
                    return plant
        return None

    def remove_plant(self, row, col):
        self.grid[row][col] = None

    def _shovel_rect(self):
        return pygame.Rect(SCREEN_W - 70, 10, 54, 40)

    def _wave_progress(self):
        if self.wave_manager.all_done or self.state == STATE_WIN:
            return 1.0
        if self.wave_manager.in_wave:
            return min(1.0, self.wave_manager.current_wave / TOTAL_WAVES)
        wave_cooldown = self.wave_manager._wave_cooldown(self)
        cooldown = min(1.0, self.wave_manager.wave_timer / wave_cooldown)
        return min(1.0, (self.wave_manager.current_wave + cooldown) / TOTAL_WAVES)

    def _card_cooldown_progress(self, key):
        duration = self._card_recharge_duration(key)
        if duration <= 0.0:
            return 1.0
        remaining = self.card_cooldowns.get(key, 0.0)
        return max(0.0, min(1.0, 1.0 - remaining / duration))

    def _card_recharge_duration(self, key):
        plant_data = PLANT_REGISTRY[key]
        return plant_data.get("recharge", plant_data.get("cooldown", 0.0))

    def _card_ready(self, key):
        plant_data = PLANT_REGISTRY[key]
        return self.sun_count >= plant_data["cost"] and self.card_cooldowns.get(key, 0.0) <= 0.0

    def _shake_card(self, key):
        self.card_shake[key] = CARD_SHAKE_DURATION

    def _draw_wave_progress(self, screen, rect):
        progress = self._wave_progress()
        shell = rect.inflate(8, 10)
        pygame.draw.rect(screen, (62, 51, 35), shell, border_radius=11)
        pygame.draw.rect(screen, (24, 30, 20), rect, border_radius=8)
        fill_w = int(rect.width * progress)
        if fill_w > 0:
            fill_rect = pygame.Rect(rect.x, rect.y, fill_w, rect.height)
            pygame.draw.rect(screen, (120, 175, 70), fill_rect, border_radius=8)
        pygame.draw.rect(screen, (185, 170, 120), rect, 2, border_radius=8)
        for wave in range(1, TOTAL_WAVES + 1):
            flag_x = rect.x + int(rect.width * wave / TOTAL_WAVES)
            reached = progress >= wave / TOTAL_WAVES
            pole_color = (230, 220, 170) if reached else (110, 105, 90)
            flag_color = (230, 70, 55) if reached else (110, 70, 65)
            pygame.draw.line(screen, pole_color, (flag_x, rect.y - 8), (flag_x, rect.y + rect.height + 7), 2)
            flag = [(flag_x, rect.y - 9), (flag_x + 10, rect.y - 5), (flag_x, rect.y - 1)]
            pygame.draw.polygon(screen, flag_color, flag)
        marker_x = rect.x + int(rect.width * progress)
        zombie_icon = self.images.get("zombie", {}).get("status")
        if zombie_icon is not None:
            ix = marker_x - zombie_icon.get_width() // 2
            iy = rect.centery - zombie_icon.get_height() // 2
            screen.blit(zombie_icon, (ix, iy))
        else:
            pygame.draw.circle(screen, ZOMBIE_COLOR, (marker_x, rect.centery), 8)
            pygame.draw.circle(screen, ZOMBIE_EYE, (marker_x - 3, rect.centery - 2), 2)
            pygame.draw.circle(screen, ZOMBIE_EYE, (marker_x + 3, rect.centery - 2), 2)

    def handle_click(self, mx, my):
        if self.state != STATE_PLAYING: return True
        if self._shovel_rect().collidepoint(mx, my):
            self.shovel_selected = not self.shovel_selected
            if self.shovel_selected:
                self.selected_card = None
            return True
        # 1. Collect sun
        for sun in self.suns:
            if sun.contains(mx, my):
                self.sun_count += sun.value; sun.dead = True; return True
        # 2. Card bar
        if my > SCREEN_H - CARD_H:
            card_gap = 5
            card_w = (SCREEN_W - card_gap*(len(self.CARD_KEYS)+1))//len(self.CARD_KEYS)
            for i, key in enumerate(self.CARD_KEYS):
                rx = card_gap + i*(card_w+card_gap)
                rect = pygame.Rect(rx, SCREEN_H-CARD_H+5, card_w, CARD_H-10)
                if rect.collidepoint(mx, my):
                    if not self._card_ready(key):
                        self._shake_card(key)
                        return True
                    self.selected_card = key if self.selected_card != key else None
                    self.shovel_selected = False
                    return True
            return False
        # 3. Grid
        if STATUS_H <= my < STATUS_H + GRID_H:
            col = mx // CELL_SIZE; row = (my - STATUS_H)//CELL_SIZE
            if not (0<=col<GRID_COLS and 0<=row<GRID_ROWS): return False
            if self.shovel_selected:
                if self.grid[row][col] is not None:
                    self.remove_plant(row, col)
                    self.shovel_selected = False
                    return True
                return False
            if col in (HOUSE_COL, SPAWN_COL): return False
            if self.selected_card is None: return False
            if self.grid[row][col] is not None:
                self.selected_card = None; return True
            plant_data = PLANT_REGISTRY.get(self.selected_card)
            if plant_data is None: return False
            cost = plant_data["cost"]
            if self.sun_count < cost: return False
            self.sun_count -= cost
            self.grid[row][col] = plant_data["class"](row, col)
            self.card_cooldowns[self.selected_card] = float(self._card_recharge_duration(self.selected_card))
            self.selected_card = None
            return True
        return False

    def handle_right_click(self):
        if self.state != STATE_PLAYING or self.selected_card is None:
            return False
        self.selected_card = None
        return True

    def _update_menu(self, dt):
        pass

    def _update_playing(self, dt):
        if self.state != STATE_PLAYING: return
        for key in self.CARD_KEYS:
            self.card_cooldowns[key] = max(0.0, self.card_cooldowns.get(key, 0.0) - dt)
            self.card_shake[key] = max(0.0, self.card_shake.get(key, 0.0) - dt)
        self.shake_time = max(0.0, self.shake_time - dt)
        self.wave_manager.try_spawn(dt, self)
        # Sky sun
        self.sky_sun_timer += dt
        if self.sky_sun_timer >= SKY_SUN_INTERVAL:
            self.sky_sun_timer = 0.0
            self.add_sun(random.randint(30,GRID_W-30), STATUS_H-10, SUN_VALUE)
        # Plants
        for row in range(GRID_ROWS):
            for col in range(GRID_COLS):
                p = self.grid[row][col]
                if p is not None:
                    if p.hp <= 0: self.remove_plant(row, col)
                    else: p.update(dt, self)
        # Suns
        for s in self.suns[:]:
            s.update(dt)
            if s.dead: self.suns.remove(s)
        # Peas
        for pea in self.peas[:]:
            pea.update(dt)
            if pea.x > GRID_W + 20: self.peas.remove(pea)
        # Zombies
        for z in self.zombies[:]:
            if z.hp <= 0:
                self.zombies.remove(z); self.kills += 1; continue
            z.update(dt, self)
        # Pea-Zombie collision
        hit = []
        for pea in self.peas:
            for z in self.zombies:
                if pea.row == z.row and z.hp > 0 and z.x <= pea.x <= z.x+z.width:
                    z.take_damage(pea.damage); hit.append(pea); break
        for p in hit:
            if p in self.peas: self.peas.remove(p)
        killed = sum(1 for z in self.zombies if z.hp <= 0)
        self.kills += killed
        self.zombies = [z for z in self.zombies if z.hp > 0]

    def _update_gameover(self, dt):
        pass

    def _update_paused(self, dt):
        pass

    def _display_text(self, text, fallback=None):
        if fallback is not None and any(ord(ch) > 127 for ch in text):
            return fallback
        if any(ord(ch) > 127 for ch in text) and "/" in text:
            return text.split("/")[-1].strip()
        return text

    def _draw_text_center(self, screen, font, text, color, center, outline=False):
        if outline:
            shadow = font.render(text, True, SHADOW_COLOR)
            for dx, dy in ((-2, 0), (2, 0), (0, -2), (0, 2)):
                rect = shadow.get_rect(center=(center[0] + dx, center[1] + dy))
                screen.blit(shadow, rect)
        rendered = font.render(text, True, color)
        rect = rendered.get_rect(center=center)
        screen.blit(rendered, rect)

    def _draw_grass_background(self, screen):
        screen.fill(BG_COLOR)
        for y in range(0, SCREEN_H, CELL_SIZE):
            for x in range(0, SCREEN_W, CELL_SIZE):
                row = y // CELL_SIZE
                col = x // CELL_SIZE
                color = GRID_A if (row+col)%2==0 else GRID_B
                pygame.draw.rect(screen, color, (x,y,CELL_SIZE,CELL_SIZE))
                pygame.draw.rect(screen, GRID_LINE, (x,y,CELL_SIZE,CELL_SIZE), 1)

    def _draw_button(self, screen, rect, text, mouse_pos, mouse_pressed):
        hovered = rect.collidepoint(mouse_pos)
        pressed = hovered and mouse_pressed
        if pressed:
            color = (70, 130, 50)
        elif hovered:
            color = (120, 200, 80)
        else:
            color = (90, 160, 60)
        pygame.draw.rect(screen, color, rect, border_radius=12)
        pygame.draw.rect(screen, (235, 255, 220), rect, 2, border_radius=12)
        label = self._display_text(text)
        font = pygame.font.Font(None, 32)
        rendered = font.render(label, True, TEXT_COLOR)
        screen.blit(rendered, rendered.get_rect(center=rect.center))
        return pressed

    def _draw_follow_shadow(self, screen, image, center, fallback_color, scale=1.0):
        if image is not None:
            ghost = image.copy()
            if scale != 1.0:
                size = (
                    max(1, int(ghost.get_width() * scale)),
                    max(1, int(ghost.get_height() * scale)),
                )
                ghost = pygame.transform.smoothscale(ghost, size)
            ghost.set_alpha(150)
            screen.blit(ghost, (center[0] - ghost.get_width()//2, center[1] - ghost.get_height()//2))
        else:
            pygame.draw.circle(screen, (*fallback_color, 120), center, int(24 * scale))

    def _card_shake_offset(self, key):
        remaining = self.card_shake.get(key, 0.0)
        if remaining <= 0.0:
            return 0
        fade = remaining / CARD_SHAKE_DURATION
        return int(math.sin(remaining * 85.0) * CARD_SHAKE_AMPLITUDE * fade)

    def _draw_card_cooldown(self, screen, rect, progress):
        if progress >= 1.0:
            return
        restored_h = int(rect.height * progress)
        dark_h = rect.height - restored_h
        if dark_h > 0:
            overlay = pygame.Surface((rect.width, dark_h), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 135))
            screen.blit(overlay, (rect.x, rect.y))
        if restored_h > 0:
            fill_rect = pygame.Rect(rect.x + 3, rect.bottom - restored_h, rect.width - 6, max(2, restored_h))
            shine = pygame.Surface((fill_rect.width, fill_rect.height), pygame.SRCALPHA)
            shine.fill((255, 255, 190, 45))
            screen.blit(shine, fill_rect.topleft)
        line_y = rect.bottom - restored_h
        if rect.y < line_y < rect.bottom:
            pygame.draw.line(screen, (255, 245, 160), (rect.x + 2, line_y), (rect.right - 2, line_y), 2)

    def _draw_menu(self, screen, mouse_pos, mouse_pressed):
        self._draw_grass_background(screen)
        title_font = pygame.font.Font(None, 72)
        subtitle_font = pygame.font.Font(None, 36)
        instruction_font = pygame.font.Font(None, 20)
        self._draw_text_center(screen, title_font, "PLANTS vs ZOMBIES", TEXT_COLOR, (SCREEN_W//2, 150), True)
        self._draw_text_center(screen, subtitle_font, "Training Demo", (210, 210, 210), (SCREEN_W//2, 215))
        button = pygame.Rect((SCREEN_W - 240)//2, 270, 240, 72)
        if self._draw_button(screen, button, "开始游戏 / START", mouse_pos, mouse_pressed):
            self.state = STATE_DIFFICULTY_SELECT
        instruction = self._display_text(
            "鼠标点击卡片选择植物，再点击格子放置 · R 重开 · ESC 返回菜单",
            "Click cards to choose plants, place on grid | R restart | ESC menu",
        )
        self._draw_text_center(screen, instruction_font, instruction, (185, 185, 185), (SCREEN_W//2, 380))

    def _draw_difficulty_select(self, screen, mouse_pos, mouse_pressed):
        self._draw_grass_background(screen)
        title_font = pygame.font.Font(None, 64)
        subtitle_font = pygame.font.Font(None, 28)
        self._draw_text_center(screen, title_font, "SELECT DIFFICULTY", TEXT_COLOR, (SCREEN_W//2, 120), True)
        self._draw_text_center(screen, subtitle_font, "Choose your lawn pressure", (210, 210, 210), (SCREEN_W//2, 172))
        button_w = 220
        button_h = 62
        start_y = 235
        gap = 82
        for i, key in enumerate(("easy", "normal", "hard")):
            data = DIFFICULTY_CONFIG[key]
            rect = pygame.Rect((SCREEN_W - button_w)//2, start_y + i * gap, button_w, button_h)
            if self._draw_button(screen, rect, data["name"].upper(), mouse_pos, mouse_pressed):
                self.start_game(key)
        back_rect = pygame.Rect((SCREEN_W - 160)//2, start_y + 3 * gap + 10, 160, 46)
        if self._draw_button(screen, back_rect, "BACK", mouse_pos, mouse_pressed):
            self.state = STATE_MENU

    def _draw_paused(self, screen, mouse_pos, mouse_pressed):
        self._draw_playing(screen)
        ov = pygame.Surface((SCREEN_W,SCREEN_H), pygame.SRCALPHA)
        ov.fill((0, 0, 0, 150))
        screen.blit(ov, (0,0))
        title_font = pygame.font.Font(None, 64)
        hint_font = pygame.font.Font(None, 24)
        self._draw_text_center(screen, title_font, "PAUSED", TEXT_COLOR, (SCREEN_W//2, SCREEN_H//2 - 115), True)
        continue_button = pygame.Rect((SCREEN_W - 220)//2, SCREEN_H//2 - 50, 220, 60)
        menu_button = pygame.Rect((SCREEN_W - 220)//2, SCREEN_H//2 + 25, 220, 60)
        if self._draw_button(screen, continue_button, "CONTINUE", mouse_pos, mouse_pressed):
            self.state = STATE_PLAYING
        if self._draw_button(screen, menu_button, "EXIT", mouse_pos, mouse_pressed):
            self.state = STATE_MENU
        self._draw_text_center(screen, hint_font, "ESC to continue", (200, 200, 200), (SCREEN_W//2, SCREEN_H//2 + 115))

    def _draw_playing(self, screen):
        output_screen = screen
        if self.shake_time > 0.0 and self.shake_intensity > 0:
            shake_amount = int(self.shake_intensity)
            shake_offset = (
                random.randint(-shake_amount, shake_amount),
                random.randint(-shake_amount, shake_amount),
            )
            screen = pygame.Surface((SCREEN_W, SCREEN_H))
        else:
            shake_offset = (0, 0)
        screen.fill(BG_COLOR)
        lawn_image = self.images.get("lawn_checker", {}).get("lawn")
        if lawn_image is not None:
            screen.blit(lawn_image, (0, STATUS_H))
        else:
            # Grid fallback when the background asset is missing.
            for row in range(GRID_ROWS):
                for col in range(GRID_COLS):
                    x = col*CELL_SIZE; y = STATUS_H + row*CELL_SIZE
                    if col == HOUSE_COL:
                        color = HOUSE_COLOR
                    elif col == SPAWN_COL:
                        color = SPAWN_COLOR
                    else:
                        color = GRID_A if (row+col)%2==0 else GRID_B
                    pygame.draw.rect(screen, color, (x,y,CELL_SIZE,CELL_SIZE))
                    pygame.draw.rect(screen, GRID_LINE, (x,y,CELL_SIZE,CELL_SIZE), 1)
        # Status bar
        pygame.draw.rect(screen, STATUS_BG, (0,0,SCREEN_W,STATUS_H))
        pygame.draw.line(screen, (60,60,60), (0,STATUS_H), (SCREEN_W,STATUS_H), 2)
        panel_color = (38, 38, 38)
        panel_border = (82, 82, 82)
        sun_panel = pygame.Rect(16, 9, 130, 42)
        kill_panel = pygame.Rect(170, 9, 140, 42)
        for panel in (sun_panel, kill_panel):
            pygame.draw.rect(screen, panel_color, panel, border_radius=8)
            pygame.draw.rect(screen, panel_border, panel, 1, border_radius=8)
        status_sun = self.images.get("sun", {}).get("status")
        if status_sun is not None:
            screen.blit(status_sun, (42 - status_sun.get_width()//2, 30 - status_sun.get_height()//2))
        else:
            pygame.draw.circle(screen, SUN_COLOR, (42,30), 14)
            pygame.draw.circle(screen, (255,255,200), (42,30), 9)
        font = pygame.font.Font(None, 28)
        txt = font.render(str(self.sun_count), True, TEXT_COLOR)
        screen.blit(txt, (66, 19))
        txt = font.render(f"Kills: {self.kills}", True, TEXT_COLOR)
        screen.blit(txt, txt.get_rect(center=kill_panel.center))
        self._draw_wave_progress(screen, pygame.Rect(512, 23, 270, 14))
        shovel_rect = self._shovel_rect()
        shovel_bg = SHOVEL_ACTIVE_BG if self.shovel_selected else SHOVEL_BG
        pygame.draw.rect(screen, shovel_bg, shovel_rect, border_radius=6)
        border = SELECT_BORDER if self.shovel_selected else (170, 170, 170)
        pygame.draw.rect(screen, border, shovel_rect, 2, border_radius=6)
        shovel_image = self.images.get("shovel", {}).get("button")
        if shovel_image is not None:
            ix = shovel_rect.x + (shovel_rect.width - shovel_image.get_width()) // 2
            iy = shovel_rect.y + (shovel_rect.height - shovel_image.get_height()) // 2
            screen.blit(shovel_image, (ix, iy))
        else:
            handle_start = (shovel_rect.x + 17, shovel_rect.y + 31)
            handle_end = (shovel_rect.x + 38, shovel_rect.y + 12)
            pygame.draw.line(screen, SHOVEL_HANDLE, handle_start, handle_end, 5)
            blade = [
                (shovel_rect.x + 34, shovel_rect.y + 8),
                (shovel_rect.x + 47, shovel_rect.y + 16),
                (shovel_rect.x + 38, shovel_rect.y + 27),
                (shovel_rect.x + 27, shovel_rect.y + 18),
            ]
            pygame.draw.polygon(screen, SHOVEL_METAL, blade)
            pygame.draw.polygon(screen, (90, 90, 90), blade, 2)
        # Plants / Zombies / Peas / Suns
        exploding_plants = []
        for row in range(GRID_ROWS):
            for col in range(GRID_COLS):
                p = self.grid[row][col]
                if p is not None:
                    if isinstance(p, CherryBomb):
                        if p.state == "exploding":
                            exploding_plants.append(p)
                        else:
                            p.draw(screen, self.images)
                    else:
                        p.draw(screen, self.images.get(p.asset_key, {}).get("grid"))
        for z in self.zombies:
            base_image = self.images.get(z.current_asset_key(), {}).get("zombie")
            z.draw(screen, base_image)
            accessory_asset_key = z.current_accessory_asset_key()
            if accessory_asset_key is not None and z.accessory_key is not None:
                accessory_image = self.images.get(accessory_asset_key, {}).get("accessory")
                accessory_offset = ACCESSORY_REGISTRY[z.accessory_key]["offset"]
                z.draw_accessory(screen, base_image, accessory_image, accessory_offset)
                z.draw_health(screen)
        for p in exploding_plants: p.draw(screen, self.images)
        for pea in self.peas: pea.draw(screen)
        for s in self.suns: s.draw(screen, self.images.get("sun", {}).get("sun"))
        # Card bar
        pygame.draw.rect(screen, CARD_BG, (0,SCREEN_H-CARD_H,SCREEN_W,CARD_H))
        pygame.draw.line(screen, (60,55,50), (0,SCREEN_H-CARD_H), (SCREEN_W,SCREEN_H-CARD_H), 2)
        card_gap = 5
        card_w = (SCREEN_W-card_gap*(len(self.CARD_KEYS)+1))//len(self.CARD_KEYS)
        for i, key in enumerate(self.CARD_KEYS):
            plant_data = PLANT_REGISTRY[key]
            name = plant_data["name"]
            cost = plant_data["cost"]
            color = plant_data["color"]
            letter = plant_data["letter"]
            asset_key = plant_data["asset_key"]
            base_rx = card_gap + i*(card_w+card_gap)
            rx = base_rx + self._card_shake_offset(key)
            ry = SCREEN_H-CARD_H+6
            rect = pygame.Rect(rx, ry, card_w, CARD_H-12)
            affordable = self.sun_count >= cost
            cooldown_progress = self._card_cooldown_progress(key)
            ready = self._card_ready(key)
            dc = color if affordable else (color[0]//3,color[1]//3,color[2]//3)
            pygame.draw.rect(screen, dc, rect, border_radius=8)
            bw = 2; bc = (180,180,180) if not ready else (220,220,220)
            if self.selected_card == key:
                bc = SELECT_BORDER; bw = 3
            f = pygame.font.Font(None, 28)
            card_image = self.images.get(asset_key, {}).get("card")
            if card_image is not None:
                ix = rx + (card_w-card_image.get_width())//2
                screen.blit(card_image, (ix, ry+3))
            else:
                t = f.render(letter, True, (0,0,0))
                screen.blit(t, (rx+(card_w-t.get_width())//2, ry+4))
            f = pygame.font.Font(None, 16)
            t = f.render(name, True, (0,0,0))
            screen.blit(t, (rx+(card_w-t.get_width())//2, ry+42))
            cc = (255,255,255) if affordable else (150,150,150)
            f = pygame.font.Font(None, 18)
            t = f.render(f"${cost}", True, cc)
            screen.blit(t, (rx+(card_w-t.get_width())//2, ry+56))
            self._draw_card_cooldown(screen, rect, cooldown_progress)
            pygame.draw.rect(screen, bc, rect, bw, border_radius=8)
        # Ghost preview
        if self.selected_card is not None and self.state == STATE_PLAYING:
            mx, my = pygame.mouse.get_pos()
            if STATUS_H <= my < STATUS_H+GRID_H:
                gc = mx//CELL_SIZE; gr = (my-STATUS_H)//CELL_SIZE
                if 0<=gc<GRID_COLS and 0<=gr<GRID_ROWS and gc not in (HOUSE_COL, SPAWN_COL) and self.grid[gr][gc] is None:
                    s = pygame.Surface((CELL_SIZE,CELL_SIZE), pygame.SRCALPHA)
                    s.fill((255,255,255,50))
                    screen.blit(s, (gc*CELL_SIZE, STATUS_H+gr*CELL_SIZE))
        if self.state == STATE_PLAYING:
            mx, my = pygame.mouse.get_pos()
            if self.selected_card is not None:
                plant_data = PLANT_REGISTRY.get(self.selected_card)
                if plant_data is not None:
                    image = self.images.get(plant_data["asset_key"], {}).get("grid")
                    self._draw_follow_shadow(screen, image, (mx, my), plant_data["color"])
            elif self.shovel_selected:
                image = self.images.get("shovel", {}).get("button")
                self._draw_follow_shadow(screen, image, (mx, my), SHOVEL_METAL, 1.75)
        if screen is not output_screen:
            output_screen.fill(BG_COLOR)
            output_screen.blit(screen, shake_offset)
    def _draw_gameover(self, screen, mouse_pos, mouse_pressed):
        self._draw_playing(screen)
        if self.state == STATE_WIN:
            overlay_color = WIN_BG
            title = "YOU WIN!"
            title_color = WIN_TEXT
        else:
            overlay_color = LOSE_BG
            title = "GAME OVER"
            title_color = LOSE_TEXT
        ov = pygame.Surface((SCREEN_W,SCREEN_H), pygame.SRCALPHA)
        ov.fill(overlay_color); screen.blit(ov, (0,0))
        f = pygame.font.Font(None, 64)
        t = f.render(title, True, title_color)
        tw, th = t.get_size()
        screen.blit(t, ((SCREEN_W-tw)//2, (SCREEN_H-th)//2-80))
        f = pygame.font.Font(None, 26)
        t = f.render("Press R to restart", True, TEXT_COLOR)
        tw, th = t.get_size()
        screen.blit(t, ((SCREEN_W-tw)//2, (SCREEN_H-th)//2-25))
        button = pygame.Rect((SCREEN_W - 200)//2, (SCREEN_H)//2 + 25, 200, 60)
        if self._draw_button(screen, button, "返回菜单 / BACK TO MENU", mouse_pos, mouse_pressed):
            self.state = STATE_MENU

# ============ MAIN ============

def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_W, SCREEN_H))
    pygame.display.set_caption("Plants vs Zombies - Simplified")
    clock = pygame.time.Clock()
    game = Game()
    running = True
    while running:
        dt = min(clock.tick(60) / 1000.0, MAX_DT)
        mouse_pressed = False
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT: running = False
            elif ev.type == pygame.KEYDOWN:
                if ev.key == pygame.K_ESCAPE and game.state == STATE_PLAYING:
                    game.state = STATE_PAUSED
                elif ev.key == pygame.K_ESCAPE and game.state == STATE_PAUSED:
                    game.state = STATE_PLAYING
                elif ev.key == pygame.K_ESCAPE and game.state == STATE_DIFFICULTY_SELECT:
                    game.state = STATE_MENU
                elif ev.key == pygame.K_r and game.state in (STATE_WIN, STATE_LOSE):
                    game.restart_game()
            elif ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 1:
                mouse_pressed = True
                if game.state == STATE_PLAYING:
                    game.handle_click(*ev.pos)
            elif ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 3:
                if game.state == STATE_PLAYING:
                    game.handle_right_click()
        mouse_pos = pygame.mouse.get_pos()
        if game.state == STATE_MENU:
            game._update_menu(dt)
            game._draw_menu(screen, mouse_pos, mouse_pressed)
        elif game.state == STATE_DIFFICULTY_SELECT:
            game._update_menu(dt)
            game._draw_difficulty_select(screen, mouse_pos, mouse_pressed)
        elif game.state == STATE_PLAYING:
            game._update_playing(dt)
            game._draw_playing(screen)
        elif game.state == STATE_PAUSED:
            game._update_paused(dt)
            game._draw_paused(screen, mouse_pos, mouse_pressed)
        elif game.state in (STATE_WIN, STATE_LOSE):
            game._update_gameover(dt)
            game._draw_gameover(screen, mouse_pos, mouse_pressed)
        pygame.display.flip()
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
