label main_menu:
    return    

label start:
    $ quick_menu = False
    $ start_game()

init 1 python:          # starat game + game loop
    config.rollback_enabled = False  
    # renpy.music.set_volume(1.0, delay=0, channel='sound')
    def start_game():        #setup iniziale + loop per il richiamo delle partite
        renpy.show ("mm_bg")        #compare solo questa volta - sfondo del gioco
        renpy.show_screen ("print_mastermind") #richiamato solo da qua - scritta MASTER MIND
        renpy.show ("board_with_shield_closed")     #solo qua 
        renpy.show_screen ("menu_button")    #screen richiamato solo da qua
        persistent.choice = "none"
        if persistent.sound:
            renpy.music.play ("audio/Gershon Kingsley - Pop Corn 1969.mp3")
        #persistent.welcome = True  #truobleshooting welcome message
        if persistent.welcome:
            renpy.show_screen("welcome_message")
            renpy.pause()
            persistent.welcome = False
            renpy.show_screen("message", "WELCOME!", "Tap the menu button indicated by the arrow and read the HELP section before you start playing.", arrow="arrow_up", arrow_x=930, arrow_y=200)
            #renpy.show_screen("tap_main_menu", "WELCOME!", "Tap the menu button indicated by the arrow and read the HELP section before you start playing.")
        else:
            #renpy.show_screen("tap_main_menu", "WELCOME", "Tap the menu button")
            renpy.show_screen("message", "WELCOME", "Tap the menu button", arrow="arrow_up", arrow_x=930, arrow_y=200)
        persistent.show_score_update = "not_show"   # può essere: "game1-game2" o "game3" o "not_show"
        renpy.show_screen("score_update")       #visualizza lo score basato sui pegs
        while True:                             # game loop
            if persistent.choice == "game1":
                if not renpy.emscripten:
                    game1(colors)
                else:
                    game1_web(colors)
            if persistent.choice == "game2":
                game2(colors)
            if persistent.choice == "game3":
                game3(colors)
            if persistent.choice == "training":
                training(colors)
            if persistent.choice == "score":
                score()
                renpy.show_screen("menu")
            if persistent.choice == "settings":
                settings()
                renpy.show_screen("menu")
            if persistent.choice == "help_tips":
                help_tips()
                renpy.show_screen("menu")
            renpy.pause()

