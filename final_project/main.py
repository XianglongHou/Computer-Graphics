import pygame
from sys import exit
from pygame.locals import *
import random


# 定义类
SCREEN_WIDTH = 480
SCREEN_HEIGHT = 800


TYPE_SMALL = 1
TYPE_MIDDLE = 2
TYPE_BIG = 3


# 子弹类
class Bullet(pygame.sprite.Sprite):
    def __init__(self, bullet_img, init_pos):
        pygame.sprite.Sprite.__init__(self)
        self.image = bullet_img
        self.rect = self.image.get_rect()
        self.rect.midbottom = init_pos
        self.speed = 10

    def move(self):
        self.rect.top -= self.speed


# 玩家类
class Player(pygame.sprite.Sprite):
    def __init__(self, plane_img, player_rect, init_pos):
        pygame.sprite.Sprite.__init__(self)
        self.image = []  # 用来存储玩家对象精灵图片的列表
        for i in range(len(player_rect)):
            self.image.append(plane_img.subsurface(player_rect[i]).convert_alpha())
        self.rect = player_rect[0]  # 初始化图片所在的矩形
        self.rect.topleft = init_pos  # 初始化矩形的左上角坐标
        self.speed = 10  # 初始化玩家速度，这里是一个确定的值
        self.bullets = pygame.sprite.Group()  # 玩家飞机所发射的子弹的集合
        self.img_index = 0  # 玩家精灵图片索引
        self.is_hit = False  # 玩家是否被击中

    def shoot(self, bullet_img):
        bullet = Bullet(bullet_img, self.rect.midtop)
        self.bullets.add(bullet)

    def moveUp(self):
        if self.rect.top <= 0:
            self.rect.top = 0
        else:
            self.rect.top -= self.speed

    def moveDown(self):
        if self.rect.top >= SCREEN_HEIGHT - self.rect.height:
            self.rect.top = SCREEN_HEIGHT - self.rect.height
        else:
            self.rect.top += self.speed

    def moveLeft(self):
        if self.rect.left <= 0:
            self.rect.left = 0
        else:
            self.rect.left -= self.speed

    def moveRight(self):
        if self.rect.left >= SCREEN_WIDTH - self.rect.width:
            self.rect.left = SCREEN_WIDTH - self.rect.width
        else:
            self.rect.left += self.speed


# 敌人类
class Enemy(pygame.sprite.Sprite):
    def __init__(self, enemy_img, enemy_down_imgs, init_pos,speed = 2):
        pygame.sprite.Sprite.__init__(self)
        self.image = enemy_img
        self.rect = self.image.get_rect()
        self.rect.topleft = init_pos
        self.down_imgs = enemy_down_imgs
        self.speed = speed
        self.down_index = 0

    def move(self, random_lr = True):
        self.rect.top += self.speed
        s = 0.5
        if random_lr ==True:
            # s = random.random()
            tp = random.random()
            if tp > s:
                self.rect.left += 4
            else:
                self.rect.left -= 4
            s = 1-tp



# 初始化游戏
pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption('飞机大战')
font = pygame.font.Font(None, 36)
pygame.mixer.music.load('resources/sound/yang.mp3')
game_over = pygame.image.load('resources/image/gameover.png')
# pygame.mixer.music.load('resources/sound/game_music.wav')
pygame.mixer.music.play(-1, 0.0)
pygame.mixer.music.set_volume(0.25)

