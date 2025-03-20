import pyglet as pg
import random as rand
import os
import sys

# Make window and set size
window = pg.window.Window()
window.set_size(1280, 720)

# All the key flags I apparently need now
space_pressed = False
w_pressed = False
s_pressed = False
esc_pressed = False

# Detects when keys are pressed for the whole program (needed as menus will likely be added)
@window.event
def on_key_press(symbol, modifiers):
    global space_pressed, w_pressed, s_pressed, esc_pressed
    if symbol == pg.window.key.SPACE:
        space_pressed = True
    if symbol == pg.window.key.W:
        w_pressed = True
    if symbol == pg.window.key.S:
        s_pressed = True
    if symbol == pg.window.key.ESCAPE:
        esc_pressed = True
        return True

@window.event
def on_key_release(symbol, modifiers):
    global space_pressed, w_pressed, s_pressed, esc_pressed
    if symbol == pg.window.key.SPACE:
        space_pressed = False
    if symbol == pg.window.key.W:
        w_pressed = False
    if symbol == pg.window.key.S:
        s_pressed = False
    if symbol == pg.window.key.ESCAPE:
        esc_pressed = False

keys = pg.window.key.KeyStateHandler()
window.push_handlers(keys)

# Gets directory of the program and decides where to find the sound
# files based off if ran as a script or as an .exe
if getattr(sys, 'frozen', False):
    # If the application is run as .exe
    current_dir = sys._MEIPASS
else:
    # If the application is run as a script
    current_dir = os.path.dirname(os.path.abspath(__file__))

# Makes filepaths using that directory
dink_path = os.path.join(current_dir, 'dink.wav')
dinkdink_path = os.path.join(current_dir, 'dinkdink.wav')
dinkdinkbackwards_path = os.path.join(current_dir, 'dinkdinkbackwards.wav')
tap_path = os.path.join(current_dir, 'tap.wav')
dun_path = os.path.join(current_dir, 'dun.wav')

# Load the files with said directories
dink = pg.media.load(dink_path, streaming=False)
dinkdink = pg.media.load(dinkdink_path, streaming=False)
dinkdinkbackwards = pg.media.load(dinkdinkbackwards_path, streaming=False)
tap = pg.media.load(tap_path, streaming=False)
dun = pg.media.load(dun_path, streaming=False)


# Make score labels
rScore = pg.text.Label('0',
                    font_name='Minecraft',
                    font_size=50,
                    x=window.width - 35, y=window.height - 50,
                    anchor_x='center', anchor_y='center')

lScore = pg.text.Label('0',
                    font_name='Minecraft',
                    font_size=50,
                    x=35, y=window.height - 50,
                    anchor_x='center', anchor_y='center')

# Make "Max Speed Up" label
speedUpText = pg.text.Label('Max Speed Up',
                            font_name='Minecraft',
                            font_size=40,
                            x=window.width / 2, y=window.height - 60,
                            anchor_x='center', anchor_y='center', color=(0, 0, 0, 0))

# Make pause label
pauseText = pg.text.Label('Paused',
                        font_name='Minecraft',
                        font_size=75,
                        x=window.width / 2, y=window.height / 2,
                        anchor_x='center', anchor_y='center', color=(0, 0, 0, 0))

# Get the window's dimensions
height = window.height
width = window.width

# Creates Right Paddle
rPad = pg.shapes.Rectangle(x=(width / 1.1), y=(height / 2) - 125, width=40, height=220, color=(255, 255, 255))
lPad = pg.shapes.Rectangle(x=(width / 20), y=(height / 2) - 125, width=40, height=220, color=(255, 255, 255))

# Creates the ball
ball = pg.shapes.Rectangle(x=0, y=0, width=40, height=40, color=(255, 255, 255))
ballTrail = pg.shapes.Rectangle(x=0, y=0, width=40, height=40, color=(255, 255, 0, 0))
ball.scale = 0.1
ballTrail.scale = 0.1
ball.x = (width / 2) - (ball.width / 2)
ball.y = (height / 2) - (ball.height / 2)

# Make "Space to start" label (Must be made after ball)
midText = pg.text.Label('Press Space to Start',
                        font_name='Minecraft',
                        font_size=30,
                        x=window.width / 2, y=ball.y - 50,
                        anchor_x='center', anchor_y='center')

# Make you win/lose label (Must be made after ball)
winText = pg.text.Label('Test', # Text is updated upon winning/losing
                        font_name='Minecraft',
                        font_size=50,
                        x=window.width / 2, y=midText.y + 147,
                        anchor_x='center', anchor_y='center', color=(0, 0, 0, 0))


