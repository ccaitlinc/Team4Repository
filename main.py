import pygame
import sys
import argparse
import psycopg2
import udp
from pathlib import Path

parser = argparse.ArgumentParser(description="Photon Laser Tag player entry")
parser.add_argument(
    "--network-address",
    default="127.0.0.1",
    help="UDP destination IPv4 address (for example 192.168.1.255)",
)
args = parser.parse_args()
if not udp.set_network_address(args.network_address):
    parser.error("--network-address must be a valid IPv4 address")

pygame.init()

WIDTH = 1000
HEIGHT = 700

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Laser Tag System")

clock = pygame.time.Clock()

# connect to the PostgreSQL database
db = psycopg2.connect(dbname="photon", user="student")

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
START_BUTTON_RECT = pygame.Rect(700, 630, 120, 40) 
CLEAR_BUTTON_RECT = pygame.Rect(830, 630, 120, 40)


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

# game start countdown timer
countdown_active = False # tells program if countdown is currently running
countdown_start_time = 0 # records when countdown started
COUNTDOWN_SECONDS = 30 # duration of countdown = 30 seconds

#screen state variable 
current_screen = "entry"  # "entry", "countdown", or "play_action"

def show_splash_screen(screen):
   logo = pygame.image.load(Path(__file__).parent / "assets" / "logo.jpg").convert()

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
    cursor = db.cursor()

    cursor.execute("SELECT codename FROM players WHERE id = %s", (int(player_id),))

    result = cursor.fetchone()
    cursor.close()

    if result:
        return result[0]

    # meaning "not found, ask for a new codename"
    return None

def add_player(player_id, codename):
    cursor = db.cursor()

    cursor.execute("INSERT INTO players (id, codename) VALUES (%s, %s)", (int(player_id), codename))

    db.commit()
    cursor.close()

def update_player(player_id, codename):
    cursor = db.cursor()

    cursor.execute("UPDATE players SET codename = %s WHERE id = %s", (codename, int(player_id)))

    db.commit()
    cursor.close()

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

def start_game():
    global current_screen
    current_screen = "countdown"
    start_countdown()


def clear_all_entries():
    global red_team, green_team
    red_team = make_empty_team()
    green_team = make_empty_team()

# countdown function to calculate/display
def start_countdown():
    global countdown_active, countdown_start_time

    countdown_active = True
    countdown_start_time = pygame.time.get_ticks()

# function to calculate seconds left on timer
def get_countdown_seconds():
    elapsed = (pygame.time.get_ticks() - countdown_start_time) / 1000
    remaining = COUNTDOWN_SECONDS - int(elapsed)

    if remaining <= 0:
        return 0
    return remaining

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
            start_editing(team, row, "codename")
        else:
            # no id typed in, or not found in db -> ask for a new codename next
            start_editing(team, row, "codename")

    elif field == "codename":
        player_id = team_list[row]["id"]
        codename = team_list[row]["codename"]

        if lookup_codename(player_id) is None:
            add_player(player_id, codename)
        else:
            update_player(player_id, codename)

        if team_list[row]["equipment_id"] == "":
            start_equipment_prompt(team, row)


def handle_mouse_click(pos):
    if START_BUTTON_RECT.collidepoint(pos):
        start_game()
        return
    if CLEAR_BUTTON_RECT.collidepoint(pos):
        clear_all_entries()
        return

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

    if event.key == pygame.K_F5:
        start_game()
        return
    if event.key == pygame.K_F12:
        clear_all_entries()
        return
    
    if waiting_for_equipment:
        if event.key == pygame.K_RETURN:
            team, row = equipment_target
            get_team_list(team)[row]["equipment_id"] = equipment_input.strip()
            
            if equipment_input.strip().isdigit():
                udp.broadcast(equipment_input.strip())
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

# make 30-second countdown display
def draw_countdown_screen():
    screen.fill((0, 0, 0))

    title_surface = FONT.render("GAME STARTING", True, (255, 255, 255))
    screen.blit(title_surface, (400, 250))

    seconds = get_countdown_seconds()

    countdown_surface = pygame.font.SysFont("arial", 100).render(str(seconds), True, (255, 255, 0))
    countdown_rect = countdown_surface.get_rect(center=(WIDTH // 2, 400))
    screen.blit(countdown_surface, countdown_rect)

def draw_play_action_screen():
    screen.fill((0, 0, 0))

    label = FONT.render("PLAY ACTION SCREEN (events coming soon)", True, (255, 255, 255))
    label_rect = label.get_rect(center=(WIDTH // 2, HEIGHT // 2))
    screen.blit(label, label_rect)

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

    # buttons (Start Game, Clear Entries, etc)
    pygame.draw.rect(screen, (40, 40, 40), (50, 620, 900, 60))
    pygame.draw.rect(screen, (0, 120, 0), START_BUTTON_RECT)
    start_label = SMALL_FONT.render("Start (F5)", True, (255, 255, 255))
    screen.blit(start_label, (START_BUTTON_RECT.x + 10, START_BUTTON_RECT.y + 10))

    pygame.draw.rect(screen, (120, 0, 0), CLEAR_BUTTON_RECT)
    clear_label = SMALL_FONT.render("Clear (F12)", True, (255, 255, 255))
    screen.blit(clear_label, (CLEAR_BUTTON_RECT.x + 5, CLEAR_BUTTON_RECT.y + 10))



show_splash_screen(screen)

running = True

while running:
   for event in pygame.event.get():
      if event.type == pygame.QUIT:
         running = False
      elif event.type == pygame.MOUSEBUTTONDOWN:
            handle_mouse_click(event.pos)
      elif event.type == pygame.KEYDOWN:
            handle_key_input(event)
   incoming = udp.receive()
   if incoming:
       print(f"Received: {incoming}")

   if current_screen == "entry":
       draw_entry_screen()
   elif current_screen == "countdown":
       draw_countdown_screen()
       if get_countdown_seconds() == 0:
           current_screen = "play_action"
   elif current_screen == "play_action":
       draw_play_action_screen()

   pygame.display.flip()
   clock.tick(60)




pygame.quit()
sys.exit()
