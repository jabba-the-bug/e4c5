import sqlite3
import time

'''
start of faster PGN import for python
Still needs to check if a piece is pinned when deciding what to move
not super fast yet but a good start

idea is to eliminate checking for validity of moves and trade with more speed

'''

class Game():
    def __init__(self):
        self.squares = [
            ["R", "N", "B", "Q", "K", "B", "N", "R"],
            ["P", "P", "P", "P", "P", "P", "P", "P"],
            ["", "", "", "", "", "", "", ""],
            ["", "", "", "", "", "", "", ""],
            ["", "", "", "", "", "", "", ""],
            ["", "", "", "", "", "", "", ""],
            ["p", "p", "p", "p", "p", "p", "p", "p"],
            ["r", "n", "b", "q", "k", "b", "n", "r"],
        ]

        self.white_move = True

        self.castle_rights = "KQkq"
        self.en_passant_square = None
        self.half_moves = 0
        self.full_moves = 1

        self.PIECES = {"R":self.rookMove, "N":self.knightMove, "B": self.bishopMove, "Q": self.queenMove, "K": self.kingMove}
        self.move_history = []

    def castles(self, to_sq, from_sq=None):
        self.move_history.append((to_sq, self.white_move))

        king = ((0,4), (0,6))
        rook = ((0,7), (0,5))
        if(to_sq == "O-O" and not self.white_move):
            king = ((7,4), (7,6))
            rook = ((7,7), (7,5))
        elif(to_sq == "O-O-O"):
            if(self.white_move):
                king = ((0,4), (0,2))
                rook = ((0,0), (0,3))
            else:
                king = ((7,4), (7,2))
                rook = ((7,0), (7,3))
        
        if(self.white_move):
            self.squares[king[1][0]][king[1][1]] = "K"
            self.squares[king[0][0]][king[0][1]] = ""

            self.squares[rook[1][0]][rook[1][1]] = "R"
            self.squares[rook[0][0]][rook[0][1]] = ""
        else:
            self.squares[king[1][0]][king[1][1]] = "k"
            self.squares[king[0][0]][king[0][1]] = ""

            self.squares[rook[1][0]][rook[1][1]] = "r"
            self.squares[rook[0][0]][rook[0][1]] = ""

        if(not self.white_move):
            self.full_moves += 1
        self.white_move = not self.white_move
    
    def pawnMove(self, to_sq, from_sq=None):
        piece = "p"
        if(self.white_move):
            piece="P"

        direction = +1
        if(self.white_move):
            direction = -1

        if(from_sq):
            new_from_sq = (to_sq[0]+direction, from_sq[1])
        else:
            new_from_sq = (to_sq[0]+direction, to_sq[1])
            p = self.getPiece(new_from_sq)
            if(p != piece):
                new_from_sq = (new_from_sq[0]+direction, to_sq[1])
            
        return new_from_sq, to_sq, piece

    def knightMove(self, to_sq, from_sq=None):
        piece = "n"
        if(self.white_move):
            piece = "N"

        check_list = (
            [to_sq[0]+1,to_sq[1]+2],
            [to_sq[0]-1,to_sq[1]-2],
            [to_sq[0]+1,to_sq[1]-2],
            [to_sq[0]-1,to_sq[1]+2],
            [to_sq[0]+2,to_sq[1]+1],
            [to_sq[0]-2,to_sq[1]-1],
            [to_sq[0]+2,to_sq[1]-1],
            [to_sq[0]-2,to_sq[1]+1]  
        )
        if(from_sq):
            new_mods = []
            if(from_sq[0] is not None):
                for m in check_list:
                    if(m[0] == from_sq[0]):
                        new_mods.append(m)
            else:
                for m in check_list:
                    if(m[1] == from_sq[1]):
                        new_mods.append(m)
            check_list = new_mods
        for m in check_list:
            p = self.getPiece(m)

            if(p == piece):
                return m, to_sq, piece

    
    def kingMove(self, to_sq, from_sq=None):
        piece = "k"
        if(self.white_move):
            piece = "K"

        dirs = ("n", "ne", "e", "se", "s", "sw", "w", "nw")
        for dir in dirs:
            looking_at_sq = self.nextSquare(to_sq, dir)
            p = self.getPiece(looking_at_sq)
            if(p == piece):
                return looking_at_sq, to_sq, piece

    def bishopMove(self, to_sq, from_sq=None):
        piece = "b"
        if(self.white_move):
            piece = "B"
        
        dirs = ("ne", "se", "nw", "sw", "nw")
        for dir in dirs:
            new_from_sq = to_sq
            for _ in range(0, 8):
                new_from_sq = self.nextSquare(new_from_sq, dir, from_sq)
                p = self.getPiece(new_from_sq)
                if(p == piece):
                    return new_from_sq, to_sq, piece
                elif(p != ""):
                    break

    def rookMove(self, to_sq, from_sq=None):
        piece = "r"
        if(self.white_move):
            piece = "R"

        dirs = ("n", "e", "s", "w")
        
        for dir in dirs:
            new_from_sq = to_sq
            for _ in range(0, 8):
                new_from_sq = self.nextSquare(new_from_sq, dir, from_sq)
                
                p = self.getPiece(new_from_sq)
                if(p == piece):
                    return new_from_sq, to_sq, piece
                elif(p != ""):
                    break

    def queenMove(self, to_sq, from_sq=None):
        piece = "q"
        if(self.white_move):
            piece = "Q"
        
        dirs = ("n", "ne", "e", "se", "s", "sw", "w", "nw")
        for dir in dirs:
            new_from_sq = to_sq
            for _ in range(0, 8):
                new_from_sq = self.nextSquare(new_from_sq, dir, from_sq)
                p = self.getPiece(new_from_sq)
                if(p == piece):
                    return new_from_sq, to_sq, piece
                elif(p != ""):
                    break


    def lToNum(self, l):
        cords = ["a", "b", "c", "d", "e", "f", "g", "h"]
        if(l in cords):
            return cords.index(l)
        else:
            return -99
        
    def numToL(self, num):
        cords = ["a", "b", "c", "d", "e", "f", "g", "h"]
        if(num >= 0 and num < 8):
            return cords[num]
        else:
            return "z"

    def getPiece(self, sq):
        row=sq[0]
        col=sq[1]
        if(row >= 0 and row < 8 and col >= 0 and col < 8):
            return self.squares[row][col]
        return ""
    
    def nextSquare(self, sq, direction, from_sq=None):
        new_row = sq[0]
        new_col = sq[1]
        if("n" in direction):
            new_row+=1
        if("e" in direction):
            new_col+=1
        if("s" in direction):
            new_row-=1
        if("w" in direction):
            new_col-=1

        if(from_sq):
            if(from_sq[0] is not None):
                new_row = from_sq[0]
            else:
                new_col = from_sq[1]
        
        return (new_row, new_col)
    
    def fen(self):
        position_fen = ""
        for row in reversed(self.squares):
            skipped=0
            for p in row:
                if(p):
                    if(skipped>0):
                        position_fen+=str(skipped)
                        skipped=0
                    position_fen+=p
                else:
                    skipped += 1
            if(skipped>0):
                position_fen+=str(skipped)
            position_fen+="/"
        position_fen = position_fen[:-1]

        en_passant_square = "-"
        if(self.en_passant_square is not None):
            en_passant_square = self.numToL(self.en_passant_square[1]) + str(self.en_passant_square[0]+1)

        #return " ".join([self.fen, self.position, self.castles, self.en_passant_square, str(self.half_moves), str(self.full_moves)])
        return position_fen + " " + self.castle_rights + " " + en_passant_square + " " + str(self.half_moves) + " " + str(self.full_moves)

    def move(self, from_square, to_square, piece, promotes=None):
        if(not self.white_move):
            self.full_moves += 1
        
        #taken_piece = self.squares[to_square[0]][to_square[1]]
        self.squares[from_square[0]][from_square[1]] = ""
        if(promotes is not None):
            self.squares[to_square[0]][to_square[1]] = promotes
        else:
            self.squares[to_square[0]][to_square[1]] = piece

        if(piece == "P" or piece == "p"):
            if(self.en_passant_square is not None):
                if(self.white_move):
                    if(to_square[0] == self.en_passant_square[0] and to_square[1] == self.en_passant_square[1]):
                        self.squares[self.en_passant_square[0]-1][self.en_passant_square[1]] = ""
                else:
                    if(to_square[0] == self.en_passant_square[0] and to_square[1] == self.en_passant_square[1]):
                        self.squares[self.en_passant_square[0]+1][self.en_passant_square[1]] = ""

            if(abs(from_square[0] - to_square[0]) == 2):
                if(self.white_move):
                    self.en_passant_square = (to_square[0]-1, to_square[1])
                else:
                    self.en_passant_square = (to_square[0]+1, to_square[1])
            else:
                self.en_passant_square  = None
        else:
            self.en_passant_square  = None

        self.move_history.append((from_square,to_square, self.white_move))
        self.white_move = not self.white_move
    
    def makeMove(self, notation):
        promotes = None
        from_n=None
        piece="P"
        if("#" in notation or "+" in notation):
            notation = notation[:-1]
        if("O-O" == notation or "O-O-O" == notation):
            self.castles(notation)
            return
        if("=" in notation):
            promotes = notation[-1]
            if(not self.white_move):
                promotes = promotes.lower()
            notation = notation[:-2]
        if(notation[0] in self.PIECES):
            piece = notation[0]
            notation = notation[1:]
        else: 
            piece = "P"
        if("x" in notation):
            from_n, to_n = notation.split("x")
        else:
            len_n = len(notation)
            
            if(len_n == 2):
                to_n = notation
            elif(len_n == 3):
                from_n = notation[0]
                to_n = notation[1:]
            elif(len_n == 4):
                from_n = notation[:2]
                to_n = notation[2:4]
                if(not self.white_move):
                    piece=piece.lower()

        to_row = int(to_n[1])-1
        to_col = self.lToNum(to_n[0])

        from_row = None
        from_col = None 
        if(from_n):
            if(from_n.isdigit()):
                from_row = int(from_n)-1
            else:
                from_col = self.lToNum(from_n)
        
        if(piece in self.PIECES):
            if(from_n):
                from_n, to_n, piece = self.PIECES[piece]((to_row, to_col), from_sq=(from_row, from_col))
            else:
                from_n, to_n, piece = self.PIECES[piece]((to_row, to_col))
        else:
            #Pawn move
            self.half_moves = 0
            if(from_n):
                from_n, to_n, piece = self.pawnMove((to_row, to_col), from_sq=(from_row, from_col))
            else:
                from_n, to_n, piece = self.pawnMove((to_row, to_col))

            

        self.move(from_n, to_n, piece, promotes)