init 1 python:          # all needed functions

    def game1(colors):    # ONE PLAYER
        # """ il giocatore deve indovinare il codice segreto scelto dal programma """   
        global clicked          
        global secret_code
        global draggable
        global droppable
        global key_board
        global board
        global thread
        global best_code_ready
        global copilot_on
        global copilot
        global yes_no
        global start_time
        global code_played
        global db_lc
        global db_bc
        global code
        global yes_no
        #mm = Mastermind_Engine()
        renpy.call_screen ("message_2_options", "Break the hidden secret code. \n\nCLASSIC: secret code can use repeating colors.\n\nBASIC: secret code uses\nonly single colors.", "CLASSIC", "BASIC")
        if option == "CLASSIC":
            db_ac, db_lc, db_bc = init_db(colors)                            #crea il database di tutti i codici, dei left e best codes

        if option == "BASIC":
            db_ac, db_lc, db_bc = init_db_basic(colors)                            #crea il database di tutti i codici, dei left e best codes

        if option == "exit":
            persistent.choice = "none"
            #renpy.show_screen("tap_main_menu", "GAME CANCELED", "Tap the menu button")
            renpy.show_screen("message", "GAME CANCELED", "Tap the menu button", arrow="arrow_up", arrow_x=930, arrow_y=200)
            return

        yes_no = ''
        best_code_ready = False
        copilot_on = False                                         
        key_board = []
        board = []
        reset_board() 
        secret_code = random.choice(db_ac)                                  #il programma sceglie il codice segreto tra tutti i codici possibili
        
        #secret_code = code_adapter("6543")                               #utilizzo di CS fisso per debugging
        
        for i in range(1,5): board[11][i] = int(secret_code[0][i-1])        # mette il codice segreto nella posizione 11 della board
        if persistent.best_code_active:
            thread = CustomThread(target=nothing())                         # per fare in modo che il test: if not thread.is_alive():  in menu non dia errore con row = 1
            thread.start()                                                  # esegue la funzione nothing()
            thread.join()                                                   # attende che la funzione sia termninata
        start_time = time.time()                                            # usato per lo score 
        board_close_update()
        persistent.show_score_update = "game1-game2"   # "game1-game2" "game3" "not_show"
        persistent.status = "on_game"
        for row in range (1, 11):  #le giocate massime sono 10 
            code = [0,0,0,0] #giocata corrente vuota
            # if row == 1:            # per troubleshooting
            #     code = [1,2,3,4]
            copilot = [True] * (colors+1)       # True per ogni colore della color bar che verrà visualizzato da input_game1 
            inserting_code = True
            clicked = 99
            while inserting_code:       #fase di input + test dei clic/drag&drop
                draggable = False
                droppable = False
                if persistent.status == "best_code" and best_code_ready == True:
                    if row > 1:
                        db_lc, db_bc = thread.join() 
                    code = random.choice(db_bc)
                    #code = db_bc[0]
                    code = code[0] 
                    code = [int(code[0]), int(code[1]), int(code[2]), int(code[3])]
                    renpy.play("audio/peg.mp3")
                    persistent.status = "on_game"
                    best_code_ready = False
                if (clicked == 11):         #click sulla   "i" per info
                    tot_lc = len(db_lc)
                    code_status = "incompleto"
                    chance = 0
                    left_code = 0
                    left_code_bs = 0
                    bs_inconsistent = False
                    if (clicked == 11) and (code[0] != 0) and (code[1] != 0) and (code[2] != 0) and (code[3] != 0): #E' stata cliccata la "i" per info sulla giocata
                        i_code = str(code[0])+str(code[1])+str(code[2])+str(code[3])
                        chance =0
                        for lc in db_lc:
                            if i_code == lc[0]:
                                chance = 1
                                break
                        tot_lc = len(db_lc)
                        i_code = code_adapter(i_code)
                        key_hits = [0]*25                                           #Ogni campo corrisponde ha un tipo di cod.chiave(1 bianco, 2 bianchi, 1 nero, ...)
                        for code_lc in db_lc:                                       #per ogni codice di db_loop ripete per tutti i possibili codici segreti 
                            whites, blacks = find_keycode(i_code, code_lc)  #trova il codice chiave tra i codici di db_loop e quelli di db_lc
                            key_hits [whites*5 + blacks] +=1                        #incrementa le ricorrenze di codici chiave uguali. *5 simula una tabella a 2 dim
                        left_code = max(key_hits)
                        code_status = "best_code_not_ready"
                        left_code_bs = 0
                        if persistent.best_code_active:
                            if not thread.is_alive() and row > 1:       #i best code sono stati generati
                                db_lc, db_bc = thread.join()
                                if db_lc[0][0] != db_bc[0][0]:
                                    bs_inconsistent = True
                                else:
                                    bs_inconsistent = False 
                                bs_code = db_bc[0]
                                key_hits = [0]*25                                           #Ogni campo corrisponde ha un tipo di cod.chiave(1 bianco, 2 bianchi, 1 nero, ...)
                                for code_lc in db_lc:                                       #per ogni codice di db_loop ripete per tutti i possibili codici segreti 
                                    whites, blacks = find_keycode(bs_code, code_lc)  #trova il codice chiave tra i codici di db_loop e quelli di db_lc
                                    key_hits [whites*5 + blacks] +=1                        #incrementa le ricorrenze di codici chiave uguali. *5 simula una tabella a 2 dim
                                left_code_bs = max(key_hits)
                                if left_code == left_code_bs:
                                    code_status = "is_best_code"
                                elif row == 1:
                                    code_status = "best_code_not_ready"
                                else:
                                    code_status = "is_not_best_code"
                    clicked = 99
                    renpy.call_screen ("attempt_info", chance, tot_lc, left_code, left_code_bs, code_status, bs_inconsistent)
                #board_close_update()  
                renpy.call_screen ("input_game1", row, colors, code)     # setta draggable e droppable in base ai drag&drop del giocatore
                code = dragged_code(row, code, draggable, droppable)     # aggiorna il codice in base al risultato di draggable e droppable 
                for i in range(1,5): board[row][i] = code[i-1]           # aggiorna la board con la giocata che si sta inserendo          
                if copilot_on:
                    copilot = copilot_engine(code, db_lc, colors)
                if (clicked == 10) and (code[0] != 0) and (code[1] != 0) and (code[2] != 0) and (code[3] != 0): #ok spunta verde e controllo che ci siano tutti i 4 colori
                    inserting_code = False
                    code_played = code_adapter (str(code[0])+str(code[1])+str(code[2])+str(code[3]))
                    whites, blacks = find_keycode(secret_code, code_played)               
                    keycode = converti_keycode (whites, blacks)
                    for i in range(0,4): key_board[row][i] = keycode[i]
                    renpy.show_screen ("code_key_update")
                    if whites + blacks > 0 and blacks != 4: renpy.play("audio/peg.mp3")
                if persistent.status == "give_up":     # E' stato cliccato lo shield per arrendersi
                    renpy.call_screen ("are_you_sure", "Do you want to give up?")
                    if yes_no == "yes":
                        board_open_update()
                        #renpy.show_screen("tap_main_menu", "GAME OVER", "Tap the menu button")
                        renpy.show_screen("message", "GAME OVER", "Tap the menu button", arrow="arrow_up", arrow_x=930, arrow_y=200)
                        blacks = 0          # serve per evitare errori nel richiamo di score_update
                        row = 10            # se ci si arrende vengono considerati 10 tentativi
                        score_update(row)
                        persistent.choice = "none"
                        return
                    else:
                        persistent.choice = "game1"
                        persistent.status = "on_game"
                if persistent.choice == "cancel":         #è stato cliccato "cancel" dal menu
                    renpy.call_screen ("are_you_sure", "Stop this game?")
                    if yes_no == "yes":
                        #renpy.show_screen("tap_main_menu", "GAME OVER", "Tap the menu button")
                        renpy.show_screen("message", "GAME OVER", "Tap the menu button", arrow="arrow_up", arrow_x=930, arrow_y=200)
                        persistent.choice = "none"
                        return
                    else:
                        persistent.choice = "game1"
                if persistent.choice == "help_tips":         #è stato cliccato "help and tips" dal menu
                    help_tips()
                    persistent.choice = "game1"
            if blacks == 4:
                board_open_update()
                #renpy.show_screen("tap_main_menu", "YOU WON", "Tap the menu button")
                renpy.show_screen("message", "YOU WON", "Tap the menu button", arrow="arrow_up", arrow_x=930, arrow_y=200)
                score_update(row)
                persistent.choice = "none"
                break 
            db_ac, db_lc = left_codes(db_ac, code_played, (whites, blacks))  #genera il db dei left codes e mette il flag True in db_ac per i lc
            if persistent.best_code_active:
                thread = CustomThread(target=best_codes, args=(db_ac, db_lc))     #generazione del database dei best codes
                thread.start()      
        if blacks != 4: #è stato superato il numero massimo di giocate senza indovinare il codice segreto
            board_open_update()
            score_update(row)
            persistent.choice = "none"
            #renpy.show_screen("tap_main_menu", "GAME OVER", "Tap the menu button")
            renpy.show_screen("message", "GAME OVER", "Tap the menu button", arrow="arrow_up", arrow_x=930, arrow_y=200)
        return

    def game1_web(colors):    # ONE PLAYER
        # """ il giocatore deve indovinare il codice segreto scelto dal programma """   
        global clicked          
        global secret_code
        global draggable
        global droppable
        global key_board
        global board
        global thread
        global best_code_ready
        global copilot_on
        global copilot
        global yes_no
        global start_time
        global code_played
        global db_lc
        global db_bc
        global code
        global yes_no
        #mm = Mastermind_Engine()
        renpy.call_screen ("message_2_options", "Break the hidden secret code. \n\nCLASSIC: secret code can use repeating colors.\n\nBASIC: secret code uses\nonly single colors.", "CLASSIC", "BASIC")
        if option == "CLASSIC":
            db_ac, db_lc, db_bc = init_db(colors)                            #crea il database di tutti i codici, dei left e best codes

        if option == "BASIC":
            db_ac, db_lc, db_bc = init_db_basic(colors)                            #crea il database di tutti i codici, dei left e best codes

        if option == "exit":
            persistent.choice = "none"
            #renpy.show_screen("tap_main_menu", "GAME CANCELED", "Tap the menu button")
            renpy.show_screen("message", "GAME CANCELED", "Tap the menu button", arrow="arrow_up", arrow_x=930, arrow_y=200)
            return

        yes_no = ''
        best_code_ready = False
        copilot_on = False                                         
        key_board = []
        board = []
        reset_board() 
        secret_code = random.choice(db_ac)                                  #il programma sceglie il codice segreto tra tutti i codici possibili
        
        #secret_code = code_adapter("6543")                               #utilizzo di CS fisso per debugging
        
        for i in range(1,5): board[11][i] = int(secret_code[0][i-1])        # mette il codice segreto nella posizione 11 della board
        # if persistent.best_code_active:
        #     thread = CustomThread(target=nothing())                          # per fare in modo che il test: if not thread.is_alive():  in menu non dia errore con row = 1
        #     thread.start()
        #     thread.join()         
        start_time = time.time()                                            # usato per lo score 
        board_close_update()
        persistent.show_score_update = "game1-game2"   # "game1-game2" "game3" "not_show"
        persistent.status = "on_game"
        for row in range (1, 11):  #le giocate massime sono 10 
            code = [0,0,0,0] #giocata corrente vuota
            # if row == 1:            # per troubleshooting
            #     code = [1,2,3,4]
            copilot = [True] * (colors+1)       # True per ogni colore della color bar che verrà visualizzato da input_game1 
            inserting_code = True
            clicked = 99
            while inserting_code:       #fase di input + test dei clic/drag&drop
                draggable = False
                droppable = False
                if persistent.status == "best_code" and best_code_ready == True:
                    # if row > 1:
                    #     db_lc, db_bc = thread.join() 
                    code = random.choice(db_bc)
                    #code = db_bc[0]
                    code = code[0] 
                    code = [int(code[0]), int(code[1]), int(code[2]), int(code[3])]
                    renpy.play("audio/peg.mp3")
                    persistent.status = "on_game"
                    best_code_ready = False
                if (clicked == 11):         #click sulla   "i" per info
                    tot_lc = len(db_lc)
                    code_status = "incompleto"
                    chance = 0
                    left_code = 0
                    left_code_bs = 0
                    bs_inconsistent = False
                    if (clicked == 11) and (code[0] != 0) and (code[1] != 0) and (code[2] != 0) and (code[3] != 0): #E' stata cliccata la "i" per info sulla giocata
                        i_code = str(code[0])+str(code[1])+str(code[2])+str(code[3])
                        chance =0
                        for lc in db_lc:
                            if i_code == lc[0]:
                                chance = 1
                                break
                        tot_lc = len(db_lc)
                        i_code = code_adapter(i_code)
                        key_hits = [0]*25                                           #Ogni campo corrisponde ha un tipo di cod.chiave(1 bianco, 2 bianchi, 1 nero, ...)
                        for code_lc in db_lc:                                       #per ogni codice di db_loop ripete per tutti i possibili codici segreti 
                            whites, blacks = find_keycode(i_code, code_lc)  #trova il codice chiave tra i codici di db_loop e quelli di db_lc
                            key_hits [whites*5 + blacks] +=1                        #incrementa le ricorrenze di codici chiave uguali. *5 simula una tabella a 2 dim
                        left_code = max(key_hits)
                        code_status = "best_code_not_ready"
                        left_code_bs = 0
                        if persistent.best_code_active:
                            # if not thread.is_alive() and row > 1:       #i best code sono stati generati
                            #     db_lc, db_bc = thread.join()
                            if db_lc[0][0] != db_bc[0][0]:
                                bs_inconsistent = True
                            else:
                                bs_inconsistent = False 
                            bs_code = db_bc[0]
                            key_hits = [0]*25                                           #Ogni campo corrisponde ha un tipo di cod.chiave(1 bianco, 2 bianchi, 1 nero, ...)
                            for code_lc in db_lc:                                       #per ogni codice di db_loop ripete per tutti i possibili codici segreti 
                                whites, blacks = find_keycode(bs_code, code_lc)  #trova il codice chiave tra i codici di db_loop e quelli di db_lc
                                key_hits [whites*5 + blacks] +=1                        #incrementa le ricorrenze di codici chiave uguali. *5 simula una tabella a 2 dim
                            left_code_bs = max(key_hits)
                            if left_code == left_code_bs:
                                code_status = "is_best_code"
                            elif row == 1:
                                code_status = "best_code_not_ready"
                            else:
                                code_status = "is_not_best_code"
                    clicked = 99
                    renpy.call_screen ("attempt_info", chance, tot_lc, left_code, left_code_bs, code_status, bs_inconsistent)
                #board_close_update()  
                renpy.call_screen ("input_game1", row, colors, code)     # setta draggable e droppable in base ai drag&drop del giocatore
                code = dragged_code(row, code, draggable, droppable)     # aggiorna il codice in base al risultato di draggable e droppable 
                for i in range(1,5): board[row][i] = code[i-1]           # aggiorna la board con la giocata che si sta inserendo          
                if copilot_on:
                    copilot = copilot_engine(code, db_lc, colors)
                if (clicked == 10) and (code[0] != 0) and (code[1] != 0) and (code[2] != 0) and (code[3] != 0): #ok spunta verde e controllo che ci siano tutti i 4 colori
                    inserting_code = False
                    code_played = code_adapter (str(code[0])+str(code[1])+str(code[2])+str(code[3]))
                    whites, blacks = find_keycode(secret_code, code_played)               
                    keycode = converti_keycode (whites, blacks)
                    for i in range(0,4): key_board[row][i] = keycode[i]
                    renpy.show_screen ("code_key_update")
                    if whites + blacks > 0 and blacks != 4: renpy.play("audio/peg.mp3")
                if persistent.status == "give_up":     # E' stato cliccato lo shield per arrendersi
                    renpy.call_screen ("are_you_sure", "Do you want to give up?")
                    if yes_no == "yes":
                        board_open_update()
                        #renpy.show_screen("tap_main_menu", "GAME OVER", "Tap the menu button")
                        renpy.show_screen("message", "GAME OVER", "Tap the menu button", arrow="arrow_up", arrow_x=930, arrow_y=200)
                        blacks = 0          # serve per evitare errori nel richiamo di score_update
                        row = 10            # se ci si arrende vengono considerati 10 tentativi
                        score_update(row)
                        persistent.choice = "none"
                        return
                    else:
                        persistent.choice = "game1"
                        persistent.status = "on_game"
                if persistent.choice == "cancel":         #è stato cliccato "cancel" dal menu
                    renpy.call_screen ("are_you_sure", "Stop this game?")
                    if yes_no == "yes":
                        #renpy.show_screen("tap_main_menu", "GAME OVER", "Tap the menu button")
                        renpy.show_screen("message", "GAME OVER", "Tap the menu button", arrow="arrow_up", arrow_x=930, arrow_y=200)
                        persistent.choice = "none"
                        return
                    else:
                        persistent.choice = "game1"
                if persistent.choice == "help_tips":         #è stato cliccato "help and tips" dal menu
                    help_tips()
                    persistent.choice = "game1"
            if blacks == 4:
                board_open_update()
                #renpy.show_screen("tap_main_menu", "YOU WON", "Tap the menu button")
                renpy.show_screen("message", "YOU WON", "Tap the menu button", arrow="arrow_up", arrow_x=930, arrow_y=200)
                score_update(row)
                persistent.choice = "none"
                break 
            db_ac, db_lc = left_codes(db_ac, code_played, (whites, blacks))  #genera il db dei left codes e mette il flag True in db_ac per i lc
            if persistent.best_code_active:
                db_lc, db_bc = best_codes (db_ac, db_lc)
                # thread = CustomThread(target=best_codes, args=(db_ac, db_lc))     #generazione del database dei best codes
                # thread.start()      
        if blacks != 4: #è stato superato il numero massimo di giocate senza indovinare il codice segreto
            board_open_update()
            score_update(row)
            persistent.choice = "none"
            #renpy.show_screen("tap_main_menu", "GAME OVER", "Tap the menu button")
            renpy.show_screen("message", "GAME OVER", "Tap the menu button", arrow="arrow_up", arrow_x=930, arrow_y=200)
        return

    def game3(colors):    # TWO PLAYERS
        """ partita tra due giocatori sullo stesso device. Primo giocatore ha lo score con pioli bianchi il secondo quelli neri"""
        global clicked          
        global secret_code
        global draggable
        global droppable
        global key_board
        global board
        global yes_no
        global option
        global secret_code
        global thread
        global best_code_ready
        global copilot_on
        global start_time
        global code_breaker
        global code_maker
        global inserting_code
        global inserting_key_code
        global code_played
        global row
        #mm = Mastermind_Engine() 
        copilot_on = False
        persistent.status = "on_game"
        key_board = []
        board = []
        reset_board()
        yes_no = ''                                  
        option = ''
        secret_code = [0,0,0,0]
        clicked = 99
        board_close_update()
        persistent.show_score_update = "game3"   # "game1-game2" "game3" "not_show" 
        renpy.call_screen ("message_2_options", "Challenge between two players. \n\n Select the player who will try to breaks the secret code.", "PLAYER 1", "PLAYER 2")
        if option == "PLAYER 1":
            code_breaker = "PLAYER 1"
            code_maker = "PLAYER 2"
        if option == "PLAYER 2":
            code_breaker = "PLAYER 2"
            code_maker = "PLAYER 1"
        if option == "exit":
            persistent.choice = "none"
            #renpy.show_screen("tap_main_menu", "GAME CANCELED", "Tap the menu button")
            renpy.show_screen("message", "GAME CANCELED", "Tap the menu button", arrow="arrow_up", arrow_x=930, arrow_y=200)
            return
        #renpy.show_screen("open_shield")
        board_open_update()
        renpy.show_screen("message", code_maker, "Choose your secret code", arrow="arrow_left", arrow_x=780, arrow_y=250)    
        while not clicked == 10:       
            draggable = False
            droppable = False
            #board_open_update()
            renpy.call_screen ("input_secret_code", colors, secret_code) # setta draggable e droppable in base ai drag&drop del giocatore
            secret_code = dragged_secret_code(secret_code, draggable, droppable) #aggiorna il codice segreto in base al risultato di draggable e droppable
            for i in range(1,5): board[11][i] = secret_code[i-1]       #aggiorna il secret code su board[]      
            if secret_code.count(0) == 0:   # tutte le posizioni sono riempite dai pegs
                renpy.show_screen("message", code_maker, "Confirm your secret code", arrow="arrow_up", arrow_x=10, arrow_y=400)
            else:
                renpy.show_screen("message", code_maker, "Choose your secret code", arrow="arrow_left", arrow_x=780, arrow_y=250)
            if persistent.choice == "cancel":         #è stato cliccato "cancel" dal menu
                    renpy.call_screen ("are_you_sure", "Stop this game?")
                    if yes_no == "yes":
                        #renpy.show_screen("tap_main_menu", "GAME OVER", "Tap the menu button")
                        renpy.show_screen("message", "GAME OVER", "Tap the menu button", arrow="arrow_up", arrow_x=930, arrow_y=200)
                        persistent.choice = "none"
                        return
                    else:
                        persistent.choice = "game3"
            if persistent.choice == "help_tips":         #è stato cliccato "help and tips" dal menu
                    help_tips()
                    persistent.choice = "game3"              
        renpy.hide_screen("message")   # rimuove lo screen per l'inserimento del codice segreto
        secret_code = code_adapter (str(secret_code[0])+str(secret_code[1])+str(secret_code[2])+str(secret_code[3]))
        for row in range (1, 11):  #le giocate massime sono 10
            if row < 7: renpy.show_screen("message", "{color=#ff0000}" + code_breaker + "{/color}", "Play your code.")
            board_close_update()  
            inserting_code = True
            code = [0,0,0,0] #giocata corrente vuota
            clicked = 99
            while inserting_code:       # loop per ogni inserimento del codice da parte del code breaker 
                draggable = False
                droppable = False
                #board_close_update()  
                renpy.call_screen ("input_game1", row, colors, code)    # setta draggable e droppable in base ai drag&drop del giocatore
                code = dragged_code(row, code, draggable, droppable)    # aggiorna il codice in base al risultato di draggable e droppable               
                for i in range(1,5): board[row][i] = code[i-1]          # aggiorna la board con la giocata che si sta inserendo               
                if (clicked == 10) and (code[0] != 0) and (code[1] != 0) and (code[2] != 0) and (code[3] != 0): #ok spunta verde e controllo che ci siano tutti i 4 colori
                    inserting_code = False
                    code_played = code_adapter (str(code[0])+str(code[1])+str(code[2])+str(code[3]))
                    whites, blacks = find_keycode(secret_code, code_played)
                if persistent.status == "give_up":     #valore impostato dalla funzione di Input. E' stato cliccato lo shield per arrendersi
                    renpy.hide_screen("message")
                    renpy.call_screen ("are_you_sure", "Do you want to give up?")
                    if yes_no == "yes":
                        board_open_update() 
                        #renpy.show_screen("tap_main_menu", "YOU GAVE UP", "Tap the menu button")
                        renpy.show_screen("message", "YOU GAVE UP", "Tap the menu button", arrow="arrow_up", arrow_x=930, arrow_y=200)
                        blacks = 0          # serve per evitare errori nel richiamo di score_update
                        row = 10    # se ci si arrende, vengono contati 10 tentativi
                        score_update(row)
                        persistent.choice = "none"
                        return
                    else:
                        persistent.choice = "game3"
                        persistent.status = "on_game"
                if persistent.choice == "cancel":         #è stato cliccato "cancel" dal main menu
                    renpy.call_screen ("are_you_sure", "Stop this game?")
                    if yes_no == "yes":
                        #renpy.show_screen("tap_main_menu", "GAME OVER", "Tap the menu button")
                        renpy.show_screen("message", "GAME OVER", "Tap the menu button", arrow="arrow_up", arrow_x=930, arrow_y=200)   
                        persistent.choice = "none"
                        return
                    else:
                        persistent.choice = "game3"
                if persistent.choice == "help_tips":         #è stato cliccato "help and tips" dal menu
                    help_tips()
                    persistent.choice = "game3"      
            renpy.hide_screen("message")   # rimuove lo screen che chiede di inserire il codice 
            inserting_key_code = True   # loop per ogni inserimento del codice chiave da parte del code maker
            key_code = [0,0,0,0]
            if blacks == 4:
                inserting_key_code = False
                key_code = [2,2,2,2]
                for i in range(0,4): key_board[row][i] = key_code[i]
            clicked = 99
            
            if row < 7: renpy.show_screen("message", code_maker, "Open the shield", arrow="arrow_left", arrow_x=830, arrow_y=300)
        
            renpy.show_screen ("code_key_update")
            while inserting_key_code:       # parte del code maker - Inserimento key code
                draggable = False
                droppable = False
                #renpy.show_screen ("code_key_update")
                renpy.call_screen ("input_game2", row, key_code)    # setta draggable e droppable in base ai drag&drop del giocatore
                key_code = dragged_key_code(row, key_code, draggable, droppable)    # aggiorna il codice chiave in base al risultato di draggable e droppable
                for i in range(0,4): key_board[row][i] = key_code[i]    #aggiorna la board con il codice chiave  
                if (clicked == 10) :    # ok spunta verde 
                    inserting_key_code = False
                    whites = 0
                    blacks = 0
                    for i in range (0,4):
                        if key_code[i] == 1:
                            whites += 1
                        if key_code[i] == 2:
                            blacks += 1
                    whites_processed, blacks_processed = find_keycode(secret_code, code_played)
                    if whites != whites_processed or blacks != blacks_processed:
                        renpy.hide_screen("message")
                        renpy.call_screen("message_x", code_maker, "The key code entered\nis incorrect.\n\nPlease try again")
                        inserting_key_code = True
                        clicked = 99   
                if persistent.choice == "cancel":         #è stato cliccato "cancel" dal main menu
                    renpy.call_screen ("are_you_sure", "Stop this game?")
                    if yes_no == "yes":
                        #renpy.show_screen("tap_main_menu", "GAME OVER", "Tap the menu button")
                        renpy.show_screen("message", "GAME OVER", "Tap the menu button", arrow="arrow_up", arrow_x=930, arrow_y=200)
                        persistent.choice = "none"
                        return
                    else:
                        persistent.choice = "game3"
                if persistent.choice == "help_tips":         #è stato cliccato "help and tips" dal menu
                    help_tips()
                    persistent.choice = "game3"
                if (clicked == 12) : # clic sullo shield per aprirlo in modo da cofrontare il codice con il codice segreto ed inseririre il codice chiave 
                    board_open_update()

                    renpy.show_screen("message", code_maker, "Drag and drop the black and white pegs.", arrow="arrow_up", arrow_x=940, arrow_y=1650)
                    
                    clicked = 99                           
            renpy.hide_screen("message")   # rimuove lo screen che chiede di inserire il codice chiave
            if blacks == 4:
                score_update(row)
                board_open_update()
                #renpy.show_screen("tap_main_menu", "YOU WON", "Tap the menu button")
                renpy.show_screen("message", "YOU WON", "Tap the menu button", arrow="arrow_up", arrow_x=930, arrow_y=200)
                persistent.choice = "none"
                break 
        if blacks != 4: #è stato superato il numero massimo di giocate senza indovinare il codice segreto
            score_update(row)
            board_open_update()
            #renpy.show_screen("tap_main_menu", "GAME OVER", "Tap the menu button")
            renpy.show_screen("message", "GAME OVER", "Tap the menu button", arrow="arrow_up", arrow_x=930, arrow_y=200)
            persistent.choice = "none"
        return

    def game2(colors):    # CPU PLAYER
        """ partita dove il programma deve indovinare il codice segreto scelto dal giocatore usando le partite già giocate """
        global clicked          
        global secret_code
        global draggable
        global droppable
        global key_board
        global board
        global yes_no
        global option
        global code_played_fake
        global code_played
        global next_key
        global secret_code_adapted
        global code_played_adapted
        global code_played_fake_adapted
        global matrix
        #mm = Mastermind_Engine()
        persistent.status = "on_game"
        key_board = []
        board = []
        reset_board()                                  
        next_key = ''
        option = ''
        yes_no = ''
        secret_code = [0,0,0,0]
        clicked = 99
        board_close_update()
        persistent.show_score_update = "game1-game2"   # "game1-game2" "game3" "not_show"   
        renpy.call_screen ("message_2_options", "The device's CPU will try to break your secret code.\n\n Do you want to enter the secret code or keep it in mind?", "ENTER", "KEEP IN MIND")
        if option == "ENTER":     # scelta di inserire il codice segreto - 
            board_open_update()
            while not clicked == 10:       
                draggable = False
                droppable = False
                renpy.show_screen("message", "Choose your secret code", "Drag and drop the pegs",  arrow="arrow_left", arrow_x=780, arrow_y=250)  
                renpy.call_screen ("input_secret_code", colors, secret_code)
                secret_code = dragged_secret_code(secret_code, draggable, droppable)
                #narrator("")
                for i in range(1,5): board[11][i] = secret_code[i-1]       #aggiorna la board in posizione 11 con il secret code                   
                if persistent.choice == "cancel":         #è stato cliccato "cancel" dal main menu
                        renpy.call_screen ("are_you_sure", "Stop this game? ")
                        if yes_no == "yes":
                            #renpy.show_screen("tap_main_menu", "GAME OVER", "Tap the menu button")
                            renpy.show_screen("message", "GAME OVER", "Tap the menu button", arrow="arrow_up", arrow_x=930, arrow_y=200)
                            persistent.choice = "none"
                            return
                        else:
                            persistent.choice = "game2"
                if persistent.choice == "help_tips":         #è stato cliccato "help and tips" dal menu
                    help_tips()
                    persistent.choice = "game2"
        if option == "exit":
            #renpy.show_screen("tap_main_menu", "GAME CANCELED", "Tap the menu button")
            renpy.show_screen("message", "GAME CANCELED", "Tap the menu button", arrow="arrow_up", arrow_x=930, arrow_y=200)
            persistent.choice = "none"
            return
        secret_code_adapted = code_adapter(str(secret_code[0]) + str(secret_code[1]) + str(secret_code[2]) + str(secret_code[3]))
        fake_pegs_dict = {6:['1', '2', '3', '4', '5', '6'], 8:['1', '2', '3', '4', '5', '6', '7', '8']}  #serve per simulare un codice random sia per la versione a 6 e a 8 colori                 
        fake_pegs = fake_pegs_dict[colors]                          #considera la fake pegs in base al numero di colori con cui si sta giocando
        random.shuffle(fake_pegs)                                   #mischia i pegs nella lista
        first_codes_list = ['2131', '1231', '2311', '2113', '1123', '1212', '1221', '1122', '1234']     
        is_first_play = True 
        first_code = random.choice(first_codes_list)                #per il primo tentativo il codice viene scelto nella lista first_codes_list
        #first_code = '1234'
        matrix = make_matrix_from_file_renpy (colors, first_code, "Game_")      #crea la matrice delle partite giocate dal file in base al numero di colori usati e al primo codice giocato   
        for row in range(1,11):                                    #loop per tutte le partite possibili
            key_code = [0,0,0,0] 
            if is_first_play:
                code_played = first_code
                next_code = first_code                              # necessario se l'app indovina al primo tentativo
                is_first_play = False                               #dalla seconda giocata il codice sarà: next_code
            else:
                code_played = next_code
            code_played_fake = ''                                   #è il codice che viene visualizzao invece di quello vero. Fa sembrare che il programma gioca sempre codici diversi          
            for i in code_played:                                   #generazione del codice fake basato sul codice vero
                code_played_fake += fake_pegs[int(i) - 1]
            code_played_fake = code_played                                      # per troubleshooting reinserire la funzione fake
            for i in range(1,5): board[row][i] = int(code_played_fake[i-1])       #aggiorna la board con la giocata che si sta inserendo
            renpy.play("audio/peg.mp3")
            inserting_key_code = True
            while inserting_key_code:
                clicked = 99
                draggable = False
                droppable = False
                renpy.show_screen("board_update")
                for i in range(0,4): key_board[row][i] = key_code[i]
                if next_key == 'XXXX':                 
                    blacks = 4
                    whites = 0
                    for i in range(0,4): key_board[row][i] = 2       # mette 4 key code neri in key_board
                    inserting_key_code = False
                else:
                    renpy.show_screen ("code_key_update")
                    renpy.show_screen("message", "Enter the key code.", "Drag and drop the black and white pegs.", arrow="arrow_up", arrow_x=940, arrow_y=1650)
                    renpy.call_screen ("input_game2", row, key_code)
                    renpy.hide_screen("message")
                    key_code = dragged_key_code(row, key_code, draggable, droppable)
                    if (clicked == 10) : #ok spunta verde 
                        inserting_key_code = False
                        whites = 0
                        blacks = 0
                        for i in range (0,4):
                            if key_code[i] == 1:
                                whites += 1
                            if key_code[i] == 2:
                                blacks += 1
                    code_played_fake_adapted = code_adapter(code_played_fake)
                    if option == "ENTER" and clicked == 10:
                        whites_processed, blacks_processed = find_keycode(secret_code_adapted, code_played_fake_adapted)
                        if whites != whites_processed or blacks != blacks_processed:
                            renpy.call_screen("message_x", "KEY CODE", "The key code entered\nis incorrect.\n\nPlease try again")
                            inserting_key_code = True
                            clicked = 99
                    if persistent.choice == "cancel":         #è stato cliccato "cancel" dal main menu
                        renpy.call_screen ("are_you_sure", "Stop this game?")
                        if yes_no == "yes":
                            #renpy.show_screen("tap_main_menu", "GAME OVER", "Tap the menu button")
                            renpy.show_screen("message", "GAME OVER", "Tap the menu button", arrow="arrow_up", arrow_x=930, arrow_y=200)
                            persistent.choice = "none"
                            return
                        else:
                            persistent.choice = "game2"
                    if persistent.choice == "help_tips":         #è stato cliccato "help and tips" dal menu
                        help_tips()
                        persistent.choice = "game2"
            if blacks == 4:
                if option == "KEEP IN MIND":
                    for i in range(1,5): board[11][i] = int(code_played_fake[i-1])
                board_open_update()
                score_update(row)
                #renpy.show_screen("tap_main_menu", "SECRET CODE BROKEN", "Tap the menu button")
                renpy.show_screen("message", "SECRET CODE BROKEN", "Tap the menu button", arrow="arrow_up", arrow_x=930, arrow_y=200)
                persistent.choice = "none"
                break
            code_plus_key = code_played + ' ' + 'X' * blacks + 'O' * whites + '_' * (4 - (blacks + whites)) 
            #compone il codice giocato + il codice chiave inserito dal giocatore per cercare il prossimo codice da gocare
            matrix, next_code, next_key = find_next_code (row, matrix, code_plus_key )                  
            #trova il prossimo codice da giocare. next_key serve solo se è uguale a XXXX
            if next_code == 'not_found':        # può non esser trovato solo se il cod segreto non è stato inserito
                persistent.choice = "none"
                #renpy.show_screen("tap_main_menu", "GAME OVER", "One or more key codes entered are incorrect.\n\nTap the menu button")
                renpy.show_screen("message", "GAME OVER", "Tap the menu button", arrow="arrow_up", arrow_x=930, arrow_y=200)
                return            

    def training(colors): # TRAINING  
        """ partita dove il programma deve indovinare il codice segreto scelto dal giocatore usando le partite già giocate """
        global clicked, secret_code, draggable, droppable, key_board, board, yes_no, option, code_played_fake
        global code_played, next_key, secret_code_adapted, code_played_adapted, code_played_fake_adapted
        global matrix, matrix, matrix_record, x, blacks, copilot_on, matrix_len, selected, training_type, training_broken
        selected = 0 
        copilot_on = False
        #mm = Mastermind_Engine()
        persistent.status = "on_game"
        persistent.show_score_update = "not_show"   # può essere: "game1-game2" o "game3" o "not_show"
        key_board = []
        board = []
        reset_board()                                  
        next_key = ''
        option = ''
        yes_no = ''
        clicked = 99
        renpy.show_screen("code_key_update")
        first_code = ''
        # matrix = make_matrix_from_file_renpy (colors, first_code, "Training_")      #crea la matrice delle partite giocate dal file in base al numero di colori usati e al primo codice giocato 
        # matrix_len = (len(matrix))
        option = ''
        renpy.call_screen ("message_2_options", "The challenge is to break the secret code with just one try.\n\nSee 'HELP' for more info.", "CLASSIC", "BASIC")          
        if option == "CLASSIC":
            matrix = make_matrix_from_file_renpy (colors, first_code, "Training_")      #crea la matrice delle partite giocate dal file in base al numero di colori usati e al primo codice giocato 
            matrix_len = (len(matrix))
            training_type = "CLASSIC"
            for x in range(matrix_len):
                if colors == 6 and persistent.training_solved_6[x] == 0:    # se la partita è già stata giocata, passa alla prossima
                    break
                if colors == 8 and persistent.training_solved_8[x] == 0:
                    break
        if option == "BASIC":
            matrix = make_matrix_from_file_renpy (colors, first_code, "Training_basic_")      #crea la matrice delle partite giocate dal file in base al numero di colori usati e al primo codice giocato 
            matrix_len = (len(matrix))
            training_type = "BASIC"
            for x in range(matrix_len):
                if colors == 6 and persistent.training_solved_basic_6[x] == 0:    # se la partita è già stata giocata, passa alla prossima
                    break
                if colors == 8 and persistent.training_solved_basic_8[x] == 0:
                    break
            # renpy.call_screen ("training_selection")
            # x = selected  
        if option == "exit":
            #renpy.show_screen("tap_main_menu", "GAME CANCELED", "Tap the menu button")
            renpy.show_screen("message", "TRAINING OVER", "Tap the menu button", arrow="arrow_up", arrow_x=930, arrow_y=200)
            persistent.choice = "none"
            return 
        training = True
        while training:     
            matrix_record = matrix[x]   # martrix_record corrisponde a una partita
            #db_ac, db_lc, db_bc = init_db(colors)
            row = 0
            key_board = []
            board = []
            reset_board()
            code = [0,0,0,0]
            board_close_update()
            for row in range (len(matrix_record)):  # popola la board con i tentativi giocati
                whites = 0
                blacks = 0   
                if matrix_record[row][5:] == "XXXX":
                    secret_code = matrix_record[row][:4]
                    for i in range (1, 5): 
                        board [11][i] = int(matrix_record[row][i-1])
                        #code [i-1] = int(matrix_record[row][i-1])       # per trouleshooting
                    break
                else:
                    for i in range (1, 5): board [row+1][i] = int(matrix_record[row][i-1])  
                    k = 3 
                    for i in range (5, 9):
                        if matrix_record[row][i] == "O":
                            key_board[row+1][k] = 1
                            whites += 1
                            k -= 1
                        if matrix_record[row][i] == "X":
                            key_board[row+1][k] = 2
                            blacks += 1
                            k -= 1
                code_played = code_adapter(matrix_record[row][:4])
                #db_ac, db_lc = left_codes(db_ac, code_played, (whites, blacks))
            row += 1    # row punta alla prossima riga da giocare.
            inserting_code = True
            clicked = 99
            renpy.show_screen("training_dispaly", x, training_type)
            while inserting_code:       #fase di input + test dei clic/drag&drop
                draggable = False
                droppable = False
                renpy.call_screen ("input_game1", row, colors, code)     # setta draggable e droppable in base ai drag&drop del giocatore
                code = dragged_code(row, code, draggable, droppable)     # aggiorna il codice in base al risultato di draggable e droppable 
                for i in range(1,5): board[row][i] = code[i-1]           # aggiorna la board con la giocata che si sta inserendo          
                if (clicked == 10) and (code[0] != 0) and (code[1] != 0) and (code[2] != 0) and (code[3] != 0): #ok spunta verde e controllo che ci siano tutti i 4 colori
                    inserting_code = False
                    code_played = code_adapter (str(code[0])+str(code[1])+str(code[2])+str(code[3])) 
                    whites, blacks = find_keycode(code_adapter(secret_code), code_played)               
                    keycode = converti_keycode (whites, blacks)
                    for i in range(0,4): key_board[row][i] = keycode[i]
                    renpy.show_screen ("code_key_update")
                if persistent.status == "give_up" or (blacks != 4 and clicked == 10):     # E' stato cliccato lo shield per arrendersi o il codice non ha indovinato
                        board_open_update()
                        renpy.vibrate(1.0)
                        renpy.call_screen ("message_2_options", "Secret Code not broken.", "NEXT", "QUIT")
                        if option == "NEXT":
                            if x < matrix_len-1:
                                x += 1
                            persistent.status = "on_game"
                            inserting_code = False
                        if option == "QUIT" or option == "exit":
                            persistent.choice = "none"
                            renpy.hide_screen("training_dispaly")
                            #renpy.show_screen("tap_main_menu", "TRAINING OVER", "Tap the menu button")
                            renpy.show_screen("message", "TRAINING OVER", "Tap the menu button", arrow="arrow_up", arrow_x=930, arrow_y=200)
                            return
                if persistent.choice == "training_select":         
                    selected = x
                    renpy.call_screen ("training_selection", training_type)
                    x = selected
                    persistent.choice = "training"
                    inserting_code = False
                if persistent.choice == "training_next":         
                    if x < matrix_len-1:
                        x += 1
                    persistent.choice = "training"
                    inserting_code = False
                if persistent.choice == "training_precedent":         
                    if x > 0:
                        x -= 1
                    persistent.choice = "training"
                    inserting_code = False
                if persistent.choice == "training_page_precedent":         
                    if x >= 50:
                        x -= 50
                    persistent.choice = "training"
                    inserting_code = False
                if persistent.choice == "training_page_next":         
                    if x < matrix_len-50:
                        x += 50
                    persistent.choice = "training"
                    inserting_code = False
                if persistent.choice == "training_reset":
                    renpy.call_screen ("are_you_sure", "Broken secret code will be reset as not broken.")
                    if yes_no == "yes":
                        if colors == 6 and training_type == "CLASSIC":
                            persistent.training_solved_6 = [0] * 1128
                        if colors == 8 and training_type == "CLASSIC":
                            persistent.training_solved_8 = [0] * 2608
                        if colors == 6 and training_type == "BASIC":
                            persistent.training_solved_basic_6 = [0] * 787
                        if colors == 8 and training_type == "BASIC":
                            persistent.training_solved_basic_8 = [0] * 2450   
                        renpy.call_screen ("message_x", "TRAINING RESET", "All " + training_type + " Training games based on " + str(colors) + " colors, have been reset.")
                        x = 0
                        inserting_code = False  
                    persistent.choice = "training"
                if persistent.choice == "training_numbers":
                    renpy.call_screen ("message_x", "TRAINING STATISTICS", "The number of secret codes broken are:\n\nClassic 6 colors: " + str(persistent.training_solved_6.count(1)) + "\n\nClassic 8 colors: " + str(persistent.training_solved_8.count(1)) + "\n\n Basic 6 colors: " + str(persistent.training_solved_basic_6.count(1)) + "\n\nBasic 8 colors: " + str(persistent.training_solved_basic_8.count(1)))  
                    persistent.choice = "training"
                if persistent.choice == "cancel":         #è stato cliccato "cancel" dal menu
                    renpy.call_screen ("are_you_sure", "Stop this training session?")
                    if yes_no == "yes":
                        renpy.hide_screen("training_dispaly")
                        renpy.show_screen("message", "TRAINING OVER", "Tap the menu button", arrow="arrow_up", arrow_x=930, arrow_y=200)
                        #renpy.show_screen("tap_main_menu", "TRAINING OVER", "Tap the menu button")   
                        persistent.choice = "none"
                        return
                    else:
                        persistent.choice = "training"
                if persistent.choice == "help_tips":         #è stato cliccato "help and tips" dal menu
                    help_tips()
                    persistent.choice = "training"
                if blacks == 4:
                    board_open_update()
                    if colors == 6 and training_type == "CLASSIC":
                        persistent.training_solved_6[x] = 1    # 0 da risolvere e 1 game risolto
                    if colors == 8 and training_type == "CLASSIC":
                        persistent.training_solved_8[x] = 1    # 0 da risolvere e 1 game risolto
                    if colors == 6 and training_type == "BASIC":
                        persistent.training_solved_basic_6[x] = 1
                    if colors == 8 and training_type == "BASIC":
                        persistent.training_solved_basic_8[x] = 1
                    renpy.vibrate(0.50)
                    renpy.pause(0.60)
                    renpy.vibrate(0.50)
                    renpy.call_screen ("message_2_options", "Well done!! You broke the secret code.", "NEXT", "QUIT")
                    if option == "NEXT":
                        if x < matrix_len-1:
                            x += 1
                        inserting_code = False
                    if option == "QUIT" or option == "exit":
                        persistent.choice = "none"
                        renpy.hide_screen("training_dispaly")
                        #renpy.show_screen("tap_main_menu", "TRAINING OVER", "Tap the menu button")
                        renpy.show_screen("message", "TRAINING OVER", "Tap the menu button", arrow="arrow_up", arrow_x=930, arrow_y=200) 
                        return

    def score():          # SCORE
        global score_option
        global board
        global key_board
        score_option = ''
        board = []
        key_board = []
        reset_board() 
        board_close_update()
        while score_option != "exit":
            renpy.call_screen("score_menu")
            if score_option == "check_score_game1_2":
                persistent.show_score_update = "game1-game2"
                renpy.show_screen ("score_update")
                renpy.call_screen ("message_x", "SCORE", "Your score: " + str(persistent.score_player) + "\n(White Pegs)\n\nApp score: " + str(persistent.score_app) + "\n(Black Pegs)")
            if score_option == "check_score_game3":
                persistent.show_score_update = "game3"
                renpy.show_screen ("score_update")
                renpy.call_screen ("message_x", "SCORE", "Player 1: " + str(persistent.score_player1) + "\n(White Pegs)\n\nPlayer 2: " + str(persistent.score_player2) + "\n(Black Pegs)")
            if score_option == "score_stats":
                renpy.call_screen ("score_statistics")
            if score_option == "reset_score_game1_2":
                persistent.score_player = 0
                persistent.score_app = 0
                persistent.perf = []   
                persistent.total_time = 0
                for i in range (30):
                    for j in range (3):
                        persistent.score_all [i][j] = 0
                renpy.call_screen ("message_x", "SCORE", "One Player and App Player score has been reset")
            if score_option == "reset_score_game3":
                persistent.score_player1 = 0
                persistent.score_player2 = 0
                for i in range (30):
                    for j in range (3, 5):
                        persistent.score_all [i][j] = 0
                renpy.call_screen ("message_x", "SCORE", "Two Players score has been reset")
        persistent.choice = "none"
        return

    def settings():       # SETTINGS
        global pref_option
        global sub_exit
        pref_option = ''
        while pref_option != "exit":
            sub_exit = False
            renpy.call_screen("settings_menu")
            if pref_option == "number_of_colors":
                renpy.call_screen ("numbers_of_colors")
                if not sub_exit:        
                    renpy.call_screen ("message_x", "COLORS", "You will play with: " + str(colors) + " colors")
            if pref_option == "music":
                if persistent.sound:
                    on_off = "ON"
                else:
                    on_off = "OFF"
                renpy.call_screen ("message_x", "MUSIC", "The music has been switched " + on_off )
            if pref_option == "best_code":
                renpy.call_screen ("best_code_feature")
                if not sub_exit:   
                    if persistent.best_code_active:
                        enable_disable = "ENABLE"
                    else:
                        enable_disable = "DISABLE"            
                    renpy.call_screen ("message_x", "BEST CODE", "Best Code feature is: " + enable_disable)
        persistent.choice = "none"
        return

    def help_tips():      # HELP
        renpy.call_screen("help_tips_view")
        persistent.choice = "none"
        return

    def board_close_update():   # nasconde il codeice segreto, chiude lo shield, e aggiorna la visualizzazione della board       
        renpy.show_screen ("open_shield")
        renpy.pause(0.2)
        renpy.hide_screen ("secret_code_update")
        renpy.hide_screen ("open_shield")
        renpy.show_screen ("board_update")
        renpy.play("audio/close.mp3")
       
    def board_open_update():
        renpy.show_screen ("board_update")
        renpy.show_screen ("open_shield")
        renpy.play("audio/open.mp3")
        renpy.show_screen ("secret_code_update")

    def score_update (row):            # Aggiorna lo score
        if row == 10:
            renpy.vibrate(1.0)
        else:
            renpy.vibrate(0.50)
            renpy.pause(0.60)
            renpy.vibrate(0.50)
        if persistent.choice == "game1":
            if persistent.score_player + row < 30:
                persistent.score_player = persistent.score_player + row
                persistent.score_all [persistent.score_player][1] = 1       # 1 è il key code bianco
                end_time = time.time()
                integer_seconds = int(end_time - start_time)
                time_conv = time_converter (integer_seconds)
                temp = [row, '']
                temp[1] = time_conv
                persistent.perf.append(temp)
                persistent.total_time += integer_seconds
                persistent.total_time_converted = time_converter (persistent.total_time)
        if persistent.choice == "game2":
            if persistent.score_app + row < 30:
                persistent.score_app = persistent.score_app + row
                persistent.score_all [persistent.score_app][2] = 2       # 2 è il key code nero
        if persistent.choice == "game3":
            if code_breaker == "PLAYER 1":
                if persistent.score_player1 + row < 30:
                    persistent.score_player1 = persistent.score_player1 + row
                    persistent.score_all [persistent.score_player1][3] = 1       # 1 è il key code bianco
            if code_breaker == "PLAYER 2":
                if persistent.score_player2 + row < 30:
                    persistent.score_player2 = persistent.score_player2 + row
                    persistent.score_all [persistent.score_player2][4] = 2       # 2 è il key code nero
        return

    def reset_board():      # azzera tutta la board compresi i keycode. 0 è vuota e  11 è la posizione del secret code
        for row in range (12):
            single_row = [0,0,0,0,0]
            single_row_key = [0,0,0,0]
            board.append(single_row)
            key_board.append(single_row_key)
    
    def converti_keycode (whites, blacks):         #converte i bianchi e i neri in key_code 1 per ogni bianco, 2 per ogni nero
        key_code = [0,0,0,0]
        for i in range (0, whites):
            key_code[i] = 1
        for i in range (0, blacks):
            key_code[i + whites] = 2
        return key_code

    def copilot_engine(code, db_lc, colors):        # mette a True solo i colori possibili per la giocata corrente
        if (code[0] == 0 and code[1] == 0 and code[2] == 0 and code[3] == 0):
            copilot = [True] * (colors+1)
        else: 
            copilot = [False] * (colors+1) 
            for lc in db_lc:
                lc_ok = True
                lc_color = [0] * 4
                for i in range (0,4):
                    if code[i] == 0:
                        lc_color[i] = int(lc[0][i])
                    if code[i] != int(lc[0][i]) and code[i] != 0:
                        lc_ok = False
                if lc_ok:
                    for i in range (0,4):
                        if lc_color[i] > 0:
                            copilot[lc_color[i]] = True
        return copilot

    def dragged_code(row, code, draggable, droppable):
        for peg in range (1, colors+1):     # se è stato droppato un peg della colonna esterna, viene aggiornato code[]
            for hole in range (1,5):        
                if draggable == "peg_" + str(peg) and droppable == "hole_" + str(hole):
                    code[hole-1] = peg
                    renpy.play("audio/peg.mp3")
        for dropped in range (0,4):    # se un peg è stato rimosso dalla giocata, viene tolto da code[]
            if draggable == "dropped_peg_" + str(dropped) and droppable == "empty_bg":
                code[dropped] = 0
                renpy.play("audio/drag_out.ogg")
            for hole in range (1,5):    # un peg può essere spostato da un buco ad un altro
                if draggable == "dropped_peg_" + str(dropped) and droppable == "hole_" + str(hole):
                    if hole-1 != dropped:       # se il peg non è rilasciato nel suo buco iniziale
                        code[hole-1] = code[dropped]
                        code[dropped] = 0
                    renpy.play("audio/peg.mp3")
        for i in range (1,row+1):       # drag dei peg dalle righe precedenta a quella attuale 
            for j in range (1, 5):      
                for hole in range (1,5):
                    if draggable == "dropped_peg_prec" + str(i-1) + str(j-1) and droppable == "hole_" + str(hole):
                        code[hole-1] = board[i-1][j]
                        #narrator("")
                        renpy.play("audio/peg.mp3")
                            
        return code
    
    def dragged_key_code(row, key_code, draggable, droppable):
        for key_peg in range (1, 3):     # se è stato droppato un peg della colonna esterna, viene aggiornato code[]
            for hole in range (1,5):        
                if draggable == "key_peg_" + str(key_peg) and droppable == "hole_" + str(hole):
                    key_code[hole-1] = key_peg      #nelle 4 posizioni del key_code ci va 1 per il bianco e 2 per il nero
                    renpy.play("audio/peg.mp3")
        for dropped in range (0,4):    # se un key peg è stato rimosso dalla giocata, viene tolto da key_code[]
            if draggable == "dropped_key_peg_" + str(dropped) and droppable == "empty_bg":
                key_code[dropped] = 0
                renpy.play("audio/drag_out.ogg")
        return key_code

    def dragged_secret_code(secret_code, draggable, droppable):
        for peg in range (1, colors+1):     # se è stato droppato un peg della colonna esterna, viene aggiornato code[]
            for hole in range (1,5):        
                if draggable == "peg_" + str(peg) and droppable == "hole_" + str(hole):
                    secret_code[hole-1] = peg
                    renpy.play("audio/peg.mp3")
        for dropped in range (0,4):    # se un peg è stato rimosso dalla giocata, viene tolto da secret_code[]
            if draggable == "dropped_peg_" + str(dropped) and droppable == "empty_bg":
                secret_code[dropped] = 0
                renpy.play("audio/drag_out.ogg")
            for hole in range (1,5):    # un peg può essere spostato da un buco ad un altro
                if draggable == "dropped_peg_" + str(dropped) and droppable == "hole_" + str(hole):
                    if hole-1 != dropped:       # se il peg non è rilasciato nel suo buco iniziale
                        secret_code[hole-1] = secret_code[dropped]
                        secret_code[dropped] = 0
                    renpy.play("audio/peg.mp3")
        return secret_code

    def drag_placed(drags, drop):   #valorizza le variabili draggable e droppable in caso d drop
        if not drop:
            return
        store.draggable = drags[0].drag_name
        store.droppable = drop.drag_name
        return True

    def time_converter (integer_seconds):
                integer_minutes = integer_seconds // 60
                remaining_seconds = integer_seconds % 60
                integer_hours = integer_minutes // 60
                remaining_minutes = integer_minutes % 60
                formatted_time = f"{integer_hours:02d}:{remaining_minutes:02d}:{remaining_seconds:02d}"
                return formatted_time   

