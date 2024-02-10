from curses.textpad import Textbox
import pygame
import datetime
import pandas as pd
import numpy as np
import random 

# program initialization

# Button object
class Button(object):
    def __init__(self, surface, color_Bg, color_Text, text, start_x, start_y, length, width, font):

        self.surface = surface    

        self.color_Bg = color_Bg                # background color of the button
        self.color_Text = color_Text            # color of the text in button
        self.text = text    

        self.start_x = start_x                
        self.start_y = start_y
        self.length = length
        self.width = width

        self.font = font
        self.color_Text = color_Text

    #  set Button
    def set_Button(self):
        #draw the structure of the rect Button
        pygame.draw.rect(self.surface, self.color_Bg, (self.start_x, self.start_y, self.length, self.width), border_radius=30)
        
        #Using the render to returns a surface containing the rendered text.
        button_text = self.font.render(self.text, True, self.color_Text)

        #put the text surface into the center of the Button
        window.blit(button_text, (self.start_x + self.length / 2 - button_text.get_rect().width / 2,
                                  self.start_y + self.width / 2 - button_text.get_rect().height / 2))
        #update
        pygame.display.flip()

    #  press botton
    def Button_press(self, mouseX, mouseY):

        #determine if user click the botton
        if (mouseX >= self.start_x and mouseX <= self.start_x + self.length
                and mouseY >= self.start_y and mouseY <= self.start_y + self.width):
            return True
        else:
            return False
        

class InputBox:
    def __init__(self, rect = pygame.Rect) -> None:
        self.boxBody = rect

        self.color_inactive = pygame.Color(211, 211, 211)  # Color when not selected
        self.color_active = pygame.Color(65, 105, 225)     # Color when selected
        self.color = self.color_inactive                   # Initial color is inactive
        
        self.active = False                                # click input box
        self.text = ''                                     # user input text
        self.text_length = 0                               # length of user input

        self.done = False                                
        self.font = font1

    def dealMouse(self, event = pygame.event.Event):

        # determine if the user click the input box
        # boxBody is an instance of the pygame.Rect class. collidepoint() is the method of the Rect class.
        if self.boxBody.collidepoint(event.pos):
            self.active = True
        else:
            self.active = False
        
        if self.active:
            self.color = self.color_active
        else:
            self.color = self.color_inactive


    def dealKeyboard(self, event: pygame.event.Event):                 
        
        if self.active:
            if event.key == pygame.K_BACKSPACE:
                self.text = self.text[:-1]
                self.text_length -= 1
            else:
                if self.text_length < 8:
                    self.text += event.unicode
                    self.text_length += 1
    
    def draw(self, screen: pygame.surface.Surface):
        pygame.draw.rect(screen, self.color, self.boxBody, 2)
        txtSurface = self.font.render(self.text, True, (0, 0, 0))        

        screen.blit(txtSurface, (self.boxBody.x+5, self.boxBody.y+5))


class TextBox:
    def __init__(self, text, color, font_size, position, max_width):

        self.text = text                  
        self.color = color                # text color
        self.position = position          # position of the text

        self.font_size = font_size
        self.max_width = max_width

        self.font = pygame.font.SysFont("Arial", font_size, bold=True)

    def render(self, surface):                                                      
        
        lines = self.text.split("\n")

        for i, line in enumerate(lines):

            # using render() to return the text surface
            text_surface = self.font.render(line, True, self.color)

            text_rect = text_surface.get_rect()
            # text starts from topleft corner, to position each line separately in order.
            text_rect.topleft = (self.position[0], self.position[1] + i * self.font_size)

            surface.blit(text_surface, text_rect)





def Font(size):
    #create the font object which is an instance of the pygame.font.Font class
    font = pygame.font.SysFont("Arial", size, bold=True)
    return font



# game initialization
pygame.init()

# Initialize Pygame mixer for sound
pygame.mixer.init()

window = pygame.display.set_mode((1100,700))
pygame.display.set_caption("GoBang")
music = pygame.mixer.Sound("bgm.mp3")


# variable initialization

# Initialize the different type of font.
font1 = Font(35)
font2 = Font(30)
font3 = Font(32)
font4 = Font(45)

