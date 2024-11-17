from curses.ascii import isdigit
from math import sqrt
from dancingLinkNode import DancingLinks 
from collections import namedtuple


class Sudoku:
    def __init__(self, board):
        self.Node = namedtuple('SudokuNode', ['row', 'column', 'number', 'name'])
        self.Move = namedtuple('SudokuMove', ['node', 'column', 'unsatisfied_constraints'])
        self.board = board
        self.N = self.check_board()
        self.solutions = []
        self.debug = False
        self.get_all_solutions = False
        self.cell_constraint_name = "C{}/{}"
        self.row_number_name = "R{}#{}"
        self.column_number_name = "C{}#{}"
        self.box_number_name = "B{}#{}"
        self.box_size = int(sqrt(self.N))
        self.box_enabled = (self.box_size ** 2) == self.N
        print(f"box_enabled {self.box_enabled}")        


    def check_board(self):
        board_ok = True
        if self.board == None:
            print("bad board: no board")
            board_ok = False
        elif len(self.board) == 0:
            print("bad board: no height")
            board_ok = False
        else:
            height = len(self.board)
            for row in self.board:
                if len(row) != height:
                    print(f"bad board: not square {row}")
                    board_ok = False
        if board_ok:
            N = len(self.board)
            print(f"board size {N}x{N}")
            return N
        return 0

    def get_box(self, row_index, col_index ):
        row = row_index - 1
        col = col_index - 1
        return ((row // self.box_size) * self.box_size + (col // self.box_size)) + 1

        
    def print_board_no_separator(self):
        for row in self.board:
            print(" | ".join(row))
            
    def generate_constraints(self):
        
        possibilities = DancingLinks()
        possibilities.debug = self.debug
        if self.debug:
            # add early to make readable printout
            for row_index in range(1, self.N+1):
                for col_index in range(1, self.N+1):
                    possibilities.add_column(self.cell_constraint_name.format(row_index, col_index))
                

            for row_index in range(1, self.N+1):
                for number in range(1, self.N+1):
                    possibilities.add_column(self.row_number_name.format(row_index, number))


            for col_index in range(1, self.N+1):
                for number in range(1, self.N+1):
                    possibilities.add_column(self.column_number_name.format(col_index, number))



        for row_index in range(1, self.N+1):
            for col_index in range(1, self.N+1):
                cell_name = self.cell_constraint_name.format(row_index, col_index)
                for number in range(1, self.N+1):
                    print(".", end="")
                    name = f"R{row_index}C{col_index}#{number}"
                    
                    node = self.Node(row_index, col_index, number, name)
                    # Cell constraint: Only one number per cell
                    possibilities.add_node(cell_name, node)                    


                    # Row constraint: Only one of each number per row
                    possibilities.add_node(self.row_number_name.format(row_index, number), node)


                    # Column constraint: Only one of each number per column
                    possibilities.add_node(self.column_number_name.format(col_index, number), node)

                    # # Box constraint: Only one of each number per box
                    if self.box_enabled:
                        box = self.get_box(row_index, col_index)
                        possibilities.add_node(self.box_number_name.format(box, number), node)

        print(".")

        possibilities.check_columns()
#        possibilities.print()

        self.possibilities = possibilities             

    def setup_puzzle(self):
        self.generate_constraints()
        for row_index, row in enumerate(self.board):
            for col_index, char in enumerate(row):
                if not char.isdigit():
                    continue
                number = int(char)
                
                name = f"R{row_index+1}C{col_index+1}#{number}"
                node = self.Node(row_index+1, col_index+1, number, name)
                self.make_move(node)

    def board_to_moves(self, board):
        moves = []
        for row_index, row in enumerate(board):
            for col_index, char in enumerate(row):
                if not char.isdigit():
                    continue
                number = int(char)

                name = f"R{row_index + 1}C{col_index + 1}#{number}"
                node = self.Node(row_index + 1, col_index + 1, number, name)
                moves.append(node)
                #move = self.Move(chosen_node, unsatisfied_constraint, unsatisfied_constraints)
        # given a set of possibilities, and a move, I can find a row/move
        # so emit a list of moves for playing
        return moves

    def print_setup(self):
        self.print_solution([])

    def print_solution(self, solution):

        board = [["." for _ in range(self.N)] for _ in range(self.N)]
        for row_index, row in enumerate(self.board):
            for col_index, char in enumerate(row):
                if not char.isdigit():
                    continue
                number = int(char)
                name = f"R{row_index+1}C{col_index+1}#{number}"
                node = self.Node(row_index+1, col_index+1, number, name)
                board[row_index][col_index] = str(number)
                
        column_names = []
        current_column = self.possibilities.header.right
        while current_column != self.possibilities.header:
            column_names.append(current_column.name)
            current_column = current_column.right
        
        for move in solution:
            # print(f"Move {move.node.data.name}  ")
            number = move.node.data.number
            row_index = move.node.data.row - 1
            col_index = move.node.data.column - 1
            board[row_index][col_index] = str(number)

        if len(solution) == 0:
            print("***** SET UP *****")
        elif len(column_names) != 0:
            print("***** STATUS *****")
        else: 
            print("***** SOLUTION *****")
    
        for row_index, row_data in enumerate(board):
            row = f"{row_index+1}: │"
            for number in row_data:
                row += f"{number}│" 
            print(row)

        
    def solve_puzzle(self, solution = []):
        self.solutions.append(solution)
        self.solved = False
        
        while self.solved == False:
            self.work_on_solution()

        for solution in self.solutions:
            self.print_setup()
            # for move in solution:
            #     print(f"Move {move.node.data.name} {move.column.name} ")
            self.print_solution(solution)

    def make_move(self, move):
        possibilities = self.possibilities
#        possibilities.print()
        print (f"making move: {move}")
        row_index = move.row
        col_index = move.column
        number = move.number
        
        covered_cell = possibilities.cover_column(possibilities.find_column_header(self.cell_constraint_name.format(row_index, col_index)))
        covered_column_number = possibilities.cover_column(possibilities.find_column_header(self.column_number_name.format(col_index, number)))
        covered_row_number = possibilities.cover_column(possibilities.find_column_header(self.row_number_name.format(row_index, number)))

        if self.box_enabled:
            box = self.get_box(row_index, col_index)
            covered_box_number = possibilities.cover_column(possibilities.find_column_header(self.box_number_name.format(box, number)))


    def unmake_move(self, move):
        possibilities = self.possibilities
#        possibilities.print()
        print (f"unmaking move: {move}")
        row_index = move.row
        col_index = move.column
        number = move.number

        if self.box_enabled:
            box = self.get_box(row_index, col_index)
            covered_box_number = possibilities.uncover_column(possibilities.find_column_header(self.box_number_name.format(box, number)))
        covered_row_number = possibilities.uncover_column(possibilities.find_column_header(self.row_number_name.format(row_index, number)))
        covered_column_number = possibilities.uncover_column(possibilities.find_column_header(self.column_number_name.format(col_index, number)))
        covered_cell = possibilities.uncover_column(possibilities.find_column_header(self.cell_constraint_name.format(row_index, col_index)))



    def get_satisfied_constraints(self, solution):
        possibilities = self.possibilities
        satisfied_constraints = set()
        for move in solution:
            # print(f"Move {move.node.data.name} {move.column.name} ")
            satisfied_constraints = satisfied_constraints.union(move.column.covered_constraints)
        #possibilities.print()
        # print("satisfied_constraints: ")
        # print(satisfied_constraints)
        return satisfied_constraints

    def get_unsatisfied_constraints(self, satisfied_constraints):
        possibilities = self.possibilities
        unsatisfied_constraints = []
        for column_header in possibilities.sorted_columns:
            # print(f"column {column_header.name}:")
            if column_header.name not in satisfied_constraints:
                # print(f"column {column_header.name}: not in set")
                unsatisfied_constraints.append(column_header)
            # else:
            #     print(f"column {column_header.name}: in set")
        unsatisfied_constraints.reverse()    
        return unsatisfied_constraints

    def get_column_with_no_solution(self):
        # Start from any column and search all columns for a column with no nodes
        possibilities = self.possibilities
        column_header = possibilities.header.right
        column_with_no_solution = None
        while column_header != possibilities.header:
            if column_header.size == 0:
                column_with_no_solution = column_header
                break
            column_header = column_header.right
        return column_with_no_solution

    def work_on_solution(self):
        possibilities = self.possibilities
        solution = self.solutions.pop()
        
        satisfied_constraints = self.get_satisfied_constraints(solution)

        unsatisfied_constraints =  self.get_unsatisfied_constraints(satisfied_constraints)

        if len(unsatisfied_constraints) == 0:
            self.solutions.append(solution)
            self.solved = True
            return
        unsatisfied_constraint = unsatisfied_constraints.pop()
        chosen_node = unsatisfied_constraint.down
        if unsatisfied_constraint.size == 1:
            print(f"Only one move")
        # print(f"Column {unsatisfied_constraint.name} has {unsatisfied_constraint.size} rows")
        
        move_ok = False
        while not move_ok:
            # if the rows are zero this is not a solution, try another column
            while chosen_node == unsatisfied_constraint:
                # print("\n!!!!!!! not a solution! !!!!!!!!")
                # self.print_setup()
                # self.print_solution(solution)
                unsatisfied_constraint = None
                while unsatisfied_constraint == None:
                    if len(unsatisfied_constraints) > 0:
                        unsatisfied_constraint = unsatisfied_constraints.pop()
                    elif len(solution) > 0:
                        previous_move = solution.pop()
                        unsatisfied_constraints = previous_move.unsatisfied_constraints
                        
                    else:
                        # unsolvable
                        print("\n!!!!!!! no solutions possible! !!!!!!!!")
                        self.print_setup()
                        self.solved = True
                        return
                chosen_node = unsatisfied_constraint.down

            
            move = self.Move(chosen_node, unsatisfied_constraint, unsatisfied_constraints)
            # print(f"Move {move.node.data.name} {move.column.name} ")

#            possibilities.print(False)
            self.make_move(move.node.data)
            solution.append(move)
            self.print_solution(solution)

            column_with_no_solution = self.get_column_with_no_solution()
            move_ok = column_with_no_solution == None
            # traverse the rows of the chosen column
            if not move_ok:
                print(f"column_with_no_solution {column_with_no_solution.name} {move.node.data.name}")
                self.unmake_move(move.node.data)
                solution.pop()
                self.print_solution(solution)
                chosen_node = chosen_node.down
                
                

        # for move in solution:
        #     print(f"Move {move.node.data.name} {move.column.name} ")
#        possibilities.print()

        self.solutions.append(solution)
            


        
                    
                


class Solution(object):
    def solveSudoku(self, board):
        """
        :type board: list[list[str]]
        :rtype: self.None Do not return anything, modify board in-place instead.
        """
        for row in board:
            print(" | ".join(row))


def main():
    # Code to execute
    print("Running Sudoku main function...")

if __name__ == "__main__":
    main()
