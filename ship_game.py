import math
import time
import threading
import random
import arcade

SCREEN_HEIGHT=600
SCREEN_WIDGHT=600
SMOKE_FADE_RATE = 7
SMOKE_RISE_RATE = 0.5
SMOKE_START_SCALE = 0.25
SMOKE_EXPANSION_RATE = 0.03
PARTICLE_FADE_RATE = 8
PARTICLE_RADIUS = 3
PARTICLE_MIN_SPEED = 2.5
PARTICLE_SPEED_RANGE = 2.5
SMOKE_CHANCE = 0.25
PARTICLE_SPARKLE_CHANCE = 0.02
PARTICLE_GRAVITY = 0.05
PARTICLE_COUNT = 20
PARTICLE_COLORS = [arcade.color.ALIZARIN_CRIMSON,
                   arcade.color.COQUELICOT,
                   arcade.color.LAVA,
                   arcade.color.KU_CRIMSON,
                   arcade.color.DARK_TANGERINE]

class Smoke(arcade.SpriteCircle):
    def __init__(self, size):
        super().__init__(size, arcade.color.LIGHT_GRAY, soft=True)
        self.change_y = SMOKE_RISE_RATE
        self.scale = SMOKE_START_SCALE

    def update(self):
        if self.alpha <= PARTICLE_FADE_RATE:
            self.remove_from_sprite_lists()
        else:
            self.alpha -= SMOKE_FADE_RATE
            self.center_x += self.change_x
            self.center_y += self.change_y
            self.scale += SMOKE_EXPANSION_RATE

class Particle(arcade.SpriteCircle):
    def __init__(self, my_list):
        color = random.choice(PARTICLE_COLORS)
        super().__init__(PARTICLE_RADIUS, color)
        self.normal_texture = self.texture
        self.my_list = my_list
        speed = random.random() * PARTICLE_SPEED_RANGE + PARTICLE_MIN_SPEED
        direction = random.randrange(360)
        self.change_x = math.sin(math.radians(direction)) * speed
        self.change_y = math.cos(math.radians(direction)) * speed
        self.my_alpha = 255
        self.my_list = my_list

    def update(self):
        if self.my_alpha <= PARTICLE_FADE_RATE:
            self.remove_from_sprite_lists()
        else:
            self.my_alpha -= PARTICLE_FADE_RATE
            self.alpha = self.my_alpha
            self.center_x += self.change_x
            self.center_y += self.change_y
            self.change_y -= PARTICLE_GRAVITY
            if random.random() <= PARTICLE_SPARKLE_CHANCE:
                self.alpha = 255
                self.texture = arcade.make_circle_texture(int(self.width), arcade.color.WHITE)
            else:
                self.texture = self.normal_texture
            if random.random() <= SMOKE_CHANCE:
                smoke = Smoke(5)
                smoke.position = self.position
                self.my_list.append(smoke)


class Big_Enemy(arcade.Sprite):
    def __init__(self):
        super().__init__(":resources:images/space_shooter/playerShip1_blue.png")
        self.center_x=300
        self.center_y=500
        self.width=100
        self.height=-100
        self.bullet=[]
        self.angle=0
        self.live=5
    
    def fire(self):
        self.angle=random.randint(90,270)
        arcade.play_sound(arcade.sound.Sound(':resources:sounds/explosion1.wav'), 0.2, 0.0,False)
        self.bullet.append(Bullet(self))

    def sound(self):
        arcade.play_sound(arcade.sound.Sound(':resources:sounds/upgrade2.wav'), 1.0, 0.0,False)

class Enemy(arcade.Sprite):
    def __init__(self,s):
        super().__init__(":resources:images/space_shooter/playerShip1_green.png")
        self.center_x=random.randint(self.width,SCREEN_WIDGHT-self.width)
        self.center_y=SCREEN_HEIGHT+self.height//2
        self.width=48
        self.height=-48
        self.speed=1+s
    
    def sound(self):
        arcade.play_sound(arcade.sound.Sound(':resources:sounds/explosion1.wav'), 1.0, 0.0,False)

    def move(self):
        self.center_y -=self.speed