# Add velocity for the ball
ball.velocity_x = 0
ball.velocity_y = 0

# Control variables
maxSpeed = 500
bounce = 1.05
varience = 0
startVelocity = 400
rScoreLast = True
bouncevar = 0
startAngle = 0
roundTimer = 0
inGame = False
redTint = 255

# For pausing
canPause = False
isPaused = False
pauseTimer = 0
canUnpause = False
xVelSave = 0
yVelSave = 0

# Setup window by drawing everything
@window.event
def on_draw():
    window.clear()
    pg.gl.glClearColor(0, 0, 0, 0)
    pauseText.draw()
    ballTrail.draw()
    ball.draw()
    rPad.draw()
    lPad.draw()
    rScore.draw()
    lScore.draw()
    midText.draw()
    speedUpText.draw()
    winText.draw()

# 120 updates per second loop, for most controls and collisions
def update(dt):
    global isPaused, canPause, pauseTimer, canUnpause, inGame, roundTimer, maxSpeed, bounce, varience, startAngle, startVelocity, rScore, lScore, rScoreLast, bouncevar, bounce, redTint, xVelSave, yVelSave, space_pressed, w_pressed, s_pressed, esc_pressed

    # Pauses game
    if esc_pressed and inGame and canPause and not isPaused:
        xVelSave = ball.velocity_x
        yVelSave = ball.velocity_y
        ball.velocity_x = 0
        ball.velocity_y = 0
        pauseTimer = 0
        isPaused = True
        canPause = False
        canUnpause = False
        pauseText.color = (255, 255, 255, 255)
        dinkdink.play()
    
    # Unpauses game
    elif esc_pressed and isPaused and canUnpause:
        isPaused = False
        ball.velocity_x = xVelSave
        ball.velocity_y = yVelSave
        pauseText.color = (255, 255, 255, 0)
        dinkdinkbackwards.play()

    # If not paused, then everything else happens
    elif not isPaused:
        # Make ball move on start
        if ball.velocity_x == 0 and ball.velocity_y == 0 and space_pressed:
            # Make text black + transparent to hide
            midText.color = (0, 0, 0, 0)
            winText.color = (0, 0, 0 ,0)

            if rScoreLast:
                ball.velocity_x = startVelocity
            else:
                ball.velocity_x = -startVelocity

            # Picks a random starting angle but doesn't let be be between
            # -0.2 and 0.2 so theres no really flat starting shots
            startAngle = rand.uniform(-1, 1)

            while -0.2 < startAngle < 0.2:
                startAngle = rand.uniform(-1, 1)

            ball.velocity_y = startAngle * startVelocity
            dun.play()

            inGame = True

        # Update position based on velocity
        ball.x += ball.velocity_x * dt
        ball.y += ball.velocity_y * dt

        # Makes trail follow ball
        ballTrail.x = ball.x - ball.velocity_x / 80
        ballTrail.y = ball.y - ball.velocity_y / 80

        # Max speed
        if ball.velocity_x > maxSpeed:
            ball.velocity_x = maxSpeed
        if ball.velocity_x < -maxSpeed:
            ball.velocity_x = -maxSpeed
        if ball.velocity_y > maxSpeed:
            ball.velocity_y = maxSpeed
        if ball.velocity_y < -maxSpeed:
            ball.velocity_y = -maxSpeed

        # Collision

        # Left paddle collision with ball
        if ball.x < lPad.x + lPad.width + 2 and ball.x > lPad.x + lPad.width - 20 and ball.y + ball.height > lPad.y + 10 and ball.y < lPad.y + lPad.height - 10:
            tempx = ball.velocity_x
            ball.velocity_x = 0
            ball.x = lPad.x + lPad.width
            ball.velocity_x = tempx * -bounce
            tap.play()

        # Right paddle collision with ball
        if ball.x + ball.width < rPad.x + 20 and ball.x + ball.width > rPad.x - 2 and ball.y + ball.height > rPad.y + 10 and ball.y < rPad.y + rPad.height - 10:
            tempx = ball.velocity_x
            ball.velocity_x = 0
            ball.x = rPad.x - ball.width
            ball.velocity_x = tempx * -bounce
            tap.play()

        # Ball collision with window
        if ball.y < 0:
            tempy = ball.velocity_y
            ball.velocity_y = 0
            ball.y = 0
            ball.velocity_y = tempy * -bouncevar
            dink.play()

        if ball.y + ball.height > window.height:
            tempy = ball.velocity_y
            ball.velocity_y = 0
            ball.y = window.height - ball.height
            ball.velocity_y = tempy * -bouncevar
            dink.play()

        # Right paddle collision with window
        if rPad.y < 0:
            rPad.y = 0
        if rPad.y + rPad.height > window.height:
            rPad.y = window.height - rPad.height

        # Left paddle collision with window
        if lPad.y < 0:
            lPad.y = 0
        if lPad.y + lPad.height > window.height:
            lPad.y = window.height - lPad.height

        # Right paddle Movement
        if w_pressed:
            rPad.y += 500 * dt
        if s_pressed:
            rPad.y -= 500 * dt

        # Left paddle Movement
        if ((ball.y + ball.height / 2) + (ball.velocity_y / 3.5) > (lPad.y + lPad.height / 2)) * varience:
            lPad.y += 500 * dt
        if ((ball.y + ball.height / 2) + (ball.velocity_y / 3.5) < (lPad.y + lPad.height / 2)) * varience:
            lPad.y -= 500 * dt

