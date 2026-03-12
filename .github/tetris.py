import pygame
import sys
import random
import os

# --- 1. CONFIGURACIÓN PARA REMOTE X11 ---
# Forzamos el driver de video a X11 para que funcione con la extensión.
# Si el audio sigue dando problemas, mantenemos el driver 'dummy'.
os.environ['SDL_VIDEODRIVER'] = 'x11'
os.environ['SDL_AUDIODRIVER'] = 'dummy'

# Si Remote X11 no configura automáticamente la variable DISPLAY, 
# la establecemos por defecto al valor estándar.
if 'DISPLAY' not in os.environ:
    os.environ['DISPLAY'] = ':0'

pygame.init()
try:
    pygame.mixer.init()
except Exception as e:
    print(f"Aviso: Audio desactivado ({e}).")

# Colores (RGB)
NEGRO = (10, 10, 20)
BLANCO = (255, 255, 255)
GRIS_CLARO = (200, 200, 200)
AZUL_CRUZETA = (50, 50, 255)
ROJO = (255, 50, 50)
VERDE = (50, 255, 50)

# Dimensiones del juego
FILAS, COLUMNAS, TAMANO_BLOQUE = 20, 10, 30
ANCHO_TABLERO = COLUMNAS * TAMANO_BLOQUE
ALTO_TABLERO = FILAS * TAMANO_BLOQUE
MARGEN_LATERAL = 200
ANCHO_PANTALLA = ANCHO_TABLERO + MARGEN_LATERAL * 2
ALTO_PANTALLA = ALTO_TABLERO + 60

# Configuración de la ventana
try:
    PANTALLA = pygame.display.set_mode((ANCHO_PANTALLA, ALTO_PANTALLA))
    pygame.display.set_caption("Tetris Mouse Edition - Remote X11")
except pygame.error as e:
    print(f"ERROR: No se pudo conectar al servidor X11. Detalle: {e}")
    print("Asegúrate de que Remote X11 esté activo y configurado correctamente.")
    sys.exit(1)

RELOJ = pygame.time.Clock()
FPS = 60

# Fuentes
def get_font(size, bold=True):
    return pygame.font.SysFont('sans-serif', size, bold=bold)

FUENTE_PEQUENA = get_font(16)
FUENTE_MEDIA = get_font(24)
FUENTE_GRANDE = get_font(45)

# Tetrominos
TETROMINOS = [
    [['....', 'AAAA', '....', '....'], (0, 200, 200)], 
    [['.B.', '.B.', 'BB.'], (0, 0, 255)], 
    [['.C.', '.C.', '.CC'], (255, 165, 0)], 
    [['DD', 'DD'], (255, 255, 0)], 
    [['.EE', 'EE.'], (0, 255, 0)], 
    [['FFF', '.F.'], (128, 0, 128)], 
    [['GG.', '.GG'], (255, 0, 0)]
]

# --- 2. CLASES ---

class Particula:
    def __init__(self, x, y, color):
        self.x, self.y = x, y
        self.color = color
        self.vel_x = random.uniform(-3, 3)
        self.vel_y = random.uniform(-5, -1)
        self.vida = 40
        self.alpha = 255
    def update(self):
        self.x += self.vel_x
        self.y += self.vel_y
        self.vel_y += 0.2
        self.vida -= 1
        self.alpha = max(0, int(255 * (self.vida / 40)))
        return self.vida > 0
    def draw(self, screen):
        s = pygame.Surface((4, 4))
        s.fill(self.color)
        s.set_alpha(self.alpha)
        screen.blit(s, (int(self.x), int(self.y)))

