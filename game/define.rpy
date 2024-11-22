
image board_with_shield_closed:
    "game_board_closed.png"
    zoom 2.300
    xpos 530
    ypos 1900
  
image shield_open:              # solo shield aperto
    "shield_open.png"
    zoom 0.5
    xpos 530
    ypos 1900

image shield_btn:               # bottone trasparente della dimensione dello shield
    "shield_btn.png"
    zoom 1.8

image menu_btn:
    "bottone_menu.png"
    zoom 0.2   

image checkmark:
    "checkmark10.png"
    zoom 0.4

image checkmark_disabled:
    "checkmark10disabled.png"
    zoom 0.4

image copilot_off:
    "copilot off.png"
    zoom 0.330

image copilot_on:
    "copilot on.png"
    zoom 0.330

image best_code_ready:
    "best code ready.png"
    zoom 0.330

image best_code_processing:
    "best code processing.png"
    zoom 0.330

image best_code_processing2:
    "best code processing2.png"
    zoom 0.330

image info:
    "info2.png"
    zoom 1.0

image x:
    "x.png"
    zoom 0.600

image arrow:
    "arrow.png"
    zoom 0.4

#######################

image drag_tip:
    "03_yellow.png"
    zoom 0.220

image shield_tip:
    "shield_tip.png"
    zoom 1.0

image info_tip:
    "info2.png"
    zoom 1.0

image best_code_processing_tip:
    "best code processing.png"
    zoom 0.300

image best_code_ready_tip:
    "best code ready.png"
    zoom 0.300

image copilot_on_tip:
    "copilot on.png"
    zoom 0.300

########################

define peg_zoom = 0.15

image 00_empty:
    "00_empty.png"
    zoom peg_zoom

image 01_blue:
    "01_blue.png"
    zoom peg_zoom

image 02_red:
    "02_red.png"
    zoom peg_zoom

image 03_yellow:
    "03_yellow.png"
    zoom peg_zoom

image 04_green:
    "04_green.png"
    zoom peg_zoom

image 05_white:
    "05_white.png"
    zoom peg_zoom

image 06_black:
    "06_black.png"
    zoom peg_zoom

image 07_orange:
    "07_orange.png"
    zoom peg_zoom

image 08_brown:
    "08_brown.png"
    zoom peg_zoom

######################

define peg_zoom_big = 0.25

image 00_empty_big:
    "00_empty.png"
    zoom peg_zoom_big

image 01_blue_big:
    "01_blue.png"
    zoom peg_zoom_big

image 02_red_big:
    "02_red.png"
    zoom peg_zoom_big

image 03_yellow_big:
    "03_yellow.png"
    zoom peg_zoom_big

image 04_green_big:
    "04_green.png"
    zoom peg_zoom_big

image 05_white_big:
    "05_white.png"
    zoom peg_zoom_big

image 06_black_big:
    "06_black.png"
    zoom peg_zoom_big

image 07_orange_big:
    "07_orange.png"
    zoom peg_zoom_big

image 08_brown_big:
    "08_brown.png"
    zoom peg_zoom_big

image key_white_big:
    "00_key_white.png"
    zoom 0.40

image key_black_big:
    "01_key_black.png"
    zoom 0.40

image key_empty_big:
    "03_key_empty.png"
    zoom 0.40

############################

image key_white:
    "00_key_white.png"
    zoom 0.12

image key_black:
    "01_key_black.png"
    zoom 0.12

image key_empty:
    #"03_key_empty.png"
    "03_key_empty"
    zoom 0.12

#definizione delle liste dei pegs e dei key pegs
define key_pegs = ["key_empty", "key_white", "key_black"]
define pegs = ["00_empty", "01_blue", "02_red", "03_yellow", "04_green", "05_white", "06_black", "07_orange", "08_brown"]
define pegs_big = ["00_empty_big", "01_blue_big", "02_red_big", "03_yellow_big", "04_green_big", "05_white_big", "06_black_big", "07_orange_big", "08_brown_big"]
define key_pegs_big = ["key_empty_big", "key_white_big", "key_black_big"]
#define key_pegs_dropped = ["key_empty_dropped", "key_white_dropped", "key_black_dropped"]

#valori per il posizionamento dei pegs
define v2 = -146
define pegs_vert = [0, 0, v2, v2*2, v2*3, v2*4, v2*5, v2*6, v2*7+5, v2*8+5, v2*9+9, v2*10-45] #distanza verticale tra le giocate di input. In teoria dovevano essere gli stessi valori della board. define 
define s1 = 123
define pegs_oriz =  [0, s1, s1, s1, s1-1, s1-2, s1-2, s1-2, s1-2, s1-2, s1-2, s1-2] #distanza orizzontale tra i pegs