# Go piece
black = pygame.image.load("black.png")
black = pygame.transform.scale(black,(40,40))
white = pygame.image.load("white.png")
white = pygame.transform.scale(white, (40,40))

page_order = 0                              # current page
game_mode = 0                               # game mode, double:0
game_state = 1                             # 0 for game end, 1 for game-ing
board = [[0] * 15 for i in range(15)]       #create 2D goBang board
go_piece_count = 0                          # count the number of the go piece in game
history = []            
draw = 0                
winner = ""                                 # winner 
loser = ""                                  # loser
user_name = []                              # player name list
sound = 0
msg = "" 


def window_change(page_order):
    # page 0: Home page  1: Play mode page   2: Game page  3: PVP prepare page  9: rule page

    # Home page
    if page_order == 0:
        global button_start
        global button_rank
        global button_hisroty
        global button_rule

    # create the game start background and sound sign
    startBackground = pygame.image.load("background.jpg")
    window.blit(startBackground, (0, 0))

    # create the sound sign
    sound = pygame.image.load("sound.png")
    sound = pygame.transform.scale(sound,(40,40))
    window.blit(sound,(1020,20))

    # start game button
    button_start = Button(window, (255, 211, 155), (0, 0, 0), "Start Game", 650, 100, 250, 120, font1)
    button_start.set_Button()
    # player's rank button
    button_rank = Button(window, (255, 174, 185), (0, 0, 0), "Player Rank", 665, 270, 220, 95, font2)
    button_rank.set_Button()
    # rank hustory button
    button_hisroty = Button(window, (175, 238, 238), (0, 0, 0), "Rank History", 665, 410, 220, 95, font2)
    button_hisroty.set_Button()
    # game rules button
    button_rule = Button(window, (202, 225, 255), (0, 0, 0), "Game Rules", 665, 550, 220, 95, font2)
    button_rule.set_Button()

    # game title
    text_title = TextBox("Go", (0, 0, 0), 200, (150, 100),300)
    text_title.render(window)
    text_title = TextBox("Bang", (0, 0, 0), 200, (50, 300),300)
    text_title.render(window)

    pygame.display.flip() 

    # play model page
    if page_order == 1:
        global button_back1
        global button_PVAI
        global button_PVP


        gameBackground = pygame.image.load("background.jpg")
        gameBackground = pygame.transform.scale(gameBackground, (1100, 700))
        window.blit(gameBackground, (0, 0))

        #set uo 3 buttons
        button_PVP = Button(window, (255, 222, 173), (0, 0, 0), "P v P", 420, 200, 300, 120, font4)
        button_PVP.set_Button()
        button_PVAI = Button(window, (255, 222, 173), (0, 0, 0), "P v AI", 420, 380, 300, 120, font4)
        button_PVAI.set_Button()
        button_back1 = Button(window, (255, 222, 173), (0, 0, 0), "Back", 830, 570, 180, 75, font1)
        button_back1.set_Button()
        pygame.display.flip()  

    # Game page
    if page_order == 2:
        global button_Undo
        global button_draw
        global button_back2

        gameBackground = pygame.image.load("background.jpg")
        window.blit(gameBackground, (0, 0))

        # draw the gobang board

        pygame.draw.rect(window, (238, 154, 73), (50, 50, 630, 630))  # (x1, y1, length, width)

        for j in range(80, 680, 40):

            pygame.draw.line(window, (0, 0, 0), (80, j), (640, j), 4)
            pygame.draw.line(window, (0, 0, 0), (j, 80), (j, 640), 4)

        pygame.draw.circle(window, (0, 0, 0), (200, 200), 5)
        pygame.draw.circle(window, (0, 0, 0), (520, 200), 5)
        pygame.draw.circle(window, (0, 0, 0), (200, 520), 5)
        pygame.draw.circle(window, (0, 0, 0), (520, 520), 5)
        pygame.draw.circle(window, (0, 0, 0), (360, 360), 5)

        #  undo button
        button_Undo = Button(window, (185, 211, 238), (0, 0, 0), "Undo", 800, 400, 200, 80, font3)
        button_Undo.set_Button()
        #  draw button
        button_draw = Button(window, (143, 188, 143), (0, 0, 0), "Draw", 800, 500, 200, 80, font3)
        button_draw.set_Button()
        # back button
        button_back2 = Button(window, (255, 222, 173), (0, 0, 0), "Back", 800, 600, 200, 80, font3)
        #update the information to the windows
        pygame.display.flip()  

    # PVP prepare page
    if page_order == 3:
        global button_back3
        global button_confirm
        global inputbox_black
        global inputbox_white
        global user_name


        gameBackground = pygame.image.load("background.jpg")
        gameBackground = pygame.transform.scale(gameBackground, (1100, 700))
        window.blit(gameBackground, (0, 0))


        text_black = TextBox("Black player: ", (0, 0, 0), 30, (80, 200),300)
        text_black.render(window)
        text_white = TextBox("White player: ", (0, 0, 0), 30, (80, 400),300)
        text_white.render(window)

        text_reminders = "Reminder: \n"  + "1.Username will be recorded, \n same username will be treated \n as one account" + "\n"+ " \n 2. name what you like but \n no more than 8 charecters"
        text_reminder = TextBox(text_reminders, (0, 0, 0), 33, (600, 200),1000)
        text_reminder.render(window)
        
        text_title = "Enter your name now!"
        text_title = TextBox(text_title, (0, 0, 0), 50, (50, 50),1000)
        text_title.render(window)
    
        inputbox_black = InputBox(pygame.Rect(300, 185, 200, 60))
        inputbox_black.draw(window)  
        inputbox_white = InputBox(pygame.Rect(300, 385, 200, 60))  
        inputbox_white.draw(window)  
        
        button_confirm = Button(window, (255, 222, 173), (0, 0, 0), "Sure", 300, 580, 180, 75, font3)
        button_confirm.set_Button()
        button_back3 = Button(window, (255, 222, 173), (0, 0, 0), "Back", 600, 580, 180, 75, font3)
        button_back3.set_Button()

        pygame.display.flip()  


    # rule page
    if page_order == 9:
        global button_back9
        ruleBackground = pygame.image.load("background.jpg")
        ruleBackground = pygame.transform.scale(ruleBackground, (1100, 700))
        window.blit(ruleBackground, (0, 0))

        text_rule_titles = "Game Rule"
        text_rule_title = TextBox(text_rule_titles, (0, 0, 0), 100, (250, 50), 800)
        text_rule_title.render(window)

        text_rules = "Players alternate turns placing a stone of their color \n on an empty intersection. Black plays first. \n The winner is the first player to form a five stones \n unbroken line of their color horizontally, vertically,\n or diagonally. \n If no one win the game, then it is draw."
        text_rule = TextBox(text_rules, (0, 0, 0), 38, (100, 200),800)
        text_rule.render(window)

        button_back9 = Button(window, (255, 222, 173), (0, 0, 0), "Back", 830, 610, 180, 75, font1)
        button_back9.set_Button()

        pygame.display.flip()  


