label main_menu:
    return    

label start:
    $ quick_menu = False
    $ game_loop()

init 1 python:
    config.rollback_enabled = False
    def game_loop():        #setup iniziale + loop per il richiamo delle partite
        renpy.show ("mm_bg")        #compare solo questa volta
        renpy.show_screen ("mm_print_mastermind") #richiamato solo da qua
        renpy.show ("board_with_shield_closed")     #solo qua 
        renpy.show_screen ("mm_menu_button")    #screen richiamato solo da qua
        renpy.show_screen("score_update")
        persistent.choice = "none"
        if persistent.sound:
            renpy.music.play ("audio/Gershon Kingsley - Pop Corn 1969.mp3")
        if persistent.welcome:
            renpy.show_screen("welcome_message")
            renpy.pause()
            renpy.show_screen("tap_main_menu")
        while True:
            if persistent.choice == "game1":
                game1(colors)
            if persistent.choice == "game2":
                game2(colors)
            if persistent.choice == "game3":
                game3(colors)
            renpy.pause()

    def game1(colors):   #game player > app
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
        best_code_ready = False
        copilot_on = False
        mm = Mastermind_Engine()                                          
        db_ac, db_lc, db_bc = mm.init_db(colors)                            #crea il database di tutti i codici, dei left e best codes
        secret_code = random.choice(db_ac)                                  #il programma sceglie il codice segreto tra tutti i codici possibili
        #secret_code = mm.code_adapter("2635")                               #utilizzo di CS fisso per debugging
        thread = CustomThread(target=mm.nothing())          # per fare in modo che il test  if not thread.is_alive():  in mm_menu non dia errore con row = 1
        thread.start()
        thread.join()         
        key_board = []
        board = []
        copilot = [True] * (colors+1) 
        reset_board()
        blacks = 0          # serve per evitare errori nel richiamo di final 
        start_time = time.time()
        renpy.hide_screen ("final_update") # nasconde lo screen che aveva aperto lo shield e visualizzato il codice segreto della partita precedente 
        #renpy.show_screen("board_update") # non necessaria perchè già presente in inserting_code
        renpy.play("audio/close.mp3")
        persistent.status = "on_game"
        # renpy.hide_screen("open_shield")        # superflua. Lo shield viene chiuso già da final_update
        # if persistent.status == "final":              # si passa da una partita finita a una che inizia
        #     renpy.hide_screen("board_update")
        #     renpy.play("audio/close.mp3")
        #     persistent.status = "on_game"
        #renpy.show_screen("board_update")
        for row in range (1, 11):  #le giocate massime sono 10 
            code = [0,0,0,0] #giocata corrente vuota
            # if row == 1:            # per troubleshooting
            #     code = [1,2,3,1]
            inserting_code = True
            clicked = 99
            while inserting_code:       #fase di input + test dei clic/drag&drop
                draggable = False
                droppable = False
                if persistent.status == "best_code" and best_code_ready == True:
                    if row > 1:
                        db_lc, db_bc = thread.join() 
                    code = random.choice(db_bc)
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
                        i_code = mm.code_adapter(i_code)
                        key_hits = [0]*25                                           #Ogni campo corrisponde ha un tipo di cod.chiave(1 bianco, 2 bianchi, 1 nero, ...)
                        for code_lc in db_lc:                                       #per ogni codice di db_loop ripete per tutti i possibili codici segreti 
                            whites, blacks = mm.find_keycode(i_code, code_lc)  #trova il codice chiave tra i codici di db_loop e quelli di db_lc
                            key_hits [whites*5 + blacks] +=1                        #incrementa le ricorrenze di codici chiave uguali. *5 simula una tabella a 2 dim
                        left_code = max(key_hits)
                        code_status = "best_code_not_ready"
                        left_code_bs = 0
                        if not thread.is_alive() and row > 1 and persistent.best_code_active:       #i best code sono stati generati
                            db_lc, db_bc = thread.join()
                            if db_lc[0][0] != db_bc[0][0]:
                                bs_inconsistent = True
                            else:
                                bs_inconsistent = False 
                            bs_code = db_bc[0]
                            key_hits = [0]*25                                           #Ogni campo corrisponde ha un tipo di cod.chiave(1 bianco, 2 bianchi, 1 nero, ...)
                            for code_lc in db_lc:                                       #per ogni codice di db_loop ripete per tutti i possibili codici segreti 
                                whites, blacks = mm.find_keycode(bs_code, code_lc)  #trova il codice chiave tra i codici di db_loop e quelli di db_lc
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
                renpy.show_screen ("board_update")
                renpy.call_screen ("input_game1", row, colors, code)

                code = dragged_code(row, code, draggable, droppable)

                # for peg in range (1, colors+1):     # se è stato droppato un peg della colonna esterna, viene aggiornato code[]
                #     for hole in range (1,5):        
                #         if draggable == "peg_" + str(peg) and droppable == "hole_" + str(hole):
                #             code[hole-1] = peg
                #             renpy.play("audio/peg.mp3")
                # for dropped in range (0,4):    # se un peg è stato rimosso dalla giocata, viene tolto da code[]
                #     if draggable == "dropped_peg_" + str(dropped) and droppable == "empty_bg":
                #         code[dropped] = 0
                #         renpy.play("audio/drag_out.ogg")
                #     for hole in range (1,5):    # un peg può essere spostato da un buco ad un altro
                #         if draggable == "dropped_peg_" + str(dropped) and droppable == "hole_" + str(hole):
                #             if hole-1 != dropped:       # se il peg non è rilasciato nel suo buco iniziale
                #                 code[hole-1] = code[dropped]
                #                 code[dropped] = 0
                #             renpy.play("audio/peg.mp3")
                #     for i in range (1,row+1):       # drag dei peg dalle righe precedenta a quella attuale 
                #         for j in range (1, 5):      
                #             for hole in range (1,5):
                #                 if draggable == "dropped_peg_prec" + str(i-1) + str(j-1) and droppable == "hole_" + str(hole):
                #                     code[hole-1] = board[i-1][j]
                #                     renpy.play("audio/peg.mp3")
                
                for i in range(1,5):        #aggiorna la board con la giocata che si sta inserendo
                    board[row][i] = code[i-1]
                copilot = [True] * (colors+1) 
                if (code[0] != 0 or code[1] != 0 or code[2] != 0 or code[3] != 0) and copilot_on:
                    copilot = mm_copilot(code, db_lc, colors)
                if (clicked == 10) and (code[0] != 0) and (code[1] != 0) and (code[2] != 0) and (code[3] != 0): #ok spunta verde e controllo che ci siano tutti i 4 colori
                    inserting_code = False
                    code_played = mm.code_adapter (str(code[0])+str(code[1])+str(code[2])+str(code[3]))
                    copilot = [True] * (colors+1) 
                    whites, blacks = mm.find_keycode(secret_code, code_played)               
                    keycode = converti_keycode (whites, blacks)
                    for i in range(0,4):
                        key_board[row][i] = keycode[i]
                    renpy.show_screen ("mm_key_board")
                if persistent.status == "final":     #valore impostato dalla funzione di Input. Click sullo shield
                    yes_no = ''
                    renpy.call_screen ("are_you_sure", "Are you sure you want to give up?")
                    if yes_no == "yes":
                        mm_final(blacks, row)
                        renpy.show_screen ("final_update")
                        renpy.show_screen("game_over", "YOU GAVE UP" )
                        return
                    else:
                        persistent.choice = "game1"
                        persistent.status = "on_game"
                if persistent.choice == "cancel":         #è stato cliccato "cancel" dal main menu
                    yes_no = ''
                    renpy.call_screen ("are_you_sure", "Do you want to quit this game?")
                    if yes_no == "yes":   
                        renpy.show_screen("board_update")
                        renpy.show_screen("game_over", "GAME CANCELLED")
                        persistent.choice = "none"
                        return
                    else:
                        persistent.choice = "game1"
            if blacks == 4:
                mm_final(blacks, row)
                renpy.show_screen ("final_update")
                renpy.show_screen("game_over", "YOU WON!")
                break
            db_ac, db_lc = mm.left_codes(db_ac, code_played, (whites, blacks))  #genera il db dei left codes e mette il flag True in db_ac per i lc
            if persistent.best_code_active:
                thread = CustomThread(target=mm.best_codes, args=(db_ac, db_lc))     #generazione del database dei best codes
                thread.start()      
        if blacks != 4: #è stato superato il numero massimo di giocate senza indovinare il codice segreto
            mm_final(blacks, row)
            renpy.show_screen ("final_update")
            renpy.show_screen("game_over", "GAME OVER")
        return

    def game2(colors):
        """ partita dove il programma deve indovinare il codice segreto scelto dal giocatore usando le partite già giocate """
        global clicked          #usata anche da input_game1
        global secret_code
        global draggable
        global droppable
        global key_board
        global board
        global yes_no
        global secret
        mm = Mastermind_Engine()
        persistent.status = "on_game"
        key_board = []
        board = []
        reset_board()                                  
        next_key = ''
        secret = ''
        secret_code = [0,0,0,0]
        clicked = 99
        renpy.hide_screen ("final_update")          # rimuove lo shield aperto della partita precedente
        renpy.hide_screen ("open_shield")
        renpy.hide_screen("board_update") 
        renpy.call_screen ("secret_code_game", "In GAME-2 the App will guess your secret code.\n\n Do you want to enter the secret code or keep it in mind?")
        if secret == "Enter":
            renpy.show_screen("open_shield")
            while not clicked == 10:       
                draggable = False
                droppable = False
                renpy.show_screen("board_update")
                renpy.call_screen ("enter_secret_code_game", colors, secret_code)

                secret_code = dragged_secret_code(secret_code, draggable, droppable)

                # for peg in range (1, colors+1):     # se è stato droppato un peg della colonna esterna, viene aggiornato code[]
                #     for hole in range (1,5):        
                #         if draggable == "peg_" + str(peg) and droppable == "hole_" + str(hole):
                #             secret_code[hole-1] = peg
                #             renpy.play("audio/peg.mp3")
                # for dropped in range (0,4):    # se un peg è stato rimosso dalla giocata, viene tolto da secret_code[]
                #     if draggable == "dropped_peg_" + str(dropped) and droppable == "empty_bg":
                #         secret_code[dropped] = 0
                #         renpy.play("audio/drag_out.ogg")
                #     for hole in range (1,5):    # un peg può essere spostato da un buco ad un altro
                #         if draggable == "dropped_peg_" + str(dropped) and droppable == "hole_" + str(hole):
                #             if hole-1 != dropped:       # se il peg non è rilasciato nel suo buco iniziale
                #                 secret_code[hole-1] = secret_code[dropped]
                #                 secret_code[dropped] = 0
                #             renpy.play("audio/peg.mp3")
                
                
                for i in range(1,5):        #aggiorna la board con la giocata che si sta inserendo
                    board[11][i] = secret_code[i-1]
                if persistent.choice == "cancel":         #è stato cliccato "cancel" dal main menu
                        yes_no = ''
                        renpy.call_screen ("are_you_sure", "Do you want to quit this game? ")
                        if yes_no == "yes":
                            key_board = []
                            board = []
                            reset_board()
                            renpy.hide_screen("open_shield")
                            renpy.show_screen("board_update")
                            renpy.show_screen("game_over", "GAME CANCELLED")
                            persistent.choice = "none"
                            return
                        else:
                            persistent.choice = "game2"
        fake_pegs_dict = {6:['1', '2', '3', '4', '5', '6'], 8:['1', '2', '3', '4', '5', '6', '7', '8']}  #serve per simulare un codice random sia per la versione a 6 e a 8 colori                 
        fake_pegs = fake_pegs_dict[colors]                          #considera la fake pegs in base al numero di colori con cui si sta giocando
        random.shuffle(fake_pegs)                                   #mischia i pegs nella lista
        first_codes_list = ['2131', '1231', '2311', '2113', '1123', '1212', '1221', '1122', '1234', '1234', '1234']     #1234 è ripetuto per aumentare le probabilità
        is_first_play = True 
        first_code = random.choice(first_codes_list)                #per il primo tentativo il codice viene scelto nella lista first_codes_list
        #first_code = first_codes_list[0]                           # per troubleshooting
        #narrator (first_code)
        matrix = mm.make_matrix_from_file_renpy (colors, first_code)      #crea la matrice delle partite giocate dal file in base al numero di colori usati e al primo codice giocato 
        for row in range(1,11):                                    #loop per tutte le partite possibili
            key_code = [0,0,0,0] 
            if is_first_play:
                code_played = first_code
                next_code = first_code                              # necessario se l'app indovina al pomo tentativo
                is_first_play = False                               #dalla seconda giocata il codice sarà: next_code
            else:
                code_played = next_code
            code_played_fake = ''                                   #è il codice che viene visualizzao invece di quello vero. Fa sembrare che il programma gioca sempre codici diversi          
            for i in code_played:                                   #generazione del codice fake basato sul codice vero
                code_played_fake += fake_pegs[int(i) - 1]
            #code_played_fake = code_played                      # per troubleshooting reinserire la funzione fake
            for i in range(1,5):        #aggiorna la board con la giocata che si sta inserendo
                board[row][i] = int(code_played_fake[i-1])
            inserting_code = True
            renpy.play("audio/peg.mp3")
            while inserting_code:
                clicked = 99
                draggable = False
                droppable = False
                #game_board.append([code_played_fake, 0, 0])             #aggiunta del codice fake
                #narrator (str(board[11]))
                renpy.show_screen("board_update")
                for i in range(0,4):
                        key_board[row][i] = key_code[i]
                if next_key == 'XXXX':
                    secret_code_str = str(secret_code[0]) + str(secret_code[1]) + str(secret_code[2]) + str(secret_code[3]) 
                    #narrator (secret_code_str)
                    #narrator (code_played_fake)
                    if secret == "Enter" and secret_code_str != code_played_fake:
                        persistent.choice = "none"
                        renpy.call_screen("wrong_key_game4", "One or more KEY CODES entered are incorrect.")
                        renpy.show_screen("game_over", "GAME OVER")
                        return
                    else:                   
                        blacks = 4
                        whites = 0
                        for i in range(0,4):
                            key_board[row][i] = 2       #mette 4 key code neri
                        inserting_code = False
                        #renpy.hide_screen ("mm_key_board_big")
                else:
                    for i in range(0,4):
                        key_board[row][i] = key_code[i]
                    renpy.show_screen ("mm_key_board")
                    #renpy.show_screen ("mm_key_board_big", row)
                    renpy.call_screen ("input_game4", row, key_code)
                    for key_peg in range (1, 3):     # se è stato droppato un peg della colonna esterna, viene aggiornato code[]
                        for hole in range (1,5):        
                            if draggable == "key_peg_" + str(key_peg) and droppable == "hole_" + str(hole):
                                key_code[hole-1] = key_peg      #nelle 4 posizioni del key_code ci va 1 per il bianco e 2 per il nero
                                renpy.play("audio/peg.mp3")
                    for dropped in range (0,4):    # se un key peg è stato rimosso dalla giocata, viene tolto da key_code[]
                        if draggable == "dropped_key_peg_" + str(dropped) and droppable == "empty_bg":
                            key_code[dropped] = 0
                            renpy.play("audio/drag_out.ogg")
                    if (clicked == 10) : #ok spunta verde 
                        inserting_code = False
                        #code_played = mm.code_adapter (str(code[0])+str(code[1])+str(code[2])+str(code[3]))
                        whites = 0
                        blacks = 0
                        for i in range (0,4):
                            if key_code[i] == 1:
                                whites += 1
                            if key_code[i] == 2:
                                blacks += 1
                    if persistent.choice == "cancel":         #è stato cliccato "cancel" dal main menu
                        yes_no = ''
                        renpy.call_screen ("are_you_sure", "Do you want to quit this game?")
                        #narrator (yes_no)
                        if yes_no == "yes":
                            renpy.show_screen("board_update")
                            renpy.show_screen("game_over", "GAME CANCELLED")
                            persistent.choice = "none"
                            return
                        else:
                            persistent.choice = "game2"
            if blacks == 4:
                secret_code =''
                for i in next_code:                                   #generazione del codice fake basato sul codice vero
                    secret_code += fake_pegs[int(i) - 1]
                secret_code = mm.code_adapter(secret_code)  
                mm_final(blacks, row)
                renpy.show_screen ("final_update")
                renpy.show_screen("game_over", "SECRET CODE GUESSED")
                break
            code_plus_key = code_played + ' ' + 'X' * blacks + 'O' * whites + '_' * (4 - (blacks + whites)) 
            #compone il codice giocato + il codice chiave inserito dal giocatore per cercare il prossimo codice da gocare
            matrix, next_code, next_key = mm.find_next_code (row, matrix, code_plus_key )                  
            #trova il prossimo codice da giocare. next_key serve solo se è uguale a XXXX
            if next_code == 'not_found':
                persistent.choice = "none"
                renpy.call_screen("wrong_key_game4", "One or more KEY CODES entered are incorrect.")
                renpy.show_screen("game_over", "GAME OVER")
                return            

    def game3(colors):
        # parte copiata da GAME2 - inserimento codice segreto
        """ partita dove il programma deve indovinare il codice segreto scelto dal giocatore usando le partite già giocate """
        global clicked          #usata anche da input_game1
        global secret_code
        global draggable
        global droppable
        global key_board
        global board
        global yes_no
        global secret
        global secret_code
        global thread
        global best_code_ready
        global copilot_on
        global copilot
        global start_time
        global inserting_code
        global inserting_key_code
        best_code_ready = False
        copilot_on = False
        mm = Mastermind_Engine()
        persistent.status = "on_game"
        persistent.shield_status = "close"
        key_board = []
        board = []
        reset_board()                                  
        next_key = ''
        secret = ''
        secret_code = [6,6,6,0]
        clicked = 99
        renpy.hide_screen ("final_update")          # rimuove lo shield aperto della partita precedente
        renpy.hide_screen ("open_shield")
        renpy.hide_screen("board_update") 
        renpy.call_screen ("secret_code_game", "In GAME-3 two players will play on the same device.\n\n The first player can enter the secret code or keep it in mind")
        if secret == "Enter":
            renpy.show_screen("open_shield")
            while not clicked == 10:       
                draggable = False
                droppable = False
                renpy.show_screen("board_update")
                renpy.call_screen ("enter_secret_code_game", colors, secret_code)
                secret_code = dragged_secret_code(secret_code, draggable, droppable)

                # for peg in range (1, colors+1):     # se è stato droppato un peg della colonna esterna, viene aggiornato code[]
                #     for hole in range (1,5):        
                #         if draggable == "peg_" + str(peg) and droppable == "hole_" + str(hole):
                #             secret_code[hole-1] = peg
                #             renpy.play("audio/peg.mp3")
                # for dropped in range (0,4):    # se un peg è stato rimosso dalla giocata, viene tolto da secret_code[]
                #     if draggable == "dropped_peg_" + str(dropped) and droppable == "empty_bg":
                #         secret_code[dropped] = 0
                #         renpy.play("audio/drag_out.ogg")
                #     for hole in range (1,5):    # un peg può essere spostato da un buco ad un altro
                #         if draggable == "dropped_peg_" + str(dropped) and droppable == "hole_" + str(hole):
                #             if hole-1 != dropped:       # se il peg non è rilasciato nel suo buco iniziale
                #                 secret_code[hole-1] = secret_code[dropped]
                #                 secret_code[dropped] = 0
                #             renpy.play("audio/peg.mp3")
                for i in range(1,5):        #aggiorna la board con la giocata che si sta inserendo
                    board[11][i] = secret_code[i-1]
                if persistent.choice == "cancel":         #è stato cliccato "cancel" dal main menu
                        yes_no = ''
                        renpy.call_screen ("are_you_sure", "Do you want to quit this game? ")
                        #narrator (yes_no)
                        if yes_no == "yes":
                            key_board = []
                            board = []
                            reset_board()
                            renpy.hide_screen("open_shield")
                            #renpy.show ("board_with_shield_closed")
                            renpy.show_screen("board_update")
                            renpy.show_screen("game_over", "GAME CANCELLED")
                            persistent.choice = "none"
                            return
                        else:
                            persistent.choice = "game3"
        secret_code = mm.code_adapter(secret_code)    
        key_board = []
        board = []
        copilot = [True] * (colors+1) 
        reset_board()
        blacks = 0          # serve per evitare errori nel richiamo di final 
        #start_time = time.time()
        renpy.hide_screen ("final_update")          # rimuove lo shield aperto della partita precedente
        renpy.hide_screen("open_shield")
        #secret_code = code_adapter (generate_secret_code(colors))
        
        if persistent.status == "final":              # si passa da una partita finita a una che inizia
            renpy.hide_screen("board_update")
            renpy.play("audio/close.mp3")
            persistent.status = "on_game"
        
        renpy.show_screen("board_update")
        for row in range (1, 11):  #le giocate massime sono 10 
            code = [1,1,1,1] #giocata corrente vuota
            key_code = [0,0,0,0] 
            inserting_code = True
            clicked = 99
            persistent.shield_status = "close"
            renpy.hide_screen ("final_update") 

            while inserting_code:
                draggable = False
                droppable = False
                renpy.show_screen ("board_update")
                renpy.call_screen ("input_game1", row, colors, code)
                code = dragged_code(row, code, draggable, droppable)

                # for peg in range (1, colors+1):     # se è stato droppato un peg della colonna esterna, viene aggiornato code[]
                #     for hole in range (1,5):        
                #         if draggable == "peg_" + str(peg) and droppable == "hole_" + str(hole):
                #             code[hole-1] = peg
                #             renpy.play("audio/peg.mp3")
                # for dropped in range (0,4):    # se un peg è stato rimosso dalla giocata, viene tolto da code[]
                #     if draggable == "dropped_peg_" + str(dropped) and droppable == "empty_bg":
                #         code[dropped] = 0
                #         renpy.play("audio/drag_out.ogg")
                #     for hole in range (1,5):    # un peg può essere spostato da un buco ad un altro
                #         if draggable == "dropped_peg_" + str(dropped) and droppable == "hole_" + str(hole):
                #             if hole-1 != dropped:       # se il peg non è rilasciato nel suo buco iniziale
                #                 code[hole-1] = code[dropped]
                #                 code[dropped] = 0
                #             renpy.play("audio/peg.mp3")
                #     for i in range (1,row+1):       # drag dei peg dalle righe precedenta a quella attuale 
                #         for j in range (1, 5):      
                #             for hole in range (1,5):
                #                 if draggable == "dropped_peg_prec" + str(i-1) + str(j-1) and droppable == "hole_" + str(hole):
                #                     code[hole-1] = board[i-1][j]
                #                     renpy.play("audio/peg.mp3")
                
                for i in range(1,5):        #aggiorna la board con la giocata che si sta inserendo
                    board[row][i] = code[i-1]
                #copilot = [True] * (colors+1) 
                # if (code[0] != 0 or code[1] != 0 or code[2] != 0 or code[3] != 0) and copilot_on:
                #     copilot = mm_copilot(code, db_lc, colors)
                if (clicked == 10) and (code[0] != 0) and (code[1] != 0) and (code[2] != 0) and (code[3] != 0): #ok spunta verde e controllo che ci siano tutti i 4 colori
                    inserting_code = False
                    code_played = mm.code_adapter (str(code[0])+str(code[1])+str(code[2])+str(code[3]))
                    #copilot = [True] * (colors+1)
                if persistent.status == "final":     #valore impostato dalla funzione di Input. Click sullo shield
                    yes_no = ''
                    renpy.call_screen ("are_you_sure", "Are you sure you want to give up?")
                    if yes_no == "yes":
                        mm_final(blacks, row)
                        renpy.show_screen ("final_update")
                        renpy.show_screen("game_over", "YOU GAVE UP" )
                        return
                    else:
                        persistent.choice = "game3"
                        persistent.status = "on_game"
                if persistent.choice == "cancel":         #è stato cliccato "cancel" dal main menu
                    yes_no = ''
                    renpy.call_screen ("are_you_sure", "Do you want to quit this game?")
                    if yes_no == "yes":   
                        renpy.show_screen("board_update")
                        renpy.show_screen("game_over", "GAME CANCELLED")
                        persistent.choice = "none"
                        return
                    else:
                        persistent.choice = "game3"

            #aggiungere nelle preferenze l'abilitazioni/disabilitazione di "INFO"
            #copilot non visualizzato se persistent.choice = "game3"
            # parte copiata da GAME 2 - inserimento key code
            inserting_key_code = True
            renpy.play("audio/peg.mp3")
            while inserting_key_code:
                clicked = 99
                draggable = False
                droppable = False
                renpy.show_screen("board_update")
                for i in range(0,4):
                        key_board[row][i] = key_code[i]
                
                renpy.show_screen ("mm_key_board")
                renpy.call_screen ("input_game4", row, key_code)
                for key_peg in range (1, 3):     # se è stato droppato un peg della colonna esterna, viene aggiornato code[]
                    for hole in range (1,5):        
                        if draggable == "key_peg_" + str(key_peg) and droppable == "hole_" + str(hole):
                            key_code[hole-1] = key_peg      #nelle 4 posizioni del key_code ci va 1 per il bianco e 2 per il nero
                            renpy.play("audio/peg.mp3")
                for dropped in range (0,4):    # se un key peg è stato rimosso dalla giocata, viene tolto da key_code[]
                    if draggable == "dropped_key_peg_" + str(dropped) and droppable == "empty_bg":
                        key_code[dropped] = 0
                        renpy.play("audio/drag_out.ogg")
                if (clicked == 10) : #ok spunta verde 
                    inserting_key_code = False
                    #code_played = mm.code_adapter (str(code[0])+str(code[1])+str(code[2])+str(code[3]))
                    whites = 0
                    blacks = 0
                    for i in range (0,4):
                        if key_code[i] == 1:
                            whites += 1
                        if key_code[i] == 2:
                            blacks += 1
                    
                if persistent.choice == "cancel":         #è stato cliccato "cancel" dal main menu
                    yes_no = ''
                    renpy.call_screen ("are_you_sure", "Do you want to quit this game?")
                    #narrator ("yes_no")
                    if yes_no == "yes":
                        renpy.show_screen("board_update")
                        renpy.show_screen("game_over", "GAME CANCELLED")
                        persistent.choice = "none"
                        return
                    else:
                        persistent.choice = "game3"
                if persistent.shield_status == "open":
                    #mm_final(blacks, row)
                    #narrator ("shield aperto")
                    renpy.show_screen ("final_update")    
                #fine input keycode game2

            if blacks == 4:
                # mm_final(blacks, row)
                renpy.show_screen ("final_update")
                #renpy.show_screen ("final_update")
                renpy.show_screen("game_over", "YOU WON!")
                persistent.choice = "none"
                break 
        if blacks != 4: #è stato superato il numero massimo di giocate senza indovinare il codice segreto
            mm_final(blacks, row)
            renpy.show_screen ("final_update")
            renpy.show_screen("game_over", "GAME OVER")
        return

    def mm_final (blacks, row):            # prepara il finale del gioco e chiama board_update
        renpy.play("audio/open.mp3")
        persistent.status = "final"
        #narrator (persistent.choice)
        if (blacks == 4 or row == 10) and persistent.choice == "game1":
            if persistent.score_player + row < 30:
                persistent.score_player = persistent.score_player + row
                persistent.score [persistent.score_player][1] = 1       # 1 è il key code bianco
                end_time = time.time()
                integer_seconds = int(end_time - start_time)
                time_conv = time_converter (integer_seconds)
                temp = [row, '']
                temp[1] = time_conv
                persistent.perf.append(temp)
                persistent.total_time += integer_seconds
                persistent.total_time_converted = time_converter (persistent.total_time)
                #narrator (persistent.total_time_converted)
        if blacks == 4 and persistent.choice == "game2":
            if persistent.score_app + row < 30:
                persistent.score_app = persistent.score_app + row
                persistent.score [persistent.score_app][2] = 2       # 2 è il key code bianco
        persistent.choice = "none"
        return

    def drag_placed(drags, drop):   #valorizza le variabili draggable e droppable in caso d drop
        if not drop:
            return
        store.draggable = drags[0].drag_name
        store.droppable = drop.drag_name
        return True

    def reset_board():      # azzera tutta la board compresi i keycode. Indice 11 è la posizione del secret code
        for row in range (12):
            single_row = [0,0,0,0,0]
            single_row_key = [0,0,0,0]
            board.append(single_row)
            key_board.append(single_row_key)
    
    def reset_score():
        persistent.score_player = 0
        persistent.score_app = 0
        #persistent.score = []
        persistent.perf = []   
        persistent.total_time = 0
        persistent.score = [[0 for i in range(3)] for j in range(30)]
        # for i in range (30):
        #     single_score = [0,0,0]
        #     persistent.score.append(single_score)

    def converti_keycode (whites, blacks):         #converte i bianchi e i neri in key_code 1 per ogni bianco, 2 per ogni nero
        key_code = [0,0,0,0]
        for i in range (0, whites):
            key_code[i] = 1
        for i in range (0, blacks):
            key_code[i + whites] = 2
        return key_code

    def mm_copilot(code, db_lc, colors):
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

    def time_converter (integer_seconds):
                integer_minutes = integer_seconds // 60
                remaining_seconds = integer_seconds % 60
                integer_hours = integer_minutes // 60
                remaining_minutes = integer_minutes % 60
                formatted_time = f"{integer_hours:02d}:{remaining_minutes:02d}:{remaining_seconds:02d}"
                #narrator (formatted_time)
                #return [integer_hours, remaining_minutes, remaining_seconds ]
                return formatted_time       

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
                            renpy.play("audio/peg.mp3")
        return code
    
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