screen board_update():      # aggiorna la visualizzaione dei codici sulla board senza il codice segreto 
    fixed:
        xsize 1080
        ysize 1920
        for i in range (1,11):             
            for j in range (1,5):
                add pegs[board[i][j]]:
                    xpos peg_pos[i][j][1]
                    ypos peg_pos[i][j][2]
                    anchor (0.5, 0.5)

screen code_key_update():     # aggiorna la visualizzaione dei codici chiave sulla board.
    fixed:
        xsize 1080
        ysize 1920
        for i in range (1,11):
            for j in range (1,5):
                add key_pegs[key_board[i][j-1]]: 
                    anchor (0.5, 0.5)
                    xpos key_pos[i][j][1]
                    ypos key_pos[i][j][2]  

screen secret_code_update():      # aggiorna la visualizzaione del codice segreto sulla board  
    fixed:
        xsize 1080
        ysize 1920         
        for j in range (1,5):
            add pegs[board[11][j]]:
                xpos peg_pos[11][j][1]
                ypos peg_pos[11][j][2]
                anchor (0.5, 0.5)

screen score_update():      # aggiorna lo score sulla board
    fixed:
        xsize 1080
        ysize 1920
        for i in range (1,30):
            if  persistent.show_score_update == "game1-game2":   # "game1-game2" "game3" "not_show"           
                for j in range (1,3):
                    add key_pegs[persistent.score_all[i][j]]:
                        xpos score_pos[i][j][1]
                        ypos score_pos[i][j][2]
            if  persistent.show_score_update == "game3":   # "game1-game2" "game3" "not_show"              
                for j in range (3,5):
                    add key_pegs[persistent.score_all[i][j]]:
                        xpos score_pos[i][j-2][1]
                        ypos score_pos[i][j-2][2]

