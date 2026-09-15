import pygame
import sys

pygame.init()

WIDTH = 1000
HEIGHT = 700

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Laser Tag System")

clock = pygame.time.Clock()

FONT = pygame.font.SysFont("arial", 20)
SMALL_FONT = pygame.font.SysFont("arial", 16)

MAX_PLAYERS_PER_TEAM = 15

# --- layout constants: change these if you want to move/resize things ---
TEAM_X = {"red": 50, "green": 550}
COLUMN_WIDTH = 400
HEADER_Y = 100
HEADER_HEIGHT = 40
ROW_START_Y = 145
ROW_HEIGHT = 28
NUMBER_WIDTH = 30
ID_WIDTH = 100
NAME_WIDTH = COLUMN_WIDTH - NUMBER_WIDTH - ID_WIDTH


def make_empty_team():
    # 15 empty player slots, so row 0 through row 14 always exist and can be clicked
    return [{"id": "", "codename": "", "equipment_id": ""} for _ in range(MAX_PLAYERS_PER_TEAM)]


red_team = make_empty_team()
green_team = make_empty_team()

# which cell (if any) is currently being typed into
active_team = None   # "red" or "green"
active_row = None    # 0-14
active_field = None  # "id" or "codename"
input_text = ""

# separate state just for the equipment id prompt at the bottom
waiting_for_equipment = False
equipment_target = None  # (team, row) tuple
equipment_input = ""

def show_splash_screen(screen):
   logo = pygame.image.load("assets/logo.jpg").convert()

   logo = pygame.transform.smoothscale(logo, (500, 500))

   screen.fill((0, 0, 0))

   x = (screen.get_width() - logo.get_width()) // 2
   y = (screen.get_height() - logo.get_height()) // 2

   screen.blit(logo, (x, y))

   pygame.display.flip()

   # changed logic due to a bug on mac 
   start_time = pygame.time.get_ticks()
   while pygame.time.get_ticks() - start_time < 3000:
        pygame.event.pump()
        clock.tick(60)

def lookup_codename(player_id):
    # TODO: replace this with a real database query later (psycopg2)
    # for now it always returns None, meaning "not found, ask for a new codename"
    return None


def get_team_list(team):
    return red_team if team == "red" else green_team


def get_id_rect(team, row):
    x = TEAM_X[team] + NUMBER_WIDTH
    y = ROW_START_Y + row * ROW_HEIGHT
    return pygame.Rect(x, y, ID_WIDTH, ROW_HEIGHT - 2)


def get_name_rect(team, row):
    x = TEAM_X[team] + NUMBER_WIDTH + ID_WIDTH
    y = ROW_START_Y + row * ROW_HEIGHT
    return pygame.Rect(x, y, NAME_WIDTH, ROW_HEIGHT - 2)


def start_editing(team, row, field):
    global active_team, active_row, active_field, input_text
    active_team = team
    active_row = row
    active_field = field
    # load whatever's already in that box, so you can edit existing entries
    input_text = get_team_list(team)[row][field]


def stop_editing():
    global active_team, active_row, active_field, input_text
    active_team = None
    active_row = None
    active_field = None
    input_text = ""


def start_equipment_prompt(team, row):
    global waiting_for_equipment, equipment_target, equipment_input
    waiting_for_equipment = True
    equipment_target = (team, row)
    equipment_input = get_team_list(team)[row]["equipment_id"]


def save_active_field():
    global active_field

    team_list = get_team_list(active_team)
    team = active_team
    row = active_row
    field = active_field

    team_list[row][field] = input_text.strip()
    stop_editing()

    if field == "id":
        player_id = team_list[row]["id"]
        codename = lookup_codename(player_id)
        if codename:
            team_list[row]["codename"] = codename
            if team_list[row]["equipment_id"] == "":
                start_equipment_prompt(team, row)
        else:
            # no id typed in, or not found in db -> ask for a new codename next
            start_editing(team, row, "codename")

    elif field == "codename":
        if team_list[row]["equipment_id"] == "":
            start_equipment_prompt(team, row)


def handle_mouse_click(pos):
    for team in ("red", "green"):
        for row in range(MAX_PLAYERS_PER_TEAM):
            if get_id_rect(team, row).collidepoint(pos):
                start_editing(team, row, "id")
                return
            if get_name_rect(team, row).collidepoint(pos):
                start_editing(team, row, "codename")
                return