screen board_update():      # aggiorna i pegs sulla board compresi i pegs del codice segreto (posizione 11)
    fixed:
        xsize 1080
        ysize 1920
        for i in range (1,12):              #aggiorna la board con le giocate
            for j in range (1,5):
                add pegs[board[i][j]]:
                    xalign 0.5
                    yalign 0.5
                    xpos peg_pos[i][j][1]
                    ypos peg_pos[i][j][2]

screen final_update():      # aggiorna i pegs sulla board e se chiamato da mm_final visualizza il codice segreto
    add "shield_open.png":
        zoom 0.5
        xpos 150
        ypos 248
    fixed:                              # visualizza il codice segreto
        xsize 1080
        ysize 1920
        for j in range (1,5):
            add pegs[int(secret_code[0][j-1])]:
                xalign 0.5
                yalign 0.5
                xpos peg_pos[11][j][1]
                ypos peg_pos[11][j][2]

screen score_update():      # aggiorna lo score sulla board
    fixed:
        xsize 1080
        ysize 1920
        for i in range (1,30):              
            for j in range (1,3):
                add key_pegs[persistent.score[i][j]]:
                    xalign 0.5
                    yalign 0.5
                    xpos score_pos[i][j][1]
                    ypos score_pos[i][j][2]
    
screen mm_key_board():     #visualizza i codici chiave di ogni giocata
    fixed:
        xsize 1080
        ysize 1920
        for i in range (1,11):
            for j in range (1,5):
                add key_pegs[key_board[i][j-1]]: 
                    xalign 0.5
                    yalign 0.5
                    xpos key_pos[i][j][1]
                    ypos key_pos[i][j][2]  

