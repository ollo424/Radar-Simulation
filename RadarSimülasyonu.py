import pygame
import simpy
import math
import random
import datetime

# --- YAPILANDIRMA VE RENK PALETİ ---
RIGHT_PANEL_W = 350
INITIAL_WIDTH, INITIAL_HEIGHT = 1200, 800
FPS = 60

# Renkler
BG_COLOR = (10, 15, 10)
UI_BG_COLOR = (20, 25, 20)
COLOR_WHITE = (200, 255, 200)
COLOR_RED = (255, 50, 50)
COLOR_CYAN = (50, 255, 255)
COLOR_RADAR = (0, 255, 0, 15)

# Pencere boyutlandıkça güncellenecek dinamik değerler
global_config = {
    'WIDTH': INITIAL_WIDTH,
    'HEIGHT': INITIAL_HEIGHT,
    'SIM_WIDTH': INITIAL_WIDTH - RIGHT_PANEL_W
}


# --- SINIFLAR ---

class EnemyAircraft:
    def __init__(self):
        self.x = random.randint(50, global_config['SIM_WIDTH'] - 50)
        self.y = random.randint(50, global_config['HEIGHT'] - 50)
        self.angle = random.uniform(0, 2 * math.pi)
        self.speed = 4.5
        self.active = True

    def update(self):
        if random.random() < 0.05:
            self.angle += random.uniform(-0.5, 0.5)

        self.x += math.cos(self.angle) * self.speed
        self.y += math.sin(self.angle) * self.speed

        sw = global_config['SIM_WIDTH']
        sh = global_config['HEIGHT']

        # Dinamik ekran sınırlarına çarpıp dönme
        if self.x < 20 or self.x > sw - 20:
            self.angle = math.pi - self.angle
            self.x = max(20, min(self.x, sw - 20))
        if self.y < 20 or self.y > sh - 20:
            self.angle = -self.angle
            self.y = max(20, min(self.y, sh - 20))

    def draw(self, surface):
        px, py = int(self.x), int(self.y)
        p1 = (px + math.cos(self.angle) * 15, py + math.sin(self.angle) * 15)
        p2 = (px + math.cos(self.angle + 2.5) * 10, py + math.sin(self.angle + 2.5) * 10)
        p3 = (px + math.cos(self.angle - 2.5) * 10, py + math.sin(self.angle - 2.5) * 10)
        pygame.draw.polygon(surface, COLOR_RED, [p1, p2, p3])
        pygame.draw.circle(surface, COLOR_RED, (px, py), 20, 1)


class WSN_Node:
    def __init__(self, name, x, y, role, parent=None):
        self.name = name
        self.x = x
        self.y = y
        self.role = role
        self.parent = parent
        self.range = 140 if role == 'sensor' else 0
        self.detected_target = None
        self.blinking = 0

    def detect(self, aircraft):
        if self.role == 'sensor':
            dist = math.hypot(aircraft.x - self.x, aircraft.y - self.y)
            if dist <= self.range:
                self.detected_target = (aircraft.x, aircraft.y)
            else:
                self.detected_target = None

    def draw(self, surface, font, is_dragged=False):
        if self.blinking > 0:
            self.blinking -= 1
            ring_radius = 15 - self.blinking
            pygame.draw.circle(surface, COLOR_CYAN, (self.x, self.y), ring_radius, 2)
            if self.parent and self.blinking % 2 == 0:
                pygame.draw.line(surface, COLOR_CYAN, (self.x, self.y), (self.parent.x, self.parent.y), 1)

        if self.role == 'sensor':
            temp_surface = pygame.Surface((self.range * 2, self.range * 2), pygame.SRCALPHA)

            area_color = (255, 50, 50, 30) if self.detected_target else COLOR_RADAR
            pygame.draw.circle(temp_surface, area_color, (self.range, self.range), self.range)
            pygame.draw.circle(temp_surface, (0, 200, 0, 100), (self.range, self.range), self.range, 1)
            surface.blit(temp_surface, (self.x - self.range, self.y - self.range))

            pin_radius = 6 if is_dragged else 4
            node_color = COLOR_RED if self.detected_target else COLOR_WHITE
            pygame.draw.circle(surface, node_color, (self.x, self.y), pin_radius)

            txt = font.render(self.name, True, COLOR_WHITE)
            surface.blit(txt, (self.x + 8, self.y - 10))

            if self.detected_target:
                pygame.draw.line(surface, COLOR_RED, (self.x, self.y),
                                 (int(self.detected_target[0]), int(self.detected_target[1])), 1)

        elif self.role == 'cluster_head':
            rect = pygame.Rect(self.x - 8, self.y - 8, 16, 16)
            pygame.draw.rect(surface, (0, 150, 0), rect)
            pygame.draw.rect(surface, COLOR_WHITE, rect, 1)
            txt = font.render(self.name, True, COLOR_WHITE)
            surface.blit(txt, (self.x + 12, self.y - 10))

        elif self.role == 'central':
            pygame.draw.polygon(surface, COLOR_CYAN,
                                [(self.x, self.y - 12), (self.x - 12, self.y + 12), (self.x + 12, self.y + 12)])
            txt = font.render(self.name, True, COLOR_CYAN)
            surface.blit(txt, (self.x - 20, self.y + 15))