flag = 0
def single_button_click(frequency_bar= 30,enemy_speed = 5, random_lr = False):
    # 载入游戏音乐
    global flag
    bullet_sound = pygame.mixer.Sound('resources/sound/bullet.wav')
    enemy1_down_sound = pygame.mixer.Sound('resources/sound/enemy1_down.wav')
    game_over_sound = pygame.mixer.Sound('resources/sound/game_over.wav')
    bullet_sound.set_volume(0.3)
    enemy1_down_sound.set_volume(0.3)
    game_over_sound.set_volume(0.3)


    # 载入背景图
    background = pygame.image.load('resources/image/background.png').convert()


    filename = 'resources/image/shoot.png'
    plane_img = pygame.image.load(filename)

    # 设置玩家相关参数
    player_rect = []
    player_rect.append(pygame.Rect(0, 99, 102, 126))  # 玩家精灵图片区域
    player_rect.append(pygame.Rect(165, 360, 102, 126))
    player_rect.append(pygame.Rect(165, 234, 102, 126))  # 玩家爆炸精灵图片区域
    player_rect.append(pygame.Rect(330, 624, 102, 126))
    player_rect.append(pygame.Rect(330, 498, 102, 126))
    player_rect.append(pygame.Rect(432, 624, 102, 126))
    player_pos = [200, 600]
    player = Player(plane_img, player_rect, player_pos)

    # 定义子弹对象使用的surface相关参数
    bullet_rect = pygame.Rect(1004, 987, 9, 21)
    bullet_img = plane_img.subsurface(bullet_rect)

    # 定义敌机对象使用的surface相关参数
    enemy1_rect = pygame.Rect(534, 612, 57, 43)
    enemy1_img = plane_img.subsurface(enemy1_rect)
    enemy1_down_imgs = []
    enemy1_down_imgs.append(plane_img.subsurface(pygame.Rect(267, 347, 57, 43)))
    enemy1_down_imgs.append(plane_img.subsurface(pygame.Rect(873, 697, 57, 43)))
    enemy1_down_imgs.append(plane_img.subsurface(pygame.Rect(267, 296, 57, 43)))
    enemy1_down_imgs.append(plane_img.subsurface(pygame.Rect(930, 697, 57, 43)))

    enemies1 = pygame.sprite.Group()

    # 存储被击毁的飞机，用来渲染击毁精灵动画
    enemies_down = pygame.sprite.Group()

    shoot_frequency = 0
    enemy_frequency = 0

    player_down_index = 16

    score = 0

    clock = pygame.time.Clock()

    running = True

    while running:
        # 控制游戏最大帧率为60
        clock.tick(60)

        # 控制发射子弹频率,并发射子弹
        if not player.is_hit:
            if shoot_frequency % 15 == 0:
                bullet_sound.play()
                player.shoot(bullet_img)
            shoot_frequency += 1
            if shoot_frequency >= 15:
                shoot_frequency = 0

        # 生成敌机
        if enemy_frequency % frequency_bar == 0:
            enemy1_pos = [random.randint(0, SCREEN_WIDTH - enemy1_rect.width), 0]
            enemy1 = Enemy(enemy1_img, enemy1_down_imgs, enemy1_pos,speed=enemy_speed)
            enemies1.add(enemy1)
        enemy_frequency += 1
        if enemy_frequency >= 100:
            enemy_frequency = 0

        # 移动子弹，若超出窗口范围则删除
        for bullet in player.bullets:
            bullet.move()
            if bullet.rect.bottom < 0:
                player.bullets.remove(bullet)

        # 移动敌机，若超出窗口范围则删除
        for enemy in enemies1:
            enemy.move(random_lr=random_lr)
            # 判断玩家是否被击中
            if pygame.sprite.collide_circle(enemy, player):
                enemies_down.add(enemy)
                enemies1.remove(enemy)
                player.is_hit = True
                game_over_sound.play()
                break
            if enemy.rect.top > SCREEN_HEIGHT:
                enemies1.remove(enemy)

        # 将被击中的敌机对象添加到击毁敌机Group中，用来渲染击毁动画
        enemies1_down = pygame.sprite.groupcollide(enemies1, player.bullets, 1, 1)
        for enemy_down in enemies1_down:
            enemies_down.add(enemy_down)

        # 绘制背景
        screen.fill(0)
        screen.blit(background, (0, 0))

        # 绘制玩家飞机
        if not player.is_hit:
            screen.blit(player.image[player.img_index], player.rect)
            # 更换图片索引使飞机有动画效果
            player.img_index = shoot_frequency // 8
        else:
            player.img_index = player_down_index // 8
            screen.blit(player.image[player.img_index], player.rect)
            player_down_index += 1
            if player_down_index > 47:
                running = False

        # 绘制击毁动画
        for enemy_down in enemies_down:
            if enemy_down.down_index == 0:
                enemy1_down_sound.play()
            if enemy_down.down_index > 7:
                enemies_down.remove(enemy_down)
                score += 10
                continue
            screen.blit(enemy_down.down_imgs[enemy_down.down_index // 2], enemy_down.rect)
            enemy_down.down_index += 1

        # 绘制子弹和敌机
        player.bullets.draw(screen)
        enemies1.draw(screen)

        # 绘制得分
        score_font = pygame.font.Font(None, 30)
        text2 = score_font.render('Score: '+str(score), True, (0, 255, 0))
        tw2, th2 = text2.get_size()
        tx2, ty2 = 240-tw2/2,40
        screen.blit(text2, (tx2, ty2))

        # 更新屏幕
        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()

        # 监听键盘事件
        key_pressed = pygame.key.get_pressed()
        # 若玩家被击中，则无效
        if not player.is_hit:
            if key_pressed[K_2] or key_pressed[K_UP]:
                player.moveUp()
            if key_pressed[K_3] or key_pressed[K_DOWN]:
                player.moveDown()
            if key_pressed[K_1] or key_pressed[K_LEFT]:
                player.moveLeft()
            if key_pressed[K_4] or key_pressed[K_RIGHT]:
                player.moveRight()
    #
    # font = pygame.font.Font(None, 48)
    # text = font.render('Score: ' + str(score), True, (255, 0, 0))
    # text_rect = text.get_rect()
    # text_rect.centerx = screen.get_rect().centerx
    # text_rect.centery = screen.get_rect().centery + 24
    # screen.blit(game_over, (0, 0))
    # screen.blit(text, text_rect)
    # pygame.display.update()
    flag = 3
    return score


def double_button_click(frequency_bar=40, enemy_speed=4, random_lr=False):
    global flag
    # 载入游戏音乐
    bullet_sound = pygame.mixer.Sound('resources/sound/bullet.wav')
    enemy1_down_sound = pygame.mixer.Sound('resources/sound/enemy1_down.wav')
    game_over_sound = pygame.mixer.Sound('resources/sound/game_over.wav')
    bullet_sound.set_volume(0.3)
    enemy1_down_sound.set_volume(0.3)
    game_over_sound.set_volume(0.3)
    # pygame.mixer.music.load('resources/sound/game_music.wav')
    # pygame.mixer.music.play(-1, 0.0)
    # pygame.mixer.music.set_volume(0.25)

    # 载入背景图
    background = pygame.image.load('resources/image/background.png').convert()
    game_over = pygame.image.load('resources/image/gameover.png')

    filename = 'resources/image/shoot.png'
    plane_img = pygame.image.load(filename)

    # 设置玩家相关参数
    player1_rect = []
    player1_rect.append(pygame.Rect(0, 99, 102, 126))  # 玩家精灵图片区域
    player1_rect.append(pygame.Rect(165, 360, 102, 126))
    player1_rect.append(pygame.Rect(165, 234, 102, 126))
    player1_rect.append(pygame.Rect(330, 624, 102, 126))
    player1_rect.append(pygame.Rect(330, 498, 102, 126))
    player1_rect.append(pygame.Rect(432, 624, 102, 126))
    player1_pos = [200, 600]
    player1 = Player(plane_img, player1_rect, player1_pos)

    player2_rect = []
    player2_rect.append(pygame.Rect(0, 99, 102, 126))  # 玩家精灵图片区域
    player2_rect.append(pygame.Rect(165, 360, 102, 126))
    player2_rect.append(pygame.Rect(165, 234, 102, 126))
    player2_rect.append(pygame.Rect(330, 624, 102, 126))
    player2_rect.append(pygame.Rect(330, 498, 102, 126))
    player2_rect.append(pygame.Rect(432, 624, 102, 126))
    player2_pos = [100, 600]
    player2 = Player(plane_img, player2_rect, player2_pos)

    # 定义子弹对象使用的surface相关参数
    bullet_rect = pygame.Rect(1004, 987, 9, 21)
    bullet_img = plane_img.subsurface(bullet_rect)

    # 定义敌机对象使用的surface相关参数
    enemy1_rect = pygame.Rect(534, 612, 57, 43)
    enemy1_img = plane_img.subsurface(enemy1_rect)
    enemy1_down_imgs = []
    enemy1_down_imgs.append(plane_img.subsurface(pygame.Rect(267, 347, 57, 43)))
    enemy1_down_imgs.append(plane_img.subsurface(pygame.Rect(873, 697, 57, 43)))
    enemy1_down_imgs.append(plane_img.subsurface(pygame.Rect(267, 296, 57, 43)))
    enemy1_down_imgs.append(plane_img.subsurface(pygame.Rect(930, 697, 57, 43)))

    enemies1 = pygame.sprite.Group()

    # 存储被击毁的飞机，用来渲染击毁精灵动画
    enemies_down = pygame.sprite.Group()

    shoot_frequency = 0
    enemy_frequency = 0

    player_down_index = 16

    score = 0

    clock = pygame.time.Clock()

    running = True

    while running:
        clock.tick(60)
        # 控制发射子弹频率,并发射子弹
        if not (player1.is_hit or player1.is_hit):
            if shoot_frequency % 15 == 0:
                bullet_sound.play()
                player1.shoot(bullet_img)
                player2.shoot(bullet_img)

            shoot_frequency += 1
            if shoot_frequency >= 15:
                shoot_frequency = 0

        # 生成敌机
        if enemy_frequency % frequency_bar == 0:
            enemy1_pos = [random.randint(0, SCREEN_WIDTH - enemy1_rect.width), 0]
            enemy1 = Enemy(enemy1_img, enemy1_down_imgs, enemy1_pos,speed=enemy_speed)
            enemies1.add(enemy1)
        enemy_frequency += 1
        if enemy_frequency >= 100:
            enemy_frequency = 0

        # 移动子弹，若超出窗口范围则删除
        for bullet in player1.bullets:
            bullet.move()
            if bullet.rect.bottom < 0:
                player1.bullets.remove(bullet)

        for bullet in player2.bullets:
            bullet.move()
            if bullet.rect.bottom < 0:
                player2.bullets.remove(bullet)

        # 移动敌机，若超出窗口范围则删除
        for enemy in enemies1:
            enemy.move(random_lr=random_lr)
            # 判断玩家是否被击中
            if pygame.sprite.collide_circle(enemy, player1):
                enemies_down.add(enemy)
                enemies1.remove(enemy)
                player1.is_hit = True
                game_over_sound.play()
                break
            if pygame.sprite.collide_circle(enemy, player2):
                enemies_down.add(enemy)
                enemies1.remove(enemy)
                player2.is_hit = True
                game_over_sound.play()
                break

            if enemy.rect.top > SCREEN_HEIGHT:
                enemies1.remove(enemy)

        # 将被击中的敌机对象添加到击毁敌机Group中，用来渲染击毁动画
        enemies1_down = pygame.sprite.groupcollide(enemies1, player1.bullets, 1, 1)
        enemies2_down = pygame.sprite.groupcollide(enemies1, player2.bullets, 1, 1)
        for enemy_down in enemies1_down:
            enemies_down.add(enemy_down)
        for enemy_down in enemies2_down:
            enemies_down.add(enemy_down)

        # 绘制背景
        screen.fill(0)
        screen.blit(background, (0, 0))

        # 绘制玩家飞机
        if not (player1.is_hit or player2.is_hit):
            screen.blit(player1.image[player1.img_index], player1.rect)
            screen.blit(player1.image[player1.img_index], player2.rect)
            # 更换图片索引使飞机有动画效果
            player1.img_index = shoot_frequency // 8
            player2.img_index = shoot_frequency // 8
        elif player1.is_hit:
            player1.img_index = player_down_index // 8
            screen.blit(player1.image[player1.img_index], player1.rect)
            player_down_index += 1
            if player_down_index > 47:
                running = False
        elif player2.is_hit:
            player2.img_index = player_down_index // 8
            screen.blit(player2.image[player2.img_index], player2.rect)
            player_down_index += 1
            if player_down_index > 47:
                running = False

        # 绘制击毁动画
        for enemy_down in enemies_down:
            if enemy_down.down_index == 0:
                enemy1_down_sound.play()
            if enemy_down.down_index > 7:
                enemies_down.remove(enemy_down)
                score += 10
                continue
            screen.blit(enemy_down.down_imgs[enemy_down.down_index // 2], enemy_down.rect)
            enemy_down.down_index += 1

        # 绘制子弹和敌机
        player1.bullets.draw(screen)
        player2.bullets.draw(screen)
        enemies1.draw(screen)

        # 绘制得分
        score_font = pygame.font.Font(None, 30)
        text2 = score_font.render('Score: '+str(score), True, (0, 255, 0))
        tw2, th2 = text2.get_size()
        tx2, ty2 = 240-tw2/2,40
        screen.blit(text2, (tx2, ty2))

        # 更新屏幕
        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()

        # 监听键盘事件
        key_pressed = pygame.key.get_pressed()
        # 若玩家被击中，则无效
        if not player1.is_hit:
            if key_pressed[K_UP]:
                player1.moveUp()
            if key_pressed[K_DOWN]:
                player1.moveDown()
            if key_pressed[K_LEFT]:
                player1.moveLeft()
            if key_pressed[K_RIGHT]:
                player1.moveRight()

        if not player2.is_hit:
            if key_pressed[K_2]:
                player2.moveUp()
            if key_pressed[K_3]:
                player2.moveDown()
            if key_pressed[K_1]:
                player2.moveLeft()
            if key_pressed[K_4]:
                player2.moveRight()

    flag = 3
    return score


def begining(mx,my):
    background1 = pygame.image.load('resources/image/first_back.png').convert()
    screen.fill(0)
    screen.blit(background1, (0, 0))

    bx1, by1, bw1, bh1 = 30, 680, 200, 50
    pygame.draw.rect(screen, (255, 0, 0), (bx1, by1, bw1, bh1))
    text1 = font.render("Single Player", True, (255, 255, 255))
    tw1, th1 = text1.get_size()
    tx1, ty1 = bx1 + bw1 / 2 - tw1 / 2, by1 + bh1 / 2 - th1 / 2
    screen.blit(text1, (tx1, ty1))


    bx2, by2, bw2, bh2 = 250, 680, 200, 50
    pygame.draw.rect(screen, (0, 255, 0), (bx2, by2, bw2, bh2))
    text2 = font.render("Double Players", True, (0, 0, 0))
    tw2, th2 = text2.get_size()
    tx2, ty2 = bx2 + bw2 / 2 - tw2 / 2, by2 + bh2 / 2 - th2 / 2
    screen.blit(text2, (tx2, ty2))

    pygame.display.update()
    if bx1 + bw1 >= mx >= bx1 and by1 + bh1 >= my >= by1:
        result = 1
    elif bx2 + bw2 >= mx >= bx2 and by2 + bh2 >= my >= by2:
        result = 2
    else:
        result = 0
    return result


def choose_difficulty(mx,my):
    background3 = pygame.image.load('resources/image/background.png').convert()
    screen.fill(0)
    screen.blit(background3, (0, 0))

    bx3, by3, bw3, bh3 = 140, 200, 200, 80
    pygame.draw.rect(screen, (255, 0, 0), (bx3, by3, bw3, bh3))
    text3 = font.render("Baby mode", True, (255, 255, 255))
    tw3, th3 = text3.get_size()
    tx3, ty3 = bx3 + bw3 / 2 - tw3 / 2, by3 + bh3 / 2 - th3 / 2
    screen.blit(text3, (tx3, ty3))

    bx4, by4, bw4, bh4 = 140, 300, 200, 80
    pygame.draw.rect(screen, (255, 0, 0), (bx4, by4, bw4, bh4))
    text4 = font.render("Normal mode", True, (255, 255, 255))
    tw4, th4 = text4.get_size()
    tx4, ty4 = bx4 + bw4 / 2 - tw4 / 2, by4 + bh4 / 2 - th4 / 2
    screen.blit(text4, (tx4, ty4))

    bx5, by5, bw5, bh5 = 140, 400, 200, 80
    pygame.draw.rect(screen, (255, 0, 0), (bx5, by5, bw5, bh5))
    text5 = font.render("Hell mode", True, (255, 255, 255))
    tw5, th5 = text5.get_size()
    tx5, ty5 = bx5 + bw5 / 2 - tw5 / 2, by5 + bh5 / 2 - th5 / 2
    screen.blit(text5, (tx5, ty5))
    pygame.display.update()

    if bx3 + bw3 >= mx >= bx3 and by3 + bh3 >= my >= by3:
        result = 1
    elif bx4 + bw4 >= mx >= bx4 and by4 + bh4 >= my >= by4:
        result = 2
    elif bx5 + bw5 >= mx >= bx5 and by5 + bh5 >= my >= by5:
        result = 3
    else:
        result = 0
    return result

def endding(score,mx,my):
    font = pygame.font.Font(None, 48)
    text = font.render('Score: ' + str(score), True, (255, 0, 0))
    text_rect = text.get_rect()
    text_rect.centerx = screen.get_rect().centerx
    text_rect.centery = screen.get_rect().centery + 24
    screen.blit(game_over, (0, 0))
    screen.blit(text, text_rect)

    bx4, by4, bw4, bh4 = 20, 550, 200, 80
    pygame.draw.rect(screen, (0, 0, 255), (bx4, by4, bw4, bh4))
    text4 = font.render("Continue", True, (255, 255, 255))
    tw4, th4 = text4.get_size()
    tx4, ty4 = bx4 + bw4 / 2 - tw4 / 2, by4 + bh4 / 2 - th4 / 2
    screen.blit(text4, (tx4, ty4))

    bx5, by5, bw5, bh5 = 250, 550, 200, 80
    pygame.draw.rect(screen, (0, 0, 255), (bx5, by5, bw5, bh5))
    text5 = font.render("Exit", True, (255, 255, 255))
    tw5, th5 = text5.get_size()
    tx5, ty5 = bx5 + bw5 / 2 - tw5 / 2, by5 + bh5 / 2 - th5 / 2
    screen.blit(text5, (tx5, ty5))
    pygame.display.update()

    pygame.display.update()

    if bx4 + bw4 >= mx >= bx4 and by4 + bh4 >= my >= by4:
        result = 1
    elif bx5 + bw5 >= mx >= bx5 and by5 + bh5 >= my >= by5:
        result = 2
    else:
        result = 0
    return result

while True:
    if flag == 0:
        begining(0,0)
        for event in pygame.event.get():
            # 对事件作出相应的响应
            if event.type == pygame.QUIT:  # 如果点击了关闭按钮
                exit()

            if event.type == pygame.MOUSEBUTTONDOWN:  # 如果鼠标按下
                mx, my = event.pos  # 获取鼠标点击的位置
                result = begining(mx,my)
                if result == 1:
                    flag = 1
                elif result == 2:
                    flag = 2


                # choose_difficulty(0,0)
    if flag == 1:
        choose_difficulty(0,0)
        for sub_event in pygame.event.get():
            if sub_event.type == pygame.MOUSEBUTTONDOWN:
                mx, my = sub_event.pos
                result = choose_difficulty(mx,my)
                if result == 1:
                    score = single_button_click(frequency_bar = 50, enemy_speed = 2, random_lr = False)
                if result == 2:
                    score = single_button_click(frequency_bar=30, enemy_speed=4, random_lr=False)
                if result == 3:
                    score = single_button_click(frequency_bar = 18, enemy_speed=6, random_lr=True)

    if flag == 2:
        choose_difficulty(0, 0)
        for sub_event in pygame.event.get():
            if sub_event.type == pygame.MOUSEBUTTONDOWN:
                mx, my = sub_event.pos
                result = choose_difficulty(mx, my)

                if result == 1:
                    score = double_button_click(frequency_bar = 50, enemy_speed = 1.5, random_lr = False)
                if result == 2:
                    score = double_button_click(frequency_bar=30, enemy_speed=4, random_lr=False)
                if result == 3:
                    score = double_button_click(frequency_bar = 25, enemy_speed=7, random_lr=True)
    
    if flag == 3:
        endding(score, 0, 0)
        for sub_event in pygame.event.get():
            if sub_event.type == pygame.MOUSEBUTTONDOWN:
                mx, my = sub_event.pos
                result = endding(score,mx,my)
                if result == 1:
                    flag = 0
                if result == 2:
                    exit()