class Ship(arcade.Sprite):
    def __init__(self):
        super().__init__(":resources:images/space_shooter/playerShip3_orange.png")
        self.center_x=SCREEN_WIDGHT//2
        self.center_y=32
        self.angle=0
        self.score=0
        self.change_x=0
        self.change_y=0
        self.change_angle=0
        self.width=48
        self.height=48
        self.speed=10
        self.bullet=[]
        self.live=3

    def fire(self):
        self.bullet.append(Bullet(self))

    def roatate(self):
        self.angle += self.speed * self.change_angle
    
    def move(self):
        self.center_x += self.speed * self.change_x
        self.center_y += self.speed * self.change_y

class Bullet(arcade.Sprite):
    def __init__(self,host):
        super().__init__(":resources:images/space_shooter/laserRed01.png")
        self.center_x=host.center_x
        self.center_y=host.center_y
        self.speed=6
        self.angle=host.angle

    def sound(self):
        arcade.play_sound(arcade.sound.Sound(':resources:sounds/hurt5.wav'), 0.2, 0.0,False)

    def move(self):
        self.center_x -= self.speed * math.sin(math.radians(self.angle))
        self.center_y += self.speed * math.cos(math.radians(self.angle))


class Game(arcade.Window):
    def __init__(self):
        super().__init__(SCREEN_WIDGHT,SCREEN_HEIGHT,"🛩 Ship Game 🛩")
        arcade.set_background_color(arcade.color.BLACK)
        self.background_image=arcade.load_texture(':resources:images/backgrounds/stars.png')
        self.heart=arcade.load_texture("heart.png")
        self.my_ship=Ship()
        self.enemy=Enemy(0)
        self.enemy_list=[]
        self.big_enemy=Big_Enemy()
        self.start_time=time.time()
        self.explosions_list = None  
        self.s_e=2
        self.th_enemy=threading.Thread(target=self.add_enemy)
        self.th_enemy.start()



    def add_enemy(self):
        while True:
            a=random.randint(4,7)
            self.enemy_list.append(Enemy(self.s_e))
            self.s_e+=0
            time.sleep(a)


    def setup(self):
        self.explosions_list = arcade.SpriteList()

    def on_draw(self):
        arcade.start_render()
        if self.my_ship.score >=10:
            if self.my_ship.live<=0:
                arcade.draw_text(' !! GAME OVER !!', SCREEN_WIDGHT//2-200, SCREEN_HEIGHT//2, arcade.color.RED, 20,width=400 , align='center')
                arcade.finish_render()
                time.sleep(2)
                exit()
            elif self.big_enemy.live<=0:
                arcade.draw_text(' !! You WIN !!', SCREEN_WIDGHT//2-200, SCREEN_HEIGHT//2, arcade.color.PINE_GREEN, 20,width=400 , align='center')
                arcade.finish_render()
                time.sleep(2)
                exit()
            else:
                arcade.draw_lrwh_rectangle_textured(0, 0, SCREEN_WIDGHT, SCREEN_HEIGHT,self.background_image)
                for i in range(self.big_enemy.live):
                    arcade.draw_rectangle_filled(490,580,200,20,arcade.color.WHITE)
                    arcade.draw_rectangle_filled(490,580,40*(i+1),20,arcade.color.BLUE)
                for i in range(self.my_ship.live):
                    arcade.draw_lrwh_rectangle_textured(10+i*35 ,10 ,30 ,30 ,self.heart)

                arcade.draw_text("SCORE::"+str(self.my_ship.score),450,10,arcade.color.WHITE,20)
                self.my_ship.draw()
                self.big_enemy.draw()
                for bullet in self.my_ship.bullet:
                    bullet.draw() 

                for bullet in self.big_enemy.bullet:
                    bullet.draw()   
        else:
            if self.my_ship.live<=0:
                arcade.draw_text(' !! GAME OVER !!', SCREEN_WIDGHT//2-200, SCREEN_HEIGHT//2, arcade.color.RED, 20,width=400 , align='center')
                arcade.finish_render()
                time.sleep(2)
                exit()
            else:
                arcade.draw_lrwh_rectangle_textured(0, 0, SCREEN_WIDGHT, SCREEN_HEIGHT,self.background_image)
                for i in range(self.my_ship.live):
                    arcade.draw_lrwh_rectangle_textured(10+i*35 ,10 ,30 ,30 ,self.heart)

                arcade.draw_text("SCORE::"+str(self.my_ship.score),450,10,arcade.color.WHITE,20)
                self.my_ship.draw()
                self.explosions_list.draw()
                for enemy in self.enemy_list:
                    enemy.draw()  

                for bullet in self.my_ship.bullet:
                    bullet.draw()  

    def on_update(self, delta_time: float):
        if self.my_ship.score >=10:
            self.my_ship.roatate()
            self.my_ship.move()
            self.end_time=time.time()

            if self.end_time - self.start_time > 0.1:
                self.big_enemy.fire()
                self.start_time=time.time()

            
            
            for bullet in self.my_ship.bullet:
                bullet.move()
            
            for bullet in self.big_enemy.bullet:
                bullet.move()
            
            for bullet in self.my_ship.bullet:
                    if arcade.check_for_collision(bullet, self.big_enemy):
                        self.enemy.sound()
                        self.my_ship.bullet.remove(bullet)
                        self.my_ship.score += 1
                        self.big_enemy.live -=1

            for bullet in self.big_enemy.bullet:
                    if arcade.check_for_collision(bullet, self.my_ship):
                        self.enemy.sound()
                        self.big_enemy.bullet.remove(bullet)
                        self.my_ship.live -=1

            for bullet in self.my_ship.bullet:
                if bullet.center_y>SCREEN_HEIGHT or bullet.center_x<0 or bullet.center_x>SCREEN_WIDGHT:
                    self.my_ship.bullet.remove(bullet) 

            for bullet in self.big_enemy.bullet:
                if bullet.center_y>SCREEN_HEIGHT or bullet.center_x<0 or bullet.center_x>SCREEN_WIDGHT:
                    self.big_enemy.bullet.remove(bullet)      

        else:
            self.explosions_list.update()
            self.my_ship.roatate()
            self.my_ship.move()
            for enemy in self.enemy_list:
                enemy.move()
            
            for bullet in self.my_ship.bullet:
                bullet.move()
            
            for enemy in self.enemy_list:
                for bullet in self.my_ship.bullet:
                    if arcade.check_for_collision(bullet, enemy):
                        for i in range(PARTICLE_COUNT):
                            particle = Particle(self.explosions_list)
                            particle.position=enemy.position
                            self.explosions_list.append(particle)

                        smoke = Smoke(50)
                        smoke.position=enemy.position
                        self.explosions_list.append(smoke)
                        self.enemy.sound()
                        self.my_ship.bullet.remove(bullet)
                        self.enemy_list.remove(enemy)
                        self.my_ship.score += 1
            
            for enemy in self.enemy_list:
                if arcade.check_for_collision(self.my_ship, enemy):           
                    for i in range(PARTICLE_COUNT):
                            particle = Particle(self.explosions_list)
                            particle.position=enemy.position
                            self.explosions_list.append(particle)

                    smoke = Smoke(50)
                    smoke.position=enemy.position
                    self.explosions_list.append(smoke)
                    self.enemy.sound()
                    self.enemy_list.remove(enemy)
                    self.my_ship.live -= 1

            for enemy in self.enemy_list:
                if enemy.center_y < 0:
                    self.my_ship.live -= 1
                    self.enemy_list.remove(enemy)

            for bullet in self.my_ship.bullet:
                if bullet.center_y>SCREEN_HEIGHT or bullet.center_x<0 or bullet.center_x>SCREEN_WIDGHT:
                    self.my_ship.bullet.remove(bullet)

    def on_key_press(self, symbol: int, modifiers: int):
        if symbol ==arcade.key.SPACE:
            self.my_ship.fire()
            self.my_ship.bullet[-1].sound()
        
        if symbol == arcade.key.UP:
            self.my_ship.change_y = 1
        if symbol == arcade.key.DOWN:
            self.my_ship.change_y = -1
        if symbol == arcade.key.LEFT:
            self.my_ship.change_x = -1
        if symbol == arcade.key.RIGHT:
            self.my_ship.change_x = 1

        if symbol == arcade.key.C:
            self.my_ship.change_angle=1
        if symbol == arcade.key.V:
            self.my_ship.change_angle=-1  

    def on_key_release(self, symbol: int, modifiers: int):
        self.my_ship.change_angle = 0
        self.my_ship.change_x = 0
        self.my_ship.change_y = 0     


window = Game()
window.center_window()
window.setup()
arcade.run()