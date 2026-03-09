import turtle
import math
import time

# --- 1. ENGINE SETUP ---
screen = turtle.Screen()
screen.setup(800, 800)
screen.bgcolor("#001219")
screen.tracer(0)

# Game State
has_key = False
game_on = True
is_grappling = False
grapple_battery = 100.0  # Max Battery
MAX_BATTERY = 100.0

# --- 2. WORLD & OBJECTS ---
walls = []
class Wall(turtle.Turtle):
    def __init__(self, x, y, w, h):
        super().__init__(shape="square")
        self.penup(); self.color("#005f73")
        self.shapesize(h/20, w/20); self.goto(x, y)
        self.w = w; self.h = h; walls.append(self)

# Maze Layout
Wall(0, 0, 150, 20)
Wall(-200, 100, 20, 200)
Wall(200, -100, 20, 200)

# Actors
player = turtle.Turtle(shape="triangle")
player.color("#00f5d4"); player.penup(); player.goto(-350, -350)
player.is_crouching = False

keycard = turtle.Turtle(shape="circle")
keycard.color("#00b4d8"); keycard.penup(); keycard.goto(0, 300)

goal = turtle.Turtle(shape="square")
goal.shapesize(2, 2); goal.color("#9b2226"); goal.penup(); goal.goto(350, 350)

# --- 3. THE GUARD & CAMERA CLASSES ---
class Guard(turtle.Turtle):
    def __init__(self, path):
        super().__init__(shape="classic")
        self.color("#ff0055"); self.penup(); self.goto(path[0])
        self.path = path; self.current_target = 0
        self.cone = turtle.Turtle(); self.cone.hideturtle()

    def move(self):
        target = self.path[self.current_target]
        self.setheading(self.towards(target)); self.forward(2.5)
        if self.distance(target) < 5:
            self.current_target = (self.current_target + 1) % len(self.path)
        self.draw_vision()

    def draw_vision(self):
        self.cone.clear(); self.cone.goto(self.xcor(), self.ycor())
        self.cone.color("#9b2226"); self.cone.setheading(self.heading())
        self.cone.pendown(); self.cone.begin_fill()
        self.cone.left(30); self.cone.forward(150); self.cone.right(120); self.cone.circle(-150, 60)
        self.cone.goto(self.xcor(), self.ycor()); self.cone.end_fill(); self.cone.penup()

class Camera(turtle.Turtle):
    def __init__(self, x, y):
        super().__init__(shape="square")
        self.shapesize(0.5, 0.5); self.color("white"); self.penup(); self.goto(x, y)
        self.cone = turtle.Turtle(); self.cone.hideturtle()
        self.angle = 0

    def scan(self):
        self.angle = (self.angle + 2) % 360
        self.setheading(self.angle); self.draw_vision()

    def draw_vision(self):
        self.cone.clear(); self.cone.goto(self.xcor(), self.ycor())
        self.cone.color("#ae2012"); self.cone.setheading(self.heading())
        self.cone.pendown(); self.cone.forward(280); self.cone.penup()

guards = [Guard([(-200, 200), (200, 200)]), Guard([(300, -150), (-300, -150)])]
cameras = [Camera(-350, 350), Camera(350, -350)]

# --- 4. ENHANCED GRAPPLE & BATTERY ---
def fire_grapple(x, y):
    global is_grappling, grapple_battery
    # Cost: 40% battery per grapple
    if is_grappling or grapple_battery < 40: return
    
    for w in walls:
        if abs(x - w.xcor()) < w.w/2 and abs(y - w.ycor()) < w.h/2:
            return 

    is_grappling = True
    grapple_battery -= 40
    player.setheading(player.towards(x, y))
    for _ in range(8):
        player.goto(player.xcor() + (x - player.xcor())*0.25, 
                    player.ycor() + (y - player.ycor())*0.25)
        screen.update()
        time.sleep(0.01)
    is_grappling = False

# --- 5. CONTROLS ---
def toggle_crouch():
    player.is_crouching = not player.is_crouching
    player.color("#94d2bd" if player.is_crouching else "#00f5d4")

screen.listen()
screen.onclick(fire_grapple)
screen.onkeypress(toggle_crouch, "Shift_L")
screen.onkeypress(lambda: player.sety(player.ycor()+10), "Up")
screen.onkeypress(lambda: player.sety(player.ycor()-10), "Down")
screen.onkeypress(lambda: player.setx(player.xcor()-10), "Left")
screen.onkeypress(lambda: player.setx(player.xcor()+10), "Right")

# --- 6. MAIN LOOP ---
ui = turtle.Turtle(); ui.hideturtle(); ui.penup(); ui.color("white")
game_writer = turtle.Turtle(); game_writer.hideturtle(); game_writer.penup(); game_writer.color("red")

while game_on:
    # 1. UI Update
    ui.clear(); ui.goto(-380, 360)
    battery_bar = "█" * int(grapple_battery // 10)
    ui.write(f"BATTERY: {battery_bar} {int(grapple_battery)}% | KEY: {'YES' if has_key else 'NO'}", font=("Courier", 14, "bold"))

    # 2. Battery Recharge (Only if moving slowly or standing still)
    if not is_grappling and grapple_battery < MAX_BATTERY:
        recharge_rate = 0.5 if player.is_crouching else 0.1
        grapple_battery = min(MAX_BATTERY, grapple_battery + recharge_rate)

    # 3. Objectives
    if not has_key and player.distance(keycard) < 30:
        has_key = True; keycard.hideturtle(); goal.color("#00f5d4")

    # 4. Detection Logic
    for g in guards:
        g.move()
        if g.distance(player) < 160:
            angle_to_p = (g.towards(player) - g.heading() + 180) % 360 - 180
            if abs(angle_to_p) < 30: game_on = False

    for c in cameras:
        c.scan()
        if c.distance(player) < 280:
            angle_to_p = (c.towards(player) - c.heading() + 180) % 360 - 180
            if abs(angle_to_p) < 3: game_on = False

    # 5. Win/Loss
    if player.distance(goal) < 30 and has_key:
        game_on = False
        game_writer.color("cyan"); game_writer.goto(0,0)
        game_writer.write("MISSION SUCCESS", align="center", font=("Courier", 35, "bold"))

    if not game_on and player.distance(goal) > 30:
        game_writer.goto(0,0)
        game_writer.write("SYSTEM COMPROMISED", align="center", font=("Courier", 35, "bold"))

    screen.update(); time.sleep(0.02)

screen.exitonclick()