screen input_game1(row, colors, code):     # input delle giocate + checkmark verde + bottone shield per rinuncia, info, best code e copilot
    fixed:
        xsize 1080
        ysize 1920
        draggroup:
            for i in range (1, colors+1):   #colonna di peg da giocare
                $ name = "peg_"+ str(i)
                if copilot_on:
                    if copilot[i]:
                        drag:
                            drag_name name
                            add pegs_big[i]
                            xpos 920
                            ypos (1870-i*180)
                            draggable True
                            droppable False
                            dragged drag_placed
                            drag_raise True
                            mouse_drop True
                if not copilot_on:
                    drag:
                        drag_name name
                        add pegs_big[i]
                        xpos 920
                        ypos (1870-i*180)
                        draggable True
                        droppable False
                        dragged drag_placed
                        drag_raise True
                        mouse_drop True

            for j in range (1, 5):      # riga di drop vuoti per posizionare i pegs
                $ name = "hole_"+ str(j)
                drag:
                    drag_name name
                    xpos peg_pos[row][j][1]
                    ypos peg_pos[row][j][2]
                    anchor (0.5, 0.5)
                    #child pegs[0]   #empty peg big come oggetto droppable
                    child "00_empty_circle"   #white circle trasp 50% come oggetto droppable
                    draggable False
                    droppable True
                    mouse_drop True  
            for j in range (1, 5):      # per la rimozionea dei pegs already dropped per la riga in progress
                $ name = "dropped_peg_"+ str(j-1)
                if code[j-1] > 0:
                    drag:
                        drag_name name
                        add pegs[code[j-1]]
                        xpos peg_pos[row][j][1]
                        ypos peg_pos[row][j][2]
                        anchor (0.5, 0.5)
                        draggable True
                        droppable False
                        dragged drag_placed
                        drag_raise False
                        mouse_drop True
            if row > 1:                 # per il drag dei peg dalle righe precedenti all'attuale
                for i in range (1,row+1):
                    for j in range (1, 5):      
                        $ name = "dropped_peg_prec"+ str(i-1)+ str(j-1)
                        drag:
                            drag_name name
                            add pegs[board[i-1][j]]
                            xpos peg_pos[i-1][j][1]
                            ypos peg_pos[i-1][j][2]
                            anchor (0.5, 0.5)
                            draggable True
                            droppable False
                            dragged drag_placed
                            drag_raise True
                            mouse_drop True     
            drag:                           # sfondo trasparente per la rimozione dei pegs della riga in progress
                drag_name "empty_bg" 
                child "empty_bg.png"
                draggable False
                droppable True
    if code[0]>0 and code[1]>0 and code[2]>0 and code[3]>0:
        imagebutton:
            ypos peg_pos[row][1][2] - 5
            xpos 75
            anchor (0.5, 0.5)
            idle "checkmark"
            hover "checkmark" 
            action SetVariable("clicked", 10), Return()
    else:
        add "checkmark10disabled.png":
            ypos peg_pos[row][1][2] - 5
            xpos 75
            anchor (0.5, 0.5)
            zoom 0.4 
    imagebutton:
        xpos 250
        ypos 250
        idle "shield_btn"
        hover "shield_btn" 
        action SetVariable("persistent.status", "give_up"), Return()

    if persistent.choice == "game1":        # solo in game1 c'è info, best code e copilot. In game 3 no
        imagebutton:
            ypos peg_pos[row][1][2] - 2
            xpos 220
            anchor (0.5, 0.5)
            idle "info"
            hover "info" 
            action SetVariable("clicked", 11), Return()
        
        imagebutton:
            ypos 250
            xpos 930
            if copilot_on:
                idle "copilot_on"
                hover Transform("copilot_on", size=(160, 160), fit="contain")
                #hover "copilot_on"
                action SetVariable("copilot_on", False), Return()
            else:
                idle "copilot_off"
                hover Transform("copilot_off", size=(160, 160), fit="contain")
                #hover "copilot_off"
                action SetVariable("copilot_on", True), Return()

        if persistent.best_code_active:
            imagebutton:
                ypos 250
                xpos 5
                if not renpy.emscripten:
                    if not thread.is_alive():       #i best code sono stati generati
                        idle "best_code_ready"
                        hover Transform("best_code_ready", size=(170, 170), fit="contain")
                        #hover "best_code_ready"
                        action SetVariable("persistent.status", "best_code"), SetVariable("best_code_ready", True), Return()
                    else:
                        idle "best_code_processing"
                        hover Transform("best_code_processing2", size=(170, 170), fit="contain")
                        #hover "best_code_processing"
                        action Return()
                else:
                    idle "best_code_ready"
                    hover Transform("best_code_ready", size=(170, 170), fit="contain")
                    #hover "best_code_ready"
                    action SetVariable("persistent.status", "best_code"), SetVariable("best_code_ready", True), Return()
      
