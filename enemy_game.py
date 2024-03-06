# enemy_game.py
#
# /////////// INSTRUCTIONS /////////////////
#
# 👾 Let's make a game with an enemy game! 👾
#
# 📄 How to run the file
#     🎮▶️ Click the Play button 
#
#
# 📖 Offical Documentation
#      - https://pygame-zero.readthedocs.io
#      - https://pygame-zero.readthedocs.io/en/stable/ptext.html
#            - how to customize text
#      - https://quirkycort.github.io/tutorials/20-Pygame-Zero-Basics/10-Intro/10-intro.html
#
# ✅💻 TO DO ✅💻
#    1) Fix the image file links
#    2) Add more enemies
#    3) Customize the art and game settings 
#    4) If the player gets the gem, they won!
#           - create game won screen 
#           - how will you know if they won?
#    5) Can you prevent bullet spamming? 
#    
# ////////////////////////////////////////////

import pgzrun
from pgzhelper import *
import random

### 🎛 Controls game settings

# Setup the Screen Size
WIDTH = 600
HEIGHT = 600

# Setup the background image
background = Actor("water.jpeg")

# Setup the player
player = Actor("frog.png", anchor=("center", "bottom"))
player.scale = 2  # scales the sprite image
player.x = 30  # sets the X position
player.y = HEIGHT / 2  # sets the Y position
player.velocityX = 5
player.velocityY = 5


# Sets up enemies 
enemy_list = []

for i in range(3):
    enemy = Actor("alien.png")
    enemy.scale = 1
    enemy.y = random.randint(75, 600)
    enemy.x = random.randint(75, 600)
    enemy.velocityY = 5
    
    enemy_list.append(enemy)

# Setup tracking if game is running
game_running = True

# Setup score
score = 0

# Sets up bullet_list
bullet_list = []

# Sets up gem
# creates a gem sprite
gem = Actor("gem.png")
gem.scale = 1
gem.x = 550
gem.y = random.randint(20, HEIGHT - 50)


def draw():

    if game_running == True:
        background.draw()

        screen.draw.text(f"Score: {str(score)}", centerx=WIDTH / 2, centery=HEIGHT / 6)

        player.draw()
        gem.draw()

        for enemy in enemy_list:
            enemy.draw()


        for bullet in bullet_list:
            bullet.draw()

    else:
        screen.fill((149, 161, 171))

        screen.draw.text(f"Score: {str(score)}", centerx=WIDTH / 2, centery=HEIGHT / 6)
        screen.draw.text(f"GAME OVER", centerx=(WIDTH / 2) + 100, centery=HEIGHT / 2)


def update():
    global ENEMY_VELOCITY, game_running, score

    # controls keyboard presses 
    if keyboard.w:
        player.y -= player.velocityY
        
    if keyboard.s:
        player.y += player.velocityY
        
    if keyboard.a:
        player.x -= player.velocityX
        
    if keyboard.d:
        player.x += player.velocityX
        
    # creates bullet if space bar is pressed 
    if keyboard.space:
        bullet = Actor('laser_sprite.png', anchor=("center", "bottom"))
        bullet.scale = 0.05
        bullet.angle = player.angle
        bullet.x = player.x
        bullet.y = player.y
        bullet_list.append(bullet)

    # controls enemy movement 
    for enemy in enemy_list:
        enemy.y += enemy.velocityY

        if enemy.y < 20 or enemy.y > 550:
            enemy.velocityY *= -1

    
    # loop through for enemy
    for enemy in enemy_list:
        
        # if player hits the enemy
        if player.colliderect(enemy):
            
            # end the game 
            game_running = False

    # loop through each bullet
    for bullet in bullet_list:
        
        # move the bullet to the right
        bullet.x = bullet.x + 5
        
        # if the bullet is off the screen, kill it
        if bullet.x > WIDTH:
            bullet_list.remove(bullet)
            
        # loop through each enemy 
        for enemy in enemy_list:
            
            # if a bullet hits an enemy, kill the enemy and bullet
            if bullet.colliderect(enemy):
                enemy_list.remove(enemy)
                bullet_list.remove(bullet)
                
                score += 1

pgzrun.go()
