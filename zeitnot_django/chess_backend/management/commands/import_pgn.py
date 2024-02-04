from django.core import management
from django.core.management.base import BaseCommand, CommandError

import chess.pgn

from chess_backend.models import Author, Comment, Position, Player, PlayerStats, Move, Game

import time

class Command(BaseCommand):
    help = 'Load data from pgn file into games DB, currently not perfomring fast enought to import games, even with only chess.pgn commands to slow to handle millions of games for import'

    def add_arguments(self, parser):
        parser.add_argument('pgn_file', type=str)

    def handle(self, *args, **options):
        players = {}
        
        player_stats = {}
        connected_moves = []

        positions = {}

        db_moves = []
        games = []
        game_moves_through = []

        pgn_file = open(options['pgn_file'])
        game = chess.pgn.read_game(pgn_file)
        i=0
        print("start reading games")
        t=time.process_time_ns()
        while game:
            game_date = game.headers["Date"].replace(".","-")
            white_name = game.headers["White"]
            white_fide_id = game.headers.get("WhiteFideId","")
            white_player_key = white_name+white_fide_id
            if(white_player_key in players):
                db_white = players[white_player_key]
            else:
                db_white = Player(name=white_name, fideID=white_fide_id)
                players[white_player_key]=db_white
            
            white_ps_key = white_fide_id+game_date
            if(white_ps_key not in player_stats):
                player_stats[white_ps_key] = PlayerStats(
                    date = game_date,
                    rating = game.headers.get("WhiteElo", None),
                    title = game.headers.get("WhiteTitle", ""),
                    player = db_white
                )
            black_name = game.headers["Black"]
            black_fide_id = game.headers.get("BlackFideId", "")
            black_player_key = black_name+black_fide_id
            if(black_player_key in players):
                db_black = players[black_player_key]
            else:
                db_black = Player(name=black_name, fideID=black_fide_id)
                players[black_player_key]=db_black
            
            black_ps_key = white_fide_id+game_date
            if(black_ps_key not in player_stats):
                player_stats[black_ps_key] = PlayerStats(
                    date = game_date,
                    rating = game.headers.get("BlackElo", None),
                    title = game.headers.get("BlackTitle", ""),
                    player = db_black
                )


            board = game.board()
            moves = game.mainline_moves()
            prev_move=None
            game_moves = []
            for move in moves:
                san = board.san(move)
                board.push(move)
                fen = board.fen()
                if(fen in positions):
                    db_position = positions[fen]
                else:
                    db_position = Position(
                        fen = fen,
                        cp = None,
                        depth = None
                    )
                    positions[fen] = db_position
                m1 = Move(
                    curent_position = db_position,
                    next_move = None,
                    san = san
                )
                if(prev_move):
                    connected_moves.append((prev_move,m1))
                prev_move = m1
                game_moves.append(prev_move)
                db_moves.append(prev_move)

            db_game = Game(
                date = game_date,
                white = db_white,
                black = db_black
            )
            games.append(db_game)
            for m in game_moves:
                game_move_through = Game.moves.through(
                    game=db_game,
                    move=m
                )
                game_moves_through.append(game_move_through)

            i+=1
            if(i%10000 == 0):
                print(i)
            #if(i >= 100000):
            #    break
                
            game = chess.pgn.read_game(pgn_file)
        print(i)
        
        Player.objects.bulk_create(players.values(), batch_size=10000)
        PlayerStats.objects.bulk_create(player_stats.values(), batch_size=10000)
        Position.objects.bulk_create(positions.values(), batch_size=10000)
        Move.objects.bulk_create(db_moves, batch_size=10000)
        for m1,m2 in connected_moves:
            m1.next_move=m2
        Move.objects.bulk_update(db_moves, ["next_move", ], batch_size=10000)
        Game.objects.bulk_create(games, batch_size=10000)
        Game.moves.through.objects.bulk_create(game_moves_through, batch_size=10000)
        print(str(round((time.process_time_ns()-t)/1000000000,2)) + " sec")
        pgn_file.close()