def handle_key_input(event):
    global input_text, equipment_input, waiting_for_equipment, equipment_target

    if waiting_for_equipment:
        if event.key == pygame.K_RETURN:
            team, row = equipment_target
            get_team_list(team)[row]["equipment_id"] = equipment_input.strip()
            # TODO: broadcast this equipment_id over UDP port 7500 here, once sockets are set up
            waiting_for_equipment = False
            equipment_target = None
            equipment_input = ""
        elif event.key == pygame.K_BACKSPACE:
            equipment_input = equipment_input[:-1]
        elif event.unicode.isprintable():
            equipment_input += event.unicode
        return

    if active_team is None:
        return  # nothing selected, nothing to type into

    if event.key == pygame.K_RETURN:
        save_active_field()
    elif event.key == pygame.K_ESCAPE:
        stop_editing()  # cancel without saving
    elif event.key == pygame.K_BACKSPACE:
        input_text = input_text[:-1]
    elif event.unicode.isprintable():
        input_text += event.unicode


def draw_cell(rect, text, is_active):
    color = (255, 255, 150) if is_active else (230, 230, 230)
    pygame.draw.rect(screen, color, rect)
    pygame.draw.rect(screen, (0, 0, 0), rect, 1)  # border
    text_surface = SMALL_FONT.render(text, True, (0, 0, 0))
    screen.blit(text_surface, (rect.x + 4, rect.y + 4))


def draw_team_column(team, team_name, team_color):
    x = TEAM_X[team]
    pygame.draw.rect(screen, team_color, (x, HEADER_Y, COLUMN_WIDTH, HEADER_HEIGHT))
    label = FONT.render(team_name, True, (255, 255, 255))
    screen.blit(label, (x + 10, HEADER_Y + 8))

    team_list = get_team_list(team)

    for row in range(MAX_PLAYERS_PER_TEAM):
        row_y = ROW_START_Y + row * ROW_HEIGHT
        number_surface = SMALL_FONT.render(str(row), True, (255, 255, 255))
        screen.blit(number_surface, (x + 4, row_y + 5))

        is_id_active = (active_team == team and active_row == row and active_field == "id")
        is_name_active = (active_team == team and active_row == row and active_field == "codename")

        id_text = input_text if is_id_active else team_list[row]["id"]
        name_text = input_text if is_name_active else team_list[row]["codename"]

        draw_cell(get_id_rect(team, row), id_text, is_id_active)
        draw_cell(get_name_rect(team, row), name_text, is_name_active)


def draw_entry_screen():
    screen.fill((0, 0, 0))
    draw_team_column("red", "RED TEAM", (120, 0, 0))
    draw_team_column("green", "GREEN TEAM", (0, 100, 0))

    if waiting_for_equipment:
        team, row = equipment_target
        prompt = f"Enter Equipment ID for {team.upper()} row {row}: " + equipment_input
        prompt_surface = FONT.render(prompt, True, (255, 255, 0))
        screen.blit(prompt_surface, (50, 590))
    else:
        hint = "Click a Player ID or Codename box to edit it. Enter to confirm, Esc to cancel."
        hint_surface = SMALL_FONT.render(hint, True, (200, 200, 200))
        screen.blit(hint_surface, (50, 590))

    # reserved space for future sprint buttons (Start Game, Clear Entries, etc)
    pygame.draw.rect(screen, (40, 40, 40), (50, 620, 900, 60))
    future_label = SMALL_FONT.render(
        "F5: Start Game   |   F12: Clear All Entries   (coming in a later sprint)",
        True, (150, 150, 150)
    )
    screen.blit(future_label, (60, 645))


show_splash_screen(screen)

running = True

while running:
   for event in pygame.event.get():
      if event.type == pygame.QUIT:
         running = False
      elif event.type == pygame.MOUSEBUTTONDOWN and not waiting_for_equipment:
            handle_mouse_click(event.pos)
      elif event.type == pygame.KEYDOWN:
            handle_key_input(event)

  # screen.fill((0, 0, 0))

   draw_entry_screen()
   pygame.display.flip()
   
   clock.tick(60)




pygame.quit()
sys.exit()

