import os, pygame

SIZE = WIDTH, HEIGHT = 1200, 700
ACC = 0.25
MAX_VEL = 6
DECEL_RATE = ACC/2
AIR_ACC = ACC/2
GRAVITY = 1
JUMP_SPEED = 16
SCROLL_WIDTH = WIDTH*0.5
JOY = False
SCROLLING = False
SCROLLING_PLAYER = None
BOUNCE = 5
BLOCK_SIZE = 50
IFRAMES = 120
MENU_FPS = 10
ASSETS_PATH = os.path.join(os.path.dirname(__file__), '..','assets')
LEGAL_CHARS = [pygame.K_0, pygame.K_1, pygame.K_2,pygame.K_3,pygame.K_4,pygame.K_5,pygame.K_6,pygame.K_7,pygame.K_8,pygame.K_9,
pygame.K_a,pygame.K_b,pygame.K_c,pygame.K_d,pygame.K_e,pygame.K_f,pygame.K_g,pygame.K_h,pygame.K_i,pygame.K_j,pygame.K_l,pygame.K_m,
pygame.K_n,pygame.K_o,pygame.K_p,pygame.K_q,pygame.K_r,pygame.K_s,pygame.K_t,pygame.K_u,pygame.K_v,pygame.K_w,pygame.K_x,pygame.K_y,
pygame.K_z,pygame.K_SPACE]