'''
Abdulaziz Junaid
ID: 145438
COMP3600

Part 1: The Dodger - SQU Student Survival
Aim: a pygame dodger game where an SQU student dodges university hazards
     (assignments, exams, parking fines, etc.) in front of the SQU clock tower.
     choose between 3 characters and survive as long as possible.

Controls : Arrow Keys or W A S D
Scoring  : +10 points per second survived
Lives    : 3 hearts

Image files that are used:
    background.jpg  - background image
    boy.png         - boy character sprite
    girl.png        - girl character sprite
    professor.png   - professor character sprite
'''

import pygame
import random
import math

WIN_W, WIN_H   = 920, 650
FPS            = 60
PLAYER_SPEED   = 5
MAX_LIVES      = 3
BASE_SPAWN_MS  = 1500
MIN_SPAWN_MS   = 350
INVINCIBLE_F   = 90

BLACK      = (  0,   0,   0)
WHITE      = (255, 255, 255)
RED        = (220,  45,  45)
GREEN      = ( 50, 200,  80)
YELLOW     = (255, 210,  30)
GOLD       = (212, 175,  55)
GRAY       = (130, 130, 130)
GLOW_BLUE  = ( 80, 150, 255)

HAZARDS = [
    {"label": ["ASSIGNMENT", "DUE!!"],   "color": (255, 230,  80), "w": 78, "h": 58},
    {"label": ["MIDTERM",    "EXAM!"],   "color": (240,  70,  70), "w": 82, "h": 60},
    {"label": ["PARKING",    "FINE!"],   "color": (255, 155,  30), "w": 76, "h": 50},
    {"label": ["LATE TO",    "CLASS!"],  "color": (100, 180, 255), "w": 82, "h": 52},
    {"label": ["SKIPPED",    "LECTURE"], "color": (180,  80, 200), "w": 85, "h": 55},
    {"label": ["MISSED",     "QUIZ!"],   "color": ( 80, 200, 130), "w": 74, "h": 52},
]


def load_image(filename):
    try:
        img = pygame.image.load(filename).convert_alpha()
        return img
    except Exception as e:
        raise SystemExit(f'Missing image: {filename} — {e}')


def scale_fit(surf, max_w, max_h):
    iw, ih = surf.get_size()
    scale  = min(max_w / iw, max_h / ih)
    return pygame.transform.scale(surf, (int(iw * scale), int(ih * scale)))


def draw_background(surf, bg_img):
    surf.blit(bg_img, (0, 0))


