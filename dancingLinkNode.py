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
        self.header = ColumnHeader("Header")  # The header node that contains all column headers
        self.header.left = self.header  # Circularly link the header
        self.header.right = self.header
        self.header.down = self.header  
        self.header.up = self.header
        self.columns = []  # List of column headers (for easier access)
        self.sorted_columns = []  # List of column headers (for easier access)
        self.debug = False
        

    def get_size(self, item):
        return item.size

    def add_sorted_column(self, column):
        if len(self.sorted_columns) == 0:
            self.sorted_columns.append(column)
            return
        position = bisect.bisect_left([self.get_size(column) for col in self.sorted_columns], column.size)
        self.sorted_columns.insert(position, column)       

    # Remove an item from the sorted list
    def remove_sorted_column(self, column):
        try:
            self.sorted_columns.remove(column)
        except ValueError:
            print(f"Item {column.name} not found in the list.")
        return column

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
        
        self.add_sorted_column(new_column)
        self.check_columns()
        
        return new_column

    def check_columns(self):
        if self.debug == False:
            return
        total_columns = len(self.columns)
        
        uncovered_columns = []
        current_column = self.header.right
        while current_column != self.header:
            uncovered_columns.append(current_column) 
            current_column = current_column.right
        total_uncovered_columns = len(uncovered_columns)

        uncovered_columns = []
        current_column = self.header.left
        while current_column != self.header:
            uncovered_columns.append(current_column) 
            current_column = current_column.left
        total_uncovered_columns_left = len(uncovered_columns)

        if total_uncovered_columns_left !=  total_uncovered_columns:
            print (f"right {total_uncovered_columns} does not equal left covered {total_uncovered_columns_left}")

        covered_columns = []
        for current_column in self.columns:
            if current_column.covered:
                covered_columns.append(current_column) 
        total_covered_columns = len(covered_columns)
                
        if total_columns != total_covered_columns + total_uncovered_columns:
            print (f"Covered {total_covered_columns} + Uncovered {total_uncovered_columns} does not equal total {total_columns}")

        for current_column in self.columns:
            rows_in_column = 0
            current_node = current_column.down
            while current_node != current_column:
                rows_in_column += 1
                current_node = current_node.down
            if rows_in_column != current_column.size:
                print(f"in column {current_column.name} found {rows_in_column} rows and has size {current_column.size}")
    
        column_size = -1
        for column in self.sorted_columns:
            if column.covered:
                print(f" column {column.name} is in the sorted list and is COVERED ")
            if column.size > column_size: # should be increasing
                column_size = column_size
            elif column.size < column_size:
                print(f" column {column.name} has size {column.size} and is not sorted correctly (prev is {column_size})")
                



    def update_sorted_column_size(self, column_header):
        self.remove_sorted_column(column_header)
        self.add_sorted_column(column_header)
        
    
    def increment_column_size(self, column_header):
        column_header.size += 1
        self.update_sorted_column_size(column_header)

    def decrement_column_size(self, column_header):
        column_header.size -= 1
        self.update_sorted_column_size(column_header)
        

    def find_column_header(self, column_name):
        found = [index for index, column in enumerate(self.columns) if column.name == column_name]
        if len(found) > 0:
            return self.columns[found[0]]
        return None
    
    # def find_row_node(self, column_name, row_name):
    #     starting_column = self.find_column_header(column_name)
    #     current_node = starting_column.down
    #     # while current_node != starting_column:
    #     #     if current_node.data.row == row:
    #     #         # Note: this technically should not happen; only one solution per node
    #     #         # Todo: send up an error instead
    #     #         return current_node
    #     #     current_node = current_node.down

    #     current_column = starting_column.right
    #     while current_column != starting_column:
    #         current_node = current_column.down
    #         while current_node != current_column:
    #             if current_node.data.name == row_name:
    #                 return current_node
    #             current_node = current_node.down
    #         current_column = current_column.right 
    #     return None
      
    def find_row_node(self, row_name):
        # Start from any column and search all columns for a node with the row_name
        column_header = self.header.right
        while column_header != self.header:
            current_node = column_header.down
            while current_node != column_header:
                if current_node.data.name == row_name:  # Match on row name
                    return current_node  # Found the node in the row
                current_node = current_node.down
            column_header = column_header.right
        return None  # Row node with the given name not found



    # Add a new node to the matrix, connecting it to appropriate column and row
    def add_node(self, column_name, data=None, row_name=None):
        self.check_columns()
        column_header = self.find_column_header(column_name)
        if column_header == None:
            column_header = self.add_column(column_name)

        name = row_name

        if data != None:
            name = f"R{data.row}C{data.column}#{data.number}" # used as row identifier
        else:
            data =  namedtuple('Node', ['row', 'column', 'number', 'name'])
            data.name = row_name
            
        row_node = self.find_row_node(name)

        new_node = DancingLinkNode(data)
        new_node.column = column_header
        # Link the new node into the column
        new_node.up = column_header.up
        new_node.down = column_header
        column_header.up.down = new_node
        column_header.up = new_node
        
        # Link the node into the row
        if row_node:
            # print(f"found row {name}")
            new_node.left = row_node.left
            new_node.right = row_node
            row_node.left.right = new_node
            row_node.left = new_node
        else:
            new_node.left = new_node
            new_node.right = new_node
            
        self.increment_column_size(column_header)
        self.check_columns()
        return new_node

    # Example of covering a column (removing it from the grid temporarily)
    def cover_column(self, column_header):
        if column_header == self.header:
            print("AURGH!")
            return None
        self.check_columns()
        column_header.covered = True
        column_header.right.left = column_header.left
        column_header.left.right = column_header.right
        
        column_header.covered_constraints = set()
        column_header.covered_constraints.add(column_header.name)
        # Remove all rows in this column (cover the column)
        row_node = column_header.down
        while row_node != column_header:
            right_node = row_node.right
            while right_node != row_node:
                right_node.up.down = right_node.down
                right_node.down.up = right_node.up
                self.decrement_column_size(right_node.column)
                column_header.covered_constraints.add(right_node.column.name)
                right_node = right_node.right
            row_node = row_node.down
        self.remove_sorted_column(column_header)
        self.check_columns()
        return column_header



    # Example of uncovering a column (putting it back into the grid)
    def uncover_column(self, column_header):
        self.check_columns()
        row_node = column_header.up
        while row_node != column_header:
            left_node = row_node.left
            while left_node != row_node:
                self.increment_column_size(left_node.column)
                left_node.up.down = left_node
                left_node.down.up = left_node
                left_node = left_node.left
            row_node = row_node.up
        column_header.right.left = column_header
        column_header.left.right = column_header
        column_header.covered = False
        self.add_sorted_column(column_header)
        self.check_columns()
        return column_header

    def print_covered(self, covered_column):
        # Step 1: Collect all distinct row names
        row_name_set = set()  # Use a set to ensure unique row names
        
    
        # Traverse all columns and add all row names to the set
        for current_column in self.columns:
            current_node = current_column.down
            while current_node != current_column:
                row_name_set.add(current_node.data.name)  # Add row name to the set
                current_node = current_node.down
    
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
                if header_column.covered :
                    if i == 0:
                        space_char = "┌"
                    elif i == max_length -1:
                        space_char = "└"
                    else:
                        space_char = "│"
                row += space_char
                
                row += header[i] if i < len(header) else " "
                if header_column.covered :
                    if i == 0:
                        space_char = "┐"
                    elif i == max_length -1:
                        space_char = "┘"
                row += space_char
            print(row)
    
        print("        " + "─┴─" * len(column_names))
    
        # Step 3: Iterate over all row names and print their respective nodes
        for row_name in row_names:
            covered = False
            # Find the first node for the row
            row_node = self.find_row_node(row_name)
            if row_node is None:
                for current_column in self.columns:
                    current_node = current_column.down
                    while current_node != current_column and row_node == None:
                        if current_node.data.name == row_name:
                            row_node = current_node
                            covered = True

                        current_node = current_node.down
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


    def print(self, entire_grid = False):
        if entire_grid :
            return self.print_all()
        return self.print_normal()

    def print_all(self):
        # Step 1: Collect all distinct row names
        row_name_set = set()  # Use a set to ensure unique row names
    
        # Traverse all columns and add all row names to the set
        for current_column in self.columns:
            current_node = current_column.down
            while current_node != current_column:
                row_name_set.add(current_node.data.name)  # Add row name to the set
                current_node = current_node.down
    
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
                if header_column.covered :
                    if i == 0:
                        space_char = "┌"
                    elif i == max_length -1:
                        space_char = "└"
                    else:
                        space_char = "│"
                row += space_char
                
                row += header[i] if i < len(header) else " "
                if header_column.covered :
                    if i == 0:
                        space_char = "┐"
                    elif i == max_length -1:
                        space_char = "┘"
                row += space_char
            print(row)
    
        # Print separator line
        print("        " + "─┴─" * len(column_names))
    
        # Step 3: Iterate over all row names and print their respective nodes
        for row_name in row_names:
            covered = False
            # Find the first node for the row
            row_node = self.find_row_node(row_name)
            if row_node is None:
                for current_column in self.columns:
                    current_node = current_column.down
                    while current_node != current_column and row_node == None:
                        if current_node.data.name == row_name:
                            row_node = current_node
                            covered = True

                        current_node = current_node.down
                    if row_node != None:
                        break
            if row_node is None:
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
    
        # Print footer line
        print("        " + "───" * len(column_names))
        print(f" rows: {len(row_names)} columns: {len(column_names)}")

    def print_normal(self):
        print()
        # Step 1: Collect all distinct row names
        row_name_set = set()  # Use a set to ensure unique row names
    
        # Traverse all columns and add all row names to the set
        current_column = self.header.right
        while current_column != self.header:
            current_node = current_column.down
            while current_node != current_column:
                row_name_set.add(current_node.data.name)  # Add row name to the set
                current_node = current_node.down
            current_column = current_column.right
    
        row_names = sorted(row_name_set)


        # Step 2: collect column headers
        column_names = []
        current_column = self.header.right
        while current_column != self.header:
            column_names.append(current_column.name)
            current_column = current_column.right
    
        if len(column_names) == 0:
            print("This puzzle is solved")
            return
        # Print column headers
        max_length = max(len(header) for header in column_names)
        for i in range(max_length):
            row = "        "
            for header in column_names:
                # Print the character if it exists, else print a space
                row += " "  # Add spacing between columns
                row += header[i] if i < len(header) else " "
                row += " "  # Add spacing between columns
            print(row)
    
        # Print separator line
        print("        " + "---" * len(column_names))
    
        # Step 3: Iterate over all row names and print their respective nodes
        for row_name in row_names:
            # Find the first node for the row
            row_node = self.find_row_node(row_name)
            if row_node is None:
                continue  # If there's no node for this row, skip
        
            # Create an empty row with placeholders for each column
            row = f"{row_name: <8}"
            row_data = ["   "] * len(column_names)  # Initialize with empty spaces
        
            # Traverse across all columns and mark "X" where the node exists
            current_node = row_node
            column_index = column_names.index(current_node.column.name)
            row_data[column_index] = " X "  # Mark with "X"
            current_node = current_node.right

            while current_node != row_node:  # Horizontal traversal
                column_index = column_names.index(current_node.column.name)
                row_data[column_index] = " X "  # Mark with "X"
                current_node = current_node.right
        
            # Print the row with Xs indicating the nodes in each column
            print(row + "".join(row_data))
    
        # Print footer line
        print("        " + "---" * len(column_names))

