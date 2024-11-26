from ast import Lambda
from cgi import test
from curses.ascii import isdigit
from math import sqrt
from dancingLinkNode import DancingLinkNode, DancingLinks
from collections import namedtuple
from collections import defaultdict
from itertools import combinations

class SudokuStrategy(namedtuple("SudokuStrategy", ["name", "test"])):
    # Define equality, hash based on 'name' attribute
    def __eq__(self, other):
        if isinstance(other, SudokuStrategy):
            return self.name == other.name
        return False

    def __hash__(self):
        return hash(self.name)


class SudokuMove:
    def __init__(self, unsatisfied_constraints, strategies):
        self.unsatisfied_constraints = unsatisfied_constraints
        
        self.move_column = 0
        for column_size in reversed(list(self.unsatisfied_constraints.keys())):
            column_list = self.unsatisfied_constraints[column_size]
            if len(column_list) > 0:
                self.move_column = column_size
                break

        if self.move_column > 0:
            self.column = self.unsatisfied_constraints[self.move_column].pop()
            self.satisfied_constraints = {self.column.name}
            self.node = self.column 
        else:
            pass
        self.strategies = strategies
        self.original_number_of_constraints = len(self.unsatisfied_constraints)

        # unsatisfied_constraint = unsatisfied_constraints.pop()
        # # we are starting with the header on top; the first move will be next()
        # self.node = unsatisfied_constraint
        # self.column = unsatisfied_constraint.down.column
        # self.unsatisfied_constraints = list(unsatisfied_constraints)
        # self.original_number_of_constraints = len(self.unsatisfied_constraints)
        # self.satisfied_constraints = {self.column.name}
        # self.name = self.column.name

    # Define equality, hash based on 'name' attribute
    def __eq__(self, other):
        if isinstance(other, SudokuMove):
            return self.name == other.name
        return False

    def __hash__(self):
        return hash(self.name)

    def next(self):

        # if len(self.unsatisfied_constraints) > 0:
        #     self.node = self.unsatisfied_constraints.pop()
        #     self.column = self.node.column
        #     self.name = self.node.data.name
        # else:
        #     self.node = None
        #         while not all([strategy.test(self.node.data) for strategy in self.strategies]):

        while True:
            self.node = self.node.down

            # we've hit the bottom of the nodes for this constraint
            while self.node == self.column:
                self.move_column = 0
                for column_size in self.unsatisfied_constraints:
                    column_list = self.unsatisfied_constraints.get(column_size,[])
                    if len(column_list) > 0:
                        self.move_column = column_size
                if self.move_column > 0:
                    self.column = self.unsatisfied_constraints[self.move_column].pop()
                    self.satisfied_constraints = {self.column.name}
                    self.node = self.column.down 
                else:
                    self.node = None


            if self.node != None:
                self.name = self.node.data.name
                if all([strategy.test(self.node.data) for strategy in self.strategies]):
                    return
            else:
                self.column = None
                self.name = "failed"
                return