screen input_game2(row, key_code):     # input dei key code + checkmark verde + bottone shield di rinuncia
    fixed:
        xsize 1080
        ysize 1920
        draggroup:
            for i in range (1, 3):   #colonna di key peg da giocare
                $ name = "key_peg_"+ str(i)
                drag:
                    drag_name name
                    add key_pegs_big[i]
                    xpos 920
                    ypos (1650-i*180)
                    draggable True
                    droppable False
                    dragged drag_placed
                    drag_raise True
                    mouse_drop True
            for j in range (1, 5):      # riga di drop vuoti per posizionare i key pegs
                if key_code[j-1] == 0:
                    $ name = "hole_"+ str(j)
                    drag:
                        drag_name name
                        anchor (0.5, 0.5)
                        xpos key_pos[row][j][1]
                        ypos key_pos[row][j][2]  
                        #child key_pegs_big[1]   #empty peg big come oggetto droppable
                        child "key_empty_circle"    # white circle trasp 50% come oggetto droppable
                        draggable False
                        droppable True
                        mouse_drop True  
            for j in range (1, 5):      # per la rimozione dei key pegs already dropped per la riga in progress
                $ name = "dropped_key_peg_"+ str(j-1)
                if key_code[j-1] > 0:
                    drag:
                        drag_name name
                        add key_pegs[key_code[j-1]]
                        anchor (0.5, 0.5)
                        xpos key_pos[row][j][1]
                        ypos key_pos[row][j][2]  
                        draggable True
                        droppable False
                        dragged drag_placed
                        drag_raise False
                        mouse_drop True
            drag:                           # sfondo trasparente per la rimozione dei pegs della riga in progress
                drag_name "empty_bg" 
                child "empty_bg.png"
                draggable False
                droppable True
    imagebutton:
        ypos peg_pos[row][1][2] - 5
        xpos 75
        anchor (0.5, 0.5)
        idle "checkmark"
        hover "checkmark" 
        action SetVariable("clicked", 10), Return()
    if persistent.choice == "game3":        # in game3 il clic allo shield lo fa aprire per vedere il codice segreto
        imagebutton:
            xpos 250
            ypos 250
            idle "shield_btn"
            hover "shield_btn" 
            action SetVariable("clicked", 12), Return()

