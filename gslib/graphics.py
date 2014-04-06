import pygame
try:
    from cStringIO import StringIO as BytesIO
except ImportError:
    from io import BytesIO


# import Maps
from gslib.constants import *

# screen = pygame.display.set_mode((800, 800))
blue = pygame.Color(0, 255, 0)


def draw_game_over(game_class):
    font = pygame.font.SysFont('helvetica', 80)
    size = font.size("GAME OVER")
    margin = (game_class.dimensions[0] - size[0]) / 2
    game_class.screen_objects_to_draw.append((font.render("GAME OVER", True, (255, 255, 255)), (margin, 100)))

    font = pygame.font.SysFont('helvetica', 20)
    size = font.size("press esc scrub")
    margin = (game_class.dimensions[0] - size[0]) / 2
    game_class.screen_objects_to_draw.append((font.render("press esc scrub", True, (255, 255, 255)), (margin, 200)))


def draw_map(game_class):
    m = game_class.map
    grid_size = TILE_SIZE
    nw = len(m.grid)
    nh = len(m.grid[0])
    if not hasattr(game_class, 'map_surf'):
        game_class.map_surf = pygame.Surface((nw * grid_size, nh * grid_size)).convert()
    surf = game_class.map_surf

    for i in range(nw):
        for j in range(nh):
            area = m.grid[i][j].tileset_area
            if (not hasattr(game_class, 'clip_area')) or game_class.clip_area.colliderect(pygame.Rect((i * grid_size + 3 * grid_size / 2, j * grid_size + 3 * grid_size / 2), (grid_size, grid_size))):
                surf.blit(m.tileset, (i * grid_size, j * grid_size), area)

            ##TEMPORARY - DRAWS SOLID TILES FOR COLLISION DEBUG
            #if not m.grid[i][j].walkable:
            #    temprect = pygame.Rect(i * grid_size, j * grid_size, TILE_SIZE, TILE_SIZE)
            #    pygame.draw.rect(surf, 0x0000ff, temprect)

    game_class.world_objects_to_draw = [(surf, (0, 0))] + game_class.world_objects_to_draw


def draw_fps(game_class):
    font = pygame.font.SysFont('helvetica', 20)
    surf = font.render(u'FPS: ' + unicode(int(game_class.fps_clock.get_fps())), True, (255, 255, 0))
    game_class.screen_objects_to_draw.append((surf, (0, game_class.dimensions[1] - 100)))


def draw_buttons(game_class):
    for button in game_class.buttons.itervalues():
        game_class.screen_objects_to_draw.append((button.surface, button.pos))


def draw_objects(game_class):
    game_class.objects.sort((lambda x, y: cmp(x.coord[1], y.coord[1])))
    for o in game_class.objects:
        if o == game_class.player1:
            if o.possessing:
                continue
        surf = pygame.Surface((SPRITE_WIDTH, SPRITE_HEIGHT))
        surf.fill((255, 0, 255))
        surf.blit(o.sprite_sheet, (0, 0), o.frame_rect)
        surf.set_colorkey((255, 0, 255))
        game_class.world_objects_to_draw.append((surf, (o.coord[0] + o.dimensions[0] - SPRITE_WIDTH, o.coord[1] + o.dimensions[1] - SPRITE_HEIGHT)))


def draw_character_stats(game_class):
    if game_class.disp_object_stats:
        game_class.screen_objects_to_draw.append((game_class.object_stats[0], game_class.object_stats[1]))


def draw_fear_bar(game_class):
    if not hasattr(game_class, 'fear_txt'):
        font = pygame.font.SysFont('helvetica', 20)
        game_class.fear_size = font.size(u"FEAR")
        game_class.fear_txt = font.render(u"FEAR", True, (200, 200, 200)).convert_alpha()

    if not hasattr(game_class, 'fear_surf'):
        game_class.fear_surf = pygame.Surface((game_class.dimensions[0], 32)).convert_alpha()

    surf = game_class.fear_surf
    surf.blit(game_class.fear_txt, (0, 0))
    pygame.draw.rect(surf, (255, 0, 0), pygame.Rect((game_class.fear_size[0], 0), ((game_class.dimensions[0] - game_class.fear_size[0]) * (game_class.player1.fear/float(MAX_FEAR)), 32)))
    game_class.screen_objects_to_draw.append((surf, (0, game_class.dimensions[1] - 32)))


def draw_world_objects(game_class):  # stuff relative to camera
    for f in game_class.world_objects_to_draw:
        blit_camera(game_class, f[0], f[1])
    game_class.world_objects_to_draw = []


def draw_screen_objects(game_class):  # stuff relative to screen
    for f in game_class.screen_objects_to_draw:
        blit(game_class, f[0], f[1])
    game_class.screen_objects_to_draw = []


def blit(game_class, surf, pos):
    game_class.surface.blit(surf, pos)


def blit_camera(game_class, surf, pos):
    cpos = (pos[0] - game_class.camera_coords[0], pos[1] - game_class.camera_coords[1])
    game_class.surface.blit(surf, cpos)


def draw_cutscene(game):
    #print game.cutscene_started
    #print hasattr(game, 'movie')
    #print game.GameState

    if game.cutscene_started and hasattr(game, 'movie'):
        if not game.movie.get_busy():
            game.GameState = MAIN_GAME
            game.cutscene_started = False
            game.clock.get_time()  # hack required for pygame.game.movie linux
            del game.movie  # hack required for pygame.movie mac os x
    else:
        game.surface.fill(pygame.Color(0, 0, 0))
        pygame.display.update()
        try:
            f = BytesIO(open(game.cutscene_next, "rb").read())
            game.movie = pygame.movie.Movie(f)
            w, h = game.movie.get_size()
            game.movie.play()
            game.cutscene_started = True
        except IOError:
            print u"Video not found: " + game.cutscene_next
            game.GameState = MAIN_MENU


def draw_torch(game_class):
    ppos = (game_class.player1.coord[0] + game_class.player1.dimensions[0] / 2, game_class.player1.coord[1] + game_class.player1.dimensions[1] / 2)

    light_size = game_class.light.get_size()
    if not hasattr(game_class, 'hole_surf'):
        game_class.hole_surf = pygame.Surface((GAME_WIDTH, GAME_HEIGHT)).convert_alpha()
    surf = game_class.hole_surf
    surf.fill((0, 0, 0, 0))

    hole = pygame.Rect((ppos[0] - light_size[0]/2 - game_class.camera_coords[0], ppos[1] - light_size[1]/2 - game_class.camera_coords[1]), light_size)
    if hasattr(game_class, 'clip_area'):
        game_class.old_clip_area = game_class.clip_area
    game_class.clip_area = hole

    pygame.draw.rect(surf, (0, 0, 0, 255), pygame.Rect((0, 0), (GAME_WIDTH, hole.top)))
    pygame.draw.rect(surf, (0, 0, 0, 255), pygame.Rect((0, 0), (hole.left, GAME_HEIGHT)))
    pygame.draw.rect(surf, (0, 0, 0, 255), pygame.Rect((hole.right, 0), (GAME_WIDTH, GAME_HEIGHT)))
    pygame.draw.rect(surf, (0, 0, 0, 255), pygame.Rect((0, hole.bottom), (GAME_WIDTH, GAME_HEIGHT)))
    game_class.screen_objects_to_draw.append((surf, (0, 0)))
    game_class.world_objects_to_draw.append((game_class.light, (ppos[0] - light_size[0]/2, ppos[1] - light_size[1]/2)))


def draw_text_box(game_class):
    game_class.surface.blit(game_class.text_box_test.background_surface, (0, 0))