screen mm_menu_button ():   # visualizza il bottone per richiamare il menu principale
    imagebutton:
        xpos 940
        ypos 70
        idle "menu_btn"
        hover Transform("menu_btn", size=(130, 130), fit="contain")
        action Hide("tap_main_menu"), Hide("game_over"), Show("mm_menu")

screen mm_menu():   # è il menu contestualizzato al richiamo delle modalità di gioco oppure mentre si gioca la voce per arrendersi
    add "gui/overlay/confirm.png"
    frame:
        style_prefix "confirm"
        yalign 0.15
        vbox:            
            spacing 20
            xalign 0.5
            yalign 0.5
            imagebutton:
                    xalign 1.0
                    idle "x"
                    hover "x"
                    action Hide("mm_menu"), Return()
            if persistent.choice == "none":                 # none = nessuna partita è attiva     
                textbutton "• PLAY GAME 1":
                    action Hide("mm_menu"), SetVariable("persistent.choice", "game1"), Return()
                textbutton "• PLAY GAME 2":
                    action Hide("mm_menu"), SetVariable("persistent.choice", "game2"), Return()
                textbutton "• PLAY GAME 3":
                    action Hide("mm_menu"), SetVariable("persistent.choice", "game3"), Return()
                textbutton "• YOUR SCORE":
                    action Hide("mm_menu"), Show("score"), Return()
                textbutton "• PREFERENCES":
                    action Hide("mm_menu"), Show("preferences"), Return()        
            if persistent.choice == "game1" or persistent.choice == "game2" or persistent.choice == "game3":
                textbutton "• CANCEL":          # voce menu CANCEL solo durante le partite
                    action Hide("mm_menu"), SetVariable("persistent.choice", "cancel"), Return()
            textbutton "• HELP AND TIPS":
                action Hide("mm_menu"), Show("tips"), Return()
            textbutton "• CLOSE THE APP":
                action Quit(confirm=None)