screen input_secret_code(colors, secret_code):     # input del codice segreto per game2 e game3
    fixed:
        xsize 1080
        ysize 1920
        draggroup:
            for i in range (1, colors+1):   #colonna di peg da giocare
                $ name = "peg_"+ str(i)
                drag:
                    drag_name name
                    add pegs_big[i]
                    xpos 920
                    ypos (1870-i*180)
                    draggable True
                    droppable False
                    dragged drag_placed
                    drag_raise True
                    mouse_drop True
            for j in range (1, 5):      # riga di drop vuoti per posizionare i pegs
                $ name = "hole_"+ str(j)
                drag:
                    drag_name name
                    xpos peg_pos[11][j][1]
                    ypos peg_pos[11][j][2]
                    anchor (0.5, 0.5)
                    #child pegs[0]   #empty peg big come oggetto droppable
                    child "00_empty_circle"   # white circle trasp 50% come oggetto droppable
                    draggable False
                    droppable True
                    mouse_drop True  
            for j in range (1, 5):      # per la rimozionea dei pegs already dropped per la riga in progress
                $ name = "dropped_peg_"+ str(j-1)
                if secret_code[j-1] > 0:
                    drag:
                        drag_name name
                        add pegs[secret_code[j-1]]
                        anchor (0.5, 0.5)
                        xpos peg_pos[11][j][1]
                        ypos peg_pos[11][j][2]
                        draggable True
                        droppable False
                        dragged drag_placed
                        drag_raise False
                        mouse_drop True   
            drag:                           # sfondo trasparente per la rimozione dei pegs della riga in progress
                drag_name "empty_bg" 
                child "empty_bg.png"
                draggable False
                droppable True
    if secret_code[0]>0 and secret_code[1]>0 and secret_code[2]>0 and secret_code[3]>0:
        imagebutton:
            ypos peg_pos[11][1][2] - 50
            xpos 25
            idle "checkmark"
            hover "checkmark" 
            action SetVariable("clicked", 10), Return()
        # add "arrow_up":
        #     xpos 15
        #     ypos 380
        #     zoom 0.4    
    else:
        add "checkmark10disabled.png":
            ypos peg_pos[11][1][2] - 50
            xpos 25
            zoom 0.4 

screen training_selection(training_type):  # Per selezionare il training game 
    ## Ensure other screens do not get input while this screen is displayed.
    modal True
    zorder 200
    style_prefix "confirm"
    add "gui/overlay/confirm.png"
    frame:
        style_prefix "confirm"
        xpos 530
        ypos 250  
        text "Select the game"
    frame:
        area(100, 350, 880, 1520)  # Adjust as needed
        viewport id "my_image_viewport":
            scrollbars "vertical"
            draggable True
            mousewheel True
            xalign 0.5
            yalign 0.5
            vbox:
                imagebutton:
                    xalign 1.0
                    idle "x"
                    hover "x"
                    action Return()
                $ start_page = selected - (selected % 50)
                if start_page + 50 < matrix_len:
                    $ end_page = start_page + 50
                else:
                    $ end_page = matrix_len 
                if training_type == "CLASSIC":                    
                    for i in range (start_page, end_page):
                        $ breaked = ""
                        if colors == 6 and persistent.training_solved_6[i] == 1:
                            $ breaked = "{color=#33cc33}Broken{/color}"
                        elif colors == 8 and persistent.training_solved_8[i] == 1:
                            $ breaked = "{color=#33cc33}Broken{/color}"
                        else:
                            $ breaked = "{color=#ff0000}Not Broken{/color}"
                        $ text_button = "{font=DejaVuSans.ttf} • " + str(i+1).zfill(4) + " {/font}" + breaked  
                        textbutton text_button:
                            action  SetVariable("selected", i), Return()
                if training_type == "BASIC":
                    for i in range (start_page, end_page):
                        $ breaked = ""
                        if colors == 6 and persistent.training_solved_basic_6[i] == 1:
                            $ breaked = "{color=#33cc33}Broken{/color}"
                        elif colors == 8 and persistent.training_solved_basic_8[i] == 1:
                            $ breaked = "{color=#33cc33}Broken{/color}"
                        else:
                            $ breaked = "{color=#ff0000}Not Broken{/color}"
                        $ text_button = "{font=DejaVuSans.ttf} • " + str(i+1).zfill(4) + " {/font}" + breaked  
                        textbutton text_button:
                            action  SetVariable("selected", i), Return()
                imagebutton:
                    xalign 1.0
                    idle "x"
                    hover "x"
                    action Return()

