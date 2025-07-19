import pygame
from math import *
import random

class Button:
    def __init__(self, x, y, width, height, text, color, hover_color, text_color, font_size=30):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.hover_color = hover_color
        self.text_color = text_color
        self.font = pygame.font.Font(None, font_size)
        self.is_hovered = False
        
    def draw(self, surface:pygame.SurfaceType):
        # 根据悬停状态选择颜色
        color = self.hover_color if self.is_hovered else self.color
        pygame.draw.rect(surface, color, self.rect, border_radius=10)
        pygame.draw.rect(surface, (0, 0, 0), self.rect, 2, border_radius=10)  # 边框
        
        # 渲染文本
        text_surface = self.font.render(self.text, True, self.text_color)
        text_rect = text_surface.get_rect(center=self.rect.center)
        surface.blit(text_surface, text_rect)
        
    def check_hover(self, mouse_pos):
        self.is_hovered = self.rect.collidepoint(mouse_pos)
        return self.is_hovered
        
    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and self.is_hovered:
                return True
        return False


class PoolTable:
    def __init__(self,rect,background,frame,framewidth=30) -> None:
        self.rect=rect
        x,y,length,width=rect
        self.framewidth=framewidth
        self.frame_rect=(x-framewidth,y-framewidth,length+2*framewidth,width+2*framewidth)

        self.background=background
        self.frame=frame
    
    def draw(self,surface:pygame.SurfaceType) -> None:
        pygame.draw.rect(surface,self.background,self.rect)
        pygame.draw.rect(surface,self.frame,self.frame_rect,self.framewidth,border_radius=20)




friction=0.985
wall_friction=0.6
restitution = 1.1  # 弹性系数
crash_friction=0.5

min_v=0
max_v=3600
tiny_v=1

class Ball:
    # x,y指桌上坐标
    # 实际渲染必须考虑实际坐标！！！
    # type: 1-solid 0-stripe
    def __init__(self,x,y,color:tuple,num:int,type:bool,vx=0,vy=0):
        self.x=x
        self.y=y
        self.color=color
        self.vx=vx
        self.vy=vy
        self.num=num
        self.type=type
        self.active=True
        self.mass=1000

    def draw(self,surface):
        if self.type:
            pygame.draw.circle(surface,self.color,(self.x+table_gap_x,self.y+table_gap_y),ball_radius)
        else:
            pygame.draw.circle(surface,White,(self.x+table_gap_x,self.y+table_gap_y),ball_radius)
            pygame.draw.rect(surface,self.color,(self.x+table_gap_x-12,self.y+table_gap_y-3,24,6))
            pygame.draw.rect(surface,self.color,(self.x+table_gap_x-11,self.y+table_gap_y-5,22,2))
            pygame.draw.rect(surface,self.color,(self.x+table_gap_x-11,self.y+table_gap_y+3,22,2))
            pygame.draw.rect(surface,self.color,(self.x+table_gap_x-10,self.y+table_gap_y-7,20,2))
            pygame.draw.rect(surface,self.color,(self.x+table_gap_x-10,self.y+table_gap_y+5,20,2))
            # num_text = font.render(str(self.num), True, (0, 0, 0))  # 黑色文字，半透明背景
            # window.blit(num_text, (self.x+table_gap_x-10, self.y+table_gap_y+5))

    def update_position(self, dt):
        self.vx=0 if abs(self.vx)<tiny_v else self.vx
        self.vy=0 if abs(self.vy)<tiny_v else self.vy

        self.x += self.vx * dt
        self.y += self.vy * dt
        
        
        self.vx *= friction
        self.vy *= friction

        if  self.x - ball_radius < 0:
             self.x = ball_radius
             self.vx = -self.vx * wall_friction  # 加入一些能量损失
        
        # 右边界
        if  self.x + ball_radius > table_length:
             self.x = table_length -  ball_radius
             self.vx = -self.vx * wall_friction
        
        # 上边界
        if  self.y - ball_radius < 0:
             self.y = ball_radius
             self.vy = -self.vy * wall_friction
        
        # 下边界
        if  self.y + ball_radius > table_width:
             self.y = table_width -  ball_radius
             self.vy = -self.vy * wall_friction



