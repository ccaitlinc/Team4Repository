import pygame
import sys

pygame.init()

WIDTH = 1000
HEIGHT = 700

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Laser Tag System")

clock = pygame.time.Clock()

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
