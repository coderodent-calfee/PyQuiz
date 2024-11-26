from collections import namedtuple
from locale import currency
import bisect


class DancingLinkNode:
    def __init__(self, data=None):
        self.data = data  # Stores the data value (optional)
        self.left = None  # Pointer to the previous node in the row
        self.right = None  # Pointer to the next node in the row
        self.up = None  # Pointer to the node above in the column
        self.down = None  # Pointer to the node below in the column
        self.column = None  # Reference to the column header (optional)


class ColumnHeader:
    def __init__(self, name):
        self.name = name  # Name of the column (for identification)
        self.size = 0  # The number of nodes in this column
        self.left = None  # Pointer to the previous column header
        self.right = None  # Pointer to the next column header
        self.up = None  # Pointer to the node above in the column
        self.down = None  # Pointer to the node below in the column
        self.covered = False


class DancingLinks:
    def __init__(self):
        self.header = ColumnHeader(
            "Header"
        )  # The header node that contains all column headers
        self.header.left = self.header  # Circularly link the header
        self.header.right = self.header
        self.header.down = self.header
        self.header.up = self.header
        self.columns = []  # List of column headers (for easier access)
        self.columns_by_size = {}
        self.debug = False
        
    def uncovered_columns(self):
        column_header = self.header.right
        while column_header != self.header:
            yield column_header
            column_header = column_header.right

    def column_nodes(self, column_header):
        current = column_header.down
        while current != column_header:
            yield current
            current = current.down


    def debug_show_column_stats(self):
        
        print("debug_show_column_stats")
        uncovered_columns = list(self.uncovered_columns())

        max_size_column = max(uncovered_columns, key=lambda item: item.size)

        columns_by_size = {i: [] for i in range(max_size_column.size, -1, -1)}
        for column in uncovered_columns:
            columns_by_size[column.size].append(column)
        for size, columns in columns_by_size.items():
            print(f"size: {size}:", end="")
            for column in columns:
                print(f" {column.name}", end="")
            print()

        print()

    def sort_columns_by_size(self):
        uncovered_columns = []
        max_size_column = self.header.right
        min_size_column = self.header.right

        for current_column in self.uncovered_columns():
            uncovered_columns.append(current_column)
            if max_size_column.size < current_column.size:
                max_size_column = current_column
            if min_size_column.size > current_column.size:
                min_size_column = current_column
        total_uncovered_columns_left = len(uncovered_columns)

        columns_by_size = {i: [] for i in range(max_size_column.size, -1, -1)}
        for column in uncovered_columns:
            columns_by_size[column.size].append(column)

        self.columns_by_size = columns_by_size
        # self.print_columns_by_size()
        return columns_by_size

    def get_ordered_uncovered(self):
        ordered_uncovered = []
        for size in self.columns_by_size.keys():
            ordered_uncovered += self.columns_by_size[size]
        return ordered_uncovered

    def print_columns_by_size(self):
        columns_by_size = self.columns_by_size
        print("columns_by_size")
        for size, columns in columns_by_size.items():
            self.print_single_column_by_size(size)
            print()

    def print_single_column_by_size(self, size):
        columns_by_size = self.columns_by_size
        columns = columns_by_size[size]
        print(f"size: {size}:", end="")
        if size <= 2:
            for column in columns:
                print(f" {column.name}", end="")
                node = column.down
                while node != column:
                    print(f"({node.data.name})", end="")
                    node = node.down
        else:
            for column in columns:
                print(f" {column.name}", end="")

    # Add a new column header to the Dancing Links structure
    def add_column(self, name):
        old_column = self.find_column_header(name)
        if old_column != None:
            return old_column
        new_column = ColumnHeader(name)
        self.columns.append(new_column)
        # Link the new column into the header list
        new_column.left = self.header.left
        new_column.right = self.header

        self.header.left.right = new_column
        self.header.left = new_column
        new_column.down = new_column
        new_column.up = new_column

        self.check_columns()

        return new_column

    def check_columns(self):
        if self.debug == False:
            return
        total_columns = len(self.columns)

        uncovered_columns = list(self.possibilities.iterate_uncovered_columns())
        total_uncovered_columns = len(uncovered_columns)

        uncovered_columns = []
        current_column = self.header.left
        while current_column != self.header:
            uncovered_columns.append(current_column)
            current_column = current_column.left
        total_uncovered_columns_left = len(uncovered_columns)

        if total_uncovered_columns_left != total_uncovered_columns:
            print(
                f"right {total_uncovered_columns} does not equal left covered {total_uncovered_columns_left}"
            )

        covered_columns = []
        for current_column in self.columns:
            if current_column.covered:
                covered_columns.append(current_column)
        total_covered_columns = len(covered_columns)

        if total_columns != total_covered_columns + total_uncovered_columns:
            print(
                f"Covered {total_covered_columns} + Uncovered {total_uncovered_columns} does not equal total {total_columns}"
            )

        for current_column in self.columns:
            rows_in_column = 0
            current_node = current_column.down
            while current_node != current_column:
                rows_in_column += 1
                current_node = current_node.down
            if rows_in_column != current_column.size:
                print(
                    f"in column {current_column.name} found {rows_in_column} rows and has size {current_column.size}"
                )

    def increment_column_size(self, column_header):
        column_header.size += 1

    def decrement_column_size(self, column_header):
        column_header.size -= 1

    def find_column_header(self, column_name):
        for column in self.columns:
            if column.name == column_name:
                return column
        return None

    def find_uncovered_column_header(self, column_name):
        for current_column in self.uncovered_columns:
            if current_column.name == column_name:
                return current_column
        return None

    def find_covered_column_header(self, column_name):
        for column in self.columns:
            if column.name == column_name:
                if column.covered == False:
                    return None
                return column
        return None


    def find_row_header(self, row_name):
        # Search all columns for a node with the row_name
        row_header = self.header.down
        while row_header != self.header:
            if row_header.name == row_name:
                return row_header
            row_header = row_header.down

        return None  # Row node with the given name not found

    # Add a new node to the matrix, connecting it to appropriate column and row
    def add_node(self, column_name, data=None, row_name=None):
        self.check_columns()
        column_header = self.find_column_header(column_name)
        if column_header == None:
            column_header = self.add_column(column_name)

        name = row_name

        if data != None:
            name = f"R{data.row}C{data.column}#{data.number}"  # used as row identifier
        else:
            data = namedtuple("Node", ["row", "column", "number", "name"])
            data.name = row_name

        new_node = DancingLinkNode(data)
        new_node.column = column_header
        # Link the new node into the column
        new_node.up = column_header.up
        new_node.down = column_header
        column_header.up.down = new_node
        column_header.up = new_node

        self.insert_into_row(new_node)

        self.increment_column_size(column_header)
        self.check_columns()
        return new_node

    def insert_into_row(self, new_node):
        name = new_node.data.name
        # Todo: improve find_row_node (maybe put a header on it)
        row_node = self.find_row_header(name)

        if row_node == None:
            row_node = self.add_row_header(new_node.data)

        # print(f"found row {name}")
        new_node.left = row_node.left
        new_node.right = row_node
        row_node.left.right = new_node
        row_node.left = new_node

    def add_row_header(self, data):
        row_name = data.name
        new_header = DancingLinkNode(data)
        new_header.name = row_name
        new_header.right = new_header
        new_header.left = new_header

        # Link into row header list (below the matrix header)
        new_header.down = self.header.down
        new_header.up = self.header
        self.header.down.up = new_header
        self.header.down = new_header

        return new_header

    # Cover a column (removing it from the grid temporarily)
    def cover_column(self, column_header):
        if column_header == self.header:
            print("AURGH!")
            return None
        self.check_columns()
        column_header.covered = True
        column_header.right.left = column_header.left
        column_header.left.right = column_header.right

        # Remove all rows in this column (cover the column)
        row_node = column_header.down
        while row_node != column_header:
            right_node = row_node.right
            while right_node != row_node:
                right_node.up.down = right_node.down
                right_node.down.up = right_node.up
                if right_node.column != None:
                    self.decrement_column_size(right_node.column)
                right_node = right_node.right
            row_node = row_node.down
        self.check_columns()
        return column_header

    # Uncovering a column (putting it back into the grid)
    def uncover_column(self, column_header):
        self.check_columns()
        row_node = column_header.up
        while row_node != column_header:
            left_node = row_node.left
            while left_node != row_node:
                if left_node.column != None:
                    self.increment_column_size(left_node.column)
                left_node.up.down = left_node
                left_node.down.up = left_node
                left_node = left_node.left
            row_node = row_node.up
        column_header.right.left = column_header
        column_header.left.right = column_header
        column_header.covered = False
        self.check_columns()
        return column_header

    def print_covered(self, covered_column):
        # Step 1: Collect all distinct row names
        row_name_set = set()  # Use a set to ensure unique row names

        # Traverse all columns and add all row names to the set
        for current_column in self.columns:
            for current_node in self.column_nodes(current_column):
                row_name_set.add(current_node.data.name)  # Add row name to the set

        row_names = sorted(row_name_set)

        # Step 2: collect column headers
        column_names = []
        for current_column in self.columns:
            column_names.append(current_column.name)
            current_column = current_column.right

        # Print column headers
        max_length = max(len(header) for header in column_names)
        max_length += 2
        for i in range(max_length):
            row = "        "
            for header_column in self.columns:
                header = f" {header_column.name}│"
                # Print the character if it exists, else print a space
                space_char = " "
                if header_column.covered:
                    if i == 0:
                        space_char = "┌"
                    elif i == max_length - 1:
                        space_char = "└"
                    else:
                        space_char = "│"
                row += space_char

                row += header[i] if i < len(header) else " "
                if header_column.covered:
                    if i == 0:
                        space_char = "┐"
                    elif i == max_length - 1:
                        space_char = "┘"
                row += space_char
            print(row)

        print("        " + "─┴─" * len(column_names))

        # Step 3: Iterate over all row names and print their respective nodes
        for row_name in row_names:
            covered = False
            # Find the first node for the row
            row_node = self.find_row_header(row_name)
            if row_node is None:
                for current_column in self.columns:
                    for current_node in self.column_nodes(current_column):
                        if current_node.data.name == row_name:
                            row_node = current_node
                            covered = True

                    if row_node != None:
                        break
            else:
                continue

            # Create an empty row with placeholders for each column
            row = f"{row_name: <8}"
            row_data = ["   "] * len(column_names)  # Initialize with empty spaces

            # Traverse across all columns and mark "X" where the node exists
            current_node = row_node
            column_index = column_names.index(current_node.column.name)
            row_data[column_index] = " O " if covered else " X "
            current_node = current_node.right

            while current_node != row_node:  # Horizontal traversal
                column_index = column_names.index(current_node.column.name)
                row_data[column_index] = " O " if covered else " X "
                current_node = current_node.right

            # Print the row with Xs indicating the nodes in each column
            print(row + "".join(row_data))

        print("        " + "─┴─" * len(column_names))
        print(covered_column.covered_constraints)



