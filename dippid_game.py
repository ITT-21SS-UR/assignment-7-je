#script written by joshua benker

import sys
import math
import random
from PyQt5 import QtGui, QtCore, QtWidgets
from DIPPID import SensorUDP
from enum import Enum


SENSOR_PORT = 5700

WINDOW_WIDTH = 650
WINDOW_HEIGHT = 650
BODY_WIDTH = 100
BODY_HEIGHT = 30


#state of the game
class GameState(Enum):
    INTRO = 1
    START = 2
    LOST = 3

#main game class
#neccesssary: an android phone to get the dippid sensor output
#creates a ball-object and two body-objects from the other classes
class Game(QtWidgets.QWidget):

    sensor = ()
    timer = ()
    body_bottom = ()
    body_top = ()
    ball = ()
    points = 0

    def __init__(self):
        super().__init__()
        self.screen_x_size = WINDOW_WIDTH
        self.screen_y_size = WINDOW_HEIGHT
        self.setFixedSize(self.screen_x_size, self.screen_y_size)
        self.setFocusPolicy(QtCore.Qt.StrongFocus)
        self.init_sensor()
        self.init_body()
        self.init_ball()
        self.timer = QtCore.QTimer(self)
        self.xPos_bt = self.frameGeometry().width() / 2 - BODY_WIDTH / 2
        self.yPos_bt = self.frameGeometry().height() - BODY_HEIGHT
        self.info = QtCore.QRect(0, self.frameGeometry().height() / 2,self.frameGeometry().width(), 100)
        self.points_box = QtCore.QRect(20, 10, self.frameGeometry().width(), 40)
        self.game_state = GameState.INTRO
        self.init_timer_game_loop()
        self.show()
    
    #initialize the painter and calls the info depending on the game state
    def paintEvent(self, event):
        painter = QtGui.QPainter(self)
        self.draw_body(painter)
        self.draw_ball(painter)
        self.draw_points(painter)
        if self.game_state == GameState.INTRO:
            self.draw_intro_message(painter)
        elif self.game_state == GameState.LOST:
            self.draw_gamover_message(painter)
  
    #paints the bodies
    def draw_body(self, painter):
        painter.setBrush(QtGui.QBrush(QtCore.Qt.blue, QtCore.Qt.SolidPattern))
        painter.drawRect(self.body_bottom)
        painter.drawRect(self.body_top)

    #paints the ball
    def draw_ball(self, painter):
        painter.setBrush(QtGui.QBrush(QtCore.Qt.cyan, QtCore.Qt.SolidPattern))
        painter.setPen(QtGui.QPen(QtCore.Qt.cyan, QtCore.Qt.SolidPattern))
        painter.drawEllipse(self.ball.x, self.ball.y, self.ball.radius, self.ball.radius)

    #paints the intro message
    def draw_intro_message(self, painter):
        painter.setPen(QtGui.QPen(QtCore.Qt.black, QtCore.Qt.SolidPattern))
        text = "Welcome.\nPress 'Button 1' to start.\nUse your phone to move " \
               "the two objects by tilting it. \n You are both players."
        painter.drawText(self.info, QtCore.Qt.AlignCenter, text)

    #paints the game over message
    def draw_gamover_message(self, painter):
        text = "Oh damn. You missed the ball! \n " \
                "You made " +str(self.points)+ " points \nPress 'Button 1' to restart."
        painter.drawText(self.info, QtCore.Qt.AlignCenter, text)

    #paints the points the player achieves
    def draw_points(self,painter):
        painter.setPen(QtGui.QPen(QtCore.Qt.black, QtCore.Qt.SolidPattern))
        points = "Points: " + str(self.points)
        painter.drawText(self.points_box, QtCore.Qt.AlignLeft, points)

    #initialize the sensor on port 5700
    def init_sensor(self):
        BUTTON_START = 'button_1'
        self.sensor = SensorUDP(SENSOR_PORT)
        self.sensor.register_callback(BUTTON_START, self.button_start_pressed)

    #initialize the two bodies with the class 'Body'
    def init_body(self):
        self.xPos_bt = self.frameGeometry().width() / 2 - BODY_WIDTH / 2
        self.yPos_bt = self.frameGeometry().height() - BODY_HEIGHT
        self.body_bottom = Body(self.xPos_bt, self.yPos_bt, BODY_WIDTH, BODY_HEIGHT, self, 'bottom')
        self.body_top = Body(self.xPos_bt, 0, BODY_WIDTH, BODY_HEIGHT, self, 'top')
 
    #initialize the ball with the class 'Ball'
    def init_ball(self):
        xPos = self.body_bottom.x() + self.body_bottom.body_width / 2
        yPos = self.body_bottom.y() - 25
        self.ball = Ball(xPos, yPos, 30, self)

    #game loop
    #found on https://doc.qt.io/qtforpython-5/PySide2/QtCore/QTimer.html
    def init_timer_game_loop(self):
        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(self.game_loop)
        self.timer.start(30)

    #gets called when the 'button 1' got pressed
    #changes the game state and restarts the game if it's over
    def button_start_pressed(self,data):
        if data == 0:
            return
        if self.game_state == GameState.INTRO:
            self.game_state = GameState.START
        if self.game_state == GameState.LOST:
            self.game_state = GameState.START
            self.start_new_round()
            

    #game loop gets called by the timer
    def game_loop(self):
        if self.game_state == GameState.START:
            if self.sensor.has_capability('accelerometer'):
                sensorVal = self.sensor.get_value('accelerometer')
            else:
                return
            value_y = sensorVal['y']
            self.body_bottom.move(value_y *7)
            self.body_top.move(value_y *7)
            self.ball.move()
            self.update()

    #gets called by the ball function is_gameover
    #sets the game state to "lost"
    def on_gameover(self):
        self.game_state = GameState.LOST
        self.update()

    #gets called when the player starts a new round after he lost
    def start_new_round(self):
        self.points = 0
        self.body_bottom.moveTo(self.xPos_bt,self.yPos_bt)
        self.body_top.moveTo(self.xPos_bt, 0)
        self.init_ball()

