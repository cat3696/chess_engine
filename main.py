"""
This is our main driver file. It will be responsible for handling user input and displaying the current Game State
object.
"""
import pygame as p
import chess_engine
import chess_ai_agent as ai
from multiprocessing import Queue

BOARD_WIDTH = BOARD_HEIGHT = 512
MOVE_LOG_PANEL_WIDTH = 320
MOVE_LOG_PANEL_HEIGHT = BOARD_HEIGHT
DIMENSION = 8  # A chess board is 8x8
SQ_SIZE = BOARD_HEIGHT // DIMENSION
MAX_FPS = 15  # For animations
IMAGES = {}

'''
Initialize the global dictionary of IMAGES only once to save on computation
'''


def load_images():
    pieces = ["wP", "wR", "wN", "wB", "wQ", "wK", "bP", "bR", "bN", "bB", "bQ", "bK"]
    for piece in pieces:
        IMAGES[piece] = p.transform.scale(p.image.load(f"images_dialexa_people/{piece}.png"), (SQ_SIZE, SQ_SIZE))
    # NOTE: we can access each image  by 'Images['wP]' for example


'''
The main driver, handling user input, and updating graphics
'''


def main():
    p.init()
    p.display.set_caption('Chess')
    screen = p.display.set_mode((BOARD_WIDTH + MOVE_LOG_PANEL_WIDTH, BOARD_HEIGHT))
    clock = p.time.Clock()
    screen.fill(p.Color("white"))
    move_log_font = p.font.SysFont("Arial", 14, False, False)
    gs = chess_engine.GameState()
    valid_moves = gs.get_valid_moves()
    move_made = False  # Flag variable when a move is made, to prevent regenerating the function pointlessly
    animate = False  # Flag variable for when we should animate
    load_images()
    running = True
    sq_selected = ()  # No square is selected initially (row, col)
    player_clicks = []  # Keep track of player clicks [(6,4), (4,4)]
    game_over = False
    player_one = False  # If a human is playing white, then this will be true.
    player_two = False  # If a human is playing black , then this will be true.
    # 0: random, 1: greedy, 2: minimax iterative, 3: minimax recursive, 4: negamax, 5: negamax alphabeta
    player_one_alg = 1
    player_two_alg = 4
    ai_thinking = False  # AI is currently trying to come up with a move
    move_finder_process = None
    move_undone = True
    while running:
        human_turn = (gs.white_to_move and player_one) or (not gs.white_to_move and player_two)
        for e in p.event.get():
            if e.type == p.QUIT:
                running = False
            elif e.type == p.MOUSEBUTTONDOWN:
                if not game_over:
                    location = p.mouse.get_pos()  # (x,y) location of mouse
                    col = location[0] // SQ_SIZE
                    row = location[1] // SQ_SIZE
                    if sq_selected == (row, col) or col >= 8 or (gs.board[row][col] == '--' and len(
                            player_clicks) == 0):  # The user clicked the same square twice or user clicked move log
                        sq_selected = ()  # Deselect
                        player_clicks = []
                    else:
                        sq_selected = (row, col)
                        player_clicks.append(sq_selected)  # Append both the 1st and 2nd clicks
                    if len(player_clicks) == 2 and human_turn:  # After 2nd click
                        move = chess_engine.Move(player_clicks[0], player_clicks[1], gs.board)
                        for i in range(len(valid_moves)):
                            if move == valid_moves[i]:
                                gs.make_move(valid_moves[i])
                                move_made = True
                                animate = True
                                sq_selected = ()
                                player_clicks = []
                        if not move_made:
                            player_clicks = [
                                sq_selected]  # Enables resetting a click when a user clicks on two same-color pieces
            elif e.type == p.KEYDOWN:
                if e.key == p.K_u:  # Undo the board
                    gs.undo_move()
                    move_made = True
                    animate = False
                    game_over = False
                    if ai_thinking:
                        move_finder_process.terminate()
                        ai_thinking = False
                    move_undone = True
                elif e.key == p.K_r:  # Reset the board
                    gs = chess_engine.GameState()
                    valid_moves = gs.get_valid_moves()
                    sq_selected = ()
                    player_clicks = []
                    move_made = False
                    animate = False
                    game_over = False
                    if ai_thinking:
                        move_finder_process.terminate()
                        ai_thinking = False
                    move_undone = True
        # AI agent
        if not game_over and not human_turn and move_undone:  # If it's the AI turn
            if not ai_thinking:
                ai_thinking = True
                return_queue = Queue()  # Used to pass data between threads
                ai.find_best_move(gs, valid_moves, (player_one_alg if gs.white_to_move else player_two_alg),
                                  return_queue)
                ai_move = return_queue.get()
                if ai_move is None:
                    ai_move = ai.find_random_move(valid_moves)  # Should never need to call this
                gs.make_move(ai_move)
                move_made = True
                animate = True
                sq_selected = ()  # Deselect
                player_clicks = []
                ai_thinking = False
        if move_made:
            if animate:
                animate_move(gs.move_log[-1], screen, gs.board, clock)
            valid_moves = gs.get_valid_moves()
            move_made = False
            animate = False
        draw_game_state(screen, gs, valid_moves, sq_selected, move_log_font)

        if gs.check_mate or gs.stale_mate:
            game_over = True
            if gs.stale_mate:
                text = "Stalemate"
            elif gs.white_to_move:
                text = "Black wins by checkmate"
            else:
                text = "White wins by checkmate"
            draw_endgame_text(screen, text)

        clock.tick(MAX_FPS)
        p.display.flip()