# --- SIMPY SÜREÇLERİ ---

def wsn_network_process(env, nodes, central_log):
    sensors = [n for n in nodes if n.role == 'sensor']
    cluster_heads = [n for n in nodes if n.role == 'cluster_head']

    while True:
        yield env.timeout(0.4)
        for ch in cluster_heads:
            ch.active_detections = []
            for s in sensors:
                if s.parent == ch and s.detected_target:
                    s.blinking = 10
                    ch.active_detections.append((s.name, s.detected_target))

        yield env.timeout(0.2)
        for ch in cluster_heads:
            if ch.active_detections:
                ch.blinking = 15
                for s_name, (tx, ty) in ch.active_detections:
                    real_time = datetime.datetime.now().strftime("%H:%M:%S")
                    coord_str = f"X:{int(tx):03d} Y:{int(ty):03d}"
                    log_entry = f"[{real_time}] Radar {s_name} | {coord_str}"

                    central_log.insert(0, log_entry)

                    # Ekrana sığacak kadar veri tut (Panel yüksekliğine göre yaklaşık 40 satır yeterli)
        if len(central_log) > 40:
            central_log.pop()


# --- UI KONTROL PANELİ ---

def draw_right_dashboard(surface, central_log, font_large, font_med, font_small):
    sw = global_config['SIM_WIDTH']
    h = global_config['HEIGHT']

    ui_rect = pygame.Rect(sw, 0, RIGHT_PANEL_W, h)
    pygame.draw.rect(surface, UI_BG_COLOR, ui_rect)
    pygame.draw.rect(surface, (50, 60, 50), ui_rect, 4)

    x_base = sw + 20
    y_offset = 20

    title = font_large.render("KOMUTA MERKEZİ", True, COLOR_CYAN)
    surface.blit(title, (x_base, y_offset));
    y_offset += 30

    subtitle = font_small.render("CANLI KOORDİNAT AKIŞI", True, (150, 150, 150))
    surface.blit(subtitle, (x_base, y_offset));
    y_offset += 20

    pygame.draw.line(surface, (50, 100, 50), (x_base, y_offset), (sw + RIGHT_PANEL_W - 20, y_offset), 2)
    y_offset += 15

    for i, log_text in enumerate(central_log):
        # Yüksekliğe sığmayan logları çizme
        if y_offset > h - 30: break

        alpha = max(50, 255 - (i * 8))
        color = (100, alpha, 100) if i > 0 else (255, 50, 50)

        txt = font_med.render(log_text, True, color)
        surface.blit(txt, (x_base, y_offset))
        y_offset += 22


# --- ANA DÖNGÜ ---