### funtions

def chessPos(p):

    if p <= 100 and p >= 60:
        pos = 0

    elif p < 60 :
        pos = -1

    elif p >= 620 and p <= 660:
        pos = 14

    elif p > 660:
        pos = 20

    elif p >= 100 and p <= 620:
        pos = int((p - 100) / 40 + 1)

    return pos



def chessDown(mouseX, mouseY):
    global go_piece_count
    global board
    global history
    global game_state
    
    col = chessPos(mouseX)
    row = chessPos(mouseY)

    windowX = col * 40 + 60
    windowY = row * 40 + 60

    if game_state == 1:
        if (mouseX >= 60 and mouseX <= 660) and (mouseY >= 60 and mouseY <= 660):
            
            # determine if is empty in this area
            if board[row][col] == 0:

                # determine is black turn or white turn
                if go_piece_count % 2 == 0:
                    
                    # black
                    chess = black
                    board[row][col] = 1
                else:

                    #white
                    chess = white
                    board[row][col] = 2

                # place the color chess on the board
                window.blit(chess, (windowX, windowY))
                pygame.display.flip()

                go_piece_count += 1

                history.append([row, col])

    return go_piece_count



def winGame(board, mouseX, mouseY):

    horizontal, vertical, diagonal = 0, 0, 0

    # determine the color of the chess
    if go_piece_count % 2 == 1:
        go_piece_color = 1

    else:
        go_piece_color = 2

    # get the col and the row
    col = chessPos(mouseX)
    row = chessPos(mouseY)
    
    if (col <= 14 and col >= 0) and (row >= 0 and row <=14):

        # vertical
        i = row
        while horizontal < 5 and i >= 0:

            if board[i][col] == go_piece_color:
                horizontal += 1

                if i != 0:
                    i -= 1
                else:
                    break
            else:
                break

        i = row + 1
        while horizontal < 5 and i <= 14:

            if i != 14:

                if (board[row][i] == go_piece_color):
                    horizontal += 1  
                else:
                    break

                i += 1
            else:
                break

        # horizontal
        j = col
        while vertical < 5 and j >= 0 :
            
            if board[row][j] == go_piece_color:
                vertical += 1

                if j != 0:
                    j -= 1
                else: 
                    break
            else:
                break

        j = col + 1
        while vertical < 5 and j <= 14:

            if j != 14:

                if (board[row][j] == go_piece_color):
                    vertical += 1  
                else:
                    break   

                j += 1
            else:
                break
            
        
        # diagonal
        if vertical < 5 and horizontal < 5:

            i, j = row, col
            while diagonal < 5 and j >= 0 and i >= 0:

                if board[i][j] == go_piece_color:

                    diagonal += 1
                    if i != 0:
                        i -= 1
                    else: 
                        break

                    if j != 0:
                        j -= 1
                    else:
                        break

                else:
                    break
            
            i , j = row+1, col+1
            while diagonal < 5 and j < 15 and  i < 15:

                if board[i][j] == go_piece_color:

                    diagonal += 1
                    if i != 14:
                        i += 1
                    else:
                        break

                    if j != 14:
                        j += 1
                    else:
                        break

                else: 
                    break

        if horizontal == 5 or vertical == 5 or diagonal == 5:
            return True
        
    return False