def test1():
    possibilities = DancingLinks()
    
    for char in range(ord('A'), ord('G') + 1):
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

    possibilities.print()
               
    covered_column = possibilities.cover_column(possibilities.find_column_header("A"))

    possibilities.print()

    possibilities.print_covered(covered_column)

    possibilities.uncover_column(possibilities.find_column_header("A"))

    possibilities.print()

def test2():
    cell_constraint_name = "c{}/{}"
    row_number_name = "R{}#{}"
    column_number_name = "C{}#{}"
    N = 2
    Node = namedtuple('SudokuNode', ['row', 'column', 'number', 'name'])
    #    self.Move = namedtuple('SudokuMove', ['node', 'column'])

        
    possibilities = DancingLinks()

    # add early to make readable printout
    for row_index in range(1, N+1):
        for col_index in range(1, N+1):
            possibilities.add_column(cell_constraint_name.format(row_index, col_index))
                

    for row_index in range(1, N+1):
        for number in range(1, N+1):
            possibilities.add_column(row_number_name.format(row_index, number))


    for col_index in range(1, N+1):
        for number in range(1, N+1):
            possibilities.add_column(column_number_name.format(col_index, number))



    for row_index in range(1, N+1):
        for col_index in range(1, N+1):
            cell_name = cell_constraint_name.format(row_index, col_index)
            for number in range(1, N+1):
                name = f"R{row_index}C{col_index}#{number}"
                    
                node = Node(row_index, col_index, number, name)
                # Cell constraint: Only one number per cell
                possibilities.add_node(cell_name, node)                    

                # Row constraint: Only one of each number per row
                possibilities.add_node(row_number_name.format(row_index, number), node)


                # Column constraint: Only one of each number per column
                
                possibilities.add_node(column_number_name.format(col_index, number), node)

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
    covered_cell = possibilities.cover_column(possibilities.find_column_header(cell_constraint_name.format(row_index, col_index)))
    covered_column_number = possibilities.cover_column(possibilities.find_column_header(column_number_name.format(col_index, number)))
    covered_row_number = possibilities.cover_column(possibilities.find_column_header(row_number_name.format(row_index, number)))

    possibilities.print()
    possibilities.print(False)


def main():
    # Code to execute
    print("Running DancingLinks main function...")
    #test1()
    test2()
    

if __name__ == "__main__":
    main()        
    
        
