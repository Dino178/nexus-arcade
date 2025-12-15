import pygame
import sys
import json
import time
import random
import math

# --- 1. CONFIGURATION & AESTHETICS ---
pygame.init()
WIDTH, HEIGHT = 1000, 700
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("NEXUS ARCADE HUB - GitHub Edition")
clock = pygame.time.Clock()

# Cyberpunk Palette
C_BG = (10, 10, 18)        # Deep Void Blue
C_PANEL = (25, 25, 40)     # Panel Grey
C_ACCENT = (0, 255, 213)   # Neon Cyan
C_SEC = (255, 0, 128)      # Neon Pink
C_TEXT = (255, 255, 255)   # White
C_WARN = (255, 204, 0)     # Gold/Yellow

# Fonts
font_xl = pygame.font.SysFont("Verdana", 50, bold=True)
font_lg = pygame.font.SysFont("Verdana", 30)
font_md = pygame.font.SysFont("Consolas", 20)
font_sm = pygame.font.SysFont("Consolas", 14)

# --- 2. SAVE SYSTEM (JSON) ---
SAVE_FILE = "game_save.json"

def load_game():
    """Loads data from a local JSON file."""
    default_data = {
        "clicker": {"score": 0, "multiplier": 1, "buildings": [0, 0, 0, 0]},
        "high_scores": {"runner": 0, "snake": 0}
    }
    try:
        with open(SAVE_FILE, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return default_data

def save_game(data):
    """Writes data to a local JSON file."""
    with open(SAVE_FILE, "w") as f:
        json.dump(data, f)

# Global State
game_data = load_game()

# --- 3. UI COMPONENTS ---
class Button:
    def __init__(self, x, y, w, h, text, color=C_PANEL, hover_color=C_ACCENT):
        self.rect = pygame.Rect(x, y, w, h)
        self.text = text
        self.color = color
        self.hover_color = hover_color
        self.hovered = False

    def draw(self, surface):
        col = self.hover_color if self.hovered else self.color
        text_col = C_BG if self.hovered else C_TEXT
        
        pygame.draw.rect(surface, col, self.rect, border_radius=10)
        pygame.draw.rect(surface, C_TEXT, self.rect, 2, border_radius=10)
        
        txt = font_md.render(self.text, True, text_col)
        txt_rect = txt.get_rect(center=self.rect.center)
        surface.blit(txt, txt_rect)

    def check_hover(self, pos):
        self.hovered = self.rect.collidepoint(pos)
        return self.hovered

    def is_clicked(self, event):
        return event.type == pygame.MOUSEBUTTONDOWN and self.hovered

# --- 4. GAME: NEON CLICKER (IDLE + PRESTIGE) ---
class ClickerGame:
    def __init__(self):
        self.items = [
            {"name": "Cursor Bot", "cost": 15, "cps": 1},
            {"name": "GPU Farm", "cost": 100, "cps": 5},
            {"name": "AI Server", "cost": 1000, "cps": 50},
            {"name": "Quantum Core", "cost": 10000, "cps": 200},
        ]
        self.last_tick = time.time()

    def run(self):
        running = True
        mine_btn = Button(50, 200, 200, 200, "MINE", C_ACCENT, C_SEC)
        back_btn = Button(20, 20, 100, 40, "< BACK")
        prestige_btn = Button(700, 600, 250, 60, "REINCARNATE (Ascend)", C_SEC, C_WARN)
        
        # Upgrade Buttons
        upg_btns = []
        for i in range(4):
            upg_btns.append(Button(300, 200 + (i * 70), 380, 60, ""))

        while running:
            screen.fill(C_BG)
            mouse_pos = pygame.mouse.get_pos()
            dt = clock.tick(60)

            # Passive Income Logic
            current_time = time.time()
            if current_time - self.last_tick >= 1.0:
                cps = sum([game_data["clicker"]["buildings"][i] * self.items[i]["cps"] for i in range(4)])
                cps *= game_data["clicker"]["multiplier"] # Apply Prestige
                game_data["clicker"]["score"] += cps
                self.last_tick = current_time
                save_game(game_data) # Auto-save

            # Draw Stats
            cps_display = sum([game_data["clicker"]["buildings"][i] * self.items[i]["cps"] for i in range(4)]) * game_data["clicker"]["multiplier"]
            
            screen.blit(font_xl.render(f"CRYPTO: {int(game_data['clicker']['score']):,}", True, C_ACCENT), (300, 50))
            screen.blit(font_md.render(f"CPS: {cps_display}/sec | Multiplier: x{game_data['clicker']['multiplier']}", True, C_TEXT), (300, 110))

            # Draw Buttons
            mine_btn.check_hover(mouse_pos)
            mine_btn.draw(screen)
            
            back_btn.check_hover(mouse_pos)
            back_btn.draw(screen)

            for i, btn in enumerate(upg_btns):
                count = game_data["clicker"]["buildings"][i]
                cost = int(self.items[i]["cost"] * (1.15 ** count))
                btn.text = f"{self.items[i]['name']} (Lvl {count}) - ${cost:,}"
                btn.check_hover(mouse_pos)
                btn.draw(screen)
            
            prestige_cost = 100000 * game_data["clicker"]["multiplier"]
            prestige_btn.text = f"ASCEND (Cost: {prestige_cost:,})"
            if game_data["clicker"]["score"] >= prestige_cost:
                prestige_btn.check_hover(mouse_pos)
                prestige_btn.draw(screen)

            # Events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    save_game(game_data)
                    sys.exit()
                
                if mine_btn.is_clicked(event):
                    game_data["clicker"]["score"] += 1 * game_data["clicker"]["multiplier"]

                if back_btn.is_clicked(event):
                    running = False
                
                if prestige_btn.is_clicked(event):
                    if game_data["clicker"]["score"] >= prestige_cost:
                        game_data["clicker"]["score"] = 0
                        game_data["clicker"]["buildings"] = [0,0,0,0]
                        game_data["clicker"]["multiplier"] += 1
                        save_game(game_data)

                for i, btn in enumerate(upg_btns):
                    cost = int(self.items[i]["cost"] * (1.15 ** game_data["clicker"]["buildings"][i]))
                    if btn.is_clicked(event) and game_data["clicker"]["score"] >= cost:
                        game_data["clicker"]["score"] -= cost
                        game_data["clicker"]["buildings"][i] += 1

            pygame.display.flip()

# --- 5. GAME: VOID RUNNER (PHYSICS) ---
def void_runner():
    player = pygame.Rect(100, 500, 40, 40)
    gravity = 0.8
    velocity_y = 0
    is_jumping = False
    
    obstacles = []
    score = 0
    speed = 6
    spawn_timer = 0
    
    running = True
    game_over = False

    while running:
        clock.tick(60)
        screen.fill(C_BG)
        
        # Floor
        pygame.draw.rect(screen, C_PANEL, (0, 540, WIDTH, HEIGHT-540))
        
        if not game_over:
            # Player Physics
            velocity_y += gravity
            player.y += velocity_y
            
            if player.y >= 500: # Ground
                player.y = 500
                velocity_y = 0
                is_jumping = False

            # Obstacles
            spawn_timer += 1
            if spawn_timer > random.randint(60, 120):
                obstacles.append(pygame.Rect(WIDTH, 510, 30, 30))
                spawn_timer = 0
            
            for obs in obstacles[:]:
                obs.x -= speed
                if obs.x < -30:
                    obstacles.remove(obs)
                    score += 1
                    if score % 10 == 0: speed += 1 # Difficulty curve
                
                if player.colliderect(obs):
                    game_over = True
                    if score > game_data["high_scores"]["runner"]:
                        game_data["high_scores"]["runner"] = score
                        save_game(game_data)

        # Draw
        col = C_ACCENT if not game_over else C_SEC
        pygame.draw.rect(screen, col, player)
        
        for obs in obstacles:
            pygame.draw.rect(screen, C_WARN, obs)
            
        screen.blit(font_lg.render(f"Score: {score}", True, C_TEXT), (WIDTH//2 - 50, 50))
        screen.blit(font_sm.render(f"High Score: {game_data['high_scores']['runner']}", True, C_WARN), (WIDTH//2 - 60, 90))

        if game_over:
            screen.blit(font_xl.render("GAME OVER", True, C_SEC), (WIDTH//2 - 150, HEIGHT//2 - 50))
            screen.blit(font_md.render("Press SPACE to Restart | ESC to Exit", True, C_TEXT), (WIDTH//2 - 200, HEIGHT//2 + 20))

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT: sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    if game_over: return void_runner() # Restart
                    if not is_jumping:
                        velocity_y = -16
                        is_jumping = True
                if event.key == pygame.K_ESCAPE: return

# --- 6. SIMPLE MINI GAMES ---
def pong_game():
    ball = pygame.Rect(WIDTH//2, HEIGHT//2, 20, 20)
    paddle = pygame.Rect(WIDTH - 40, HEIGHT//2, 20, 100)
    ball_spd = [6, 6]
    
    while True:
        clock.tick(60)
        screen.fill(C_BG)
        pygame.draw.rect(screen, C_PANEL, (WIDTH//2 - 2, 0, 4, HEIGHT)) # Net
        
        ball.x += ball_spd[0]
        ball.y += ball_spd[1]
        
        if ball.top <= 0 or ball.bottom >= HEIGHT: ball_spd[1] *= -1
        if ball.left <= 0: ball_spd[0] *= -1 # Wall bounce
        if ball.colliderect(paddle): ball_spd[0] *= -1
        if ball.right > WIDTH: 
            ball.x, ball.y = WIDTH//2, HEIGHT//2 # Reset
        
        # AI Follow
        if paddle.centery < ball.centery: paddle.y += 5
        if paddle.centery > ball.centery: paddle.y -= 5

        pygame.draw.ellipse(screen, C_ACCENT, ball)
        pygame.draw.rect(screen, C_SEC, paddle)
        screen.blit(font_md.render("Press ESC to Exit", True, C_TEXT), (20, 20))
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT: sys.exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE: return

def snake_game():
    # A simplified placeholder for Snake to keep code length manageable
    # In a full repo, this would be a full class
    screen.fill(C_BG)
    screen.blit(font_lg.render("Snake Module Loaded...", True, C_ACCENT), (100, 100))
    pygame.display.flip()
    time.sleep(1) # Simulated loading

def reaction_test():
    screen.fill(C_BG)
    screen.blit(font_lg.render("Click when GREEN!", True, C_TEXT), (300, 300))
    pygame.display.flip()
    time.sleep(random.uniform(1, 3))
    
    start = time.time()
    screen.fill(C_SUCCESS)
    pygame.display.flip()
    
    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.MOUSEBUTTONDOWN:
                reaction = int((time.time() - start) * 1000)
                screen.fill(C_BG)
                screen.blit(font_lg.render(f"{reaction} ms", True, C_TEXT), (400, 300))
                pygame.display.flip()
                time.sleep(2)
                waiting = False
            if event.type == pygame.QUIT: sys.exit()

def magic_8_ball():
    answers = ["Yes", "No", "Ask Later", "Definitely", "Impossible"]
    ans = random.choice(answers)
    screen.fill(C_BG)
    screen.blit(font_xl.render(ans, True, C_ACCENT), (350, 300))
    pygame.display.flip()
    time.sleep(2)

def coin_flip():
    res = "HEADS" if random.random() > 0.5 else "TAILS"
    screen.fill(C_BG)
    screen.blit(font_xl.render(res, True, C_WARN), (400, 300))
    pygame.display.flip()
    time.sleep(1.5)

# --- 7. MAIN MENU (THE HUB) ---
def main_menu():
    games = [
        ("NEON CLICKER", ClickerGame().run),
        ("VOID RUNNER", void_runner),
        ("CYBER PONG", pong_game),
        ("REACTION TEST", reaction_test),
        ("MAGIC 8 BALL", magic_8_ball),
        ("COIN FLIP", coin_flip),
        ("EXIT", sys.exit)
    ]
    
    buttons = []
    for i, (name, func) in enumerate(games):
        x = 250
        y = 150 + (i * 70)
        buttons.append(Button(x, y, 500, 50, name))

    while True:
        screen.fill(C_BG)
        screen.blit(font_xl.render("/// NEXUS HUB ///", True, C_ACCENT), (280, 50))
        
        mouse_pos = pygame.mouse.get_pos()
        
        for i, btn in enumerate(buttons):
            btn.check_hover(mouse_pos)
            btn.draw(screen)
            # Run the associated function if clicked
            if pygame.mouse.get_pressed()[0] and btn.hovered:
                games[i][1]() # Call the function
                time.sleep(0.2) # Prevent double click

        pygame.display.flip()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()

if __name__ == "__main__":
    main_menu()
