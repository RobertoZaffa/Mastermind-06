init python:
        
    class Mastermind_Engine:
    
        def init_db(self, colors):
            """
            init_db crea le seguenti liste di liste:
            db_ac: database all codes - include tutte le combinazioni di codici possibili 1296 per 6 colori e 4096 per 8 colori
            db_lc: database dei left codes - sono tutti i codici eleggibili come codice segreto. All'inizio del gioco, è identico ad db_ac
            db_bc: database dei best codes - sono i migliori codici da giocare. All'inizio sono del tipo 1234 1123 1122 con la versione 6 colori e 1234 per la versione a 8 colori

            Ogni codice è così composto: 0 stringa che rappresenta il codice mastermind (un numero per ogni colore), 1 flag left code(True se il codice è un left code), 2-9 numero di volte che un colore è presente nel codice.
            Ogni posizione è un colore. 10 score best code(inizializzato a 0), 11 valore nel range 1-25 utilizzato per determinare i best codes. Inizializzato a zero
            """                  
            self.colors = colors
            db_ac = []                              
            db_lc = []                              
            db_bc = []                              
            for a in range(1, colors+1):
                for b in range(1, colors+1):
                    for c in range(1, colors+1):
                        for d in range(1, colors+1):
                            code = str(a) + str(b) + str(c) + str(d)
                            t = [code, True, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0] 
                            t[1 + a] += 1                   
                            t[1 + b] += 1
                            t[1 + c] += 1
                            t[1 + d] += 1
                            db_ac.append(t)                 
                            db_lc.append(t)                 
                            if colors == 6 and t[2]<3 and t[3]<3 and t[4]<3 and t[5]<3 and t[6]<3 and t[7]<3 and t[8]<3 and t[9]<3:
                                db_bc.append(t)             
                            if colors == 8 and t[2]<2 and t[3]<2 and t[4]<2 and t[5]<2 and t[6]<2 and t[7]<2 and t[8]<2 and t[9]<2:
                                db_bc.append(t)             
            return db_ac, db_lc, db_bc

        def find_keycode(self, code_a, code_b):     
            """
            riceve due codici ad esempio, codice segreto e codice giocato e dal confronto ritorna il codice chiave in termini di piolini bianchi e neri.
            Non viene usato un loop FOR per migliorare le prestazioni del metodo best codes.
            Viene sommato a blacks_whites il minor numero di volte che ogni colore è presente in entrambi i codici.
            trova poi il numero di neri per confronto e ricava per differenza i numeri di bianchi
            """
            blacks_whites = 0                       
            blacks = 0                              
            if code_a[2] < code_b[2]:               
                blacks_whites += code_a[2]
            else:
                blacks_whites += code_b[2]
            if code_a[3] < code_b[3]:
                blacks_whites += code_a[3]
            else:
                blacks_whites += code_b[3]
            if code_a[4] < code_b[4]:
                blacks_whites += code_a[4]
            else:
                blacks_whites += code_b[4]
            if code_a[5] < code_b[5]:
                blacks_whites += code_a[5]
            else:
                blacks_whites += code_b[5]
            if code_a[6] < code_b[6]:
                blacks_whites += code_a[6]
            else:
                blacks_whites += code_b[6]
            if code_a[7] < code_b[7]:
                blacks_whites += code_a[7]
            else:
                blacks_whites += code_b[7]
            if code_a[8] < code_b[8]:
                blacks_whites += code_a[8]
            else:
                blacks_whites += code_b[8]
            if code_a[9] < code_b[9]:
                blacks_whites += code_a[9]
            else:
                blacks_whites += code_b[9]
            if code_a[0][0] == code_b[0][0]:
                blacks += 1
            if code_a[0][1] == code_b[0][1]:
                blacks += 1
            if code_a[0][2] == code_b[0][2]:
                blacks += 1
            if code_a[0][3] == code_b[0][3]:
                blacks += 1
            return (blacks_whites - blacks, blacks) 

        def left_codes(self, db_ac, code_played, key_code ):         
            """
            Riceve il db di tutti i codici, il codice giocato e il codice chiave.
            Crea db_lc che contiene tutti i codici segreti possibili. Mette il flag True per tutti i codici segreti possibili in db_ac.
            Confronta il codice giocato con tutti i codici di db_ac. Per tutti quelli che non erano già stati eliminati e che il codice chiave generato è uguale a quello
            della partita, vengono aggiunti a db_lc. Altrimenti non vengono aggiunti e il flag in db_ac viene settato a False 
            """
            db_lc = []                                                   
            for code_ac in db_ac:                                        
                found_keycode = self.find_keycode(code_played, code_ac) 
                if key_code == found_keycode and code_ac[1] == True:      
                    db_lc.append(code_ac)
                else:                                                  
                    code_ac[1]=False                                                                                
            return db_ac, db_lc

        def best_codes (self, db_ac, db_lc):                                #Crea db_bc con i best codes e ripopola i left codes con il rate corretto
            """ check mastermind.altervista.org to understand how this algorithm works"""
            min_of_max = 99999                                              #inizializza un valore sicuramente più alto per il confronto                                              
            db_loop = []                                                    #lista temporanea                                           
            colors = self.colors
            """ Se i possibili codici segreti sono molti, i codici per la simulazione saranno i left codes. Evita che il loop richieda troppo tempo per l'esecuzione.
            Produce db_loop con [10] = a max_hit e [11] con num_of_zero. Fornisce anche min_of_max  """
            if (len(db_lc) > 252 and colors == 6) or (len(db_lc) > 80 and colors == 8):    
                db_loop = db_lc                                             
            else:
                db_loop = db_ac            
            for code_loop in db_loop:                                                                                             
                key_hits = [0]*25                                           #Ogni campo corrisponde ha un tipo di cod.chiave(1 bianco, 2 bianchi, 1 nero, ...)
                for code_lc in db_lc:                                       #per ogni codice di db_loop ripete per tutti i possibili codici segreti 
                    whites, blacks = self.find_keycode(code_loop, code_lc)  #trova il codice chiave tra i codici di db_loop e quelli di db_lc
                    key_hits [whites*5 + blacks] +=1                        #incrementa le ricorrenze di codici chiave uguali. *5 simula una tabella a 2 dim
                max_hit = max(key_hits)                                     #trova il numero massimo di ricorrenze dei codici chiave. Questo valore indica al massimo quanti cod segreti possono rimanee giocando code_loop
                code_loop[10] = max_hit                                     #assegnazione del rate al codice
                if max_hit < min_of_max:                                    
                    min_of_max = max_hit                                    #assegna a min_of_max il più piccolo dei max
                num_of_zero = key_hits.count(0)                             #pochi campi a zero significa miglior distribuzione dei codici chiave e quindi maggior possiblità di lasciare un num di cod segreti inferiore
                code_loop[11] = num_of_zero                                 #memorizza in code_loop[11] il numero di campi a zero
            """ Usa db_loop, min_of_max e crea db_bc_1 con tutti i code_loop[10] = min_of_max,  produce min_num_of_zero e db_lc ordinato in base a min_of_max """
            db_bc_1 = []                                                    # db temporaneo per utile per poi produrre db_bc  
            db_lc = []                                                      #azzera il db dei left codes. Vengono ripopolati con il rate corretto
            min_num_of_zero = 25                                            #assegna un valore più alto di quelli possibili reali 
            for code_loop in db_loop:                                       #ripete per tutti i codici in db_loop
                if code_loop[10] == min_of_max:                             #se il codice ha un rate uguale a minimo dei massimi, allora è un best code...
                    db_bc_1.append(code_loop)                               #... e viene messo nel db temporaneo dei best codes
                    num_of_zero = code_loop[11]                
                    if num_of_zero < min_num_of_zero:                                    
                        min_num_of_zero = num_of_zero                       #trova il minor numero di campi a zero presenti tra i vari bc
                if code_loop[1] == True:                                    #se è un left code, viene messo in db_lc con il suo rate
                    db_lc.append(code_loop)       
            db_lc.sort(key=lambda x: x[10])                                 #ordina db_lc in base al rate in ordine crescente
            """ Se c'è almeno un left code in db_bc, allora elimina tutti quelli iconsistenti altrimenti passa al prossimo blocco
            Usa db_lc, db_bc_1, min_of_max e crea db_bc_2 con i soli bc consistenti. Ricalcola min_num_of_zero e fa puntare a db_bc_1 a db_bc_2  """
            if db_lc [0][10] == min_of_max:                                 #test se [10] del primo lc è uguale a min_of_max                 
                db_bc_2 = []                                                #db dei bc temporaneo
                min_num_of_zero = 25                                        #resetta min_num_of_zero a 25 per essere poi ricalcolato
                for code_bc_1 in db_bc_1:                                   #ripeti per tutti i codici in db_bc_1
                    if code_bc_1[1] == True:                                #se è un left code, tienilo e mettilo in db_bc_2.
                        db_bc_2.append(code_bc_1)
                        num_of_zero = code_bc_1[11]                     
                        if num_of_zero < min_num_of_zero:                                    
                            min_num_of_zero = num_of_zero                   #trova il nuovo min_num_of_zero
                db_bc_1 = db_bc_2                                           #riassegnazione per il prossimo blocco
            """ Crea db_bc definitivo prendendo tutti i codici da db_bc_1 che hanno [11] = min_num_of_zero """
            db_bc = []
            for code_bc_1 in db_bc_1:
                if code_bc_1[11] == min_num_of_zero:
                    db_bc.append(code_bc_1)  
            return db_lc, db_bc

        def code_adapter (self, code):
            """ il codice viene trasformato nel formato dei codici presenti nei database """
            adapted_code = [code, True,0,0,0,0,0,0,0,0,0,0]               
            for i in range (0,4):                                           #i campi dal 5 al 12 sono uno per ogni colore.                             
                adapted_code[1 + int(code[i])] += 1                         #ognuno di questi campi contiene quante volte il colore è presente nel codice
            return adapted_code

        def make_matrix_from_file_renpy (self, colors, code):             #used by game3/4 and idented_played
            #file = os.path.join('Played_Games', 'Game_' + str(colors) + '_' + code + '.txt')
            file = 'Played_Games/' + 'Game_' + str(colors) + '_' + code + '.txt'
            #file = 'Game_' + str(colors) + '_' + code + '.txt'
            #dir = os.path.join('Played_Games', 'Game_')
            #narrator(file)   
            fin = renpy.open_file(file)     # esempio apre il file Played_Games\Game_6_1234.txt
            matrix = []
            #delimiter = ';'
            for row in fin:                                 #esempio di row: 1234 XO__;1135 X___;6343 XOOO;4336 XXXX; ; ;  
                row = row.strip()                           #1234 O___;1556 OOO_;5161 XXXX; ; ; ; togli spazi prima  dopo è \n
                sub_lista = []                              #['1234 OO__', '2545 X___', '2612 XXXX', ' ', ' ', ' ', ''] da stringa a lista   
                temp_str = ''
                for c in row:
                    char = chr(c)
                    if char != ';':
                        temp_str = temp_str + char
                    else:
                        sub_lista.append(temp_str)
                        temp_str = ''
                #narrator (str(sub_lista))
                #row = row.split(delimiter)                  # da stringa a lista. In renpy non funziona. Sostituito con righe da sub_lista = []   
                matrix.append(sub_lista)
            return matrix

        def find_next_code (self, row, matrix, code_plus_key ):
            """ usato solo da Game4. Usa matrix in memoria e cerca il prossimo codice da giocare + la chiave """
            matrix_temp = []
            for i in range(len(matrix)):                                    #looppa pr tutte le righe di matrix
                #narrator (str(matrix))
                if matrix[i][row - 1] == code_plus_key:                    #cerca il codice giocato nella colonna che corrisponde al numero di giocata. Colonna 0 di matrix per il primo turno, colonna 1 per secondo turno, ... 
                    matrix_temp.append(matrix[i])                           #salva in matrix_temp tute le righe ok. Esempio, prima giocata 1234 XX__ salva: ['1234 XX__', '1145 ____', '2166 O___', '3232 XXXX', ' ', ' ', '']
            matrix = matrix_temp                                            #il nuovo matrix ha solo le partite che portano al codice segreto
            if len(matrix) > 0:                                             #se len di matrix è 0, almeno un codice chiave inserito è sbagliato perchè non c'è nessun codice che può essere il codice segreto
                next_code_plus_key = matrix [0][row]                       #prende il primo codice+chiave della prossima colonna per il  prossimo turno. In questa colonna i codici+chiave sono comunque tutti uguali
                next_code = next_code_plus_key[:4]                          #estrapola il prossimo codice da giocare
                next_key = next_code_plus_key[5:]                           #estrapola il codice chiave. Serve solo a Game4 per capire se il codice è stato indovinato (codice chiave = XXXX) 
                return matrix, next_code, next_key
            else:
                next_key = ''
                return matrix, 'not_found', next_key

        def nothing(self):
            pass           

    class CustomThread(Thread):
        def __init__(self, group=None, target=None, name=None,
                    args=(), kwargs={}, Verbose=None):
            Thread.__init__(self, group, target, name, args, kwargs)
            self._return = None
    
        def run(self):
            if self._target is not None:
                self._return = self._target(*self._args, **self._kwargs)
                
        def join(self, *args):
            Thread.join(self, *args)
            return self._return 