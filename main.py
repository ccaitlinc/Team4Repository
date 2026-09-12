import pygame
import sys

pygame.init()

WIDTH = 1000
HEIGHT = 700

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Laser Tag System")

clock = pygame.time.Clock()

def show_splash_screen(screen):
   logo = pygame.image.load("assets/logo.jpg").convert()

   logo = pygame.transform.smoothscale(logo, (500, 500))

   screen.fill((0, 0, 0))

   x = (screen.get_width() - logo.get_width()) // 2
   y = (screen.get_height() - logo.get_height()) // 2

   screen.blit(logo, (x, y))

   pygame.display.flip()

   pygame.time.wait(3000)

show_splash_screen(screen)

running = True

while running:
   for event in pygame.event.get():
      if event.type == pygame.QUIT:
         running = False

   screen.fill((0, 0, 0))

   pygame.display.flip()
   
   clock.tick(60)

pygame.quit()
sys.exit()