screen input_game1(row, colors, code):     # input delle giocate + checkmark verde + bottone shield per rinuncia, info, best code e copilot
    fixed:
        xsize 1080
        ysize 1920
        draggroup:
            for i in range (1, colors+1):   #colonna di peg da giocare
                $ name = "peg_"+ str(i)
                if copilot[i]:
                    drag:
                        drag_name name
                        add pegs_big[i]
                        xpos 930
                        ypos (1900-i*180)
                        draggable True
                        droppable False
                        dragged drag_placed
                        drag_raise True
                        mouse_drop True
            for j in range (1, 5):      # riga di drop vuoti per posizionare i pegs
                $ name = "hole_"+ str(j)
                drag:
                    xalign 0.5
                    yalign 0.5
                    drag_name name
                    xpos peg_pos[row][j][1]
                    ypos peg_pos[row][j][2] 
                    child pegs_big[0]   #empty peg big come oggetto droppable
                    draggable False
                    droppable True
                    mouse_drop True  
            for j in range (1, 5):      # per la rimozionea dei pegs already dropped per la riga in progress
                $ name = "dropped_peg_"+ str(j-1)
                if code[j-1] > 0:
                    drag:
                        xalign 0.5
                        yalign 0.5
                        drag_name name
                        add pegs[code[j-1]]
                        xpos peg_pos[row][j][1]
                        ypos peg_pos[row][j][2]
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
                            xalign 0.5
                            yalign 0.5
                            drag_name name
                            add pegs[board[i-1][j]]
                            xpos peg_pos[i-1][j][1]
                            ypos peg_pos[i-1][j][2]
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
            ypos peg_pos[row][1][2] - 50
            xpos 25
            idle "checkmark"
            hover "checkmark" 
            action SetVariable("clicked", 10), Return()
    else:
        add "checkmark10disabled.png":
            ypos peg_pos[row][1][2] - 50
            xpos 25
            zoom 0.4 

    imagebutton:
        xpos 250
        ypos 250
        idle "shield_btn"
        hover "shield_btn" 
        action SetVariable("persistent.status", "final"), Return()

    if persistent.choice == "game1":        # solo in game1 c'è info, best code e copilot. In game 3 no
        imagebutton:
            ypos peg_pos[row][1][2] - 47
            xpos 167
            idle "info"
            hover "info" 
            action SetVariable("clicked", 11), Return()
        
        imagebutton:
            ypos 250
            xpos 920
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
        