#valori per il posizionamento dei key pegs
define s2 = 61
define key_space =  [0, s2, s2, s2, s2, s2, s2, s2, s2, s2, s2] #distanza orizzontale tra i key pegs
define v3 = -147 #distanza tra una giocata e l'altra
define v4 = -60 #distnaza tra i key code verticate nell'ambito della stessa giocata
define key_oriz = [0, 0, s2]
define key_vert_sopra =  [0, v4, v3+v4, v3*2+v4, v3*3+v4, v3*4+v4, v3*5+2+v4, v3*6+4+v4, v3*7+5+v4, v3*8+5+v4, v3*9+8+v4, v3*10+8+v4] #distanza verticale tra le giocate di tutta la board 
define key_vert_sotto =  [0, 0, v3, v3*2, v3*3, v3*4, v3*5+2, v3*6+4, v3*7+5, v3*8+5, v3*9+5, v3*10+5] #distanza verticale tra le giocate di tutta la board 

#valori per il posizionamento dei score pegs
define v5 = -49
define score_vert = [0, 0, v5, v5*2, v5*3, v5*4, v5*5, v5*6, v5*7, v5*8, v5*9, v5*10, v5*11, v5*12, v5*13, v5*14, v5*15, v5*16, v5*17,
                    v5*18+4, v5*19+4, v5*20+4, v5*21+8, v5*22+8, v5*23+8, v5*24+8, v5*25+8, v5*26+9, v5*27+10, v5*28+10] #distanza verticale tra i pegs score 
define s5 = 64
define score_oriz =  [0, s5-2, s5-2, s5-2, s5-2, s5-2, s5-2, s5-2, s5-2, s5-2, s5-2, s5-3, s5-3, s5-3, s5-4, s5-4, s5-5, s5-5, s5-5,
                    s5-5, s5-5, s5-5, s5-5, s5-5, s5-5, s5-5, s5-5, s5-5, s5-5, s5-5] #distanza orizzontale tra i pegs score

# dimensioni della lista tridimensionale
define n_rows = 11
define n_columns = 4
define n_depth = 2      # indice 1 per xpos e indice 2 per ypos

init 0 python:
    peg_pos = [[[0 for _ in range(n_depth+1)] for _ in range(n_columns+1)] for _ in range(n_rows+1)]    # Crea una lista tridimensionale per posizionamento pegs
    for i in range (1,12):
        for j in range (1,5):
            peg_pos[i][j][1] =  227 + pegs_oriz[i]*j        # posizione orizontale
            peg_pos[i][j][2] = 1810 + pegs_vert[i]          # posizione verticale
    key_pos = [[[0 for _ in range(n_depth+1)] for _ in range(n_columns+1)] for _ in range(n_rows)]    # Crea una lista tridimensionale per posizionamento key pegs
    for i in range (1,11):
        for j in range (1,5):
            if j == 1 or j ==3:                                     #se i key peg sono sulla sx
                key_pos[i][j][1] =  189 + key_oriz[1]               # posizione orizontale
            if j == 2 or j ==4:                                     #se i key peg sono sulla dx
                key_pos[i][j][1] =  189 + key_oriz[2]               # posizione orizontale
            if j == 1 or j ==2:                                     #key peg sopra  
                key_pos[i][j][2] = 1845 + key_vert_sopra[i]         # posizione verticale
            if j == 3 or j ==4:                                     #key peg sopra  
                key_pos[i][j][2] = 1845 + key_vert_sotto[i]         # posizione verticale
    score_pos = [[[0 for _ in range(n_depth+1)] for _ in range(n_columns-1)] for _ in range(n_rows+20)]    # Crea una lista tridimensionale per posizionamento key pegs
    for i in range (1,30):
        for j in range (1,3):
            score_pos[i][j][1] =  745 + score_oriz[i]*j        # posizione orizontale
            score_pos[i][j][2] = 1840 + score_vert[i]          # posizione verticale

init -1 python:
    import random
    from threading import Thread
    import time

default persistent.choice = "none"           # valori che può assumere: play_6, play_8, challenge_6, challenge_8, none
default persistent.status = "on_game"        # valori che può assumere: on_game, final
default persistent.score = [[0 for i in range(3)] for j in range(30)]
default persistent.score_player = 0
default persistent.score_app = 0
default persistent.best_code_active = True
default persistent.perf = []
default persistent.total_time = 0
default persistent.total_time_converted = [0,0,0]
default persistent.welcome = True
default persistent.sound = False

default colors = 6