def test1():
    possibilities = DancingLinks()

    for char in range(ord("A"), ord("G") + 1):
        possibilities.add_column(str(chr(char)))

    possibilities.add_node("C", None, "1")
    possibilities.add_node("E", None, "1")
    possibilities.add_node("F", None, "1")

    possibilities.add_node("A", None, "2")
    possibilities.add_node("D", None, "2")
    possibilities.add_node("G", None, "2")

    possibilities.add_node("B", None, "3")
    possibilities.add_node("C", None, "3")
    possibilities.add_node("F", None, "3")

    possibilities.add_node("A", None, "4")
    possibilities.add_node("D", None, "4")

    possibilities.add_node("B", None, "5")
    possibilities.add_node("G", None, "5")

    possibilities.add_node("D", None, "6")
    possibilities.add_node("E", None, "6")
    possibilities.add_node("G", None, "6")


    covered_column = possibilities.cover_column(possibilities.find_column_header("A"))

    possibilities.uncover_column(possibilities.find_column_header("A"))



def test2():
    cell_constraint_name = "c{}/{}"
    row_number_name = "R{}#{}"
    column_number_name = "C{}#{}"
    N = 2
    Node = namedtuple("SudokuNode", ["row", "column", "number", "name"])

    possibilities = DancingLinks()

    # add early to make readable printout
    for row_index in range(1, N + 1):
        for col_index in range(1, N + 1):
            possibilities.add_column(cell_constraint_name.format(row_index, col_index))

    for row_index in range(1, N + 1):
        for number in range(1, N + 1):
            possibilities.add_column(row_number_name.format(row_index, number))

    for col_index in range(1, N + 1):
        for number in range(1, N + 1):
            possibilities.add_column(column_number_name.format(col_index, number))

    for row_index in range(1, N + 1):
        for col_index in range(1, N + 1):
            cell_name = cell_constraint_name.format(row_index, col_index)
            for number in range(1, N + 1):
                name = f"R{row_index}C{col_index}#{number}"

                node = Node(row_index, col_index, number, name)
                # Cell constraint: Only one number per cell
                possibilities.add_node(cell_name, node)

                # Row constraint: Only one of each number per row
                possibilities.add_node(row_number_name.format(row_index, number), node)

                # Column constraint: Only one of each number per column

                possibilities.add_node(
                    column_number_name.format(col_index, number), node
                )

                # # Box constraint: Only one of each number per 3x3 box
                # box_index = (row_index // 3) * 3 + (col_index // 3)
                # possibilities.add_node(f"Box-{box_index}-self.Number-{number}", node)
    possibilities.print()

    row_index = 2
    col_index = 2
    number = 2
    name = f"R{row_index}C{col_index}#{number}"
    move = Node(row_index, col_index, number, name)

    print(f"Move {move.name}")
    covered_cell = possibilities.cover_column(
        possibilities.find_column_header(
            cell_constraint_name.format(row_index, col_index)
        )
    )
    covered_column_number = possibilities.cover_column(
        possibilities.find_column_header(column_number_name.format(col_index, number))
    )
    covered_row_number = possibilities.cover_column(
        possibilities.find_column_header(row_number_name.format(row_index, number))
    )

    possibilities.print()
    possibilities.print(False)


def main():
    # Code to execute
    print("Running DancingLinks main function...")
    test1()
    test2()


if __name__ == "__main__":
    main()
