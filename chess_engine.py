import copy


class GameState:
    """
    This class is responsible for storing all the information about the current state of a chess game.
    It will also be responsible for determining the valid moves at the current state.
    It will also keep a move Log.
    """

    def __init__(self):
        # The Board is an 8x8 2D list.
        # Each piece consists of 2 characters, the first represents whether it's white or black,
        # while the second represents the type of the piece Empty spaces are marked as
        # "--" as it adds to the symmetry of the board
        # self.board = [
        #     ["bR", "bN", "bB", "bQ", "bK", "bB", "bN", "bR"],
        #     ["bP", "bP", "bP", "bP", "bP", "bP", "bP", "bP"],
        #     ["--", "--", "--", "--", "--", "--", "--", "--"],
        #     ["--", "--", "--", "--", "--", "--", "--", "--"],
        #     ["--", "--", "--", "--", "--", "--", "--", "--"],
        #     ["--", "--", "--", "--", "--", "--", "--", "--"],
        #     ["wP", "wP", "wP", "wP", "wP", "wP", "wP", "wP"],
        #     ["wR", "wN", "wB", "wQ", "wK", "wB", "wN", "wR"],
        # ]
        self.board = [
            ["bR", "bN", "bB", "bQ", "bK", "bB", "bN", "bR"],
            ["bP", "bP", "bP", "bP", "bP", "bP", "bP", "bP"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["wP", "wP", "wP", "wP", "wP", "wP", "wP", "wP"],
            ["wR", "wN", "wB", "wQ", "wK", "wB", "wN", "wR"],
        ]
        self.move_functions = {'P': self.get_pawn_moves, 'R': self.get_rook_moves,
                               'N': self.get_knight_moves, 'B': self.get_bishop_moves, 'Q': self.get_queen_moves,
                               'K': self.get_king_moves, }
        self.white_to_move = True
        self.move_log = []
        self.white_king_location = (7, 4)
        self.black_king_location = (0, 4)
        self.check_mate = False
        self.stale_mate = False
        self.enpassant_possible = ()  # Coordinates for the possible enpassant
        self.enpassant_log = [self.enpassant_possible]
        self.current_castling_right = CastleRights(True, True, True, True)
        self.castle_rights_log = [CastleRights(self.current_castling_right.wks,
                                               self.current_castling_right.bks, self.current_castling_right.wqs,
                                               self.current_castling_right.bqs)]

    def make_move(self, move):
        """
        Takes a move as a parameter and executes it (It won't work on castling and enpassant,
        and promotion)
        """
        self.board[move.start_row][move.start_col] = "--"
        self.board[move.end_row][move.end_col] = move.piece_moved
        self.move_log.append(move)  # Log the move to undo it later
        self.white_to_move = not self.white_to_move
        # Update the king's location
        if move.piece_moved == 'wK':
            self.white_king_location = (move.end_row, move.end_col)
        elif move.piece_moved == 'bK':
            self.black_king_location = (move.end_row, move.end_col)

        # Pawn promotion
        if move.is_pawn_promotion:
            self.board[move.end_row][move.end_col] = move.piece_moved[0] + 'Q'  # Color + Piece

        # Enpassant
        if move.is_enpassant_move:
            self.board[move.start_row][move.end_col] = '--'  # Capturing the pawn

        # Update enpassant_possible variable
        if move.piece_moved[1] == 'P' and abs(move.start_row - move.end_row) == 2:
            self.enpassant_possible = ((move.start_row + move.end_row) // 2, move.end_col)
        else:
            self.enpassant_possible = ()
        # Castle move
        if move.is_castle_move:
            if move.end_col - move.start_col == 2:  # King's side castle
                self.board[move.end_row][move.end_col - 1] = self.board[move.end_row][
                    move.end_col + 1]  # Copies the rook into its new square
                self.board[move.end_row][move.end_col + 1] = '--'  # Remove the rook from its position
            else:  # Queen's side castle
                self.board[move.end_row][move.end_col + 1] = self.board[move.end_row][
                    move.end_col - 2]  # Copies the rook into its new square
                self.board[move.end_row][move.end_col - 2] = '--'  # Remove the rook from its position

        # Update enpassant rights
        self.enpassant_log.append(self.enpassant_possible)
        # Update Castling Rights - whenever a rook or a king moves
        self.update_castle_rights(move)
        self.castle_rights_log.append(CastleRights(self.current_castling_right.wks,
                                                   self.current_castling_right.bks, self.current_castling_right.wqs,
                                                   self.current_castling_right.bqs))

    def undo_move(self):
        """
        Undo the last move
        """
        if self.move_log:  # Make sure there's at least one move played
            move = self.move_log.pop()
            self.board[move.start_row][move.start_col] = move.piece_moved
            self.board[move.end_row][move.end_col] = move.piece_captured
            self.white_to_move = not self.white_to_move
            # Update the king's location
            if move.piece_moved == 'wK':
                self.white_king_location = (move.start_row, move.start_col)
            elif move.piece_moved == 'bK':
                self.black_king_location = (move.start_row, move.start_col)
            # Undo enpassant move
            if move.is_enpassant_move:
                self.board[move.end_row][move.end_col] = '--'
                self.board[move.start_row][move.end_col] = move.piece_captured
            # Undo enpassant rights
            self.enpassant_log.pop()
            self.enpassant_possible = copy.deepcopy(self.enpassant_log[-1])
            # Undo castle rights
            self.castle_rights_log.pop()
            castle_rights = copy.deepcopy(self.castle_rights_log[-1])
            self.current_castling_right = castle_rights
            # Undo castle move
            if move.is_castle_move:
                if move.end_col - move.start_col == 2:  # King's side castle
                    self.board[move.end_row][move.end_col + 1] = self.board[move.end_row][
                        move.end_col - 1]  # Move the rook back to its position
                    self.board[move.end_row][move.end_col - 1] = '--'  # Empties the rook's square
                else:  # Queen's side castle
                    self.board[move.end_row][move.end_col - 2] = self.board[move.end_row][
                        move.end_col + 1]  # Move the rook back to its position
                    self.board[move.end_row][move.end_col + 1] = '--'  # Empties the rook's square
            self.check_mate = self.stale_mate = False

    def update_castle_rights(self, move):
        """
        Update castling rights based on king and rook moves
        """
        # King moves
        if move.piece_moved == 'wK':
            self.current_castling_right.wks = False
            self.current_castling_right.wqs = False
        elif move.piece_moved == 'bK':
            self.current_castling_right.bks = False
            self.current_castling_right.bqs = False
        # Rook moves
        elif move.piece_moved == 'wR':
            if move.start_row == 7:
                if move.start_col == 0:  # left rook
                    self.current_castling_right.wqs = False
                elif move.start_col == 7:  # right rook
                    self.current_castling_right.wks = False
        elif move.piece_moved == 'bR':
            if move.start_row == 0:
                if move.start_col == 0:  # left rook
                    self.current_castling_right.bqs = False
                elif move.start_col == 7:  # right rook
                    self.current_castling_right.bks = False
        # if a rook is captured
        if move.piece_captured == 'wR':
            if move.end_row == 7:
                if move.end_col == 0:
                    self.current_castling_right.wqs = False
                elif move.end_col == 7:
                    self.current_castling_right.wks = False
        elif move.piece_captured == 'bR':
            if move.end_row == 0:
                if move.end_col == 0:
                    self.current_castling_right.bqs = False
                elif move.end_col == 7:
                    self.current_castling_right.bks = False

    def get_valid_moves(self):
        """
        All moves considering checks
        """
        temp_enpassant_possible = self.enpassant_possible
        temp_castle_rights = CastleRights(self.current_castling_right.wks,
                                          self.current_castling_right.bks, self.current_castling_right.wqs,
                                          self.current_castling_right.bqs)  # Copy the current castling rights
        # 1- Generate all the moves
        moves = self.get_possible_moves()

        if self.white_to_move:
            self.get_castle_moves(self.white_king_location[0], self.white_king_location[1], moves)
        else:
            self.get_castle_moves(self.black_king_location[0], self.black_king_location[1], moves)
        # 2- for each move, make that move
        for i in range(len(moves) - 1, -1, -1):  # Remove from the list backwards
            self.make_move(moves[i])
            # 3- Generate all opponent moves and for each move check if
            # it attacks the king
            self.white_to_move = not self.white_to_move
            if self.in_check():
                # It's not a valid move as it attacks the king
                moves.remove(moves[i])
            self.white_to_move = not self.white_to_move
            self.undo_move()
        # Check for checkmate and stalemate
        if not moves:
            if self.in_check():
                self.check_mate = True
            else:
                self.stale_mate = True
        else:
            self.check_mate = self.check_mate = False  # For undo

        self.enpassant_possible = temp_enpassant_possible
        self.current_castling_right = temp_castle_rights
        return moves

    def in_check(self):
        """
        Determine if the current player is under check
        """
        return self.square_under_attack(self.white_king_location[0], self.white_king_location[1]) \
            if self.white_to_move else self.square_under_attack(self.black_king_location[0],
                                                                self.black_king_location[1])

    def square_under_attack(self, r, c):
        """
        Determine if the enemy can attack location (r,c)
        """
        self.white_to_move = not self.white_to_move  # Switch to opponent's turn
        opp_moves = self.get_possible_moves()
        self.white_to_move = not self.white_to_move  # SWitch turns back
        for move in opp_moves:
            if move.end_row == r and move.end_col == c:  # Swuare is under attack
                return True
        return False

    def get_possible_moves(self):
        """
        All moves not considering checks
        """
        moves = []
        # pylint: disable=locally-disabled, invalid-name
        for r, _ in enumerate(self.board):
            for c, _ in enumerate(self.board[r]):
                turn = self.board[r][c][0]
                if (turn == 'w' and self.white_to_move) or (turn == 'b' and not self.white_to_move):
                    piece = self.board[r][c][1]
                    self.move_functions[piece](r, c, moves)
        return moves

    # pylint: disable=locally-disabled, invalid-name
    def get_pawn_moves(self, r, c, moves):
        """
        Get all possible moves for the pawn located at (r, w) and add them the list of all
        possible moves
        """
        if self.white_to_move:  # White pawn moves
            if self.board[r - 1][c] == "--":  # 1 square pawn advance
                moves.append(Move((r, c), (r - 1, c), self.board))
                if r == 6 and self.board[r - 2][c] == "--":  # 2 square pawn advance
                    moves.append(Move((r, c), (r - 2, c), self.board))
            if c - 1 >= 0:  # Captures to the left
                if self.board[r - 1][c - 1][0] == 'b':
                    moves.append(Move((r, c), (r - 1, c - 1), self.board))
                elif (r - 1, c - 1) == self.enpassant_possible:
                    moves.append(Move((r, c), (r - 1, c - 1), self.board,
                                      is_enpassant_move=True))  # Setting the optional parameter
            if c + 1 <= 7:  # Captures to the left
                if self.board[r - 1][c + 1][0] == 'b':
                    moves.append(Move((r, c), (r - 1, c + 1), self.board))
                elif (r - 1, c + 1) == self.enpassant_possible:
                    moves.append(Move((r, c), (r - 1, c + 1), self.board,
                                      is_enpassant_move=True))  # Setting the optional parameter

        if not self.white_to_move:  # Black pawn moves
            if self.board[r + 1][c] == "--":  # 1 square pawn advance
                moves.append(Move((r, c), (r + 1, c), self.board))
                if r == 1 and self.board[r + 2][c] == "--":  # 2 square pawn advance
                    moves.append(Move((r, c), (r + 2, c), self.board))
            if c - 1 >= 0:  # Captures to the left
                if self.board[r + 1][c - 1][0] == 'w':
                    moves.append(Move((r, c), (r + 1, c - 1), self.board))
                elif (r + 1, c - 1) == self.enpassant_possible:
                    moves.append(Move((r, c), (r + 1, c - 1), self.board,
                                      is_enpassant_move=True))  # Setting the optional parameter

            if c + 1 <= 7:  # Captures to the left
                if self.board[r + 1][c + 1][0] == 'w':
                    moves.append(Move((r, c), (r + 1, c + 1), self.board))
                elif (r + 1, c + 1) == self.enpassant_possible:
                    moves.append(Move((r, c), (r + 1, c + 1), self.board,
                                      is_enpassant_move=True))  # Setting the optional parameter

    # pylint: disable=locally-disabled, invalid-name
    def get_rook_moves(self, r, c, moves):
        """
        Get all possible moves for the rock located at (r, w) and add them the list of all
        possible moves
        """
        top = right = down = left = True
        for i in range(1, 8):
            if top and r - i >= 0:  # There were no obstacles top or end of the board
                if self.board[r - i][c] == '--':
                    moves.append(Move((r, c), (r - i, c), self.board))
                elif self.board[r - i][c][0] != self.board[r][c][0]:  # If it's an enemy piece
                    # Capture it and don't look for movre moves
                    moves.append(Move((r, c), (r - i, c), self.board))
                    top = False
                else:
                    top = False
            if right and c + i <= 7:
                if self.board[r][c + i] == '--':
                    moves.append(Move((r, c), (r, c + i), self.board))
                elif self.board[r][c + i][0] != self.board[r][c][0]:  # If it's an enemy piece
                    moves.append(Move((r, c), (r, c + i), self.board))
                    right = False
                else:
                    right = False
            if down and r + i <= 7:
                if self.board[r + i][c] == '--':
                    moves.append(Move((r, c), (r + i, c), self.board))
                elif self.board[r + i][c][0] != self.board[r][c][0]:  # If it's an enemy piece
                    # Capture it and don't look for movre moves
                    moves.append(Move((r, c), (r + i, c), self.board))
                    down = False
                else:
                    down = False
            if left and c - i >= 0:
                if self.board[r][c - i] == '--':
                    moves.append(Move((r, c), (r, c - i), self.board))
                elif self.board[r][c - i][0] != self.board[r][c][0]:  # If it's an enemy piece
                    moves.append(Move((r, c), (r, c - i), self.board))
                    left = False
                else:
                    left = False

    def get_knight_moves(self, r, c, moves):
        """
        Get all possible moves for the knight located at (r, w) and add them the list of all
        possible moves
        """
        if r - 2 >= 0 and c + 1 <= 7:  # There were no obstacles top or end of the board
            if self.board[r - 2][c + 1][0] != self.board[r][c][0]:  # If it's an enemy piece pr empty
                # Capture it and don't look for movre moves
                moves.append(Move((r, c), (r - 2, c + 1), self.board))
        if c + 2 <= 7 and r - 1 >= 0:
            if self.board[r - 1][c + 2][0] != self.board[r][c][0]:  # If it's an enemy piece pr empty
                moves.append(Move((r, c), (r - 1, c + 2), self.board))
        if c + 2 <= 7 and r + 1 <= 7:
            if self.board[r + 1][c + 2][0] != self.board[r][c][0]:  # If it's an enemy piece pr empty
                # Capture it and don't look for movre moves
                moves.append(Move((r, c), (r + 1, c + 2), self.board))
        if c + 1 <= 7 and r + 2 <= 7:
            if self.board[r + 2][c + 1][0] != self.board[r][c][0]:  # If it's an enemy piece pr empty
                moves.append(Move((r, c), (r + 2, c + 1), self.board))
        if r + 2 <= 7 and c - 1 >= 0:  # There were no obstacles top or end of the board
            if self.board[r + 2][c - 1][0] != self.board[r][c][0]:  # If it's an enemy piece
                # Capture it and don't look for movre moves
                moves.append(Move((r, c), (r + 2, c - 1), self.board))
        if c - 2 >= 0 and r + 1 <= 7:
            if self.board[r + 1][c - 2][0] != self.board[r][c][0]:  # If it's an enemy piece
                moves.append(Move((r, c), (r + 1, c - 2), self.board))
        if r - 1 >= 0 and c - 2 >= 0:
            if self.board[r - 1][c - 2][0] != self.board[r][c][0]:  # If it's an enemy piece
                # Capture it and don't look for movre moves
                moves.append(Move((r, c), (r - 1, c - 2), self.board))
        if c - 1 >= 0 and r - 2 >= 0:
            if self.board[r - 2][c - 1][0] != self.board[r][c][0]:  # If it's an enemy piece
                moves.append(Move((r, c), (r - 2, c - 1), self.board))

    def get_bishop_moves(self, r, c, moves):
        """
        Get all possible moves for the bishop located at (r, w) and add them the list of all
        possible moves
        """
        top_right = down_right = down_left = top_left = True
        for i in range(1, 8):
            if top_right and r - i >= 0 and c + i <= 7:  # There were no obstacles top or end of the board
                if self.board[r - i][c + i] == '--':
                    moves.append(Move((r, c), (r - i, c + i), self.board))
                elif self.board[r - i][c + i][0] != self.board[r][c][0]:  # If it's an enemy piece
                    # Capture it and don't look for movre moves
                    moves.append(Move((r, c), (r - i, c + i), self.board))
                    top_right = False
                else:
                    top_right = False
            if down_right and c + i <= 7 and r + i <= 7:
                if self.board[r + i][c + i] == '--':
                    moves.append(Move((r, c), (r + i, c + i), self.board))
                elif self.board[r + i][c + i][0] != self.board[r][c][0]:  # If it's an enemy piece
                    moves.append(Move((r, c), (r + i, c + i), self.board))
                    down_right = False
                else:
                    down_right = False
            if down_left and r + i <= 7 and c - i >= 0:
                if self.board[r + i][c - i] == '--':
                    moves.append(Move((r, c), (r + i, c - i), self.board))
                elif self.board[r + i][c - i][0] != self.board[r][c][0]:  # If it's an enemy piece
                    # Capture it and don't look for movre moves
                    moves.append(Move((r, c), (r + i, c - i), self.board))
                    down_left = False
                else:
                    down_left = False
            if top_left and c - i >= 0 and r - i >= 0:
                if self.board[r - i][c - i] == '--':
                    moves.append(Move((r, c), (r - i, c - i), self.board))
                elif self.board[r - i][c - i][0] != self.board[r][c][0]:  # If it's an enemy piece
                    moves.append(Move((r, c), (r - i, c - i), self.board))
                    top_left = False
                else:
                    top_left = False

    def get_queen_moves(self, r, c, moves):
        """
        Get all possible moves for the queen located at (r, w) and add them the list of all
        possible moves
        """
        self.get_rook_moves(r, c, moves)
        self.get_bishop_moves(r, c, moves)

    def get_king_moves(self, r, c, moves):
        """
        Get all possible moves for the king located at (r, w) and add them the list of all
        possible moves
        """
        i = 1
        if r - i >= 0:  # There were no obstacles top or end of the board
            if self.board[r - i][c][0] != self.board[r][c][0]:  # If it's an enemy piece pr empty
                # Capture it and don't look for movre moves
                moves.append(Move((r, c), (r - i, c), self.board))
        if c + i <= 7:
            if self.board[r][c + i][0] != self.board[r][c][0]:  # If it's an enemy piece pr empty
                moves.append(Move((r, c), (r, c + i), self.board))
        if r + i <= 7:
            if self.board[r + i][c][0] != self.board[r][c][0]:  # If it's an enemy piece pr empty
                # Capture it and don't look for movre moves
                moves.append(Move((r, c), (r + i, c), self.board))
        if c - i >= 0:
            if self.board[r][c - i][0] != self.board[r][c][0]:  # If it's an enemy piece pr empty
                moves.append(Move((r, c), (r, c - i), self.board))
        if r - i >= 0 and c + i <= 7:  # There were no obstacles top or end of the board
            if self.board[r - i][c + i][0] != self.board[r][c][0]:  # If it's an enemy piece
                # Capture it and don't look for movre moves
                moves.append(Move((r, c), (r - i, c + i), self.board))
        if c + i <= 7 and r + i <= 7:
            if self.board[r + i][c + i][0] != self.board[r][c][0]:  # If it's an enemy piece
                moves.append(Move((r, c), (r + i, c + i), self.board))
        if r + i <= 7 and c - i >= 0:
            if self.board[r + i][c - i][0] != self.board[r][c][0]:  # If it's an enemy piece
                # Capture it and don't look for movre moves
                moves.append(Move((r, c), (r + i, c - i), self.board))
        if c - i >= 0 and r - i >= 0:
            if self.board[r - i][c - i][0] != self.board[r][c][0]:  # If it's an enemy piece
                moves.append(Move((r, c), (r - i, c - i), self.board))

    def get_castle_moves(self, r, c, moves):
        """
        Get all valid castle moves for the king at (r,c) and add them to the list of moves
        """
        if self.square_under_attack(r, c):
            return  # Can't castle in check
        if self.white_to_move and self.current_castling_right.wks or (
                not self.white_to_move) and self.current_castling_right.bks:
            self.get_king_side_castle_moves(r, c, moves)
        if self.white_to_move and self.current_castling_right.wqs or (
                not self.white_to_move) and self.current_castling_right.bqs:
            self.get_queen_side_castle_moves(r, c, moves)

    def get_king_side_castle_moves(self, r, c, moves):
        """
        Helper function to check the king's side castling
        """
        if self.board[r][c + 1] == '--' and self.board[r][c + 2] == '--':  # Check that the in-between squares are empty
            if not self.square_under_attack(r, c + 1) and not self.square_under_attack(r, c + 2):
                moves.append(Move((r, c), (r, c + 2), self.board, is_castle_move=True))

    def get_queen_side_castle_moves(self, r, c, moves):
        """
        Helper function to check the queen's side castling
        """
        if self.board[r][c - 1] == '--' and self.board[r][c - 2] == '--' and self.board[r][c - 3] == '--':
            # Check that the in-between squares are empty
            if not self.square_under_attack(r, c - 1) and not self.square_under_attack(r, c - 2):
                moves.append(Move((r, c), (r, c - 2), self.board, is_castle_move=True))


class CastleRights:
    """
    Keeps track of whether a player can castle, and which side
    """

    def __init__(self, wks, bks, wqs, bqs):
        self.wks = wks
        self.bks = bks
        self.wqs = wqs
        self.bqs = bqs


class Move:
    """
    Stores all information related to a move, such as rows, columns, and pieces
    """
    # maps keys to values for chess notation
    ranks_to_rows = {"8": 0, "7": 1, "6": 2, "5": 3,
                     "4": 4, "3": 5, "2": 6, "1": 7}
    rows_to_ranks = {v: k for k, v in ranks_to_rows.items()}
    files_to_cols = {"a": 0, "b": 1, "c": 2, "d": 3,
                     "e": 4, "f": 5, "g": 6, "h": 7}
    cols_to_files = {v: k for k, v in files_to_cols.items()}

    def __init__(self, start_sq, end_sq, board, is_enpassant_move=False, is_castle_move=False):
        self.start_row = start_sq[0]
        self.start_col = start_sq[1]
        self.end_row = end_sq[0]
        self.end_col = end_sq[1]
        self.piece_moved = board[self.start_row][self.start_col]
        self.piece_captured = board[self.end_row][self.end_col]
        # Pawn promotion
        self.is_pawn_promotion = (self.piece_moved == 'wP' and self.end_row == 0) or (
                self.piece_moved == 'bP' and self.end_row == 7)
        # Enpassant
        self.is_enpassant_move = is_enpassant_move
        if self.is_enpassant_move:
            self.piece_captured = 'wP' if self.piece_moved == 'bP' else 'bP'
        # Castle move
        self.is_castle_move = is_castle_move
        # Capture move
        self.is_capture_move = self.piece_captured != "--"
        # Unique id for each move
        self.move_id = self.start_row * 1000 + self.start_col * 100 + self.end_row * 10 + self.end_col

    def __eq__(self, other):
        """
        Overriding the equals method
        """
        if isinstance(other, Move):
            return self.move_id == other.move_id
        return False

    def __str__(self):
        """
        Overriding the str function
        """
        return (self.cols_to_files[self.start_col] + self.rows_to_ranks[self.start_row] + self.cols_to_files[
            self.end_col] + self.rows_to_ranks[self.end_row])

    def get_chess_notation(self):
        return self.get_rank_file(self.start_row, self.start_col) + self.get_rank_file(self.end_row, self.end_col)

    def get_rank_file(self, r, c):
        return self.cols_to_files[c] + self.rows_to_ranks[r]