# 1 update per second loop, for score and game clock mainly
def slower_update(dt):
    global isPaused, canPause, pauseTimer, canUnpause, inGame, roundTimer, maxSpeed, bounce, varience, startAngle, startVelocity, rScore, lScore, rScoreLast, bouncevar, bounce, redTint, xVelSave, yVelSave, space_pressed, w_pressed, s_pressed, esc_pressed

    # Varience added to the left paddle movement and ball bounce angle
    varience = rand.uniform(.8, 1.2)
    bouncevar = rand.uniform(.8, 1.6)

    # Update scores
    if ball.x < 0:
        ball.x = (width / 2) - (ball.width / 2)
        ball.y = (height / 2) - (ball.height / 2)
        ball.velocity_x = 0
        ball.velocity_y = 0
        rScore.text = str(int(rScore.text) + 1)
        rScoreLast = False
        midText.color = (255, 255, 255, 255)
        inGame = False
        resetRound()

    if ball.x + ball.width > width:
        ball.x = (width / 2) - (ball.width / 2)
        ball.y = (height / 2) - (ball.height / 2)
        ball.velocity_x = 0
        ball.velocity_y = 0
        lScore.text = str(int(lScore.text) + 1)
        rScoreLast = True
        resetRound()
    
    # Has the player to get 7 points first be the winner
    lScore_value = lScore.text
    if int(lScore_value) >= 7:
        lScore.text = ('0')
        lScore_value = 0
        winText.text = ("You Lose!")
        winText.color = (255, 255, 255 ,255)
        
    rScore_value = rScore.text
    if int(rScore_value) >= 7:
        rScore.text = ('0')
        rScore_value = 0
        winText.text = ("You Win!")
        winText.color = (255, 255, 255 ,255)

    # Timer for checking when you can pause / unpause again
    if inGame and not isPaused:
        pauseTimer += 1
        if pauseTimer >= 1 and not isPaused:
            canPause = True
            pauseTimer = 0

    if isPaused:
        pauseTimer += 1
        if pauseTimer >= 1:
            canUnpause = True
            pauseTimer = 0

    # Timer that counts once per sec for ball speed
    if inGame and not isPaused:
        roundTimer += 1
        speedUpText.color = (0, 0, 0, 0)

        # Increase max speed by 250 every 10 sec
        if maxSpeed < 1100:
            speedUpText.text = ("Max Speed Up")
            if roundTimer >= 10:
                maxSpeed += 100
                roundTimer = 0

                # Caps how red the ball can get
                if redTint > 41:
                    redTint -= 40
                    ball.color = (255, redTint, redTint, 255)
                speedUpText.color = (255, 255, 255, 255)
        else:
            speedUpText.text = ("Max Speed")
            speedUpText.color = (255, 255, 255, 255)
            ballTrail.color = (255, 100, 0, 255)

    else:
        roundTimer = 0

"""The only function, just used to reset everything whenever a round ends"""
def resetRound():
    global inGame, redTint, roundTimer, maxSpeed
    midText.color = (255, 255, 255, 255)
    inGame = False
    ball.color = (255, 255, 255, 255)
    redTint = 255
    maxSpeed = 500
    speedUpText.color = (0, 0, 0, 0)
    roundTimer = 0
    ballTrail.color = (255, 100, 0, 0)

# Schedule updates
pg.clock.schedule_interval(update, 1 / 120.0)
pg.clock.schedule_interval(slower_update, 1 / 1.0)
# Run the app
pg.app.run()