class Tablero:
    def __init__(self):
        self.grid = [[(0,0,0)] * COLUMNAS for _ in range(FILAS)]
        self.particulas = []
        self.score = 0
        self.level = 1
        self.game_over = False

    def is_valid_space(self, shape, pos):
        for i, fila in enumerate(shape):
            for j, col in enumerate(fila):
                if col != '.':
                    x, y = pos[0] + j, pos[1] + i
                    if not (0 <= x < COLUMNAS and y < FILAS):
                        return False
                    if y >= 0 and self.grid[y][x] != (0,0,0):
                        return False
        return True

    def place_piece(self, piece):
        for i, fila in enumerate(piece.shape):
            for j, col in enumerate(fila):
                if col != '.':
                    if piece.y + i >= 0:
                        self.grid[piece.y + i][piece.x + j] = piece.color
        self.check_lines()

    def check_lines(self):
        lineas_llenas = [i for i, fila in enumerate(self.grid) if (0,0,0) not in fila]
        if lineas_llenas:
            for r in lineas_llenas:
                for c in range(COLUMNAS):
                    for _ in range(4):
                        px = (ANCHO_PANTALLA//2 - ANCHO_TABLERO//2) + c * TAMANO_BLOQUE + 15
                        py = 50 + r * TAMANO_BLOQUE + 15
                        self.particulas.append(Particula(px, py, self.grid[r][c]))
            for r in sorted(lineas_llenas, reverse=True):
                self.grid.pop(r)
                self.grid.insert(0, [(0,0,0)] * COLUMNAS)
            puntos = [0, 100, 300, 500, 1000]
            self.score += puntos[min(len(lineas_llenas), 4)] * self.level
            self.level = self.score // 1000 + 1

    def draw(self, screen):
        ox = ANCHO_PANTALLA // 2 - ANCHO_TABLERO // 2
        for i in range(FILAS):
            for j in range(COLUMNAS):
                pygame.draw.rect(screen, self.grid[i][j], (ox + j*TAMANO_BLOQUE, 50 + i*TAMANO_BLOQUE, TAMANO_BLOQUE, TAMANO_BLOQUE))
                pygame.draw.rect(screen, (30, 30, 50), (ox + j*TAMANO_BLOQUE, 50 + i*TAMANO_BLOQUE, TAMANO_BLOQUE, TAMANO_BLOQUE), 1)
        for p in self.particulas: p.draw(screen)

class Pieza:
    def __init__(self, x, y, data):
        self.x, self.y = x, y
        self.shape_data = data
        self.shape = data[0]
        self.color = data[1]
    def rotate(self):
        m = [list(f) for f in self.shape]
        nueva = ["".join(f) for f in zip(*m[::-1])]
        return nueva
    def draw(self, screen, ox, oy, ghost=False):
        c = self.color if not ghost else (40, 40, 60)
        for i, fila in enumerate(self.shape):
            for j, col in enumerate(fila):
                if col != '.':
                    pygame.draw.rect(screen, c, (ox + (self.x + j)*TAMANO_BLOQUE, oy + (self.y + i)*TAMANO_BLOQUE, TAMANO_BLOQUE, TAMANO_BLOQUE))

class Cruceta:
    def __init__(self, x, y, size):
        self.rect_base = pygame.Rect(x, y, size, size)
        self.lado = size // 3
        self.btns = {
            "UP": pygame.Rect(x + self.lado, y, self.lado, self.lado),
            "LEFT": pygame.Rect(x, y + self.lado, self.lado, self.lado),
            "DOWN": pygame.Rect(x + self.lado, y + self.lado, self.lado, self.lado),
            "RIGHT": pygame.Rect(x + 2*self.lado, y + self.lado, self.lado, self.lado)
        }
    def draw(self, screen):
        pygame.draw.rect(screen, (30, 30, 50), self.rect_base, 0, 10)
        for k, r in self.btns.items():
            pygame.draw.rect(screen, AZUL_CRUZETA, r, 0, 5)
            pygame.draw.rect(screen, BLANCO, r, 1, 5)

# --- 3. LÓGICA PRINCIPAL ---

def main():
    print("Iniciando ventana gráfica en X11...")
    tablero = Tablero()
    def gen(): return Pieza(COLUMNAS//2 - 2, 0, random.choice(TETROMINOS))
    
    curr = gen()
    next_p = gen()
    fall_time = 0
    ox, oy = ANCHO_PANTALLA//2 - ANCHO_TABLERO//2, 50
    cruceta = Cruceta(40, ALTO_PANTALLA - 160, 120)

    running = True
    while running:
        dt = RELOJ.tick(FPS)
        m_pos = pygame.mouse.get_pos()
        
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                running = False
            
            if e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
                # Control por cruceta (Mouse)
                if cruceta.btns["UP"].collidepoint(m_pos):
                    nueva = curr.rotate()
                    if tablero.is_valid_space(nueva, (curr.x, curr.y)): curr.shape = nueva
                if cruceta.btns["LEFT"].collidepoint(m_pos) and tablero.is_valid_space(curr.shape, (curr.x-1, curr.y)): curr.x -= 1
                if cruceta.btns["RIGHT"].collidepoint(m_pos) and tablero.is_valid_space(curr.shape, (curr.x+1, curr.y)): curr.x += 1
                if cruceta.btns["DOWN"].collidepoint(m_pos) and tablero.is_valid_space(curr.shape, (curr.x, curr.y+1)): curr.y += 1

            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_LEFT and tablero.is_valid_space(curr.shape, (curr.x-1, curr.y)): curr.x -= 1
                if e.key == pygame.K_RIGHT and tablero.is_valid_space(curr.shape, (curr.x+1, curr.y)): curr.x += 1
                if e.key == pygame.K_DOWN and tablero.is_valid_space(curr.shape, (curr.x, curr.y+1)): curr.y += 1
                if e.key == pygame.K_UP:
                    nueva = curr.rotate()
                    if tablero.is_valid_space(nueva, (curr.x, curr.y)): curr.shape = nueva

        if not tablero.game_over:
            fall_time += dt
            velocidad = max(100, 1000 - (tablero.level * 100))
            if fall_time > velocidad:
                if tablero.is_valid_space(curr.shape, (curr.x, curr.y + 1)):
                    curr.y += 1
                else:
                    tablero.place_piece(curr)
                    curr = next_p
                    next_p = gen()
                    if not tablero.is_valid_space(curr.shape, (curr.x, curr.y)):
                        tablero.game_over = True
                fall_time = 0
            tablero.particulas = [p for p in tablero.particulas if p.update()]

        # DIBUJAR
        PANTALLA.fill(NEGRO)
        tablero.draw(PANTALLA)
        
        # Pieza fantasma
        old_y = curr.y
        while tablero.is_valid_space(curr.shape, (curr.x, curr.y + 1)): curr.y += 1
        curr.draw(PANTALLA, ox, oy, True)
        curr.y = old_y
        
        # Pieza actual
        curr.draw(PANTALLA, ox, oy)
        
        # UI
        cruceta.draw(PANTALLA)
        infox = ox + ANCHO_TABLERO + 40
        PANTALLA.blit(FUENTE_MEDIA.render(f"PUNTOS: {tablero.score}", True, BLANCO), (infox, 80))
        PANTALLA.blit(FUENTE_PEQUENA.render("SIGUIENTE:", True, GRIS_CLARO), (infox, 140))
        next_p.draw(PANTALLA, infox - (next_p.x * TAMANO_BLOQUE), 180)
        
        if tablero.game_over:
            txt = FUENTE_GRANDE.render("GAME OVER", True, ROJO)
            PANTALLA.blit(txt, txt.get_rect(center=(ANCHO_PANTALLA//2, ALTO_PANTALLA//2)))

        pygame.display.flip()
    
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()