def undo(pos):                    
    global board
    global go_piece_count
    global history

    row = pos[0]
    col = pos[1]

    windowX = col * 40 + 60
    windowY = row * 40 + 60
    pygame.draw.rect(window, (238, 154, 73), (windowX, windowY, 40, 40))
    
    
    if col != 0:  
        pygame.draw.line(window, (0, 0, 0), (60 + col * 40, 80 + row * 40), (80 + col * 40, 80 + row * 40), 3)
    if col != 14:  
        pygame.draw.line(window, (0, 0, 0), (80 + col * 40, 80 + row * 40), (100 + col * 40, 80 + row * 40), 3)
    if row != 0:  
        pygame.draw.line(window, (0, 0, 0), (80 + col * 40, 60 + row * 40), (80 + col * 40, 80 + row * 40), 3)
    if row != 14:  
        pygame.draw.line(window, (0, 0, 0), (80 + col * 40, 80 + row * 40), (80 + col * 40, 100 + row * 40), 3)
    
    board[row][col] = 0
    
    go_piece_count -= 1
    pygame.display.flip()  


def endGame (draw1):
    global user_name
    global winner
    global loser
    global draw
    global msg
    global go_piece_count

    #draw situation
    if draw1:
        draw = 1
        msg = "Draw!"

    else:

        if go_piece_count % 2 ==1:
            msg = user_name[0] + " win!"
            winner = user_name[0]
            loser = user_name[1]

        else:
            msg = user_name[1] + " win!"
            winner = user_name[1]
            loser = user_name[0]

    # show the winner congraduation
    result_text = font4.render(msg, True, (255, 0, 0))
    window.blit(result_text, (790, 300))
    pygame.display.flip()




def startFunc():
    global page_order
    global winner
    global loser
    global go_piece_count
    global board
    global msg
    global game_state
    global sound
    global history

    winner = ""
    loser = ""
    go_piece_count = 0
    history = []
    board = [[0] * 15 for i in range(15)]

    if event.type == pygame.MOUSEBUTTONDOWN:
        x, y = event.pos

        # press start button
        if button_start.Button_press(x, y):
            page_order = 1
            game_state = 1
            window_change(page_order)

        # press rule button
        if button_rule.Button_press(x, y):
            page_order = 9
            window_change(page_order)

        # open or close the bgm
        if x <= 1060 and x >= 1020 and y <= 60 and y >= 20:
            if sound:
                music.stop()
                sound = 0
            else:
                music.play()
                sound = 1


