import random

DEPTH = 2

# Scoring each piece
piece_score = {'K': 0, 'Q': 10, 'R': 5, 'B': 3, 'N': 3,
               'P': 1}  # King's values doesn't matter since no way to capture it,

# Positional chess
# A knight is worth more in the middle since it can have more moves
knight_scores = [
    [1, 1, 1, 1, 1, 1, 1, 1],
    [1, 2, 2, 2, 2, 2, 2, 1],
    [1, 2, 3, 3, 3, 3, 2, 1],
    [1, 2, 3, 4, 4, 3, 2, 1],
    [1, 2, 3, 4, 4, 3, 2, 1],
    [1, 2, 3, 3, 3, 3, 2, 1],
    [1, 2, 2, 2, 2, 2, 2, 1],
    [1, 1, 1, 1, 1, 1, 1, 1]
]

# A bishop is worth more on diagonally longer parts of the board since it allows for more moves
bishop_scores = [
    [4, 3, 2, 1, 1, 2, 3, 4],
    [3, 4, 3, 2, 2, 3, 4, 3],
    [2, 3, 4, 3, 3, 4, 3, 2],
    [1, 2, 3, 4, 4, 3, 2, 1],
    [1, 2, 3, 4, 4, 3, 2, 1],
    [2, 3, 4, 3, 3, 4, 3, 2],
    [3, 4, 3, 2, 2, 3, 4, 3],
    [4, 3, 2, 1, 1, 2, 3, 4]
]
# A queen is worth more in the middle since it can protect more pieces and move more
queen_scores = [
    [1, 1, 1, 3, 1, 1, 1, 1],
    [1, 2, 3, 3, 3, 1, 1, 1],
    [1, 4, 3, 3, 3, 4, 2, 1],
    [1, 2, 3, 3, 3, 2, 2, 1],
    [1, 2, 3, 3, 3, 2, 2, 1],
    [1, 4, 3, 3, 3, 4, 2, 1],
    [1, 2, 3, 3, 3, 1, 1, 1],
    [1, 1, 1, 3, 1, 1, 1, 1]
]

# Rooks are worth more either in centers, or in the first and second ranks to target more pawns
rook_scores = [
    [4, 3, 4, 4, 4, 4, 3, 4],
    [4, 4, 4, 4, 4, 4, 4, 4],
    [1, 1, 2, 3, 3, 2, 1, 1],
    [1, 2, 3, 4, 4, 3, 2, 1],
    [1, 2, 3, 4, 4, 3, 2, 1],
    [1, 1, 2, 3, 3, 2, 1, 1],
    [4, 4, 4, 4, 4, 4, 4, 4],
    [4, 3, 4, 4, 4, 4, 3, 4]
]
# The pawns of both colors are the same, but flipped. the center pawns are always
# better further in the center, while all pawns should always advance, so they can promote
white_pawn_scores = [
    [10, 10, 10, 10, 10, 10, 10, 10],
    [8, 8, 8, 8, 8, 8, 8, 8],
    [5, 6, 6, 7, 7, 6, 6, 5],
    [2, 3, 3, 5, 5, 3, 3, 2],
    [1, 2, 3, 4, 4, 3, 2, 1],
    [1, 1, 2, 3, 3, 2, 1, 1],
    [1, 1, 1, 0, 0, 1, 1, 1],
    [0, 0, 0, 0, 0, 0, 0, 0],
]
black_pawn_scores = [
    [0, 0, 0, 0, 0, 0, 0, 0],
    [1, 1, 1, 0, 0, 1, 1, 1],
    [1, 1, 2, 3, 3, 2, 1, 1],
    [2, 3, 3, 5, 5, 3, 3, 2],
    [5, 6, 6, 7, 7, 6, 6, 5],
    [8, 8, 8, 8, 8, 8, 8, 8],
    [10, 10, 10, 10, 10, 10, 10, 10],
]

piece_position_scores = {"N": knight_scores, "B": bishop_scores, "Q": queen_scores,
                         "R": rook_scores, "bP": black_pawn_scores, "wP": white_pawn_scores}
CHECKMATE = 1000  # Checkmate is the most important
STALEMATE = 0  # Stalemate is better than a losing position

# Counters for testing and benchmarking
random_ai_counter = 0
greedy_ai_counter = 0
minimax_iterative_ai_counter = 0
minimax_recursive_ai_counter = 0
negamax_ai_counter = 0
negamax_alphabeta_ai_counter = 0


