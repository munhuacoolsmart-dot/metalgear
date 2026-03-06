import turtle
import math
import time

# --- 1. SETUP ---
screen = turtle.Screen()
screen.setup(700, 700)
screen.bgcolor("#001219")
screen.tracer(0)

# The Player (Snake)
player = turtle.Turtle()
player.shape("triangle")
player.color("#00f5d4")
player.penup()
player.goto(-300, -300)

# The Exit
goal = turtle.Turtle()
goal.shape("square")
goal.shapesize(2, 2)
goal.color("#fee440")
goal.penup()
goal.goto(300, 300)

# --- 2. THE GUARDS ---
class Guard(turtle.Turtle):
    def __init__(self, path):
        super().__init__(shape="classic")
        self.color("#ff0055")
        self.penup()
        self.path = path
        self.current_target = 0
        self.goto(path[0])
        self.speed_val = 2

    def move(self):
        # Move toward next waypoint
        target = self.path[self.current_target]
        angle = self.towards(target)
        self.setheading(angle)
        self.forward(self.speed_val)
        
        if self.distance(target) < 5:
            self.current_target = (self.current_target + 1) % len(self.path)

    def check_vision(self, target_p):
        # Math: Is player inside a 60-degree cone?
        dist = self.distance(target_p)
        if dist < 150:
            angle_to_player = self.towards(target_p)
            # Normalize angle difference
            diff = (angle_to_player - self.heading() + 180) % 360 - 180
            if abs(diff) < 30: # 30 degrees either side
                return True
        return False

guards = [
    Guard([(-100, 100), (100, 100), (100, -100), (-100, -100)]),
    Guard([(200, -200), (200, 200)]),
    Guard([(-250, 50), (50, 50)])
]

# --- 3. CONTROLS ---
def move_up(): player.setheading(90); player.forward(10)
def move_down(): player.setheading(270); player.forward(10)
def move_left(): player.setheading(180); player.forward(10)
def move_right(): player.setheading(0); player.forward(10)

screen.listen()
screen.onkeypress(move_up, "Up")
screen.onkeypress(move_down, "Down")
screen.onkeypress(move_left, "Left")
screen.onkeypress(move_right, "Right")

# --- 4. GAME LOOP ---
game_on = True
writer = turtle.Turtle()
writer.hideturtle()
writer.color("white")

while game_on:
    # Move Guards
    for g in guards:
        g.move()
        if g.check_vision(player):
            game_on = False
            writer.write("ALERT: SPOTTED!", align="center", font=("Courier", 30, "bold"))
    
    # Check Victory
    if player.distance(goal) < 30:
        game_on = False
        writer.write("MISSION ACCOMPLISHED", align="center", font=("Courier", 30, "bold"))

    screen.update()
    time.sleep(0.02)

screen.exitonclick()