def modeFunc():
    global page_order
    global game_mode


    if event.type == pygame.MOUSEBUTTONDOWN:
        x, y = event.pos

        
        if button_PVP.Button_press(x, y):
            page_order = 3
            window_change(page_order)

        # back to home page
        if button_back1.Button_press(x,y):
            page_order = 0
            window_change(page_order)


def pairFunc():
    global page_order
    global inputbox_black
    global inputbox_white
    global user_name
    global button_back3
    global button_confirm

    if event.type == pygame.MOUSEBUTTONDOWN:
        pygame.draw.rect(window, (255, 255, 255), (300, 185, 200, 60))  
        pygame.draw.rect(window, (255, 255, 255), (300, 385, 200, 60))
        inputbox_black.dealMouse(event)
        inputbox_white.dealMouse(event)
        inputbox_black.draw(window)                                     
        inputbox_white.draw(window)
        pygame.display.flip()

        x, y = event.pos
        if button_back3.Button_press(x, y):
            page_order = 1
            window_change(page_order)

        elif button_confirm.Button_press(x, y):
            if len(inputbox_black.text) > 0 and len(inputbox_white.text) > 0:
                user_name.append(inputbox_black.text)
                user_name.append(inputbox_white.text)
                page_order = 2
                window_change(page_order)
    
    if event.type == pygame.KEYDOWN:
        pygame.draw.rect(window, (255, 255, 255), (300, 185, 200, 60))  
        pygame.draw.rect(window, (255, 255, 255), (300, 385, 200, 60))
        inputbox_black.dealKeyboard(event)
        inputbox_white.dealKeyboard(event)
        inputbox_black.draw(window)  
        inputbox_white.draw(window)
        pygame.display.flip()

    


#
def gameFunc():
    global go_piece_count
    global board
    global history
    global page_order
    global game_state
    global user_name
    global button_back2
    global winner
    global draw

    
    font = pygame.font.SysFont("Arial", 60, bold=True)

    textBlack = font.render(user_name[0], True, (65, 105, 225))
    window.blit(textBlack, (890 - textBlack.get_rect().width / 2, 80))

    textVS = TextBox("VS", (0, 0, 0), 60, (850, 160),800)
    textVS.render(window)

    textWhite = font.render(user_name[1], True, (65, 105, 225))
    window.blit(textWhite, (890 - textWhite.get_rect().width / 2, 240))


    if event.type == pygame.MOUSEBUTTONDOWN:
        x, y = event.pos
        chessDown(x, y)

        if go_piece_count == 225:           
            endGame(True)
            game_state = 0

        if winGame(board, x, y):            
            endGame(False)
            game_state = 0

        if game_state == 1 and button_Undo.Button_press(x, y):         
            if go_piece_count > 0:
                undo(history.pop())

        if game_state == 1 and button_draw.Button_press(x, y):          
            endGame(True)
            game_state = 0

        if game_state == 0 or draw == 1:
            button_back2.set_Button()
            pygame.display.flip()

            if button_back2.Button_press(x, y):
                page_order = 0
                window_change(page_order)



# 9 rule
def ruleFunc():

    global page_order

    if event.type == pygame.MOUSEBUTTONDOWN:
        x, y = event.pos

        if button_back9.Button_press(x, y):
            page_order = 0
            window_change(page_order)

    
    
    

# game initialization
pygame.init()

# Initialize Pygame mixer for sound
pygame.mixer.init()
music = pygame.mixer.Sound("bgm.mp3")

window = pygame.display.set_mode((1100,700))
pygame.display.set_caption("GoBang")



window_change(0)
while True:

    for event in pygame.event.get():
        
        if event.type == pygame.QUIT:
            exit()
            sys.exit()
        if page_order == 0:
            startFunc()
        
        if page_order ==1:
            modeFunc()

        if page_order == 3:
            pairFunc()
        
        if page_order == 2:
            gameFunc()
        
        if page_order ==9:
            ruleFunc()
        


    pygame.display.flip()

        