#class for the body
#handles moving depending on the body-type (bottom or top body)
class Body(QtCore.QRect):

    def __init__(self, x, y, width, height, window, body_type):
        super().__init__(x, y, width, height)
        self.window = window
        self.body_width = width
        self.body_height = height
        self.body_type = body_type

    def move(self, value_y):
        if self.body_type == 'bottom':
            self.moveLeft(self.x() + value_y)
            if self.x() < 0:
                self.moveLeft(0)
            elif self.x() > self.window.frameGeometry().width() - self.body_width:
                self.moveLeft(self.window.frameGeometry().width() - self.body_width)
        elif self.body_type == 'top':
            self.moveLeft(self.x() - value_y)
            if self.x() < 0:
                self.moveLeft(0)
            elif self.x() > self.window.frameGeometry().width() - self.body_width:
                self.moveLeft(self.window.frameGeometry().width() - self.body_width)

#class for the ball
#handles moving and if it hits the window or the body
class Ball:

    def __init__(self, x, y, diameter, window):
        self.window = window
        self.x = x
        self.y = y
        self.diameter = diameter
        self.radius = diameter / 2
        self.speed_x = 6
        self.speed_y = -6

    #handles ball-moving
    def move(self):
        self.x += self.speed_x
        self.y += self.speed_y
        self.hit_window()
        self.hit_body()
        self.is_gameover()

    #checks if ball hits the body
    def hit_body(self):
        hit = self.touch_body(self.window.body_bottom)
        if hit == False:
            hit = self.touch_body(self.window.body_top)
        if hit == 1:
            self.speed_x *= -1
        elif hit == 2:
            self.window.points += 1
            self.speed_y *= -1

    #checks if ball hits the window   
    def hit_window(self):
        if self.x + self.radius * 2 > self.window.frameGeometry().width() or self.x <= 0:
            self.speed_x *= -1

        elif self.y <= 0:
            self.speed_y *= -1


    #calculates the distance and returns where the ball hit the body 
    def touch_body(self, rect):
        x_middle = self.x + self.radius
        y_middle = self.y + self.radius
        x_value = x_middle
        y_value = y_middle

        if y_middle > rect.bottom():
            y_value = rect.bottom()
        elif y_middle < rect.top():
            y_value = -rect.top()
        if x_middle < rect.left():
            x_value = rect.left()
        elif x_middle > rect.right():
            x_value = rect.right()

        distance_x = x_middle - x_value
        distance_y = y_middle - y_value
        distance = math.sqrt(distance_x **2 + distance_y **2)

        if distance <= self.radius:
            if distance_x == 0:
                return 2
            elif distance_y == 0:
                return 1

        return False

    #checks if player is game over
    def is_gameover(self):
        if self.y > self.window.frameGeometry().height() or self.y <= 0:
            self.window.on_gameover()

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    game = Game()
    app.exec()

