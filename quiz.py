from deckOfCards import DeckOfCards
from sudoku import Sudoku




def main():
    # Code to execute
    print("Running main quiz function...")
    print("Hello, World!")


    # deck = DeckOfCards(9)
    # deck.print_len()

    # card = deck.pull_random_card()
    # print(f"Pulled a {card}")
    # deck.print_len()
    # deck.print_deck()

    # board = [[".","."],[".","."]]
    # print( "======== set up board ========" )
    # sudoku = Sudoku(board)
    # sudoku.setup_puzzle()
    # sudoku.print_setup()
    # print( "======== solve puzzle ========" )
    # sudoku.solve_puzzle()
    
    
    # board = [[".","1"],[".","."]]
    # print( "======== set up board ========" )
    # sudoku = Sudoku(board)
    # sudoku.setup_puzzle()
    # sudoku.print_setup()
    # print( "======== solve puzzle ========" )
    # sudoku.solve_puzzle()

    # board = [[".", "2", ".", "."],[".", ".", "4", "."],[".", "4", ".", "."],[".", ".", "1", "."]]
    # print( "======== set up board ========" )
    # sudoku = Sudoku(board)
    # sudoku.setup_puzzle()
    # sudoku.print_setup()
    # print( "======== solve puzzle ========" )
    # sudoku.solve_puzzle()

    # board = [["1", "2", "3", "4"],["1", "2", "3", "4"],[".", "4", ".", "."],[".", ".", "1", "."]]
    # print( "======== set up board ========" )
    # sudoku = Sudoku(board)
    # sudoku.setup_puzzle()
    # sudoku.print_setup()
    # print( "======== solve puzzle ========" )
    # sudoku.solve_puzzle()


    # board = [["1", "2", "3", "4"],["4", "3", "2", "1"],["3", ".", ".", "."],["2", ".", "1", "."]]
    # print( "======== set up board ========" )
    # sudoku = Sudoku(board)
    # sudoku.setup_puzzle()
    # sudoku.print_setup()
    # print( "======== solve puzzle ========" )
    # sudoku.solve_puzzle()

    '''board = [
        [".", ".", ".", "2", "6", ".", "7", ".", "1"],
        ["6", "8", ".", ".", "7", ".", ".", "9", "."],
        ["1", "9", ".", ".", ".", "4", "5", ".", "."],
        ["8", "2", ".", "1", ".", ".", ".", "4", "."],
        [".", ".", "4", "6", ".", "2", "9", ".", "."],
        [".", "5", ".", ".", ".", "3", ".", "2", "8"],
        [".", ".", "9", "3", ".", ".", ".", "7", "4"],
        [".", "4", ".", ".", "5", ".", ".", "3", "6"],
        ["7", ".", "3", ".", "1", "8", ".", ".", "."],
    ]'''

    board = [
        [".", ".", ".", "2", "6", ".", "7", ".", "1"],
        ["6", "8", ".", ".", "7", ".", ".", "9", "."],
        ["1", "9", ".", ".", ".", "4", "5", ".", "."],
        ["8", "2", ".", "1", ".", ".", ".", "4", "."],
        [".", ".", "4", "6", ".", "2", "9", ".", "."],
        [".", "5", ".", ".", ".", "3", ".", "2", "8"],
        [".", ".", "9", "3", ".", ".", ".", "7", "4"],
        [".", "4", ".", ".", "5", ".", ".", "3", "6"],
        ["7", ".", "3", ".", "1", "8", ".", ".", "."],
    ]
    print( "======== set up board ========" )
    sudoku = Sudoku(board)
    sudoku.setup_puzzle()
    sudoku.print_setup()

    board_moves = [
        ["4", "3", "5", ".", ".", "9", ".", "8", "."],
        [".", ".", "2", "5", ".", "1", "4", ".", "."],
        [".", ".", "7", "8", "3", ".", ".", "6", "2"],
        [".", ".", "6", ".", "9", "5", "3", ".", "7"],
        ["3", "7", ".", ".", "8", ".", ".", "1", "5"],
        ["9", ".", "1", "7", "4", ".", "6", ".", "."],
        ["5", "1", ".", ".", "2", "6", "8", ".", "."],
        ["2", ".", "8", "9", ".", "7", "1", ".", "."],
        [".", "6", ".", "4", ".", ".", "2", "5", "9"],
    ]

    solution = []

    moves = sudoku.board_to_moves(board_moves)
    for move in moves:
        print(move)
        # use move to find row
        row = sudoku.possibilities.find_row_node(move.name)
        # use row to find column
        print(row)

    print( "======== solve puzzle ========" )
    sudoku.solve_puzzle()

    # board = [["5","3",".",".","7",".",".",".","."],["6",".",".","1","9","5",".",".","."],[".","9","8",".",".",".",".","6","."],["8",".",".",".","6",".",".",".","3"],["4",".",".","8",".","3",".",".","1"],["7",".",".",".","2",".",".",".","6"],[".","6",".",".",".",".","2","8","."],[".",".",".","4","1","9",".",".","5"],[".",".",".",".","8",".",".","7","9"]]
    # print( "======== set up board ========" )
    # sudoku = Sudoku(board)
    # sudoku.setup_puzzle()
    # sudoku.print_setup()
    # print( "======== solve puzzle ========" )
    # sudoku.solve_puzzle()
    
if __name__ == "__main__":
    main()

