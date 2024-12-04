import copy
# slide puzzle:
# 
# 1-N blocks
# . is empty
# X is wall
#
class SlidingBlocks:
    def __init__(self, board):
        self.board = copy.deepcopy(board)

    @classmethod
    def DIRECTIONS(deck_of_cards):
        return {
            "UP" : (0, -1),
            "DOWN" : (0, 1),
            "LEFT" : (-1, 0),
            "RIGHT" : (1, 0),
        }

    def print(self):
        for row in self.board:
            print(row)
        print()

    def get_pieces(self):
        pieces = []
        for row in self.board:
            for square in row:
                if square.isdigit():
                    pieces.append(square)
        return sorted(pieces)

    def clear_moves(self):
        for y, row in enumerate(self.board):
            for x, square in enumerate(row):
                if square == '+':
                    self.board[y][x] = '.'                    

    def find_piece(self, piece):
        for y, row in enumerate(self.board):
            for x, square in enumerate(row):
                if square == piece:
                    return (x, y)
        return None

    def is_clear(self, piece, dir):
        piece_coord = self.find_piece(piece)
        if piece_coord == None:
            return False
        delta = SlidingBlocks.DIRECTIONS().get(dir, None)
        if delta == None:
            return False
        (dx, dy) = delta
        (x, y) = piece_coord
        x += dx
        y += dy
        height = len(self.board) # number of rows (y indicates which row)
        if y >= height :
            return False
        width = len(self.board[y]) # number of squares in the row (x indicates which square)
        while x >= 0 and y >= 0 and x < width and y < height:
            if self.board[y][x] != '.':
                return False
            x += dx
            y += dy
        return True

    def move(self, piece, dir):
        print (f" move {piece} {dir}")
        piece_coord = self.find_piece(piece)
        if piece_coord == None:
            print(f"piece: {piece} is not on the board.")
            return False
        delta = SlidingBlocks.DIRECTIONS().get(dir, None)
        if delta == None:
            return False
        (dx, dy) = delta
        (x, y) = piece_coord
        self.board[y][x] = '+'
        x1 = x+dx
        y1 = y+dy
        height = len(self.board) # number of rows (y indicates which row)
        # did I move off board?
        if y1 >= height or y1 < 0:
            return True
        width = len(self.board[y]) # number of squares in the row (x indicates which square)
        if x1 >= width or x1 < 0:
            return True
        self.board[y1][x1] = piece
        return True
    
    def solve(self):
        moves = []
        print(f"pieces: {self.get_pieces()}")
        self.print()
        made_move = True
        while made_move and len(self.get_pieces()) > 0:
            made_move = False
            for piece in self.get_pieces():
                for dir in SlidingBlocks.DIRECTIONS().keys():
                    print(f"{dir}: is clear: {self.is_clear(piece, dir)}")
                    if self.is_clear(piece, dir):
                        moves.append(f"{piece} {dir}")
                        made_move = True
                        self.print()
                        while self.move(piece, dir):
                            self.print()
                        self.clear_moves()
                        self.print()
                        break
        return made_move, moves

def main():
    # Code to execute
    print("Running Slide Puzzle function...")
    # board = [
    #     ['.', '.', '.', '.', '.'],
    #     ['.', '.', '.', '.', '.'],
    #     ['.', '.', '1', '.', '.'],
    #     ['.', '.', '.', '.', '.'],
    #     ['.', '.', '.', '.', '.'],
    #     ['.', '.', '.', '.', '.'],
    # ]
    # SlidingBlocks(board).solve()
    # board = [
    #     ['.', '.', 'X', '.', '.'],
    #     ['.', '.', '.', '.', '.'],
    #     ['.', '.', '1', '.', '.'],
    #     ['.', '.', '.', '.', '.'],
    #     ['.', '.', '.', '.', '.'],
    #     ['.', '.', '.', '.', '.'],
    # ]
    # SlidingBlocks(board).solve()
    # board = [
    #     ['.', '.', 'X', '.', '.'],
    #     ['.', '.', '.', '.', '.'],
    #     ['.', '.', '1', '.', '.'],
    #     ['.', '.', '2', '.', '.'],
    #     ['.', '.', '.', '.', '.'],
    #     ['.', '.', '.', '.', '.'],
    # ]
    # SlidingBlocks(board).solve()
    # board = [
    #     ['.', '.', 'X', '.', '.'],
    #     ['.', '.', '.', '.', '.'],
    #     ['X', '.', '1', '.', 'X'],
    #     ['.', '.', '2', '.', '.'],
    #     ['.', '.', '.', '.', '.'],
    #     ['.', '.', '.', '.', '.'],
    # ]
    # SlidingBlocks(board).solve()
    # 
    # board = [
    #     ['.', '.', 'X', '.', '.'],
    #     ['.', '.', '.', '.', '.'],
    #     ['X', '.', '1', '.', 'X'],
    #     ['.', '.', '2', '.', '.'],
    #     ['.', '.', '.', '.', '.'],
    #     ['.', '.', 'X', '.', '.'],
    # ]
    # solved, _ = SlidingBlocks(board).solve()
    # print(f"The board is {'' if solved else 'not '}solved")

    board = [
        ['X', 'X', '.', 'X', 'X'],
        ['X', '.', '.', '.', 'X'],
        ['X', '3', '1', '4', '.'],
        ['.', '.', '2', '5', '.'],
        ['.', '.', '.', '6', 'X'],
        ['X', 'X', '.', 'X', 'X'],
    ]
    solved, moves = SlidingBlocks(board).solve()
    print('\n'.join([' '.join(row) for row in board]))

    print(f"The board is {'' if solved else 'not '}solved")
    print(f"Moves were:{', '.join(moves)}")


if __name__ == "__main__":
    main()