class Sudoku:
    def __init__(self, board):
        self.Node = namedtuple("SudokuNode", ["row", "column", "number", "name"])
        self.Move = namedtuple(
            "SudokuMove",
            ["node", "column", "unsatisfied_constraints", "satisfied_constraints"],
        )
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
        self.box_enabled = (self.box_size**2) == self.N
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

    def get_box(self, row_index, col_index):
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
        for row_index in range(1, self.N + 1):
            for col_index in range(1, self.N + 1):
                possibilities.add_column(
                    self.cell_constraint_name.format(row_index, col_index)
                )

        for row_index in range(1, self.N + 1):
            for number in range(1, self.N + 1):
                possibilities.add_column(self.row_number_name.format(row_index, number))

        for col_index in range(1, self.N + 1):
            for number in range(1, self.N + 1):
                possibilities.add_column(
                    self.column_number_name.format(col_index, number)
                )

        if self.box_enabled:
            for box in range(1, self.N + 1):
                for number in range(1, self.N + 1):
                    possibilities.add_column(self.box_number_name.format(box, number))

        for row_index in range(1, self.N + 1):
            for col_index in range(1, self.N + 1):
                cell_name = self.cell_constraint_name.format(row_index, col_index)
                for number in range(1, self.N + 1):
                    #                    think.print()
                    name = f"R{row_index}C{col_index}#{number}"

                    node = self.Node(row_index, col_index, number, name)
                    # Cell constraint: Only one number per cell
                    possibilities.add_node(cell_name, node)

                    # Row constraint: Only one of each number per row
                    possibilities.add_node(
                        self.row_number_name.format(row_index, number), node
                    )

                    # Column constraint: Only one of each number per column
                    possibilities.add_node(
                        self.column_number_name.format(col_index, number), node
                    )

                    # # Box constraint: Only one of each number per box
                    if self.box_enabled:
                        box = self.get_box(row_index, col_index)
                        possibilities.add_node(
                            self.box_number_name.format(box, number), node
                        )

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
                node = self.Node(row_index + 1, col_index + 1, number, name)
                move = self.Move(DancingLinkNode(node), None, None, set())
                spaces_on_board -= 1
                self.make_move(move)
        self.possibilities.debug_show_column_stats()

        possibilities = self.possibilities
        # sort on start
        possibilities.sort_columns_by_size()

        self.starting_strategies = set()
        self.current_strategies = set()
        
        current_strategies = self.get_current_strategies()
        self.starting_strategies.update(set(current_strategies))
        for strategy in list(self.starting_strategies):
            print(f"starting_strategy {strategy.name}")

        self.print_setup(self.current_strategies)

        self.moves_left = spaces_on_board
        print(
            f"Moves left on board: {self.N * self.N} - {self.N * self.N - self.moves_left} = {self.moves_left}"
        )

    def get_counts_for_moves_left(self, strategies):
        if not self.box_enabled:
            return None, None, None
        # cell_candidates = [[[[] for _ in range(self.N)] for _ in range(self.N)] for _ in range(self.N)]
        # box_candidates = [[[[] for _ in range(self.box_size)] for _ in range(self.box_size)] for _ in range(self.N)]
        col_count = [[[] for _ in range(self.N)] for _ in range(self.N)]
        row_count = [[[] for _ in range(self.N)] for _ in range(self.N)]
        box_count = [[[] for _ in range(self.N)] for _ in range(self.N)]

        rejected = []

        for move in self.possibilities.column_nodes(self.possibilities.header):
            row = move.data.row
            col = move.data.column
            number = move.data.number
            box = self.get_box(row, col)

            if all([strategy.test(move.data) for strategy in strategies]):
                row_count[row - 1][number - 1].append((row, col))
                col_count[col - 1][number - 1].append((row, col))
                box_count[box - 1][number - 1].append((row, col))
            else:
                rejected.append((row, col))
        return row_count, col_count, box_count, set(rejected)
    
    def get_current_strategies(self):
        self.possibilities.sort_columns_by_size()
        row_count, col_count, box_count, rejected = self.get_counts_for_moves_left(self.current_strategies)
        strategy_actions = list(self.get_strategies(row_count, col_count, box_count))
        self.current_strategies.update(set(strategy_actions))
        rejected_size = -1
        strategy_size = -1
        while rejected_size != len(rejected) or strategy_size != len(strategy_actions):
            rejected_size = len(rejected)
            row_count, col_count, box_count, rejected = self.get_counts_for_moves_left(self.current_strategies)
            strategy_size = len(strategy_actions)
            strategy_actions = self.get_strategies(row_count, col_count, box_count)
            self.current_strategies.update(set(strategy_actions))

        return self.current_strategies

            
        

    def get_strategies(self, row_count, col_count, box_count):
        strategies = self.get_pointing_pairs_and_triples(
            row_count, col_count, box_count
        )
        strategies = strategies.union(
            self.get_hidden_pairs(row_count, col_count, box_count)
        )
        strategies = strategies.union(
            self.get_naked_pairs(row_count, col_count, box_count)
        )        
        strategies = strategies.union(
            self.get_Y_wing_XY_wing(row_count, col_count, box_count)
        )        
        
        
        return strategies

    def get_hidden_pairs(self, row_count, col_count, box_count):
        strategy_actions = set()
        for group in col_count:
            strategy_actions = strategy_actions.union( self.get_hidden_pairs_in_group(group) )
        for group in row_count:
            strategy_actions = strategy_actions.union( self.get_hidden_pairs_in_group(group) )
        for group in box_count:
            strategy_actions = strategy_actions.union( self.get_hidden_pairs_in_group(group) )
        return strategy_actions

    def get_hidden_pairs_in_group(self, group):
        candidates = {}
        strategy_actions = set()

        def identical_cells(cell_0, cell_1):
            return cell_0[0] == cell_1[0] and cell_0[1] == cell_1[1]

        def hidden_pair_in_cells(data, n0, n1, c0, c1):
            cell = (data.row, data.column)
            number = data.number
            return (cell != c0 and cell != c1) or (number == n0 or number == n1)

        for number, number_placements in enumerate(group):
            if len(number_placements) == 2:
                candidates[number] = number_placements
        while len(candidates) > 1:
            test_subject_number = next(iter(candidates))
            test_subject = candidates.pop(test_subject_number)
            test_cell_0 = test_subject[0]
            test_cell_1 = test_subject[1]
            # print(test_cell_0)
            # print(test_cell_1)

            for candidate_number in iter(candidates):
                candidate_cell_0 = candidates[candidate_number][0]
                candidate_cell_1 = candidates[candidate_number][1]
                # print(candidate_cell_0)
                # print(candidate_cell_1)
                if (
                    identical_cells(test_cell_0, candidate_cell_0)
                    and identical_cells(test_cell_1, candidate_cell_1)
                ) or (
                    identical_cells(test_cell_0, candidate_cell_1)
                    and identical_cells(test_cell_1, candidate_cell_0)
                ):
                    number_0 = min(test_subject_number, candidate_number) + 1
                    number_1 = max(test_subject_number, candidate_number) + 1
                    test_subject = sorted(test_subject)
                    name = f"Hidden pair: {test_subject}, numbers {number_0}/{number_1}"
                    # print(name)
                    strategy = SudokuStrategy(
                        name,
                        lambda data, n0=number_0, n1=number_1, c0=test_subject[
                            0
                        ], c1=test_subject[1]: (
                            hidden_pair_in_cells(data, n0, n1, c0, c1)
                        ),
                    )
                    strategy_actions.add(strategy)
        return strategy_actions
    
    def get_naked_pairs(self, row_count, col_count, box_count):
        strategy_actions = set()
        for group in col_count:
            strategy_actions = strategy_actions.union( self.get_naked_pairs_in_group(group) )
        for group in row_count:
            strategy_actions = strategy_actions.union( self.get_naked_pairs_in_group(group) )
        for group in box_count:
            strategy_actions = strategy_actions.union( self.get_naked_pairs_in_group(group) )
        return strategy_actions
    
    def get_naked_pairs_in_group(self, group):
        candidates = {}
        strategy_actions = set()

        def identical_cells(cell_0, cell_1):
            return cell_0[0] == cell_1[0] and cell_0[1] == cell_1[1]

        def naked_pair_in_cells(data, n0, n1, c0, c1):
            cell = (data.row, data.column)
            number = data.number
            return (cell != c0 and cell != c1) or (number == n0 or number == n1)
        
        pair_to_lists = defaultdict(set)
        for n, sublist in enumerate(group):
            number = n + 1
            for pair in sublist:
                if len(sublist) == 2:
                    pair_to_lists[pair].add(number)

        number_pairs = defaultdict(list)

        pairs_in_two_lists = []
        for (pair1, lists1), (pair2, lists2) in combinations(pair_to_lists.items(), 2):
            # Find common lists where both pairs appear
            common_lists = lists1 & lists2
            if len(common_lists) == 2:
                numbers = tuple(sorted(list(common_lists)))
                pairs_in_two_lists.append({
                    "pairs": (pair1, pair2),
                    "numbers": numbers,
                })            
                number_pairs[numbers].append((pair1, pair2))
                
        for numbers in number_pairs:
            number_pair = number_pairs[numbers]
            if len(number_pair) == 1:
                good = True
                for candidate in number_pairs:
                    if candidate == numbers:
                        continue
                    if any(elem in candidate for elem in numbers):
                        good = False
                if good:
                    name = f"Naked pair {numbers} can only be in {number_pair[0]} "
                    print(name)
                    strategy = SudokuStrategy(
                        name,
                        lambda data, n0=numbers[0], n1=numbers[1], c0=number_pair[0][0], c1=number_pair[0][1]: (
                            naked_pair_in_cells(data, n0, n1, c0, c1)
                        ),
                    )
                    strategy_actions.add(strategy)                    
    
        return strategy_actions


    def get_pointing_pairs_and_triples(self, row_count, col_count, box_count):
        strategy_actions = set()
        if box_count == None:
            return strategy_actions

        cell_row = 0
        cell_column = 1
        for b in range(self.N):
            for n in range(self.N):
                # list indices are -1 from actual values
                number = n + 1
                box = b + 1
                box_contents = box_count[b][n]
                occurance = len(box_contents)
                column_name = None
                if (
                    occurance == 2
                    and box_contents[0][cell_row] == box_contents[1][cell_row]
                ) or (
                    occurance == 3
                    and box_contents[0][cell_row]
                    == box_contents[1][cell_row]
                    == box_contents[2][cell_row]
                ):
                    row_index = box_contents[0][cell_row]
                    if len(row_count[row_index - 1][n]) > occurance:
                        name = f"Pointing Pair {number} row {row_index} and box:{box}:({occurance})"
                        # print(name)
                        strategy = SudokuStrategy(
                            name,
                            lambda data, n=number, row_id=row_index, box_id=box: (
                                (n != data.number)
                                or (row_id != data.row)
                                or (self.get_box(data.row, data.column) == box_id)
                            ),
                        )
                        strategy_actions.add(strategy)

                elif (
                    occurance == 2
                    and box_contents[0][cell_column] == box_contents[1][cell_column]
                ) or (
                    occurance == 3
                    and box_contents[0][cell_column]
                    == box_contents[1][cell_column]
                    == box_contents[2][cell_column]
                ):
                    column_index = box_contents[0][cell_column]
                    if len(col_count[column_index - 1][n]) > occurance:
                        name = f"in column {column_index} and in box:{box}, number {number}: {box_contents} ({occurance})"
                        # print(name)
                        strategy = SudokuStrategy(
                            name,
                            lambda data, n=number, col_id=column_index, box_id=box: (
                                (n != data.number)
                                or (col_id != data.column)
                                or (self.get_box(data.row, data.column) == box_id)
                            ),
                        )
                        strategy_actions.add(strategy)
        return strategy_actions


    # row_count [row][number] = list of coords
    # number of candidates  = len(list of coords)
    def get_Y_wing_XY_wing(self, row_count, col_count, box_count):

        strategy_actions = set()
        
        # Step 1: Identify cells with two candidate numbers
        filtered_data = {}
        for row_idx, row_data in enumerate(row_count):
            for number, coords in enumerate(row_data):
                for coord in coords:
                    filtered_data.setdefault(coord, []).append(number+1)

        # Optionally filter further: keep entries where numbers associated with a coord are exactly 2
        candidates = {coord: numbers for coord, numbers in filtered_data.items() if len(numbers) == 2}
        
        if len(candidates) < 3: 
            # Y_wing needs three coords: pivot and two pincers
            return set()
        if (1,1) in candidates:
            if (1,5) in candidates:
                if (3,6) in candidates:
                    print()

        def cell_sees_cell(a, b):
            x, y, = a
            x1, y1 = b
            box_a = self.get_box(x, y)
            if ((x != x1) and (y != y1) and (self.get_box(*b) != box_a)):
                return False
            return True

        def get_pincer_candidates(pivot, pivot_numbers, candidates):
            pincer_candidates = {}
            pivot_box = self.get_box(*pivot)
            
            keys = list(candidates.keys())

            # Iterate over the keys by index
            for i in range(len(keys)):
                pincer_candidate1 = keys[i]
                candidate1_numbers = candidates[pincer_candidate1]
                if pincer_candidate1 == pivot:
                    continue
                if not cell_sees_cell(pincer_candidate1, pivot):
                    continue
                if len([n for n in candidate1_numbers if n in pivot_numbers]) != 1:
                    continue
                pincer_candidates.update({pincer_candidate1:candidate1_numbers})
            return pincer_candidates

        # Step 2: Iterate through potential pivots
        pivot_pincers = []
        for pivot, pivot_numbers in candidates.items():
            print(f"Y_wing {pivot}: {pivot_numbers}")
            pincer_candidates = get_pincer_candidates(pivot, pivot_numbers, candidates)
            if len(pincer_candidates) < 2:
                continue
            print(f"pivot: {pivot}:{pivot_numbers} pincers:{pincer_candidates}")
            print()
            pincer_candidate_coords = list(pincer_candidates.keys())
            key_count = len(pincer_candidate_coords)

            # get pincer pairs
            for i in range(key_count):
                for j in range(i+1, key_count):
                    pincer_candidate1 = pincer_candidate_coords[i]
                    pincer_candidate2 = pincer_candidate_coords[j]
                    if cell_sees_cell(pincer_candidate1, pincer_candidate2):
                        continue
                    pincer_candidate1_numbers = candidates[pincer_candidate1]
                    pincer_candidate2_numbers = candidates[pincer_candidate2]
                    z_list = [n for n in pincer_candidate1_numbers if n in pincer_candidate2_numbers]
                    if len(z_list) != 1:
                        continue
                    z = z_list[0]
                    x = [n for n in pincer_candidate1_numbers if n in pivot_numbers][0]
                    y = [n for n in pincer_candidate2_numbers if n in pivot_numbers][0]
                    if x == y or x == z or y == z:
                        continue
                    pivot_pincers.append({pivot:[pincer_candidate1,pincer_candidate2]})
                    

        def y_wing_cell_number(data, c0, c1, z):
            cell = (data.row, data.column)
            number = data.number
            # can't see both the pincers or not the z number
            return number != z or not cell_sees_cell(c0, cell) or not cell_sees_cell(c1, cell)

        if len(pivot_pincers) > 0:
            print(f"pivot_pincers: {pivot_pincers}")
            for y_wing in pivot_pincers:
                for pivot, pivot_pincer_pair in y_wing.items():
                    z_list = [n for n in candidates[pivot_pincer_pair[0]] if n in candidates[pivot_pincer_pair[1]]]
                    print(f"pivot: {pivot} {candidates[pivot]} Z:{z_list[0]}")
                    print(f"\t pincer1:{pivot_pincer_pair[0]}  {candidates[pivot_pincer_pair[0]]}")
                    print(f"\t pincer2:{pivot_pincer_pair[1]}  {candidates[pivot_pincer_pair[1]]}")
                    
                    name = f"Y-Wing (XY-Wing) pivot: {pivot} pincers: {pivot_pincer_pair}"
                    print(name)
                    strategy = SudokuStrategy(
                        name,
                        lambda data, c0=pivot_pincer_pair[0], c1=pivot_pincer_pair[1], z=z_list[0]: (
                            y_wing_cell_number(data, c0, c1, z)
                        ),
                    )
                    strategy_actions.add(strategy)    
        return strategy_actions


    def debug_print_cells(self, solution, strategies=set()):
        row_count, col_count, box_count, rejected = self.get_counts_for_moves_left(strategies)
        board, _, _ = self.solution_to_board(solution)
        print("    " + "   ".join(str(i) for i in range(1, 10)))
        print("  ┌───┬───┬───╥───┬───┬───╥───┬───┬───┐")
        for row in range(1, self.N + 1):
            self.debug_print_row(row, row_count, board, strategies)
            if row == 9:
                print("  └───┴───┴───┴───┴───┴───┴───┴───┴───┘")  # ╨ ╞ ═ ╪ ╡╬
            elif row == 3 or row == 6:
                print("  ╞═══╪═══╪═══╬═══╪═══╪═══╬═══╪═══╪═══╡")
            else:
                print("  ├───┼───┼───╫───┼───┼───╫───┼───┼───┤")

    def debug_print_row(self, row, row_count, board, strategies=set()):
        board_row = board[row - 1]
        box_top = "┌─┐"
        box_bottom = "└─┘"
        for i in range(3):
            if i == 1:
                print(f"{row} │", end="")
            else:
                print("  │", end="")
            for col in range(9):
                column = col + 1
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
                        number = j + i * 3 + 1
                        if (row, column) in row_count[row - 1][number - 1]:
                            data = self.Node(row, column, number, "")
                            if strategies == None or all(
                                [strategy.test(data) for strategy in strategies]
                            ):
                                print(f"{number}", end="")
                            else:
                                print("·", end="")
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

    def print_setup(self, strategies=None):
        board, blanks, errors = self.solution_to_board([])

        self.print_solution_from_board(board, [])
        self.debug_print_cells([], strategies)

    def print_moves_and_solution(self, solution, strategies=set()):
        board, blanks, errors = self.solution_to_board(solution)
        self.print_moves(solution)
        for i in range(len(solution), self.moves_left):
            print(f"Move {i:10}:  ")

        self.print_solution_from_board(board, solution)
        self.debug_print_cells(solution, strategies)

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
                node = self.Node(row_index + 1, col_index + 1, number, name)
                board[row_index][col_index] = str(number)

        column_names = []
        for current_column in self.possibilities.uncovered_columns():
            column_names.append(current_column.name)

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
        board, _, _ = self.solution_to_board(solution)
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
            changed = (
                "*"
                if len(move.unsatisfied_constraints)
                != move.original_number_of_constraints
                else " "
            )
            if len(self.solution_move_names) > 0:
                if move.node.data.name in self.solution_move_names:
                    right_or_wrong = "Right"
                else:
                    right_or_wrong = "Wrong"
            print(
                f"Move {index:10}: {move.node.data.name}: UC:{len(move.unsatisfied_constraints):6}{changed} {right_or_wrong}"
            )

    def solve_puzzle(self, solution=[], solution_moves=None):

        solution_move_names = []
        if solution_moves != None:
            for move in solution_moves:
                solution_move_names.append(move.name)

        self.solution_move_names = solution_move_names

        self.start_solution(solution, solution_moves)
        think = Thinking()

        while self.solved == False:
            # think.print()
            self.work_on_solution()

        for solution in self.solutions:
            self.print_setup()
            # for move in solution:
            #     print(f"Move {move.node.data.name} {move.column.name} ")
            self.print_solution(solution)

    def start_solution(self, solution=[], solution_moves=None):
        self.debug_solution_moves = solution_moves

        if self.debug_solution_moves  != None:
            for data in self.debug_solution_moves:
                if not all([strategy.test(data) for strategy in self.starting_strategies]):
                    print(f" strategy is blocking solution!")



        self.starting_move = self.get_move(solution)

        self.solutions.append(solution)
        self.solved = False
        
    def get_move(self, solution):
        satisfied_constraints = self.get_satisfied_constraints(solution)
        unsatisfied_constraints = self.get_unsatisfied_constraints(satisfied_constraints)
        win = self.check_win(solution, unsatisfied_constraints)
        if len(unsatisfied_constraints.get(1,[])) == 0:
            unsatisfied_constraints = self.get_modified_unsatisfied_constraints(satisfied_constraints, self.current_strategies)

        return SudokuMove(unsatisfied_constraints, self.current_strategies), win

    def check_win(self, solution, unsatisfied_constraints):
        if all(len(unsatisfied_constraints[key])==0 for key in unsatisfied_constraints.keys()):
            self.solutions.append(solution)
            self.solved = True
            print("")
            return True
        return False

        
    def work_on_solution(self):
        possibilities = self.possibilities
        solution = self.solutions.pop()

        move, win = self.get_move(solution)

        if win == True:
            return

        # if move.node.data.name not in self.solution_move_names:
        #     pass

        move_ok = False
        while not move_ok:
            move.next()

            # this move is exhausted its constraints
            while move.node == None:
                if len(solution) > 0:
                    move = solution.pop()
                    self.unmake_move(move.node.data)
                    #sort when a move is made
                    possibilities.sort_columns_by_size()
                    if len(self.current_strategies)  != len(move.strategies):
                        print()
                    
                    self.current_strategies = move.strategies
                    move.next()
                # there are no previous moves
                else:
                    # unsolvable
                    print("\n!!!!!!! no solutions possible! !!!!!!!!")
                    self.print_setup()
                    self.solved = True
                    return


            self.make_move(move)

            column_with_no_solution = self.get_column_with_no_solution()
            move_ok = column_with_no_solution == None


            # if len(self.solution_move_names) > 0:
            #     if move.name in self.solution_move_names:
            #         right_or_wrong = "Right"
            #     else:
            #         if not all([strategy.test(move.node.data) for strategy in self.starting_strategies]):
            #             print(f" strategy disallowed move!")                    
            #         right_or_wrong = "Wrong"
            #         move_ok = False


            if move_ok:
                solution.append(move)
                current_strategies = self.get_current_strategies()
                for strategy in sorted(list(current_strategies)):
                    print(f"current_strategies {strategy.name}")
                if self.debug_solution_moves  != None:
                    for data in self.debug_solution_moves:
                        if not all([strategy.test(data) for strategy in self.starting_strategies]):
                            print(f" strategy is blocking solution!")


            if not move_ok:
                # self.print_moves_and_solution(solution)
                # print(f"If I play {move.name} I lose {column_with_no_solution.name}")
                self.unmake_move(move.node.data)

        # for move in solution:
        #     print(f"Move {move.node.data.name} {move.column.name} ")
        #        possibilities.print()
        self.print_moves_and_solution(solution, self.current_strategies)
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

        covered_cell = possibilities.cover_column(
            possibilities.find_column_header(covered_cell_name)
        )
        covered_column_number = possibilities.cover_column(
            possibilities.find_column_header(covered_column_name)
        )
        covered_row_number = possibilities.cover_column(
            possibilities.find_column_header(covered_row_name)
        )

        if self.box_enabled:
            box = self.get_box(row_index, col_index)
            covered_box_name = self.box_number_name.format(box, number)
            move.satisfied_constraints.add(covered_box_name)
            covered_box_number = possibilities.cover_column(
                possibilities.find_column_header(covered_box_name)
            )

    def unmake_move(self, move):
        possibilities = self.possibilities
        #        possibilities.print()
        #       print (f"unmaking move: {move}")
        row_index = move.row
        col_index = move.column
        number = move.number

        if self.box_enabled:
            box = self.get_box(row_index, col_index)
            covered_box_number = possibilities.uncover_column(
                possibilities.find_column_header(
                    self.box_number_name.format(box, number)
                )
            )
        covered_row_number = possibilities.uncover_column(
            possibilities.find_column_header(
                self.row_number_name.format(row_index, number)
            )
        )
        covered_column_number = possibilities.uncover_column(
            possibilities.find_column_header(
                self.column_number_name.format(col_index, number)
            )
        )
        covered_cell = possibilities.uncover_column(
            possibilities.find_column_header(
                self.cell_constraint_name.format(row_index, col_index)
            )
        )

    def get_satisfied_constraints(self, solution):
        possibilities = self.possibilities
        satisfied_constraints = set()
        for move in solution:
            satisfied_constraints = satisfied_constraints.union(
                move.satisfied_constraints
            )
        return satisfied_constraints

    def get_unsatisfied_constraints(self, satisfied_constraints):
        possibilities = self.possibilities
        uc = {i: [] for i in range(9, -1, -1)}

        for columns_size in self.possibilities.columns_by_size:
            for column in self.possibilities.columns_by_size[columns_size]:
                if column.name not in satisfied_constraints:
                    uc[column.size].append(column)
        return uc

    def get_modified_unsatisfied_constraints(self, satisfied_constraints, strategies):

        # columns_by_size[size of the node lists following] list of node headers
        # we build a modified list of nodes only
        possibilities = self.possibilities
        uc = {i: [] for i in range(9, -1, -1)}

        rejected = []
        for columns_size in self.possibilities.columns_by_size:
            for column in self.possibilities.columns_by_size[columns_size]:
                if column.name not in satisfied_constraints:
                    node_list = []
                    failed_tests = False
                    for node in self.possibilities.column_nodes(column):
                        if all([strategy.test(node.data) for strategy in strategies]):
                            node_list.append(node)
                        else:
                            failed_tests = True

                    size = len(node_list)
                    if failed_tests:
                        # print (f"altered in size {size} number {len(uc.get(size, []))}")
                        pass
                    sized_node_lists = uc.get(size, [])
                    sized_node_lists.append(column)
                    uc[size] = sized_node_lists
        if len(uc.get(0, [])) > 0:
            pass
            #print(f"unsolvable?")  # not likely
        # this is just nodes, and storeage is high;
        # I can use size to reorder altered lists, and do this strategy checking inside the move
        # saving storage space, but doing strategies tw1ce (once here, once in move.next())
        return uc

    def get_column_with_no_solution(self):
        for column_header in self.possibilities.uncovered_columns():
            if column_header.size == 0:
                return column_header
        return None

    def debug_can_i_place(self, placement):
        row_index = placement.row
        col_index = placement.column
        number = placement.number
        cell_name = self.cell_constraint_name.format(row_index, col_index)
        cell_column = self.possibilities.find_uncovered_column_header(cell_name)

        row_name = self.row_number_name.format(row_index, number)
        row_column = self.possibilities.find_uncovered_column_header(row_name)

        column_name = self.column_number_name.format(col_index, number)
        column_column = self.possibilities.find_uncovered_column_header(column_name)

        if self.box_enabled:
            box = self.get_box(row_index, col_index)
            box_name = self.box_number_name.format(box, number)
            box_column = self.possibilities.find_uncovered_column_header(box_name)

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


class Thinking:
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