def highlight_squares(screen, gs, valid_moves, sq_selected):
    """
    Highlight square selected and the piece's available moves
    """
    if sq_selected != ():
        r, c = sq_selected
        if gs.board[r][c][0] == ('w' if gs.white_to_move else 'b'):  # sq_selected is a piece that can be moved
            # Highlight square
            s = p.Surface((SQ_SIZE, SQ_SIZE))
            s.set_alpha(150)  # transparency value -> 0: transparent - 255: opaque
            s.fill(p.Color(170, 140, 110))
            screen.blit(s, (c * SQ_SIZE, r * SQ_SIZE))
            # Highlight moves from that square
            s.fill(p.Color(120, 40, 180, 150))
            for move in valid_moves:
                if move.start_row == r and move.start_col == c:
                    screen.blit(s, (move.end_col * SQ_SIZE, move.end_row * SQ_SIZE))


'''
Responsible for all the graphics withing our current game state
'''


def draw_game_state(screen, gs, valid_moves, sq_selected, movelog_font):
    draw_board(screen)  # Draw squares on the board
    highlight_squares(screen, gs, valid_moves, sq_selected)
    draw_pieces(screen, gs.board)  # Draw pieces on top of the board
    draw_move_log(screen, gs, movelog_font)


''' Draw the squares on the board. The top left square is always light '''


def draw_board(screen):
    global colors
    colors = {'light': (245, 230, 190), 'dark': (100, 70, 60)}
    for r in range(DIMENSION):
        for c in range(DIMENSION):
            color = colors["light"] if (r + c) % 2 == 0 else colors["dark"]
            square = p.Rect(SQ_SIZE * c, SQ_SIZE * r, SQ_SIZE, SQ_SIZE)
            p.draw.rect(screen, color, square)


def draw_pieces(screen, board):
    """
    Draw the pieces on the board using the current state
    """
    for r in range(DIMENSION):
        for c in range(DIMENSION):
            piece = board[r][c]
            if piece != "--":
                screen.blit(IMAGES[piece], p.Rect(SQ_SIZE * c, SQ_SIZE * r, SQ_SIZE, SQ_SIZE))


def animate_move(move, screen, board, clock):
    """
    Animating the move
    """
    global colors
    d_r = move.end_row - move.start_row
    d_c = move.end_col - move.start_col
    frames_per_square = 10  # Frames to move one square
    frame_count = (abs(d_r) + abs(d_c)) * frames_per_square
    for frame in range(frame_count + 1):
        r, c = (move.start_row + d_r * (frame / frame_count), move.start_col + d_c * (frame / frame_count))
        draw_board(screen)
        draw_pieces(screen, board)
        # Erase the piece moved from its ending square
        color = colors['dark'] if (move.end_row + move.end_col) % 2 else colors['light']
        end_square = p.Rect(move.end_col * SQ_SIZE, move.end_row * SQ_SIZE, SQ_SIZE, SQ_SIZE)
        p.draw.rect(screen, color, end_square)
        # Draw captured piece into rectangle
        if move.piece_captured != '--':
            # Enpassant case
            if move.is_enpassant_move:
                enpassant_row = move.end_row + (1 if move.piece_captured[0] == 'b' else -1)
                end_square = p.Rect(move.end_col * SQ_SIZE, enpassant_row * SQ_SIZE, SQ_SIZE, SQ_SIZE)
            screen.blit(IMAGES[move.piece_captured], end_square)
        # Draw moving piece
        screen.blit(IMAGES[move.piece_moved], p.Rect(c * SQ_SIZE, r * SQ_SIZE, SQ_SIZE, SQ_SIZE))
        p.display.flip()
        clock.tick(60)


def draw_move_log(screen, gs, font):
    """
    Draws a move log on the screen
    """
    move_log_rect = p.Rect(BOARD_WIDTH, 0, MOVE_LOG_PANEL_WIDTH, MOVE_LOG_PANEL_HEIGHT)
    p.draw.rect(screen, p.Color("black"), move_log_rect)
    move_log = gs.move_log
    move_texts = []
    # Create a move_log string
    moves_per_row = 3
    for i in range(0, len(move_log), 2):
        move_texts.append(
            f"{(i // 2 + 1)}. {str(move_log[i])} " + (str(move_log[i + 1]) if len(move_log) > i + 1 else "") + " ")
    padding = 5
    text_y = padding
    line_spacing = 2
    for i in range(0, len(move_texts), moves_per_row):
        text = ""
        for j in range(moves_per_row):
            if i + j < len(move_texts):
                text += move_texts[i + j]
        text_object = font.render(text, True, p.Color('White'))
        text_location = move_log_rect.move(padding, text_y)
        screen.blit(text_object, text_location)
        text_y += text_object.get_height() + line_spacing


def draw_endgame_text(screen, text):
    font = p.font.SysFont("Helvetica", 32, True, False)
    text_object = font.render(text, 0, p.Color('Black'))
    text_location = p.Rect(0, 0, BOARD_WIDTH, BOARD_HEIGHT).move(BOARD_WIDTH / 2 - text_object.get_width() / 2,
                                                                 BOARD_HEIGHT / 2 - text_object.get_height() / 2)
    screen.blit(text_object, text_location)
    text_object = font.render(text, 0, p.Color('Gray'))
    screen.blit(text_object, text_location.move(2, 2))


# Best practice to ensure the function only runs when the file is run directly
if __name__ == "__main__":
    main()