def check_ball_collision(ball1:Ball, ball2:Ball):
    dx = ball2.x - ball1.x
    dy = ball2.y - ball1.y
    distance = sqrt(dx**2 + dy**2)
    
    # 检测碰撞
    if distance < 2*ball_radius:
        # 计算碰撞法线
        nx = dx / distance
        ny = dy / distance
        
        # 计算相对速度
        dvx = ball2.vx - ball1.vx
        dvy = ball2.vy - ball1.vy
        
        # 计算相对速度在法线方向的投影
        velocity_along_normal = dvx * nx + dvy * ny
        
        # 只有相互靠近时才碰撞
        if velocity_along_normal > 0:
            return
        
        # 计算冲量

        j = -(1 + restitution) * velocity_along_normal
        j /= 1/ball1.mass + 1/ball2.mass
        
        # 应用冲量
        impulse_x = j * nx
        impulse_y = j * ny
        
        ball1.vx -= impulse_x / ball1.mass
        ball1.vy -= impulse_y / ball1.mass
        ball2.vx += impulse_x / ball2.mass
        ball2.vy += impulse_y / ball2.mass
        
        # 防止球体重叠
        overlap = (2*ball_radius - distance) / 2
        ball1.x -= overlap * nx
        ball1.y -= overlap * ny
        ball2.x += overlap * nx
        ball2.y += overlap * ny



pygame.display.init()
pygame.font.init()


window=pygame.display.set_mode((1280,720),  pygame.DOUBLEBUF | pygame.HWSURFACE, vsync=1)

pygame.display.set_caption("Pool Game")

font = pygame.font.SysFont('Arial', 10)

clock = pygame.time.Clock()


DarkGreen=(0,51,0)
White = (255,255,255)
Red = (255,0,0)
Black = (0,0,0)
Brown = (100,51,0)

#运行状态
running=True

#全局状态：menu/game
global_status="menu"

#击球状态：
hit_available = False


start_button = Button(500,500,280,100,"Start",Red,Red,Black,40)
def menu():
    window.fill(DarkGreen)  
    start_button.draw(window)
    start_button.check_hover(mouse_pos)



table_length=1024
table_width=512
ball_radius=12
window_length,window_height=window.get_size()
table_gap_x=(window_length-table_length)/2
table_gap_y=(window_height-table_width)/2


balls=[]
balls_data=[(256, 256.0, (255, 255, 255), 0, 1),
            (768.0, 256.0, (255, 215, 0), 1, 1), 
            (788.78, 268.0, (0, 90, 255), 2, 1), 
            (809.57, 232.0, (255, 50, 50), 3, 1), 
            (830.35, 244.0, (128, 0, 128), 4, 1), 
            (830.35, 292.0, (255, 140, 0), 5, 1), 
            (851.14, 208.0, (0, 160, 0), 6, 1), 
            (851.14, 280.0, (160, 0, 0), 7, 1), 
            (809.57, 256.0, (0, 0, 0), 8, 1), 
            (788.78, 244.0, (255, 215, 0), 9, 0), 
            (809.57, 280.0, (0, 90, 255), 10, 0), 
            (830.35, 220.0, (255, 50, 50), 11, 0), 
            (830.35, 268.0, (128, 0, 128), 12, 0), 
            (851.14, 232.0, (255, 140, 0), 13, 0), 
            (851.14, 256.0, (0, 160, 0), 14, 0), 
            (851.14, 304.0, (160, 0, 0), 15, 0)]





def game_init():
    global table,cueball
    table = PoolTable((table_gap_x,table_gap_y,table_length,table_width),DarkGreen,Brown)
    for ball_data in balls_data:
        balls.append(Ball(*ball_data))
    # balls[0].vx=max_v
    # print(cueball)


def hit_cueball(mouse_x,mouse_y):
    dx=mouse_x-balls[0].x
    dy=mouse_y-balls[0].y
    distance=sqrt(dx**2+dy**2)
    vn=distance/500 if distance<=500 else 1
    v=min_v+vn*(max_v-min_v)
    balls[0].vx=v*dx/distance
    balls[0].vy=v*dy/distance




window.fill(White)



while running:
    dt = clock.tick(60) / 1000.0
    mouse_pos = pygame.mouse.get_pos()
    mouse_x=mouse_pos[0]-table_gap_x
    mouse_y=mouse_pos[1]-table_gap_y
    

    #print(hit_available)

    for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running=False
            if global_status=="menu" and start_button.handle_event(event):
                global_status = "game"
                game_init()
            if global_status=="game":
                if event.type==pygame.MOUSEBUTTONUP and event.button==3 and hit_available:
                    hit_cueball(mouse_x,mouse_y)
                    



    if global_status=="menu":
        menu()

    elif global_status=="game":

        #print(balls[0].vx,balls[0].vy)

        window.fill((0,0,128))
        table.draw(window)
        
        for ball in balls:
            ball.update_position(dt)

        
        for i in range(len(balls)):
            for j in range(i+1, len(balls)):
                check_ball_collision(balls[i], balls[j])

        
        hit_available=True
        for ball in balls:
            if ball.vx!=0 or ball.vy!=0:
                hit_available=False
                break

  
            



        # cueball.draw(window)
        for ball in balls:
            ball.draw(window)


    


    
    





    
    
    pygame.display.flip()