def handle_game(game_str):
    result_str = game_str[:-3] 
    result = 1
    result_length=4
    if("/" in result_str):
        result = 0
        result_length=9
    elif("0-1" == result_str):
        result = -1
    

    headers = {}
    c=0
    game = Game()
    for l in game_str.split("\n"):
        
        if(l[0] == "["):
            split = l[1:].split(" \"")
            k = split[0]
            v = split[1][:-2]
            headers[k] = v
        else:
            
            for m in game_str[c:-result_length].replace("\n","").split(" ")[:-1]:
                if("." in m):
                    m = m.split(".")[1]
                try:
                    game.makeMove(m)
                except Exception as e:
                    #print("https://lichess.org/analysis/standard/" + game.fen().replace(" ", "_"))
                    #print(game_str[c:-result_length])
                    #raise e
                    break
            break
        c+=len(l)+1
    return result, headers, game.fen()

def main():
    con = sqlite3.connect("db.sqlite3")
    cur = con.cursor()

    pgn_file = open("games.pgn")
    games = []
    line_break_c = 0
    pgn_str = ""
    
    t=time.process_time_ns()
    print("Running import")
    for line in pgn_file.readlines():
        if(line == "\n"):
            line_break_c += 1
        else:
            if(line[-2] not in (" ", ".", "]") and line != "\n"):
                line += " "
            pgn_str += line
        if(line_break_c == 2):
            line_break_c=0
            with open("temp.pgn", "w+") as f:
                f.write(pgn_str)
            games.append(handle_game(pgn_str))
            pgn_str = ""
            if(len(games) % 100 == 0):
                print(len(games))
                print(str(round((time.process_time_ns()-t)/100000000,2)) + " sec")

    print(len(games))

    

    pgn_file.close()

def create_smaller_file():
    pgn_file = open("games.pgn")
    line_break_c = 0
    pgn_str = ""
    
    with open("less_games.pgn", "w+") as f: 
        for line in pgn_file.readlines():
            pgn_str += line
            if(line == "\n"):
                line_break_c += 1

            if(line_break_c / 2 == 1000):
                break
        f.write(pgn_str)
main()
#create_smaller_file()