def draw_sprite(surf, x, y, inv, img):
    # blink when hit
    if inv > 0 and (inv // 6) % 2 == 0:
        return
    surf.blit(img, (x, y))


def character_select_screen(screen, clock, f_title, f_large, f_med, f_sm,
                             game_imgs, preview_imgs, bg_img):
    chars = [
        {"key": "boy",       "num": "1", "name": "Boy",
         "desc": ["SQU Student", "ready to cook (figuratively).", "unmatched aura."]},
        {"key": "girl",      "num": "2", "name": "Girl",
         "desc": ["SQU Student", "also has aura", "perfume overload."]},
        {"key": "professor", "num": "3", "name": "Doctor Noushath",
         "desc": ["Stepping into", "his students shoes.", "(Loves to give bonus marks)"]},
    ]

    CARD_W, CARD_H = 220, 340
    CARD_Y         = WIN_H//2 - CARD_H//2 + 20
    total_w        = CARD_W * 3 + 40 * 2
    start_x        = (WIN_W - total_w) // 2
    CARD_XS        = [start_x, start_x + CARD_W + 40, start_x + (CARD_W + 40) * 2]

    selected   = 0
    PREV_MAX_W = 120
    PREV_MAX_H = 160

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_1: selected = 0
                if event.key == pygame.K_2: selected = 1
                if event.key == pygame.K_3: selected = 2
                if event.key in (pygame.K_RETURN, pygame.K_SPACE, pygame.K_KP_ENTER):
                    return chars[selected]["key"]
                if event.key == pygame.K_LEFT:  selected = (selected - 1) % 3
                if event.key == pygame.K_RIGHT: selected = (selected + 1) % 3
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mx, my = event.pos
                for i, cx_card in enumerate(CARD_XS):
                    if cx_card <= mx < cx_card + CARD_W and CARD_Y <= my < CARD_Y + CARD_H:
                        if selected == i:
                            return chars[selected]["key"]
                        selected = i

        draw_background(screen, bg_img)
        ov = pygame.Surface((WIN_W, WIN_H), pygame.SRCALPHA)
        ov.fill((0, 0, 0, 140)); screen.blit(ov, (0, 0))

        t = f_title.render("SELECT YOUR CHARACTER", True, GOLD)
        screen.blit(t, (WIN_W//2 - t.get_width()//2, 50))
        sub = f_sm.render("Click a card  or  press  1 / 2 / 3  |  ENTER to confirm", True, (180, 180, 255))
        screen.blit(sub, (WIN_W//2 - sub.get_width()//2, 105))

        for i, char in enumerate(chars):
            cx_card  = CARD_XS[i]
            is_sel   = (i == selected)
            glow     = 4 if is_sel else 1
            card_col = (50, 60, 90) if is_sel else (35, 38, 55)
            border   = GLOW_BLUE   if is_sel else (80, 80, 110)
            pygame.draw.rect(screen, card_col, (cx_card, CARD_Y, CARD_W, CARD_H), border_radius=12)
            pygame.draw.rect(screen, border,   (cx_card, CARD_Y, CARD_W, CARD_H), glow, border_radius=12)
            num_surf = f_large.render(char["num"], True, GOLD)
            screen.blit(num_surf, (cx_card + 12, CARD_Y + 10))

            prev_surf   = preview_imgs[char["key"]]
            pw, ph      = prev_surf.get_size()
            prev_area_x = cx_card + CARD_W//2 - PREV_MAX_W//2
            prev_area_y = CARD_Y + 50
            pygame.draw.rect(screen, (25, 30, 50),
                             (prev_area_x - 6, prev_area_y - 6, PREV_MAX_W + 12, PREV_MAX_H + 12),
                             border_radius=6)
            blit_x = prev_area_x + (PREV_MAX_W - pw) // 2
            blit_y = prev_area_y + (PREV_MAX_H - ph) // 2
            screen.blit(prev_surf, (blit_x, blit_y))

            text_y    = CARD_Y + 50 + PREV_MAX_H + 18
            name_surf = f_med.render(char["name"], True, WHITE if is_sel else (200, 200, 220))
            screen.blit(name_surf, (cx_card + CARD_W//2 - name_surf.get_width()//2, text_y))
            for j, line in enumerate(char["desc"]):
                line_surf = f_sm.render(line, True, (200, 220, 255) if is_sel else GRAY)
                screen.blit(line_surf, (cx_card + CARD_W//2 - line_surf.get_width()//2,
                                        text_y + 24 + j * 18))
            if is_sel:
                sel_surf = f_sm.render("▶  SELECTED  ◀", True, GOLD)
                screen.blit(sel_surf, (cx_card + CARD_W//2 - sel_surf.get_width()//2,
                                       CARD_Y + CARD_H - 28))

        prompt = f_large.render("Press ENTER to start", True, GREEN)
        screen.blit(prompt, (WIN_W//2 - prompt.get_width()//2, WIN_H - 55))
        pygame.display.flip()
        clock.tick(FPS)


class Player:
    def __init__(self, character='boy', imgs=None):
        self.imgs      = imgs or {}
        self.character = character
        img            = self.imgs[character]
        self.W         = img.get_width()
        self.H         = img.get_height()
        self.x         = WIN_W//2 - self.W//2
        self.y         = WIN_H - self.H - 20
        self.lives     = MAX_LIVES
        self.inv       = 0

    @property
    def rect(self):
        return pygame.Rect(self.x + 5, self.y + 5, self.W - 10, self.H - 10)

    def update(self, keys):
        if keys[pygame.K_LEFT]  or keys[pygame.K_a]: self.x -= PLAYER_SPEED
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]: self.x += PLAYER_SPEED
        if keys[pygame.K_UP]    or keys[pygame.K_w]: self.y -= PLAYER_SPEED
        if keys[pygame.K_DOWN]  or keys[pygame.K_s]: self.y += PLAYER_SPEED
        self.x = max(0, min(WIN_W - self.W, self.x))
        self.y = max(60, min(WIN_H - self.H, self.y))
        if self.inv > 0: self.inv -= 1

    def hit(self):
        if self.inv == 0:
            self.lives -= 1; self.inv = INVINCIBLE_F; return True
        return False

    def draw(self, surf):
        draw_sprite(surf, self.x, self.y, self.inv, self.imgs[self.character])


class Hazard:
    def __init__(self, htype, speed_scale=1.0):
        self.w     = htype["w"]; self.h = htype["h"]
        self.color = htype["color"]; self.label = htype["label"]
        edge = random.choice(["top", "left", "right"])
        if edge == "top":
            self.x = random.randint(0, WIN_W - self.w); self.y = -self.h - 10
            angle  = random.uniform(60, 120)
        elif edge == "left":
            self.x = -self.w - 10; self.y = random.randint(0, WIN_H - 200)
            angle  = random.uniform(-40, 40)
        else:
            self.x = WIN_W + 10; self.y = random.randint(0, WIN_H - 200)
            angle  = random.uniform(140, 220)
        speed  = random.uniform(2.8, 5.2) * speed_scale
        self.vx = speed * math.cos(math.radians(angle))
        self.vy = speed * math.sin(math.radians(angle))
        self.spin  = random.uniform(-2.5, 2.5)
        self.angle = random.uniform(0, 360)
        self.active = True

    def update(self):
        self.x += self.vx; self.y += self.vy; self.angle += self.spin
        if (self.x < -200 or self.x > WIN_W + 200 or
                self.y < -200 or self.y > WIN_H + 200):
            self.active = False

    def draw(self, surf, font_sm):
        s = pygame.Surface((self.w + 4, self.h + 4), pygame.SRCALPHA)
        pygame.draw.rect(s, self.color, (0, 0, self.w, self.h), border_radius=5)
        pygame.draw.rect(s, BLACK,      (0, 0, self.w, self.h), 2, border_radius=5)
        for py in range(10, self.h - 8, 9):
            pygame.draw.line(s, (0, 0, 0, 60), (6, py), (self.w - 6, py), 1)
        fold = 14
        fc = tuple(max(0, c - 30) for c in self.color)
        pygame.draw.polygon(s, fc, [(self.w - fold, 0), (self.w, 0), (self.w, fold)])
        for i, line in enumerate(self.label):
            txt = font_sm.render(line, True, BLACK)
            ty  = self.h//2 - 9 * len(self.label)//2 + i * 16
            s.blit(txt, (self.w//2 - txt.get_width()//2, ty))
        rs = pygame.transform.rotate(s, self.angle)
        surf.blit(rs, (self.x - (rs.get_width()  - self.w) // 2,
                       self.y - (rs.get_height() - self.h) // 2))

    @property
    def rect(self):
        return pygame.Rect(self.x, self.y, self.w, self.h)


def draw_hud(surf, score, lives, level, char_name, f_med, f_sm):
    hud = pygame.Surface((WIN_W, 52), pygame.SRCALPHA)
    hud.fill((0, 0, 20, 170)); surf.blit(hud, (0, 0))
    pygame.draw.line(surf, GOLD, (0, 52), (WIN_W, 52), 1)
    surf.blit(f_med.render(f'Score: {score:,}', True, YELLOW), (18, 13))
    lvl_col = (200, 200, 255) if level < 4 else (255, 150, 80) if level < 7 else RED
    surf.blit(f_sm.render(f'Level {level}  |  {char_name}', True, lvl_col), (WIN_W//2 - 80, 17))
    for i in range(MAX_LIVES):
        hx = WIN_W - 30 - i * 38; hy = 8
        col = RED if i < lives else (60, 60, 80)
        pygame.draw.circle(surf, col, (hx - 8, hy + 10), 9)
        pygame.draw.circle(surf, col, (hx + 8, hy + 10), 9)
        pygame.draw.polygon(surf, col, [(hx - 16, hy + 14), (hx, hy + 34), (hx + 16, hy + 14)])
    surf.blit(f_sm.render('Lives:', True, WHITE), (WIN_W - 195, 17))


def draw_game_over(surf, score, char_name, f_title, f_large, f_med):
    ov = pygame.Surface((WIN_W, WIN_H), pygame.SRCALPHA)
    ov.fill((0, 0, 0, 170)); surf.blit(ov, (0, 0))
    surf.blit(f_title.render('GAME OVER', True, RED),
              (WIN_W//2 - f_title.size('GAME OVER')[0]//2, 180))
    lines      = [f'{char_name} couldn\'t dodge everything...',
                  f'Final Score: {score:,}',
                  'R — Try Again    |    Q — Quit']
    colors_lst = [WHITE, YELLOW, (180, 255, 180)]
    for i, (line, col) in enumerate(zip(lines, colors_lst)):
        fs = f_large if i == 1 else f_med
        s  = fs.render(line, True, col)
        surf.blit(s, (WIN_W//2 - s.get_width()//2, 270 + i * 65))


def draw_start_screen(surf, f_title, f_large, f_med, f_sm, bg_img):
    draw_background(surf, bg_img)
    ov = pygame.Surface((WIN_W, WIN_H), pygame.SRCALPHA)
    ov.fill((0, 0, 0, 120)); surf.blit(ov, (0, 0))
    surf.blit(f_title.render('SQU STUDENT SURVIVAL', True, GOLD),
              (WIN_W//2 - f_title.size('SQU STUDENT SURVIVAL')[0]//2, 100))
    surf.blit(f_med.render('Dodge all university hazards!', True, WHITE),
              (WIN_W//2 - 160, 165))
    surf.blit(f_med.render('Controls:  Arrow Keys  or  W A S D', True, (180, 220, 255)),
              (WIN_W//2 - 165, 215))
    preview_y = 300
    for i, h in enumerate(HAZARDS):
        px = 30 + i * 150
        pygame.draw.rect(surf, h["color"], (px, preview_y, h["w"], h["h"]), border_radius=4)
        pygame.draw.rect(surf, BLACK,      (px, preview_y, h["w"], h["h"]), 2, border_radius=4)
        for j, ln in enumerate(h["label"]):
            lt = f_sm.render(ln, True, BLACK)
            surf.blit(lt, (px + h["w"]//2 - lt.get_width()//2, preview_y + h["h"]//2 - 9 + j * 15))
    surf.blit(f_large.render('Press  SPACE  or  ENTER  to Begin', True, GREEN),
              (WIN_W//2 - 190, 435))
    surf.blit(f_sm.render('COMP3600 Intelligent Systems  |  Sultan Qaboos University', True, GRAY),
              (WIN_W//2 - 225, WIN_H - 28))


def main():
    pygame.init()
    screen = pygame.display.set_mode((WIN_W, WIN_H))
    pygame.display.set_caption('SQU Student Survival — The Dodger  |  COMP3600')
    clock  = pygame.time.Clock()

    f_title = pygame.font.SysFont('Arial', 42, bold=True)
    f_large = pygame.font.SysFont('Arial', 28, bold=True)
    f_med   = pygame.font.SysFont('Arial', 20)
    f_sm    = pygame.font.SysFont('Arial', 13, bold=True)

    # load images
    bg_img = pygame.transform.scale(load_image('background.jpg'), (WIN_W, WIN_H))
    raw = {
        'boy'       : load_image('boy.png'),
        'girl'      : load_image('girl.png'),
        'professor' : load_image('professor.png'),
    }
    game_imgs    = {k: scale_fit(v, 110, 150)  for k, v in raw.items()}
    preview_imgs = {k: scale_fit(v, 120, 160) for k, v in raw.items()}

    # start screen
    in_start = True
    while in_start:
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT: pygame.quit(); return
            if ev.type == pygame.KEYDOWN:
                if ev.key in (pygame.K_SPACE, pygame.K_RETURN, pygame.K_KP_ENTER):
                    in_start = False
        draw_start_screen(screen, f_title, f_large, f_med, f_sm, bg_img)
        pygame.display.flip(); clock.tick(FPS)

    # character select
    chosen = character_select_screen(screen, clock, f_title, f_large,
                                     f_med, f_sm, game_imgs, preview_imgs, bg_img)
    char_display_names = {'boy': 'Ahmad', 'girl': 'Fatma', 'professor': 'The Professor'}
    char_name = char_display_names.get(chosen, chosen)

    def new_game():
        return {
            'player'     : Player(chosen, game_imgs),
            'hazards'    : [],
            'score'      : 0,
            'frame'      : 0,
            'spawn_ms'   : BASE_SPAWN_MS,
            'spawn_timer': pygame.time.get_ticks(),
            'state'      : 'playing',
        }

    game    = new_game()
    running = True

    while running:
        now = pygame.time.get_ticks()
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT: running = False
            if ev.type == pygame.KEYDOWN:
                if ev.key == pygame.K_ESCAPE: running = False
                if game['state'] == 'game_over':
                    if ev.key == pygame.K_r: game = new_game()
                    elif ev.key == pygame.K_q: running = False

        if game['state'] == 'playing':
            keys = pygame.key.get_pressed()
            game['player'].update(keys)
            game['frame']  += 1
            game['score']   = (game['frame'] // FPS) * 10
            level  = game['frame'] // (FPS * 5) + 1
            target = max(MIN_SPAWN_MS, BASE_SPAWN_MS - level * 120)
            game['spawn_ms'] = target
            if now - game['spawn_timer'] >= game['spawn_ms']:
                game['spawn_timer'] = now
                game['hazards'].append(
                    Hazard(random.choice(HAZARDS), 1.0 + (level - 1) * 0.07))
            for hz in game['hazards']: hz.update()
            game['hazards'] = [hz for hz in game['hazards'] if hz.active]
            p = game['player']
            if p.inv == 0:
                for hz in game['hazards']:
                    if p.rect.colliderect(hz.rect):
                        if p.hit():
                            if p.lives <= 0: game['state'] = 'game_over'
                        break

        draw_background(screen, bg_img)
        for hz in game['hazards']: hz.draw(screen, f_sm)
        game['player'].draw(screen)
        draw_hud(screen, game['score'], game['player'].lives,
                 game['frame'] // (FPS * 5) + 1, char_name, f_med, f_sm)
        if game['state'] == 'game_over':
            draw_game_over(screen, game['score'], char_name, f_title, f_large, f_med)
        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()


if __name__ == '__main__':
    main()