screen input_game4(row, key_code):     # input dei key code + checkmark verde + bottone di rinuncia
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
                        xalign 0.5
                        yalign 0.5
                        drag_name name
                        xpos key_pos[row][j][1]
                        ypos key_pos[row][j][2]  
                        child key_pegs_big[0]   #empty peg big come oggetto droppable
                        draggable False
                        droppable True
                        mouse_drop True  
            for j in range (1, 5):      # per la rimozione dei key pegs already dropped per la riga in progress
                $ name = "dropped_key_peg_"+ str(j-1)
                if key_code[j-1] > 0:
                    drag:
                        xalign 0.5
                        yalign 0.5
                        drag_name name
                        add key_pegs[key_code[j-1]]
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
        ypos peg_pos[row][1][2] - 50
        xpos 25
        idle "checkmark"
        hover "checkmark" 
        action SetVariable("clicked", 10), Return()
    if persistent.choice == "game3":        # in game3 il clic allo shield lo fa aprire per vedere il codice segreto
        imagebutton:
            xpos 250
            ypos 250
            idle "shield_btn"
            hover "shield_btn" 
            action SetVariable("persistent.shield_status", "open"), Return()
            
screen mm_print_mastermind():   #visualizza la scritta MASTER MIND
    fixed:
        xpos -20
        ypos 70 
        hbox:
            xalign 0.5
            text "MASTER MIND":
                size 80
                #bold True
                color "#ffffff"
                font "fonts/joystix monospace.otf"