def main():
    pygame.init()

    # pygame.RESIZABLE parametresi eklendi
    screen = pygame.display.set_mode((INITIAL_WIDTH, INITIAL_HEIGHT), pygame.RESIZABLE)
    pygame.display.set_caption("WSN Hava Savunma Radar Simülasyonu")
    clock = pygame.time.Clock()

    font_s = pygame.font.SysFont("Consolas", 12, bold=False)
    font_m = pygame.font.SysFont("Consolas", 14, bold=True)
    font_l = pygame.font.SysFont("Consolas", 18, bold=True)

    env = simpy.Environment()
    nodes = []
    central_log = []

    aircraft = EnemyAircraft()

    central = WSN_Node("MERKEZ", 750, 360, 'central')
    nodes.append(central)

    ch_1 = WSN_Node("CH-BATI", 250, 360, 'cluster_head', central)
    ch_2 = WSN_Node("CH-DOGU", 550, 360, 'cluster_head', central)
    nodes.extend([ch_1, ch_2])

    nodes.append(WSN_Node("R-1", 150, 150, 'sensor', ch_1))
    nodes.append(WSN_Node("R-2", 350, 200, 'sensor', ch_1))
    nodes.append(WSN_Node("R-3", 150, 550, 'sensor', ch_1))
    nodes.append(WSN_Node("R-4", 350, 500, 'sensor', ch_1))

    nodes.append(WSN_Node("R-5", 450, 150, 'sensor', ch_2))
    nodes.append(WSN_Node("R-6", 650, 200, 'sensor', ch_2))
    nodes.append(WSN_Node("R-7", 450, 550, 'sensor', ch_2))
    nodes.append(WSN_Node("R-8", 650, 500, 'sensor', ch_2))

    env.process(wsn_network_process(env, nodes, central_log))

    running, paused = True, False
    dragged_sensor = None
    sim_time, dt = 0.0, 1.0 / FPS
    scan_angle = 0

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT: running = False

            # PENCERE BOYUTLANDIRMA OLAYI
            if event.type == pygame.VIDEORESIZE:
                # Minimum pencere boyutunu sınırla
                new_w = max(800, event.w)
                new_h = max(600, event.h)
                screen = pygame.display.set_mode((new_w, new_h), pygame.RESIZABLE)

                global_config['WIDTH'] = new_w
                global_config['HEIGHT'] = new_h
                global_config['SIM_WIDTH'] = new_w - RIGHT_PANEL_W

                # Boyut küçüldüğünde ekran dışında kalan düğümleri içeri çek
                for n in nodes:
                    n.x = min(n.x, global_config['SIM_WIDTH'] - 20)
                    n.y = min(n.y, global_config['HEIGHT'] - 20)

            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                paused = not paused

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mx, my = pygame.mouse.get_pos()
                if mx < global_config['SIM_WIDTH']:
                    clicked_sensor = None
                    for node in nodes:
                        if node.role == 'sensor' and math.hypot(node.x - mx, node.y - my) < 20:
                            clicked_sensor = node
                            break
                    if clicked_sensor: dragged_sensor = clicked_sensor

            if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                dragged_sensor = None

            if event.type == pygame.MOUSEMOTION:
                if dragged_sensor:
                    mx, my = pygame.mouse.get_pos()
                    dragged_sensor.x = max(0, min(mx, global_config['SIM_WIDTH']))
                    dragged_sensor.y = max(0, min(my, global_config['HEIGHT']))

        if not paused:
            sim_time += dt
            scan_angle = (scan_angle + 0.05) % (2 * math.pi)
            env.run(until=sim_time)

            aircraft.update()
            for node in nodes: node.detect(aircraft)

        screen.fill(BG_COLOR)

        # Dinamik ızgara çizimi
        sw = global_config['SIM_WIDTH']
        h = global_config['HEIGHT']
        for x in range(0, sw, 50):
            pygame.draw.line(screen, (20, 30, 20), (x, 0), (x, h))
        for y in range(0, h, 50):
            pygame.draw.line(screen, (20, 30, 20), (0, y), (sw, y))

        for node in nodes: node.draw(screen, font_s, is_dragged=(node == dragged_sensor))
        aircraft.draw(screen)

        draw_right_dashboard(screen, central_log, font_l, font_m, font_s)

        inst_txt = font_m.render("DURAKLAT: SPACE | SENSÖRLERİ SÜRÜKLE", True, (100, 200, 100))
        screen.blit(inst_txt, (20, h - 30))

        if paused:
            p_txt = font_l.render("SIMÜLASYON DURDURULDU", True, COLOR_RED)
            screen.blit(p_txt, (sw // 2 - 100, 40))

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()


if __name__ == "__main__":
    main()