screen training_dispaly(x, training_type):
    #modal True
    $ breaked = ""
    if training_type == "CLASSIC":
        if colors == 6 and persistent.training_solved_6[x] == 1:
            $ breaked = "{color=#33cc33}   Broken  {/color}"
        elif colors == 8 and persistent.training_solved_8[x] == 1:
            $ breaked = "{color=#33cc33}   Broken  {/color}"
        else:
            $ breaked = "{color=#ff0000}Not Broken{/color}"
        $ text_button = "{font=DejaVuSans.ttf} " + str(x+1).zfill(4) + " {/font}" + breaked + " "    
    if training_type == "BASIC":
        if colors == 6 and persistent.training_solved_basic_6[x] == 1:
            $ breaked = "{color=#33cc33}   Broken  {/color}"
        elif colors == 8 and persistent.training_solved_basic_8[x] == 1:
            $ breaked = "{color=#33cc33}   Broken  {/color}"
        else:
            $ breaked = "{color=#ff0000}Not Broken{/color}"
        $ text_button = "{font=DejaVuSans.ttf} " + str(x+1).zfill(4) + " {/font}" + breaked + " " 
    frame:
        style_prefix "confirm"
        xpos 530
        ypos 620
        hbox:
            textbutton "<< ":
                action  SetVariable("persistent.choice", "training_page_precedent"), Return()
            textbutton " < ":
                action  SetVariable("persistent.choice", "training_precedent"), Return()
            textbutton text_button:
                text_size 40
                yalign 0.5
                action  SetVariable("persistent.choice", "training_select"), Return()
            textbutton " > ":
                action  SetVariable("persistent.choice", "training_next"), Return()
            textbutton " >>":
                action  SetVariable("persistent.choice", "training_page_next"), Return()
            
screen score_menu():   # menu settings per numbers of colors, switch music on/off, enable/disable best codes
    modal True
    style_prefix "confirm"
    add "gui/overlay/confirm.png"
    frame:
        xalign 0.5
        ypos 650
        vbox:            
            spacing 20
            xalign 0.5
            yalign 0.5
            imagebutton:
                xalign 1.0
                idle "x"
                hover "x"
                action SetVariable("score_option", "exit"), Return()             
            textbutton _("• Score One Player/CPU"):
                action SetVariable("score_option", "check_score_game1_2"), Return()
            textbutton _("• Score Two Players"):
                action SetVariable("score_option", "check_score_game3"), Return()  
            textbutton _("• Statistics One Player"):
                action SetVariable("score_option", "score_stats"), Return()  
            textbutton _("• Reset score One Player/CPU"):
                action SetVariable("score_option", "reset_score_game1_2"), Return() 
            textbutton _("• Reset score Two Players"):
                action SetVariable("score_option", "reset_score_game3"), Return()

screen score_statistics():     # visualizza il popup del punteggio
    ## Ensure other screens do not get input while this screen is displayed.
    modal True
    zorder 200
    style_prefix "confirm"
    add "gui/overlay/confirm.png"
    $ message = ''
    $ total_games = 0
    $ total =''
    if len(persistent.perf) == 0:
        $ message = message + "        Play some games\n        to see your score.\n\n\n"
    else:
        for i in range (len(persistent.perf)):
            $ message = message + "       {b}Game     : " + str(i+1) + "{/b}"  + "\n" 
            $ message = message + "       Attemps : " + str(persistent.perf[i][0]) + "\n"
            #$ message = message + "       Time       :  " + str(persistent.perf[i][1]) + ":" + str(persistent.perf[i][2]) + ":" + str(persistent.perf[i][3]) + "\n\n"
            $ message = message + "       Time      : " + str(persistent.perf[i][1]) + "\n\n"
        $ average = persistent.score_player / (i+1)
        $ average = round(average,2)
        #text (str(i))
        #$ total_games = i
        #$ total = "       {b}Total Games: " + str(i+1) + "{/b}\n       Total attemps: " + str(persistent.score_player) + "\n       Total time       : " + str(persistent.total_time_converted[0]) + ":" + str(persistent.total_time_converted[1]) + ":" + str(persistent.total_time_converted[2]) + "\n"
        $ total = "       {b}Total Games  : " + str(i+1) + "{/b}\n       Total attemps: " + str(persistent.score_player) + "\n       Total time     : " + str(persistent.total_time_converted) + "\n       Average       :  " + str(average)
    frame:   
        area(100, 200, 900, 1650) 
        viewport id "my_image_viewport":
            draggable True
            mousewheel True
            vbox:
                xsize 780
                xalign 1.0
                yalign 0.0
                imagebutton:
                    #xpos 500
                    xalign 1.0
                    idle "x"
                    hover "x"
                    action Return()
                label _("{color=#0099ff}Statistics for One Player:{/color}\n"):
                    text_color "#000000"
                    xalign 0.5
                text _(message)
                text _(total)     

screen settings_menu():   # menu settings per numbers of colors, switch music on/off, enable/disable best codes
    modal True
    style_prefix "confirm"
    add "gui/overlay/confirm.png"
    frame:
        xalign 0.5
        ypos 550
        vbox:            
            spacing 20
            xalign 0.5
            yalign 0.5
            imagebutton:
                    xalign 1.0
                    idle "x"
                    hover "x"
                    action SetVariable("pref_option", "exit"), Return() 
            textbutton "• Number of colors":
                action  SetVariable("pref_option", "number_of_colors"), Return() 
            if persistent.sound:
                textbutton "• Switch Music Off":
                    action SetVariable("pref_option", "music"), SetVariable("persistent.sound", False), Stop("music"), Return()
            if not persistent.sound:
                textbutton "• Switch Music On":
                    action SetVariable("pref_option", "music"), SetVariable("persistent.sound", True), Play("music", "Gershon Kingsley - Pop Corn 1969.mp3"), Return()
            textbutton "• Best Code feature":
                    action SetVariable("pref_option", "best_code"), Return()

screen numbers_of_colors():     # richiamato dallo screen settings_menu 
    ## Ensure other screens do not get input while this screen is displayed.
    modal True
    zorder 200
    style_prefix "confirm"
    add "gui/overlay/confirm.png"
    frame:
        yalign 0.6
        vbox:
            xalign .5
            yalign .5
            spacing 45
            imagebutton:
                xalign 1.0
                idle "x"
                hover "x"
                action SetVariable("sub_exit", True), Return()
            label _("How many colors do you want to play with?"):
                style "confirm_prompt"
                #text_size 50
                #text_color "#030331"
                xalign 0.5
            hbox:
                xalign 0.5
                spacing 150
                textbutton _("6 COLORS"):
                    #text_size 50
                    text_color "#000078"
                    text_hover_color "#0099ff"
                    #text_bold True
                    action SetVariable("colors", 6), SetVariable("persistent.colors", 6), Return()
                textbutton _("8 COLORS"):
                    #ext_size 50
                    text_color "#000078"
                    text_hover_color "#0099ff"
                    #text_bold True
                    action SetVariable("colors", 8), SetVariable("persistent.colors", 8), Return()

screen best_code_feature():     # richiamato dallo screen settings_menu
    ## Ensure other screens do not get input while this screen is displayed.
    modal True
    zorder 200
    style_prefix "confirm"
    add "gui/overlay/confirm.png"
    frame:
        yalign 0.6
        vbox:
            xalign .5
            yalign .5
            spacing 45
            imagebutton:
                xalign 1.0
                idle "x"
                hover "x"
                action SetVariable("sub_exit", True), Return()
            label _("Do you want to enable or disable the best code option?"):
                style "confirm_prompt"
                #text_size 50
                #text_color "#030331"
                xalign 0.5
            hbox:
                xalign 0.5
                spacing 150
                textbutton _("ENABLE"):
                    #text_size 50
                    text_color "#000078"
                    text_hover_color "#0099ff"
                    #text_bold True
                    action SetVariable("persistent.best_code_active", True), Return()
                textbutton _("DISABLE"):
                    #ext_size 50
                    text_color "#000078"
                    text_hover_color "#0099ff"
                    #text_bold True
                    action SetVariable("persistent.best_code_active", False), Return()

screen help_tips_view():  # menu Help and Tips 
    ## Ensure other screens do not get input while this screen is displayed.
    modal True
    zorder 200
    style_prefix "confirm"
    add "gui/overlay/confirm.png"

    $ message = "• {color=#f20070}ONE PLAYER{/color} You will try to break the secret code chosen randomly by the App.\
    \n• if you want to give up and see the secret code, tap the shield on the game board\
    \n• Other features are explained later in this section\
    \n• For the game rules, tap {a=https://mastermind.altervista.org/rules-of-the-game/}here {/a}.\n\n"
   
    $ message = message + "• {color=#f20070}TWO PLAYERS{/color} Challenge between two players using the same device.\
    \n• Player 1 and player 2 will take turns to break the secret code hidden by the opponent.\
    \n• Player 1's score is marked with white pegs and player 2's with black pegs.\n\n"

    $ message = message + "• {color=#f20070}CPU PLAYER{/color} The device's CPU will try to break your hidden secret code. \n\n"

    $ message = message + '• {color=#f20070}TRAINING{/color} You will improve your game skills.\
    \n• You can choose to play with 6 or 8 colors from "SETTINGS" and then "Number of Colors".\
    \n• "CLASSIC" Secret code can use repeating colors.\
    \n• "BASIC" Secret code uses only single colors.\
    \n• "0001 Not Broken" Number of current game and if the secret code has been alrady broken. Click here to select a new training game from the list.\
    \n• "<" and ">" To move to the previous or next game.\
    \n• "<<" and ">>" to move 50 games forward or backward.\
    \n• While you are training, in the main menu are also available: "TRAINING RESET" and "TRAINING STATISTICS".\n\n'

    $ message = message + "• {color=#f20070}SCORE.{/color} Like in the classic game, on the right side of game board the score is marked\
    with white and black pegs.\nYour score is marked with white pegs and the CPU's with black pegs.\
    \n• In TWO PLAYERS game, the score is relative to the two opposing players\n\n"

    $ message = message + "• {color=#f20070}SETTINGS.{/color}\n• Number of colors: This setting affecting all game types.\
    \n• Switch music on: to hear popcorn song while playing.\n• Best code feauture: enable/disable Best code feature.\n\n" 

    $ message = message + "{color=#f20070}Interrupting a game.{/color} Tap the menu button and choose CANCEL.\n\n"

    $ message = message + "{color=#f20070}Drag and Drop.{/color} To compose your code, grab pegs from the side column of colors and drop them into the highlighted placeholders.\
    \n• You can take pegs from attempts already played or move a peg to another placeholder.\n• To remove a peg, drag it out.\n\n"

    $ message = message + "{color=#f20070}Info {/color}Tells you how many chances of breaking the secret code you have,\
    and how many you'd have, should you use the best code feature.\n\n"
    
    $ message = message + "{color=#f20070}Copilot{/color} Helps you choose a possible secret code.\
    Based on the pegs already chosen, it excludes those that would make the attempt iconsistent.\
    \n• An inconsistent attempt has zero chance of breaking the secret code.\n\n"

    $ message = message + "{color=#f20070}Best code{/color} This feature provides the code that, \
    in case it does not breaks the secret code, is the one that has the greatest chance of breaking it on the next attempt.\n"
    
    $ message = message + "• It can be an inconsistent code. {a=https://mastermind.altervista.org/left-code-and-best-codes/}Here{/a} \
    you will find the explanation why an inconsistent code can be a best code anyway.\n"
    
    $ message = message + "• The best code is generated in the background. To check if it is ready tap the Best Code \
    button. For slow devices, disable this feature from settings menu.\n\n"
    
    $ message = message + "• {color=#f20070}Bonus{/color} Enjoy a video of a LEGO creation breaking Master Mind secret\
    code: {size=-22}{a=https://mastermind.altervista.org/lego-robot-inventor/}https://mastermind.altervista.org/lego-robot-inventor{/a}{/size}\
    \nFind more Master Mind related stuff on the same site."
    
    frame:
        area(10, 10, 1060, 1900)  # Adjust as needed
        viewport id "my_image_viewport":
            draggable True
            mousewheel True
            xalign 0.5
            yalign 0.5
            vbox:
                imagebutton:
                    xalign 1.0
                    idle "x"
                    hover "x"
                    action Return()
                label _(message):
                        #style "confirm_prompt"
                        #style_prefix "confirm"
                        text_size 50
                        text_color "#000000"
                imagebutton:
                    xalign 1.0
                    idle "x"
                    hover "x"
                    action Return()