screen secret_code_game(message):   #chiede se vuoi inserire il codice segreto o tenere in mente. Game2 e game3
    modal True
    zorder 200
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
                textbutton _("ENTER"):
                    #text_size 50
                    text_color "#000078"
                    text_hover_color "#0099ff"
                    #text_bold True
                    action SetVariable("secret", "Enter"), Return()
                textbutton _("KEEP IN MIND"):
                    #text_size 50
                    text_color "#000078"
                    text_hover_color "#0099ff"
                    #text_bold True
                    action SetVariable("secret", "Keep in mind"), Return()
    ## Right-click and escape answer "no".
    #key "game_menu" action no_action

screen wrong_key_game4(message):
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
                    action Hide("wrong_key_game4"), Return()
            label _(message):
                style "confirm_prompt"
                #text_size 50
                #text_color "#030331"
                xalign 0.5
            hbox:
                xalign 0.5
                spacing 150
                textbutton _("Tap here to close this popup"):
                    #text_size 50
                    text_color "#000078"
                    text_hover_color "#0099ff"
                    #text_bold True
                    action Return()
                
    ## Right-click and escape answer "no".
    #key "game_menu" action no_action

screen tips():
    ## Ensure other screens do not get input while this screen is displayed.
    modal True
    zorder 200
    style_prefix "confirm"
    add "gui/overlay/confirm.png"

    $ message = "• {color=#f20070}GAME-1{/color} You will try to guess the secret code chosen randomly by the App.\n• You can find the game rules {a=https://mastermind.altervista.org/rules-of-the-game/}here {/a}.\n\n"

    $ message = message + "• {color=#f20070}GAME-2{/color} The App will guess your secret code. \n\n"

    $ message = message + "{image=info_tip} {color=#f20070}Info {/color}Tells you how many chances of guessing the secret code you have, and how many you'd have, should you use the best code feature\n\n"
    
    $ message = message + "{image=copilot_on_tip} {color=#f20070}Copilot{/color} helps you choose a possible secret code. Based on the pegs already chosen, it excludes those that would make the attempt iconsistent.\n"

    $ message = message + "• An INCONSISTENT attemp has zero chance of guessing the secret code.\n\n"

    $ message = message + "{image=best_code_ready_tip} {color=#f20070}Best code feature{/color} provides the code that, in case it does not guess the secret code, is the one that has the greatest chance of guessing it on the next attempt.\n"
    
    $ message = message + "• It can be an inconsistent code. {a=https://mastermind.altervista.org/left-code-and-best-codes/}Here{/a} you will find the explanation why an inconsistent code can be a best code anyway.\n"
    
    $ message = message + "• The best code is generated in the background. To check if it is ready tap the {image=best_code_processing_tip} button. For slow devices, disable this feature from preferences menu.\n\n"
    
    $ message = message + "{image=drag_tip} {color=#f20070}Drag and Drop.{/color} Drag and drop pegs to compose your attempts. You can take pegs from attempts already played, move a peg to another placeholder . To remove a peg, drag it out.\n\n"

    $ message = message + "{image=shield_tip} {color=#f20070}Secret Code.{/color} In GAME-1, if you want to give up and see the secret code, tap the shield on the game board.\n\n"
    
    $ message = message + "• {color=#f20070}Score.{/color} Like in the classic game, on the right side of game board your score is marked with white pegs and that of the app with black pegs.\nChoose 'Your score' from the main menu for more detailed information.\n\n"

    $ message = message + "• {color=#f20070}LEGO Video.{/color} Enjoy a {a=https://mastermind.altervista.org/lego-robot-inventor/}video{/a} of a LEGO creation guessing the secret code."
    
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
                    action Hide("tips"), Return()
                label _(message):
                        #style "confirm_prompt"
                        #style_prefix "confirm"
                        #text_size 50
                        text_color "#000000"