def find_random_move(valid_moves):
    """
    This function just returns one valid move at random
    """
    global random_ai_counter
    random_ai_counter += 1
    return valid_moves[random.randint(0, len(valid_moves) - 1)]


def find_greedy_move(gs, valid_moves):
    """
    This function uses a greedy algorithms to return a move that gives the current player the highest score based only
    on one move ahead.
    """
    global greedy_ai_counter
    turn_multiplier = 1 if gs.white_to_move else -1  # 1 if white to move, otherwise -1, for zero-sum game
    max_score = -CHECKMATE
    best_move = None
    random.shuffle(valid_moves)  # Prevents the agent from being predictable when multiple moves have same score
    for player_move in valid_moves:
        greedy_ai_counter += 1
        gs.make_move(player_move)
        if gs.check_mate:
            score = CHECKMATE
        elif gs.stale_mate:
            score = STALEMATE
        else:
            score = turn_multiplier * score_board(gs)
        if score > max_score:
            max_score = score
            best_move = player_move
        gs.undo_move()
    return best_move


def find_minimax_move_iteratively(gs, valid_moves):
    """
    This function uses minimax algorithm iteratively to return the best move by looking 2 moves ahead.
    This essentially now gives the AI agent the ability to checkmate better and think about trading pieces
    """
    global minimax_iterative_ai_counter
    turn_multiplier = 1 if gs.white_to_move else -1  # 1 if white to move, otherwise -1, for zero-sum game
    opponent_minimax_score = CHECKMATE  # I want to minimize this score
    best_player_move = None
    random.shuffle(valid_moves)  # Prevents the agent from being predictable when multiple moves have same score
    for player_move in valid_moves:
        gs.make_move(player_move)
        # Finding best move for opponent
        opponent_moves = gs.get_valid_moves()
        # If the player is in stalemate or checkmate, there's no need to check the opponent's moves
        if gs.check_mate:
            opponent_max_score = -CHECKMATE
        elif gs.stale_mate:
            opponent_max_score = STALEMATE
        else:
            opponent_max_score = -CHECKMATE  # Maximize this score-this will be the ideal move for the opponent
            for opponent_move in opponent_moves:
                minimax_iterative_ai_counter += 1
                gs.make_move(opponent_move)
                gs.get_valid_moves()
                if gs.check_mate:
                    score = CHECKMATE
                elif gs.stale_mate:
                    score = STALEMATE
                else:
                    score = -turn_multiplier * score_board(gs)
                if score > opponent_max_score:
                    opponent_max_score = score
                gs.undo_move()
        if opponent_max_score < opponent_minimax_score:  # If their new score is less than their previous,
            # then that's the move I should go for
            opponent_minimax_score = opponent_max_score
            best_player_move = player_move
        gs.undo_move()
    return best_player_move


def find_minimax_move_recursively(gs, valid_moves, depth, white_to_move):
    """
    This function uses minimax algorithm recursively to return the best move by looking multiple moves ahead.
    This essentially now gives the AI agent the ability to checkmate better and think about trading pieces
    """
    global minimax_recursive_ai_counter
    minimax_recursive_ai_counter += 1
    global next_move
    if depth == 0:
        return score_board(gs)
    random.shuffle(valid_moves)  # Prevents the agent from being predictable when multiple moves have same score
    if white_to_move:
        max_score = -CHECKMATE
        for move in valid_moves:
            gs.make_move(move)
            next_moves = gs.get_valid_moves()
            score = find_minimax_move_recursively(gs, next_moves, depth - 1, False)
            if score > max_score:
                max_score = score
                if depth == DEPTH:
                    next_move = move
            gs.undo_move()
        return max_score
    else:
        min_score = CHECKMATE
        for move in valid_moves:
            gs.make_move(move)
            next_moves = gs.get_valid_moves()
            score = find_minimax_move_recursively(gs, next_moves, depth - 1, True)
            if score < min_score:
                min_score = score
                if depth == DEPTH:
                    next_move = move
            gs.undo_move()
        return min_score


def find_negamax_move(gs, valid_moves, depth, turn_multiplier):
    """
    This function uses negamax algorithm recursively to return the best move by looking multiple moves ahead.
    This is a variant of minimax used in zero-sum games for cleaner code
    """
    global negamax_ai_counter
    negamax_ai_counter += 1
    global next_move
    random.shuffle(valid_moves)  # Prevents the agent from being predictable when multiple moves have same score
    if depth == 0:
        return turn_multiplier * score_board(gs)
    max_score = -CHECKMATE
    for move in valid_moves:
        gs.make_move(move)
        next_moves = gs.get_valid_moves()
        # Negating the return value for negamax
        score = -find_negamax_move(gs, next_moves, depth - 1, -turn_multiplier)
        if score > max_score:
            max_score = score
            if depth == DEPTH:
                next_move = move
        gs.undo_move()
    return max_score


