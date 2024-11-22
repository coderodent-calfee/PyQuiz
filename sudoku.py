from ast import Lambda
from curses.ascii import isdigit
from math import sqrt
from dancingLinkNode import DancingLinkNode, DancingLinks 
from collections import namedtuple

class SudokuStrategy(namedtuple('SudokuStrategy', ['name', 'test'])):
    # Define equality, hash based on 'name' attribute
    def __eq__(self, other):
        if isinstance(other, SudokuStrategy):
            return self.name == other.name
        return False
    
    def __hash__(self):
        return hash(self.name)


class SudokuMoveNew(namedtuple('SudokuStrategy', ['node', 'column', 'unsatisfied_constraints', 'satisfied_constraints'])):
    # Define equality, hash based on 'name' attribute
    def __eq__(self, other):
        if isinstance(other, SudokuStrategy):
            return self.name == other.name
        return False
    
    def __hash__(self):
        return hash(self.name)

    
class Sudoku:
    def __init__(self, board):
        self.Node = namedtuple('SudokuNode', ['row', 'column', 'number', 'name'])
        self.Move = namedtuple('SudokuMove', ['node', 'column', 'unsatisfied_constraints', 'satisfied_constraints'])
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
        self.debug_solution_moves = None
        self.debug_in_solution = False


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
        local_row = (row_index - 1) % 3
        local_col = (col_index - 1) % 3
        return ((row // self.box_size) * self.box_size + (col // self.box_size)) + 1

        
    def print_board_no_separator(self):
        for row in self.board:
            print(" | ".join(row))
            
    def generate_constraints(self):
        
        possibilities = DancingLinks()
        possibilities.debug = self.debug
        think = Thinking()
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

        if self.box_enabled:
            for box in range(1, self.N+1):
                for number in range(1, self.N+1):
                    possibilities.add_column(self.box_number_name.format(box, number))

        for row_index in range(1, self.N+1):
            for col_index in range(1, self.N+1):
                cell_name = self.cell_constraint_name.format(row_index, col_index)
                for number in range(1, self.N+1):
#                    think.print()
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

        think.end()
        possibilities.check_columns()
        self.possibilities = possibilities             

    def setup_puzzle(self):
        
        spaces_on_board = self.N * self.N
        self.generate_constraints()
        for row_index, row in enumerate(self.board):
            for col_index, char in enumerate(row):
                if not char.isdigit():
                    continue
                number = int(char)
                name = f"R{row_index+1}C{col_index+1}#{number}"
                node = self.Node(row_index+1, col_index+1, number, name)
                move = self.Move(DancingLinkNode(node), None, None, set())
                spaces_on_board -= 1
                self.make_move(move)
        self.possibilities.debug_show_column_stats()

        self.print_setup()

        self.moves_left = spaces_on_board
        print(f"Moves left on board: {self.N * self.N} - {self.N * self.N - self.moves_left} = {self.moves_left}")
        
    def get_counts_for_moves_left(self):
        if not self.box_enabled:
            return None, None, None
        # cell_candidates = [[[[] for _ in range(self.N)] for _ in range(self.N)] for _ in range(self.N)]
        # box_candidates = [[[[] for _ in range(self.box_size)] for _ in range(self.box_size)] for _ in range(self.N)]
        col_count = [[[] for _ in range(self.N)] for _ in range(self.N)]
        row_count = [[[] for _ in range(self.N)] for _ in range(self.N)]
        box_count = [[[] for _ in range(self.N)] for _ in range(self.N)]
        move = self.possibilities.header.down
        while move != self.possibilities.header:
            row = move.data.row
            col = move.data.column
            number = move.data.number
            box= self.get_box(row, col)
            
            row_count[row-1][number-1].append((row, col))
            col_count[col-1][number-1].append((row, col))
            box_count[box-1][number-1].append((row, col))

            move = move.down
        return row_count, col_count, box_count

    def get_pointing_pairs_and_triples(self,row_count, col_count, box_count):
        if row_count == None:
            return False
        
        strategy_actions = set()

        cell_row = 0
        cell_column = 1
        for b in range(self.N):
            for n in range(self.N):
                # list indices are -1 from actual values
                number = n+1
                box = b+1
                box_contents = box_count[b][n]
                occurance = len(box_contents)
                column_name = None
                if ((occurance == 2 and box_contents[0][cell_row] == box_contents[1][cell_row]) or 
                   (occurance == 3 and box_contents[0][cell_row] == box_contents[1][cell_row] == box_contents[2][cell_row])):
                        row_index = box_contents[0][cell_row]
                        if len(row_count[row_index-1][n]) > occurance:
                            name = f"in row {row_index}and in box:{box}, number {number}: {box_contents} ({occurance})"
                            print(name)
                            strategy = SudokuStrategy(name, lambda data, n = number, row_id = row_index, box_id = box: ((n != data.number) or (row_id != data.row) or (self.get_box(data.row,data.column) == box_id)) )
                            print(f"strategy {strategy} ")
                            strategy_actions.add(strategy)
                            
                elif ((occurance == 2 and box_contents[0][cell_column] == box_contents[1][cell_column]) or 
                   (occurance == 3 and box_contents[0][cell_column] == box_contents[1][cell_column] == box_contents[2][cell_column])):
                        column_index = box_contents[0][cell_column]
                        if len(col_count[column_index-1][n]) > occurance:
                            name = f"in column {column_index} and in box:{box}, number {number}: {box_contents} ({occurance})"
                            print(name)
                            strategy = SudokuStrategy(name, lambda data, n = number, col_id = column_index, box_id = box: ((n != data.number) or (col_id != data.column) or (self.get_box(data.row,data.column) == box_id)) )
                            print(f"strategy {strategy} ")
                            strategy_actions.add(strategy)

        return list(strategy_actions)
                    


    def debug_print_cells(self, solution):
        row_count, col_count, box_count = self.get_counts_for_moves_left()
        row = 1
        col = 1
        number = 1
        row_count, col_count, box_count = self.get_counts_for_moves_left()
        board, _, _ = self.solution_to_board(solution)
        print("    " + "   ".join(str(i) for i in range(1, 10)))
        print(    "  ┌───┬───┬───╥───┬───┬───╥───┬───┬───┐")        
        for row in range(1, self.N+1):
            self.debug_print_row(row, row_count, board)
            if row == 9:
                print("  └───┴───┴───┴───┴───┴───┴───┴───┴───┘")      #╨ ╞ ═ ╪ ╡╬
            elif row == 3 or row  == 6:
                print("  ╞═══╪═══╪═══╬═══╪═══╪═══╬═══╪═══╪═══╡")        
            else:
                print("  ├───┼───┼───╫───┼───┼───╫───┼───┼───┤")        

        
    def debug_print_row(self, row, row_count, board):
        board_row = board[row-1]
        box_top =    "┌─┐"
        box_bottom = "└─┘"
        for i in range(3):
            if i == 1:
                print(f"{row} │", end="")
            else:
                print("  │", end="")
            for col in range(9):
                column = col+1
                for j in range(3):
                    if board_row[col].isdigit():
                        if j == 1 and i == 1:
                            print(f"{board_row[col]}", end="")
                        elif i == 0:
                            print(str(box_top[j]), end="")
                        elif i == 2:
                            print(str(box_bottom[j]), end="")
                        else:
                            print("│", end="")
                    else:
                        number = j + i * 3 +1
                        if (row, column) in row_count[row-1][number-1]:
                            print(f"{number}", end="")
                        else:
                            print(" ", end="")
                if col % 3 == 2 and col != 8:
                    print("║", end="")
                else:
                    print("│", end="")
            print("")
                    

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
        return moves

    def print_setup(self):
        self.print_solution([])
        self.debug_print_cells([])


    def print_moves_and_solution(self, solution):
        board, blanks, errors  = self.solution_to_board(solution)
        self.print_moves(solution)
        for i in range(len(solution), self.moves_left):
            print(f"Move {i:10}:  ")

        
        self.print_solution_from_board(board, solution)
        self.debug_print_cells(solution)
        
            
    def solution_to_board(self, solution):
        errors = []
        blanks = 0
        board = [["." for _ in range(self.N)] for _ in range(self.N)]
        for row_index, row in enumerate(self.board):
            for col_index, char in enumerate(row):
                if not char.isdigit():
                    blanks += 1
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
            if board[row_index][col_index].isdigit(): 
                errors.append((row_index, col_index, number))
            else:
                blanks -= 1
            board[row_index][col_index] = str(number)
        return board, blanks, errors

    def print_solution(self, solution):
        board, _, _  = self.solution_to_board(solution)
        self.print_solution_from_board(board, solution)

    def print_solution_from_board(self, board, solution):

        if len(solution) == 0:
            print("****** SET UP ******")
        elif self.solved:
            print("***** SOLUTION *****")
        else: 
            print("****** STATUS ******")
    
        for row_index, row_data in enumerate(board):
            row = f"{row_index+1}: │"
            for number in row_data:
                row += f"{number}│" 
            print(row)


    def print_moves(self, solution):
        for index, move in enumerate(solution):
            right_or_wrong = ""
            if len(self.solution_move_names) > 0 :
                right_or_wrong = "Wrong"
                if move.node.data.name in self.solution_move_names:
                    right_or_wrong = "Right"
            print(f"Move {index:10}: {move.node.data.name}: UC:{len(move.unsatisfied_constraints):6} {right_or_wrong}")

        
    def solve_puzzle(self, solution = [], solution_moves = None):
        
        solution_move_names = []
        if solution_moves != None:
           for move in solution_moves:
                solution_move_names.append(move.name)

        self.solution_move_names = solution_move_names


        self.start_solution( solution, solution_moves)
        think = Thinking()
        
        while self.solved == False:
            #think.print()
            self.work_on_solution()

        for solution in self.solutions:
            self.print_setup()
            # for move in solution:
            #     print(f"Move {move.node.data.name} {move.column.name} ")
            self.print_solution(solution)

    def start_solution(self, solution = [], solution_moves = None):
        self.debug_solution_moves = solution_moves
        if self.debug_solution_moves != None:
            self.debug_in_solution = True

        possibilities = self.possibilities
        
        possibilities.sort_columns_by_size()
        
        strategy_actions = self.get_pointing_pairs_and_triples(*self.get_counts_for_moves_left())
        self.starting_strategies = set()

        if len(strategy_actions):
            self.starting_strategies = set(strategy_actions)
            for strategy in list(self.starting_strategies):
                print(f"starting_strategy {self.starting_strategies }")
            self.debug_print_cells(solution)
        self.current_strategies = list(self.starting_strategies)


        satisfied_constraints = self.get_satisfied_constraints(solution)
        unsatisfied_constraints =  self.get_unsatisfied_constraints(satisfied_constraints)

        self.starting_move = self.Move(None, None, unsatisfied_constraints, satisfied_constraints)

        self.solutions.append(solution)
        self.solved = False


    def work_on_solution(self):
        possibilities = self.possibilities
        solution = self.solutions.pop()
        
        satisfied_constraints = self.get_satisfied_constraints(solution)

        unsatisfied_constraints =  self.get_unsatisfied_constraints(satisfied_constraints)
        

        if len(unsatisfied_constraints) == 0:
            self.solutions.append(solution)
            self.solved = True
            print("")
            return

        unsatisfied_constraint = unsatisfied_constraints.pop()
        chosen_node = unsatisfied_constraint.down

        move = self.Move(chosen_node, chosen_node.column, unsatisfied_constraints, {chosen_node.column.name})

        
        move_ok = False
        while not move_ok:
            # we've hit the bottom of the nodes for this constraint
            while chosen_node == unsatisfied_constraint:
                # pick the next constraint from the list of unsatisfied constraints
                unsatisfied_constraint = None
                while unsatisfied_constraint == None:
                    # there are more in the list of unsatisfied constraints
                    if len(unsatisfied_constraints) > 0:
                        unsatisfied_constraint = unsatisfied_constraints.pop()
                        chosen_node = unsatisfied_constraint.down
                    # there are no more in the list of unsatisfied constraints
                    # go up to the previous move and continue from there    
                    elif len(solution) > 0:
                        previous_move = solution.pop()
                        # self.current_strategies = list(previous_move.strategies)
                        
                        self.unmake_move(previous_move.node.data)
                        possibilities.sort_columns_by_size()
                        if len(solution) == 0: 
                            if self.debug_solution_moves != None :
                               self.debug_in_solution = True
                        unsatisfied_constraints = previous_move.unsatisfied_constraints
                        # the next node we want is the node down from previous_node
                        unsatisfied_constraint = previous_move.column
                        chosen_node = previous_move.node.down
                    # there are no previous moves
                    # go up to the starting selection of unsatisfied constraints and continue from there    
                    elif len(self.starting_move.unsatisfied_constraints) > 0:
                        unsatisfied_constraint = self.starting_move.unsatisfied_constraints.pop()
                        chosen_node = unsatisfied_constraint.down
                        if self.debug_solution_moves != None :
                           self.debug_in_solution = True
                    else:
                        # unsolvable
                        print("\n!!!!!!! no solutions possible! !!!!!!!!")
                        self.print_setup()
                        self.solved = True
                        return

            # print(f"\r{move.node.data.name}\tMove: {len(solution)}\t UC:{len(unsatisfied_constraints)}", end="")

#            possibilities.print(False)
            if self.debug_in_solution:
                if move.node.data not in self.debug_solution_moves:
                    print(f"Bad Move {move.node.data.name} {move.column.name} ")
                    self.debug_in_solution = False
                elif len(solution) == 0: 
                    print(f"Good Move {move.node.data.name} {move.column.name} ")

            self.make_move(move)
    
            column_with_no_solution = self.get_column_with_no_solution()
            move_ok = column_with_no_solution == None
            
            if move_ok:
                solution.append(move)
                # we don't immediately undo, so we should ensure good sort order
                possibilities.sort_columns_by_size()
                
                current_strategies = self.current_strategies
                self.debug_print_cells(solution)
                strategy_actions = self.get_pointing_pairs_and_triples(*self.get_counts_for_moves_left())
                #current_strategies = move.strategies.union(set(strategy_actions))
                if len(current_strategies):
                    failed = False
                    possibilities.sort_columns_by_size()
                    for strategy in list(current_strategies):
                        print(f"{strategy.name}: {strategy.test(move.node.data)}")
                        if strategy.test(move.node.data) == False:
                            failed = True
                    if failed:
                        # move_ok = False
                        print(f"Not gonna Move {move.node.data.name} {move.column.name} ")
                        self.debug_print_cells(solution)
                        
                    else: 
                        move.strategies.update(current_strategies)
                        self.current_strategies = list(move.strategies)

            if not move_ok:
                if self.debug_in_solution:
                    self.print_solution(solution)
                    self.possibilities.print_all()
                self.unmake_move(move.node.data)
                chosen_node = chosen_node.down
                
                

        # for move in solution:
        #     print(f"Move {move.node.data.name} {move.column.name} ")
#        possibilities.print()
        self.print_moves_and_solution(solution)
        self.solutions.append(solution)


    def make_move(self, move):
        possibilities = self.possibilities
#        possibilities.print()
#        print (f"making move: {move}")
        row_index = move.node.data.row
        col_index = move.node.data.column
        number = move.node.data.number

        covered_cell_name = self.cell_constraint_name.format(row_index, col_index)
        covered_column_name = self.column_number_name.format(col_index, number)
        covered_row_name = self.row_number_name.format(row_index, number)

        move.satisfied_constraints.add(covered_cell_name)
        move.satisfied_constraints.add(covered_column_name)
        move.satisfied_constraints.add(covered_row_name)
        
        covered_cell = possibilities.cover_column(possibilities.find_column_header(covered_cell_name))
        covered_column_number = possibilities.cover_column(possibilities.find_column_header(covered_column_name))
        covered_row_number = possibilities.cover_column(possibilities.find_column_header(covered_row_name))

        if self.box_enabled:
            box= self.get_box(row_index, col_index)
            covered_box_name = self.box_number_name.format(box, number)
            move.satisfied_constraints.add(covered_box_name)
            covered_box_number = possibilities.cover_column(possibilities.find_column_header(covered_box_name))


    def unmake_move(self, move):
        possibilities = self.possibilities
#        possibilities.print()
 #       print (f"unmaking move: {move}")
        row_index = move.row
        col_index = move.column
        number = move.number

        if self.box_enabled:
            box= self.get_box(row_index, col_index)
            covered_box_number = possibilities.uncover_column(possibilities.find_column_header(self.box_number_name.format(box, number)))
        covered_row_number = possibilities.uncover_column(possibilities.find_column_header(self.row_number_name.format(row_index, number)))
        covered_column_number = possibilities.uncover_column(possibilities.find_column_header(self.column_number_name.format(col_index, number)))
        covered_cell = possibilities.uncover_column(possibilities.find_column_header(self.cell_constraint_name.format(row_index, col_index)))



    def get_satisfied_constraints(self, solution):
        possibilities = self.possibilities
        satisfied_constraints = set()
        for move in solution:
            satisfied_constraints = satisfied_constraints.union(move.satisfied_constraints)
        return satisfied_constraints

    def get_unsatisfied_constraints(self, satisfied_constraints):
        possibilities = self.possibilities
        ordered_uncovered = possibilities.get_ordered_uncovered()
        unsatisfied_constraints = [item for item in ordered_uncovered if item not in satisfied_constraints]
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

            
    def debug_can_i_place(self, placement):
        row_index = placement.row
        col_index = placement.column
        number = placement.number
        cell_name = self.cell_constraint_name.format(row_index, col_index)
        cell_column = self.possibilities.find_uncovered_column_header(cell_name)
        
        row_name = self.row_number_name.format(row_index, number)
        row_column = self.possibilities.find_uncovered_column_header(row_name)
        
        column_name = self.column_number_name.format(col_index, number)
        column_column  = self.possibilities.find_uncovered_column_header(column_name)

        if self.box_enabled:
            box= self.get_box(row_index, col_index)
            box_name = self.box_number_name.format(box, number)
            box_column  = self.possibilities.find_uncovered_column_header(box_name)

        if row_column == None:
            return False
        if column_column == None:
            return False
        if cell_column == None:
            return False
        if self.box_enabled and box_column == None:
            return False

        if cell_column.covered == False:
            if row_column.covered == False:
                if column_column.covered == False:
                    if not self.box_enabled or box_column.covered == False:
                        return True
        return False



class Thinking():
    def __init__(self):
        self.count = 0
        
    def end(self):
        print()
    
    def print(self):
        if self.count == 0:
            print("\r|", end="")
        elif self.count == 1:
            print("\r/", end="")
        elif self.count == 2:
            print("\r-", end="")
        elif self.count == 3:
            print("\r\\", end="")
        self.count += 1
        self.count = self.count % 4
        
                    
                


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