screen score():     # visualizza il popup del punteggio
    ## Ensure other screens do not get input while this screen is displayed.
    modal True
    zorder 200
    style_prefix "confirm"
    add "gui/overlay/confirm.png"
    #$ message = "{b}Your score{/b}:\n\n"
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
            #xalign 0.5
            #yalign 0.5
            #spacing 45
            vbox:
                xsize 780
                xalign 1.0
                yalign 0.0
                imagebutton:
                    #xpos 500
                    xalign 1.0
                    idle "x"
                    hover "x"
                    action Hide("score"), Return()
                label _("{color=#0099ff}YOUR SCORE:{/color}\n"):
                    text_color "#000000"
                    xalign 0.5
                text _(message)
                text _(total)
                textbutton _("\n• Tap here to reset the score."):
                    xalign 0.5
                    text_color "#000078"
                    text_hover_color "#0099ff"
                    #text_bold True
                    text_align 0.5
                    action Function(reset_score), Return()      

screen attempt_info(chance, tot_lc, left_code, left_code_bs, code_status, bs_inconsistent): # ifo visulaizzate cliccand la "i" di Info
    ## Ensure other screens do not get input while this screen is displayed.
    modal True
    zorder 200
    style_prefix "confirm"
    add "gui/overlay/confirm.png"
    #text code_status
    if code_status == "incompleto":
        $ message = "You have {color=#0000ff}1{/color} in {color=#0000ff}[tot_lc]{/color} chance of guessing the secret code."
    if code_status == "best_code_not_ready": 
        $ message = "Your attempt has a {color=#0000ff}[chance]{/color} in {color=#0000ff}[tot_lc]{/color} chance of guessing the secret code. \n\n"
        if tot_lc > 1:
            if chance > 0:
                $message = message + "If you don't guess, you will have at maximum {color=#0000ff}1{/color} in {color=#0000ff}[left_code]{/color} chance on your next try."
            else:
                $ message = message + "You will have at maximum {color=#0000ff}1{/color} in {color=#0000ff}[left_code]{/color} chance on your next try."
    if code_status == "is_best_code":
        $ message = "Your attempt is a BEST CODE and has a {color=#0000ff}[chance]{/color} in {color=#0000ff}[tot_lc]{/color} chance of guessing the secret code. \n\n"
        if tot_lc > 1:
            if chance > 0:
                $message = message + "If you don't guess, you will have at maximum {color=#0000ff}1{/color} in {color=#0000ff}[left_code]{/color} chance on your next try."
            else:
                $ message = message + "You will have at maximum {color=#0000ff}1{/color} in {color=#0000ff}[left_code]{/color} chance on your next try."
    if code_status == "is_not_best_code":
        $ message = "Your attempt has a {color=#0000ff}[chance]{/color} in {color=#0000ff}[tot_lc]{/color} chance of guessing the secret code. \n\n"
        if tot_lc > 1:
            if chance > 0:
                $message = message + "If you don't guess, you will have at maximum {color=#0000ff}1{/color} in {color=#0000ff}[left_code]{/color} chance on your next try.\n\n"
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