screen welcome_message():   # messaggio per il primo avvio dell'app
    ## Ensure other screens do not get input while this screen is displayed.
    modal True
    zorder 200
    style_prefix "confirm"
    add "gui/overlay/confirm.png"
    $ message = """{size=+26}{color=#0099ff}{font=fonts/joystix monospace.otf} Master Mind {/font}{/color}{/size}\n\nThe true and classic\nMaster Mind that uses the original board game from the 70s/80s.\n\nYou will also discover two exclusive features: {color=#0099ff}"Copilot"{/color} and {color=#0099ff}"Best Code"{/color}.\n\n{size=+20}{color=#0099ff}Have fun!!{/color}{/size}"""
    
    frame:
        yalign 0.65
        vbox:
            xalign .5
            yalign .5
            spacing 45
            imagebutton:
                    xalign 1.0
                    idle "x"
                    hover "x"
                    action Hide("welcome_message"), Return()
            label _(message):
                style "confirm_prompt"
                #text_size 50
                #text_color "#030331"
                xalign 0.5
            imagebutton:
                    xalign 1.0
                    idle "x"
                    hover "x"
                    action Hide("welcome_message"), Return()

screen print_mastermind():   #visualizza la scritta MASTER MIND
    fixed:
        xpos -20
        ypos 70 
        hbox:
            xalign 0.5
            text "{color=#ff0000}M{color=#0099ff}A{color=#ffff00}S{color=#00ff00}T{color=#ffffff}E{color=#ff9900}R {color=#ff0000}M{color=#0099ff}I{color=#ffff00}N{color=#00ff00}D{/color}":
                size 80
                #bold True
                color "#ffffff"
                font "fonts/joystix monospace.otf"

screen menu_button ():   # visualizza il bottone per richiamare il menu principale
    imagebutton:
        xpos 940
        ypos 70
        idle "menu_btn"
        hover Transform("menu_btn", size=(130, 130), fit="contain")
        action Hide("message"), Show("menu")

screen menu():   # è il menu contestualizzato al richiamo delle modalità di gioco oppure mentre si gioca
    add "gui/overlay/confirm.png"
    frame:
        style_prefix "confirm"
        yalign 0.20
        vbox:            
            spacing 20
            xalign 0.5
            yalign 0.5
            imagebutton:
                    xalign 1.0
                    idle "x"
                    hover "x"
                    action Hide("menu"), Return()
            if persistent.choice == "none":                 # none = nessuna partita è attiva     
                textbutton "• ONE PLAYER":
                    action Hide("menu"), SetVariable("persistent.choice", "game1"), Return()
                textbutton "• TWO PLAYERS":
                    action Hide("menu"), SetVariable("persistent.choice", "game3"), Return()
                textbutton "• CPU PLAYER":
                    action Hide("menu"), SetVariable("persistent.choice", "game2"), Return()
                textbutton "• TRAINING":
                    action Hide("menu"), SetVariable("persistent.choice", "training"), Return()
                textbutton "• SCORE":
                    action Hide("menu"), SetVariable("persistent.choice", "score"), Return()
                textbutton "• SETTINGS":
                    action Hide("menu"), SetVariable("persistent.choice", "settings"), Return()
            if persistent.choice == "training":
                textbutton "• TRAINING RESET":          # solo durante il training
                    action Hide("menu"), SetVariable("persistent.choice", "training_reset"), Return()
                textbutton "• TRAINING STATISTICS":          # solo durante il training
                    action Hide("menu"), SetVariable("persistent.choice", "training_numbers"), Return()
            if persistent.choice == "game1" or persistent.choice == "game2" or persistent.choice == "game3" or persistent.choice == "training":
                textbutton "• CANCEL":          # voce menu CANCEL solo durante le partite
                    action Hide("menu"), SetVariable("persistent.choice", "cancel"), Return()
            textbutton "• HELP":
                action Hide("menu"), SetVariable("persistent.choice", "help_tips"), Return()
            if not renpy.emscripten:
                textbutton "• CLOSE THE APP":
                    action Quit(confirm=None)

screen are_you_sure(message):   # usato in game1/2/3. Per cancel e give_up,    
    ## Ensure other screens do not get input while this screen is displayed.
    modal True
    #zorder 200
    style_prefix "confirm"
    add "gui/overlay/confirm.png"
    frame:
        vbox:
            xalign .5
            yalign .5
            spacing 45
            label _(message):
                style "confirm_prompt"
                #text_size 50
                #text_color "#030331"
                xalign 0.5
            hbox:
                xalign 0.5
                spacing 150
                textbutton _("YES"):
                    #text_size 50
                    text_color "#000078"
                    text_hover_color "#0099ff"
                    #text_bold True
                    action Hide("are_you_sure"), SetVariable("yes_no", "yes"), Return()
                textbutton _("NO"):
                    #text_size 50
                    text_color "#000078"
                    text_hover_color "#0099ff"
                    #text_bold True
                    action Hide("are_you_sure"), SetVariable("yes_no", "no"), Return()

screen message (message1, message2, arrow=None, arrow_x=0, arrow_y=0): # usato con YOU GAVE UP, SECRET CODE BROKEN, GAME OVER, GAME CANCELLED, [code_breaker], [code_maker]
    #modal True
    style_prefix "confirm"
    #add "gui/overlay/confirm.png"
    if arrow != None:
        add arrow:
            xpos arrow_x
            ypos arrow_y
            zoom 0.4
    frame:
        yalign 0.37
        vbox:
            #add "arrow"
            xalign .5
            yalign .5
            spacing 20
            label _("{color=#0099ff}[message1]{/color}\n\n[message2]"):
                style "confirm_prompt"
                #text_size 50
                #text_color "#030331"
                xalign 0.5

screen message_org (message1, message2): # usato con YOU GAVE UP, SECRET CODE BROKEN, GAME OVER, GAME CANCELLED, [code_breaker], [code_maker]
    #modal True
    style_prefix "confirm"
    #add "gui/overlay/confirm.png"
    frame:
        yalign 0.37
        vbox:
            #add "arrow"
            xalign .5
            yalign .5
            spacing 20
            label _("{color=#0099ff}[message1]{/color}\n\n[message2]"):
                style "confirm_prompt"
                #text_size 50
                #text_color "#030331"
                xalign 0.5

screen message_x (message1, message2):    # usato da score, colors, best code, ... 
    modal True
    # zorder 200
    style_prefix "confirm"
    add "gui/overlay/confirm.png"
    frame:
        xalign 0.5
        yalign 0.5
        vbox:
            xalign 0.5
            yalign 0.5
            spacing 10
            imagebutton:
                    xalign 1.0
                    idle "x"
                    hover "x"
                    action Return()
            label _("{color=#0099ff}[message1]{/color}\n\n[message2]"):
                style "confirm_prompt"
                #size 60
                #text_align 0.5
                #text_color "#030331"
                xalign 0.5

screen message_2_options(message, option1, option2):   # usato in option ritorna ad esempio: "PLAYER 1", "PLAYER 2", "ENTER", "KEEP IN MIND"
    modal True
    zorder 200
    style_prefix "confirm"
    add "gui/overlay/confirm.png"
    frame:
        vbox:
            xalign .5
            yalign .5
            spacing 45
            imagebutton:
                    xalign 1.0
                    idle "x"
                    hover "x"
                    action SetVariable("option", "exit"), Return() 
            label _(message):
                style "confirm_prompt"
                #text_size 50
                #text_color "#030331"
                xalign 0.5
            hbox:
                xalign 0.5
                spacing 150
                textbutton _(option1):
                    #text_size 50
                    text_color "#000078"
                    text_hover_color "#0099ff"
                    #text_bold True
                    action SetVariable("option", option1), Return()
                textbutton _(option2):
                    #text_size 50
                    text_color "#000078"
                    text_hover_color "#0099ff"
                    #text_bold True
                    action SetVariable("option", option2), Return()
    ## Right-click and escape answer "no".
    #key "game_menu" action no_action

screen open_shield():   # visualizza lo shield aperto 
        add "shield_open.png":
            zoom 0.5
            xpos 150
            ypos 248

screen attempt_info(chance, tot_lc, left_code, left_code_bs, code_status, bs_inconsistent): # info visulaizzate cliccand la "i" di Info
    ## Ensure other screens do not get input while this screen is displayed.
    modal True
    zorder 200
    style_prefix "confirm"
    add "gui/overlay/confirm.png"
    #text code_status
    if code_status == "incompleto":
        $ message = "You have {color=#0000ff}1{/color} in {color=#0000ff}[tot_lc]{/color} chance of breaking the secret code."
    if code_status == "best_code_not_ready": 
        $ message = "Your attempt has a {color=#0000ff}[chance]{/color} in {color=#0000ff}[tot_lc]{/color} chance of breaking the secret code. \n\n"
        if tot_lc > 1:
            if chance > 0:
                $message = message + "If you don't break, you will have at maximum {color=#0000ff}1{/color} in {color=#0000ff}[left_code]{/color} chance on your next try."
            else:
                $ message = message + "You will have at maximum {color=#0000ff}1{/color} in {color=#0000ff}[left_code]{/color} chance on your next try."
    if code_status == "is_best_code":
        $ message = "Your attempt is a BEST CODE and has a {color=#0000ff}[chance]{/color} in {color=#0000ff}[tot_lc]{/color} chance of breaking the secret code. \n\n"
        if tot_lc > 1:
            if chance > 0:
                $message = message + "If you don't break, you will have at maximum {color=#0000ff}1{/color} in {color=#0000ff}[left_code]{/color} chance on your next try."
            else:
                $ message = message + "You will have at maximum {color=#0000ff}1{/color} in {color=#0000ff}[left_code]{/color} chance on your next try."
    if code_status == "is_not_best_code":
        $ message = "Your attempt has a {color=#0000ff}[chance]{/color} in {color=#0000ff}[tot_lc]{/color} chance of breaking the secret code. \n\n"
        if tot_lc > 1:
            if chance > 0:
                $message = message + "If you don't break, you will have at maximum {color=#0000ff}1{/color} in {color=#0000ff}[left_code]{/color} chance on your next try.\n\n"
            else:
                $ message = message + "You will have at maximum {color=#0000ff}1{/color} in {color=#0000ff}[left_code]{/color} chance on your next try.\n\n"
        if bs_inconsistent:
            $ message = message + "If you play an INCONSISTENT BEST CODE, You will have at maximum {color=#0000ff}1{/color} in {color=#0000ff}[left_code_bs]{/color} chance on your next try."
        else:
            $ message = message + "If you play a BEST CODE, You will have at maximum {color=#0000ff}1{/color} in {color=#0000ff}[left_code_bs]{/color} chance on your next try."
    frame:
        vbox:
            xalign .5
            yalign .5
            spacing 45
            imagebutton:
                xalign 1.0
                idle "x"
                hover "x"
                action Return()
            label _(message):
                style "confirm_prompt"
                #text_size 50
                xalign 0.5
