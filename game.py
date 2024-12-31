from pynput import keyboard
from pynput.keyboard import Key
import os, sys
import curses
import time
import random
#stdscr = curses.initscr()

#curses.noecho()
#curses.cbreak()
#stdscr.keypad(True)

WIDTH = 40
HEIGHT = 20
matrix = [' '] * WIDTH * HEIGHT
sprites = []
FPS = 60
arrows = [False] * 4
lives = 3



def display():
    global matrix
    print('\033c', end="")
    print('$' + '-'*(WIDTH) + '$')
    print('|' + ' '*(WIDTH//2) + str(lives)+' '*(WIDTH//2+WIDTH%2-1) + '|')
    print('$' + '-'*(WIDTH) + '$')
    for i in range(HEIGHT):
        print('|', end="")
        for j in range(WIDTH):
            print(matrix[i*WIDTH + j], end="")
        print('|')
    print('$' + '-'*(WIDTH) + '$')

def on_press(key):
    global matrix
    if key == Key.right:
        arrows[0] = True
    elif key == Key.left:
        arrows[1] = True
    elif key == Key.up:
        arrows[2] = True
    elif key == Key.down:
        arrows[3] = True
    elif key == Key.esc:
        exit()

listener = keyboard.Listener(on_press=on_press)
listener.start()


class Sprite():
    def __init__(self):
        sprites.append(self)
    def kill(self):
        sprites.remove(self)
    def display(self):
        global matrix, HEIGHT, WIDTH
        matrix[self.y * WIDTH + self.x] = self.c

class Player(Sprite):
    c = '#'
    def __init__(self):
        super().__init__()
        self.x = 3
        self.y = 4
        

    def update(self):
        global arrows, WIDTH, HEIGHT, lives
        if arrows[2]: self.y = max(self.y -1, 0)
        if arrows[3]: self.y = min(self.y +1, HEIGHT - 1)
        if arrows[0]:
            Bullet(self.x+1, self.y)
        arrows = [False] * 4
        self.display()
        if lives <= 0:
            self.kill()
        
class Bullet(Sprite):
    c = '*'
    move_speed = 0.05
    def __init__(self, x, y):
        super().__init__()
        self.x = x
        self.y = y
        self.start = time.time()

    def update(self):
        global WIDTH, HEIGHT, sprites
        self.display()
        if time.time()-self.start > self.move_speed:
            self.start = time.time()
            self.x += 1
        for s in sprites:
            if type(s) == Enemy and s.x == self.x and s.y == self.y:
                s.kill()
                self.kill()
                return

        if self.x >= WIDTH:
            self.kill()

class BulletEnemy(Sprite):
    c = '-'
    move_speed = 0.05
    def __init__(self, x, y):
        super().__init__()
        self.x = x
        self.y = y
        self.start = time.time()

    def update(self):
        global WIDTH, HEIGHT, sprites, lives
        self.display()
        if time.time()-self.start > self.move_speed:
            self.start = time.time()
            self.x -= 1
        for s in sprites:
            if type(s) == Player and s.x == self.x and s.y == self.y:
                lives -= 1
                self.kill()
                return
        if self.x <= 0:
            self.kill()
        

class Enemy(Sprite):
    c = '<'
    move_speed = 1
    shoot_percent = 0.006
    def __init__(self, x, y):
        super().__init__()
        self.x = x
        self.y = y
        self.move_direction = 1
        self.moving_time = 0
        self.start = time.time()

    def update(self):
        global WIDTH, HEIGHT
        if time.time()-self.start > self.move_speed:
            self.start = time.time()
            self.y += self.move_direction
            if self.moving_time >= 4:
                self.move_direction = -self.move_direction
                self.moving_time = 0
            self.moving_time += 1
        if random.randint(1, 10000)/10000 <= self.shoot_percent:
            BulletEnemy(self.x-1, self.y)
        self.display()
        
        
enemy_count = 1

def update():
    global sprites, matrix, enemy_count
    matrix = [' '] * WIDTH * HEIGHT
    enemy_count = 0
    for s in sprites:
        s.update()
        if type(s) == Enemy:
            enemy_count += 1
        
def loop():
    global FPS
    while lives and enemy_count:

        start = time.time()
        
        update()
        display()

        end = time.time()
        length = end - start
        if length < 1 / FPS:
            time.sleep(1 / FPS - length)
    return lives > 0
        
def main():
    global sprites
    Player()
    for x in range(34, 39, 2):
        for y in range(3, 15, 3):
            Enemy(x, y)

    if loop():
        for i, c in enumerate(list("You Won!")):
            print(i, c, (HEIGHT//2) * WIDTH + WIDTH//2-5 + i)
            matrix[(HEIGHT//2) * WIDTH + WIDTH//2-5 + i] = c
    else:
        for i, c in enumerate(list("You Lost!")):
            print(i, c, (HEIGHT//2) * WIDTH + WIDTH//2-5 + i)
            matrix[(HEIGHT//2) * WIDTH + WIDTH//2-5 + i] = c
    display()
    #if os.environ.get("DISABLE_COLOR", '').lower() != "true":
    #print(f'\033[38;2;{r%255};{g%255};{b%255}m', end="")
    

if __name__ == "__main__":
    main()