screen are_you_sure(message):
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

screen disable_best_code():
    ## Ensure other screens do not get input while this screen is displayed.
    modal True
    zorder 200
    style_prefix "confirm"
    add "gui/overlay/confirm.png"
    if persistent.best_code_active:
        $ message = "From the next game, the Best Codes feature will be:\n{color=#00cc00}ACTIVATED{/color}"
    else:
        $ message = "From the next game, the Best Codes feature will be:\n{color=#ff0000}DEACTIVATED{/color}"
    frame:
        vbox:
            xalign .5
            yalign .5
            spacing 0
            imagebutton:
                    xalign 1.0
                    idle "x"
                    hover "x"
                    action Hide("disable_best_code"), Return()
            label _(message):
                style "confirm_prompt"
                #text_size 50
                #text_color "#030331"
                xalign 0.5

screen welcome_message():
    ## Ensure other screens do not get input while this screen is displayed.
    modal True
    zorder 200
    style_prefix "confirm"
    add "gui/overlay/confirm.png"
    $ message = """{size=+28}{color=#0099ff}{font=fonts/joystix monospace.otf}Master Mind {/font}{/color}{/size}\n\nThis App offers you a gaming experience of the Classic version of Master Mind.\n\nYou will also discover two exclusive features: {color=#0099ff}"Copilot"{/color} and {color=#0099ff}"Best Code"{/color}.\n\nClose this pop-up and tap the menu at the top right to get started.\n\n{size=+20}{color=#0099ff}Have fun!!{/color}{/size}"""
    frame:
        yalign 0.68
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
            hbox:
                xalign 0.5
                spacing 150
                textbutton _("• Tap here to do not show this message again"):
                    #text_size 50
                    text_color "#000078"
                    text_hover_color "#0099ff"
                    #text_bold True
                    action SetVariable("persistent.welcome", False), Hide("welcome_message"), Return()

screen enter_secret_code_game(colors, secret_code):     # input del codice segreto per game2 e game3
    fixed:
        xsize 1080
        ysize 1920
        draggroup:
            for i in range (1, colors+1):   #colonna di peg da giocare
                $ name = "peg_"+ str(i)
                drag:
                    drag_name name
                    add pegs_big[i]
                    xpos 930
                    ypos (1900-i*180)
                    draggable True
                    droppable False
                    dragged drag_placed
                    drag_raise True
                    mouse_drop True
            for j in range (1, 5):      # riga di drop vuoti per posizionare i pegs
                $ name = "hole_"+ str(j)
                drag:
                    xalign 0.5
                    yalign 0.5
                    drag_name name
                    xpos peg_pos[11][j][1]
                    ypos peg_pos[11][j][2] 
                    child pegs_big[0]   #empty peg big come oggetto droppable
                    draggable False
                    droppable True
                    mouse_drop True  
            for j in range (1, 5):      # per la rimozionea dei pegs already dropped per la riga in progress
                $ name = "dropped_peg_"+ str(j-1)
                if secret_code[j-1] > 0:
                    drag:
                        xalign 0.5
                        yalign 0.5
                        drag_name name
                        add pegs[secret_code[j-1]]
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
    else:
        add "checkmark10disabled.png":
            ypos peg_pos[11][1][2] - 50
            xpos 25
            zoom 0.4 

screen open_shield():
        add "shield_open.png":
            zoom 0.5
            xpos 150
            ypos 248

screen tap_main_menu():
    ## Ensure other screens do not get input while this screen is displayed.
    # modal True
    # zorder 200
    style_prefix "confirm"
    #add "gui/overlay/confirm.png"
    frame:
        yalign 0.15
        vbox:
            #add "arrow"
            xalign .5
            yalign .5
            spacing 20
            label _("                          {image=arrow}\nTap the menu button to start."):
                style "confirm_prompt"
                #text_size 50
                #text_color "#030331"
                xalign 0.5

screen preferences():
    add "gui/overlay/confirm.png"
    frame:
        # xsize 800
        # ysize 750
        xalign 0.5
        ypos 270
        vbox:            
            spacing 20
            xalign 0.5
            yalign 0.5
            imagebutton:
                    xalign 1.0
                    idle "x"
                    hover "x"
                    action Hide("preferences"), Return()
            textbutton "• Number of colors":
                action  Show ("numbers_of_colors"), Return() #Hide("preferences"),
            if persistent.sound:
                textbutton "• Switch Music Off":
                    action Hide("mm_menu"), SetVariable("persistent.sound", False), Stop("music"), Return()
            if not persistent.sound:
                textbutton "• Switch Music On":
                    action Hide("mm_menu"), SetVariable("persistent.sound", True), Play("music", "Gershon Kingsley - Pop Corn 1969.mp3"), Return()
            textbutton "• Best Code feature":
                    action  Show ("best_code_feature"), Return()

screen numbers_of_colors():
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
                action Hide("numbers_of_colors"), Return()
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
                    action Hide("numbers_of_colors"), SetVariable("colors", 6), # Return()
                textbutton _("8 COLORS"):
                    #ext_size 50
                    text_color "#000078"
                    text_hover_color "#0099ff"
                    #text_bold True
                    action Hide("numbers_of_colors"), SetVariable("colors", 8), # Return()

screen best_code_feature():
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
                action Hide("best_code_feature"), Return()
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
                    action Hide("best_code_feature"), SetVariable("persistent.best_code_active", True), # Return()
                textbutton _("DISABLE"):
                    #ext_size 50
                    text_color "#000078"
                    text_hover_color "#0099ff"
                    #text_bold True
                    action Hide("best_code_feature"), SetVariable("persistent.best_code_active", False), # Return()

screen game_over(message):
    style_prefix "confirm"
    #add "gui/overlay/confirm.png"
    frame:
        yalign 0.37
        vbox:
            #add "arrow"
            xalign .5
            yalign .5
            spacing 20
            label _("{color=#0099ff}[message]{/color}\n\nTap the menu button to start a new game"):
                style "confirm_prompt"
                #text_size 50
                #text_color "#030331"
                xalign 0.5