def find_negamax_move_alphabeta(gs, valid_moves, depth, alpha, beta, turn_multiplier):
    """
    This function uses negamax algorithm along with alphabeta pruning recursively to return the best move by looking multiple moves ahead.
    This is a variant of minimax used in zero-sum games for cleaner and faster code
    """
    global negamax_alphabeta_ai_counter
    negamax_alphabeta_ai_counter += 1
    global next_move
    random.shuffle(valid_moves)  # Prevents the agent from being predictable when multiple moves have same score
    if depth == 0:
        return turn_multiplier * score_board(gs)

    max_score = -CHECKMATE
    for move in valid_moves:
        gs.make_move(move)
        next_moves = gs.get_valid_moves()
        # Negating the return value for negamax
        score = -find_negamax_move_alphabeta(gs, next_moves, depth - 1, -beta, -alpha, -turn_multiplier)
        if score > max_score:
            max_score = score
            if depth == DEPTH:
                next_move = move
        gs.undo_move()
        if max_score > alpha:  # Pruning happens
            alpha = max_score
        if alpha >= beta:
            break
    return max_score


def score_board(gs):
    """
    Score the board based on material AND other rules.
    A positive score is good for white, while a negative score is good for black
    """
    if gs.check_mate:
        if gs.white_to_move:
            return -CHECKMATE
        else:
            return CHECKMATE
    elif gs.stale_mate:
        return STALEMATE

    score = 0
    # pylint: disable=locally-disabled, consider-using-enumerate
    for row in range(len(gs.board)):
        for col in range(len(gs.board[row])):
            # Since this is a zero-sum game, whatever points white gains, black loses, so white would
            # add to the score, while black will subtract
            square = gs.board[row][col]
            if square != '--':
                piece_position_score = 0
                # Score it positionally with a factor of 0.3
                if square[1] != "K":  # No position table for the king
                    # For pawns
                    if square[1] == "P":
                        piece_position_score = piece_position_scores[square][row][col]
                    # For other pieces
                    else:
                        piece_position_score = piece_position_scores[square[1]][row][col]

                if square[0] == 'w':  # If it's a white piece
                    score += piece_score[square[1]] + piece_position_score * 0.3
                elif square[0] == 'b':
                    score -= piece_score[square[1]] + piece_position_score * 0.3
    return score


def score_material(board):
    """
    Score the board based on material
    """
    score = 0
    for row in board:
        for square in row:
            # Since this is a zero-sum game, whatever points white gains, black loses, so white would
            # add to the score, while black will subtract
            if square[0] == 'w':  # If it's a white piece
                score += piece_score[square[1]]
            elif square[0] == 'b':
                score -= piece_score[square[1]]
    return score


def find_best_move(gs, valid_moves, algo_type, return_queue):
    """
    A helper function for the first recursive call of find_minimax_move_recursively() function
    that will return the global variable next_move
    """
    global next_move
    next_move = None
    if algo_type == 0:
        next_move = find_random_move(valid_moves)
    elif algo_type == 1:
        next_move = find_greedy_move(gs, valid_moves)
    elif algo_type == 2:
        next_move = find_minimax_move_iteratively(gs, valid_moves)
    elif algo_type == 3:
        find_minimax_move_recursively(gs, valid_moves, DEPTH, gs.white_to_move)
    elif algo_type == 4:
        find_negamax_move(gs, valid_moves, DEPTH, 1 if gs.white_to_move else -1)
    elif algo_type == 5:
        find_negamax_move_alphabeta(gs, valid_moves, DEPTH, -CHECKMATE, CHECKMATE, 1 if gs.white_to_move else -1)
    if random_ai_counter:
        print("Random AI counter:", random_ai_counter)
    if greedy_ai_counter:
        print("Greedy AI counter:", greedy_ai_counter)
    if minimax_iterative_ai_counter:
        print("Minimax Iterative AI counter:", minimax_iterative_ai_counter)
    if minimax_recursive_ai_counter:
        print("Minimax Recursive AI counter:", minimax_recursive_ai_counter)
    if negamax_ai_counter:
        print("Negamax AI counter:", negamax_ai_counter)
    if negamax_alphabeta_ai_counter:
        print("Negamax alphabeta AI counter:", negamax_alphabeta_ai_counter)
    return_queue.put(next_move)
