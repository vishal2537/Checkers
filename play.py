import tkinter as tk
from tkinter import messagebox
from PIL import ImageTk, Image
from enum import Enum
from typing import Callable, List, Tuple
import random
from copy import deepcopy
from collections import Counter

window = tk.Tk()
window.title("Checkers")
image_size = 100
b_men = ImageTk.PhotoImage(Image.open(
    'black_man.png').resize((image_size, image_size)))
b_king = ImageTk.PhotoImage(Image.open(
    'black_king.png').resize((image_size, image_size)))
w_men = ImageTk.PhotoImage(Image.open(
    'white_man.png').resize((image_size, image_size)))
w_king = ImageTk.PhotoImage(Image.open(
    'white_king.png').resize((image_size, image_size)))
blank = ImageTk.PhotoImage(Image.open(
    'blank.png').resize((image_size, image_size)))

Board = List[List[int]]
position_coordinates = Tuple[int, int]
list_position_coordinate = List[position_coordinates]
possible_moves = List[Tuple[position_coordinates, list_position_coordinate]]


class Checkers(object):
    INFI = 10 ** 9
    WHITE = 1
    WHITE_MAN = 1
    WHITE_KING = 3
    BLACK = 0
    BLACK_MAN = 2
    BLACK_KING = 4
    move_x = [1, 1, -1, -1]
    move_y = [1, -1, 1, -1]

    def __init__(self, siz: int = 8) -> None:
        if siz % 2 != 0 or siz < 4:
            print("board not possible")
        self.siz = siz
        self.board = []
        piece = self.WHITE_MAN
        for i in range(siz):
            lst = []
            if i % 2 == 1:
                ch = 1
            else:
                ch = 0
            x = siz/2
            if i == x - 1:
                piece = 0
            elif i == x + 1:
                piece = self.BLACK_MAN
            for _ in range(siz):
                if ch:
                    lst.append(piece)
                else:
                    lst.append(0)
                ch = not ch
            self.board.append(lst)
            print(lst)
        self.stateCounter = Counter()

    def evalfn(self) -> int:
        value = 0
        for i in range(self.siz):
            for j in range(self.siz):
                num = i * self.siz + j + 5
                value += num * self.board[i][j]

        print("encode : ", self.board, self.siz, value)
        return value

    def getBoard(self):
        return deepcopy(self.board)

    def is_valid(self, x: int, y: int) -> bool:
        z = x >= 0 and x < self.siz and y >= 0 and y < self.siz
        return z

    def next_positions(self, x: int, y: int) -> Tuple[list_position_coordinate, list_position_coordinate]:
        if self.board[x][y] == 0:
            return []

        player = self.board[x][y] % 2
        capture_moves = []
        normal_moves = []
        sign = 1 if player == self.WHITE else -1
        rng = 2 if self.board[x][y] <= 2 else 4
        for i in range(rng):
            next_x = x + sign * self.move_x[i]
            next_y = y + sign * self.move_y[i]
            if self.is_valid(next_x, next_y):
                if self.board[next_x][next_y] == 0:
                    normal_moves.append((next_x, next_y))
                elif self.board[next_x][next_y] % 2 == 1 - player:
                    next_x += sign * self.move_x[i]
                    next_y += sign * self.move_y[i]
                    if self.is_valid(next_x, next_y) and self.board[next_x][next_y] == 0:
                        capture_moves.append((next_x, next_y))
        return normal_moves, capture_moves

    def next_moves(self, player: int) -> possible_moves:
        capture_moves = []
        normal_moves = []
        for x in range(self.siz):
            for y in range(self.siz):
                if self.board[x][y] != 0 and self.board[x][y] % 2 == player:
                    normal, capture = self.next_positions(x, y)
                    if len(normal) != 0:
                        normal_moves.append(((x, y), normal))
                    if len(capture) != 0:
                        capture_moves.append(((x, y), capture))
        if len(capture_moves) != 0:
            return capture_moves
        return normal_moves

    def play_moves(self, x: int, y: int, next_x: int, next_y: int) -> Tuple[bool, int, bool]:
        self.board[next_x][next_y] = self.board[x][y]
        self.board[x][y] = 0
        removed = 0
        if abs(next_x - x) == 2:
            dx = next_x - x
            dy = next_y - y
            removed = self.board[x + dx // 2][y + dy // 2]
            self.board[x + dx // 2][y + dy // 2] = 0

        if self.board[next_x][next_y] == self.WHITE_MAN and next_x == self.siz - 1:
            self.board[next_x][next_y] = self.WHITE_KING
            return False, removed, True
        if self.board[next_x][next_y] == self.BLACK_MAN and next_x == 0:
            self.board[next_x][next_y] = self.BLACK_KING
            return False, removed, True

        if abs(next_x - x) != 2:
            return False, removed, False

        return True, removed, False

    def undoMove(self, x: int, y: int, next_x: int, next_y: int, removed=0, promoted=False):
        if promoted:
            if self.board[next_x][next_y] == self.WHITE_KING:
                self.board[next_x][next_y] = self.WHITE_MAN

            if self.board[next_x][next_y] == self.BLACK_KING:
                self.board[next_x][next_y] = self.BLACK_MAN

        self.board[x][y] = self.board[next_x][next_y]
        self.board[next_x][next_y] = 0

        if abs(next_x - x) == 2:
            dx = next_x - x
            dy = next_y - y
            self.board[x + dx // 2][y + dy // 2] = removed

    def evaluate(self, maximizer: int) -> int:
        score = 0
        for i in range(self.siz):
            for j in range(self.siz):
                if self.board[i][j] != 0:
                    if self.board[i][j] % 2 == maximizer:
                        score += (self.board[i][j] + 1) // 2
                    else:
                        score -= (self.board[i][j] + 1) // 2
        return score * 100

    def stateValue(self, maximizer: int) -> int:
        maxPieces = 0
        minPieces = 0
        for i in range(self.siz):
            for j in range(self.siz):
                if self.board[i][j] != 0:
                    if self.board[i][j] % 2 == maximizer:
                        maxPieces += 1
                    else:
                        minPieces += 1
        if (maxPieces > minPieces):
            return -self.stateCounter[self.evalfn()]
        return 0

    def minimax(self, player: int, maximizer: int,  depth: int = 0, alpha: int = -INFI, beta: int = INFI, maxDepth: int = 4, evaluate: Callable[[int], int] = evaluate, moves: possible_moves = None,) -> int:
        if moves == None:
            moves = self.next_moves(player)
        if len(moves) == 0 or depth == maxDepth:
            score = evaluate(self, maximizer)
            if score < 0:
                score += depth
            return score
        bestValue = -self.INFI
        if player != maximizer:
            bestValue = self.INFI
        moves.sort(key=lambda move: len(move[1]))
        for position in moves:
            x, y = position[0]
            for next_x, next_y in position[1]:
                canCapture, removed, promoted = self.play_moves(
                    x, y, next_x, next_y)
                played = False
                if canCapture:
                    _, nextCaptures = self.next_positions(next_x, next_y)
                    if len(nextCaptures) != 0:
                        played = True
                        nMoves = [((next_x, next_y), nextCaptures)]
                        if player == maximizer:
                            bestValue = max(bestValue, self.minimax(
                                player, maximizer, depth + 1, alpha, beta, maxDepth, evaluate, nMoves))
                            alpha = max(alpha, bestValue)
                        else:
                            bestValue = min(bestValue, self.minimax(
                                player, maximizer, depth + 1, alpha, beta, maxDepth, evaluate, nMoves))
                            beta = min(beta, bestValue)
                if not played:
                    if player == maximizer:
                        bestValue = max(bestValue, self.minimax(
                            1 - player, maximizer, depth + 1, alpha, beta, maxDepth, evaluate))
                        alpha = max(alpha, bestValue)
                    else:
                        bestValue = min(bestValue, self.minimax(
                            1 - player, maximizer, depth + 1, alpha, beta, maxDepth, evaluate))
                        beta = min(beta, bestValue)
                self.undoMove(x, y, next_x, next_y, removed, promoted)
                if beta <= alpha:
                    break
            if beta <= alpha:
                break
        return bestValue

    def alpha_beta_application(self, player: int, moves: possible_moves = None, maxDepth: int = 4, evaluate: Callable[[int], int] = evaluate, enablePrint: bool = True,) -> Tuple[bool, bool]:
        if moves == None:
            moves = self.next_moves(player)
        if len(moves) == 0:
            if enablePrint:
                print(("WHITE" if player == self.BLACK else "BLACK") + " Player wins")
            return False, False
        self.stateCounter[self.evalfn()] += 1
        random.shuffle(moves)
        bestValue = -self.INFI
        bestMove = None

        for position in moves:
            x, y = position[0]
            for next_x, next_y in position[1]:
                _, removed, promoted = self.play_moves(x, y, next_x, next_y)
                value = self.minimax(1 - player, player,
                                     maxDepth=maxDepth, evaluate=evaluate)
                value += 2*self.stateValue(player)
                self.undoMove(x, y, next_x, next_y, removed, promoted)
                if value > bestValue:
                    bestValue = value
                    bestMove = (x, y, next_x, next_y)

        x, y, next_x, next_y = bestMove
        print("\n############ bestvalue : ", bestValue)
        print("\n############ bestmove : ", (x, y), (next_x, next_y))
        canCapture, removed, _ = self.play_moves(x, y, next_x, next_y)
        if canCapture:
            _, captures = self.next_positions(next_x, next_y)
            if len(captures) != 0:
                self.alpha_beta_application(
                    player, [((next_x, next_y), captures)], maxDepth, evaluate, enablePrint)
        self.stateCounter[self.evalfn()] += 1
        reset = removed != 0
        return True, reset


CHECKER_SIZE = 8
FIRST_PLAYER = Checkers.BLACK
MAX_DEPTH = 5
INCREASE_DEPTH = True


class Mode(Enum):
    SINGLE_PLAYER = 0
    MULTIPLE_PLAYER = 1


class Algorithm(Enum):
    MINIMAX = 0


GAME_MODE = Mode.SINGLE_PLAYER


class GUI:
    def __init__(self) -> None:
        super().__init__()
        self.game = Checkers(CHECKER_SIZE)
        self.previous_board = [self.game.getBoard()]
        self.previous_ptr = 0
        self.maxDepth = MAX_DEPTH

        self.player = FIRST_PLAYER
        if self.player == Checkers.WHITE and GAME_MODE == Mode.SINGLE_PLAYER:
            if Algorithm.MINIMAX == Algorithm.MINIMAX:
                self.game.alpha_beta_application(
                    1-self.player, maxDepth=self.maxDepth, evaluate=Checkers.evaluate, enablePrint=False)
            self.previous_board = [self.game.getBoard()]

        self.prev_coordinate_x = None
        self.prev_coordinate_y = None
        self.willCapture = False
        self.cnt = 0
        self.game_board = [
            [None]*self.game.siz for _ in range(self.game.siz)]

        board_frame = tk.Frame(master=window)
        board_frame.pack(fill=tk.BOTH, expand=True)
        for i in range(self.game.siz):
            board_frame.columnconfigure(i, weight=1, minsize=image_size)
            board_frame.rowconfigure(i, weight=1, minsize=image_size)

            for j in range(self.game.siz):
                frame = tk.Frame(master=board_frame)
                frame.grid(row=i, column=j, sticky="nsew")

                self.game_board[i][j] = tk.Button(
                    master=frame, width=image_size, height=image_size, relief=tk.FLAT)
                self.game_board[i][j].bind("<Button-1>", self.click)
                self.game_board[i][j].pack(expand=True, fill=tk.BOTH)

        frame_options = tk.Frame(master=window)
        frame_options.pack(expand=False)
        frame_counter = tk.Frame(master=window)
        frame_counter.pack(expand=False)

        self.update()
        next_positions = [move[0]
                          for move in self.game.next_moves(self.player)]
        self.highlighted_moves(next_positions)
        window.mainloop()

    def update(self):
        for i in range(self.game.siz):
            f = i % 2 == 1
            for j in range(self.game.siz):
                if f:
                    self.game_board[i][j]['bg'] = '#3C486B'
                else:
                    self.game_board[i][j]['bg'] = '#F0F0F0'
                img = blank
                if self.game.board[i][j] == Checkers.BLACK_MAN:
                    img = b_men
                elif self.game.board[i][j] == Checkers.BLACK_KING:
                    img = b_king
                elif self.game.board[i][j] == Checkers.WHITE_MAN:
                    img = w_men
                elif self.game.board[i][j] == Checkers.WHITE_KING:
                    img = w_king
                self.game_board[i][j]["image"] = img

                f = not f
        window.update()

    def highlighted_moves(self, positions: list_position_coordinate):
        for x in range(self.game.siz):
            for y in range(self.game.siz):
                def_bg = self.game_board[x][y].cget('bg')
                self.game_board[x][y].master.config(
                    highlightbackground=def_bg, highlightthickness=3)

        for position in positions:
            x, y = position
            self.game_board[x][y].master.config(
                highlightbackground="yellow", highlightthickness=3)

    def click(self, event):
        info = event.widget.master.grid_info()
        x, y = info["row"], info["column"]
        if self.prev_coordinate_x == None or self.prev_coordinate_y == None:
            moves = self.game.next_moves(self.player)
            print("\n\nmoves : ", moves)
            found = (x, y) in [move[0] for move in moves]

            if found:
                self.prev_coordinate_x = x
                self.prev_coordinate_y = y
                normal, capture = self.game.next_positions(x, y)
                positions = normal if len(capture) == 0 else capture
                self.highlighted_moves(positions)
            else:
                print("Invalid position")
            return

        normalPositions, capturePositions = self.game.next_positions(
            self.prev_coordinate_x, self.prev_coordinate_y)
        positions = normalPositions if (
            len(capturePositions) == 0) else capturePositions
        print("\n################ -- possible position : ", positions)

        if (x, y) not in positions:
            print("invalid move")
            if not self.willCapture:
                self.prev_coordinate_x = None
                self.prev_coordinate_y = None
                next_positions = [move[0]
                                  for move in self.game.next_moves(self.player)]
                self.highlighted_moves(next_positions)
            return

        canCapture, removed, _ = self.game.play_moves(
            self.prev_coordinate_x, self.prev_coordinate_y, x, y)
        self.highlighted_moves([])
        self.update()
        self.cnt += 1
        self.prev_coordinate_x = None
        self.prev_coordinate_y = None
        self.willCapture = False

        if removed != 0:
            self.cnt = 0
        if canCapture:
            _, nextCaptures = self.game.next_positions(x, y)
            if len(nextCaptures) != 0:
                self.willCapture = True
                self.prev_coordinate_x = x
                self.prev_coordinate_y = y
                self.highlighted_moves(nextCaptures)
                return

        if GAME_MODE == Mode.SINGLE_PLAYER:
            cont, reset = True, False
            if Algorithm.MINIMAX == Algorithm.MINIMAX:
                evaluate = Checkers.evaluate
                if self.cnt > 20:
                    evaluate = Checkers.evaluate
                    if INCREASE_DEPTH:
                        self.maxDepth = 7
                else:
                    evaluate = Checkers.evaluate
                    self.maxDepth = MAX_DEPTH

                cont, reset = self.game.alpha_beta_application(
                    1-self.player, maxDepth=self.maxDepth, evaluate=evaluate, enablePrint=False)
            self.cnt += 1
            if not cont:
                messagebox.showinfo(message="You Won!", title="Checkers")
                window.destroy()
                return
            self.update()
            if reset:
                self.cnt = 0
        else:
            self.player = 1-self.player

        if self.cnt >= 100:
            messagebox.showinfo(message="Draw!", title="Checkers")
            window.destroy()
            return

        next_positions = [move[0]
                          for move in self.game.next_moves(self.player)]
        self.highlighted_moves(next_positions)
        if len(next_positions) == 0:
            if GAME_MODE == Mode.SINGLE_PLAYER:
                messagebox.showinfo(message="You lost!", title="Checkers")
            else:
                winner = "BLACK" if self.player == Checkers.WHITE else "WHITE"
                messagebox.showinfo(
                    message=f"{winner} Player won!", title="Checkers")
            window.destroy()

        self.previous_board = self.previous_board[:self.previous_ptr+1]
        self.previous_board.append(self.game.getBoard())
        self.previous_ptr += 1


GUI()