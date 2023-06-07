import itertools
import random


class Minesweeper():
    """
    Minesweeper game representation
    """

    def __init__(self, height=8, width=8, mines=8):

        # Set initial width, height, and number of mines
        self.height = height
        self.width = width
        self.mines = set()

        # Initialize an empty field with no mines
        self.board = []
        for i in range(self.height):
            row = []
            for j in range(self.width):
                row.append(False)
            self.board.append(row)

        # Add mines randomly
        while len(self.mines) != mines:
            i = random.randrange(height)
            j = random.randrange(width)
            if not self.board[i][j]:
                self.mines.add((i, j))
                self.board[i][j] = True

        # At first, player has found no mines
        self.mines_found = set()

    def print(self):
        """
        Prints a text-based representation
        of where mines are located.
        """
        for i in range(self.height):
            print("--" * self.width + "-")
            for j in range(self.width):
                if self.board[i][j]:
                    print("|X", end="")
                else:
                    print("| ", end="")
            print("|")
        print("--" * self.width + "-")

    def is_mine(self, cell):
        i, j = cell
        return self.board[i][j]

    def nearby_mines(self, cell):
        """
        Returns the number of mines that are
        within one row and column of a given cell,
        not including the cell itself.
        """

        # Keep count of nearby mines
        count = 0

        # Loop over all cells within one row and column
        for i in range(cell[0] - 1, cell[0] + 2):
            for j in range(cell[1] - 1, cell[1] + 2):

                # Ignore the cell itself
                if (i, j) == cell:
                    continue

                # Update count if cell in bounds and is mine
                if 0 <= i < self.height and 0 <= j < self.width:
                    if self.board[i][j]:
                        count += 1

        return count

    def won(self):
        """
        Checks if all mines have been flagged.
        """
        return self.mines_found == self.mines

class Sentence():
    """
    Logical statement about a Minesweeper game
    A sentence consists of a set of board cells,
    and a count of the number of those cells which are mines.
    """

    def __init__(self, cells, count):
        self.cells = set(cells)
        self.count = count

    def __eq__(self, other):
        return self.cells == other.cells and self.count == other.count

    def __str__(self):
        return f"{self.cells} = {self.count}"

    def known_mines(self):
        """
        Returns the set of all cells in self.cells known to be mines.
        """
        #raise NotImplementedError
        if self.count is len(self.cells):
            return self.cells.copy()
        else:
            return set()

    def known_safes(self):
        """
        Returns the set of all cells in self.cells known to be safe.
        """
        #raise NotImplementedError
        if self.count is 0:
            return self.cells.copy()
        else:
            return set()

    def mark_mine(self, cell):
        """
        Updates internal knowledge representation given the fact that
        a cell is known to be a mine.
        """
        #raise NotImplementedError
        if self.count is not 0 and cell in self.cells:
            self.cells.remove(cell)
            self.count -= 1

    def mark_safe(self, cell):
        """
        Updates internal knowledge representation given the fact that
        a cell is known to be safe.
        """
        #raise NotImplementedError
        if self.count is not 0 and cell in self.cells:
            self.cells.remove(cell)

class MinesweeperAI():
    """
    Minesweeper game player
    """

    def __init__(self, height=8, width=8):

        # Set initial height and width
        self.height = height
        self.width = width

        # Keep track of which cells have been clicked on
        self.moves_made = set()

        # Keep track of cells known to be safe or mines
        self.mines = set()
        self.safes = set()

        # List of sentences about the game known to be true
        self.knowledge = []

    def mark_mine(self, cell):
        """
        Marks a cell as a mine, and updates all knowledge
        to mark that cell as a mine as well.
        """
        self.mines.add(cell)
        for sentence in self.knowledge:
            sentence.mark_mine(cell)

    def mark_safe(self, cell):
        """
        Marks a cell as safe, and updates all knowledge
        to mark that cell as safe as well.
        """
        #print("Safe cell added:", cell)
        self.safes.add(cell)
        for sentence in self.knowledge:
            sentence.mark_safe(cell)

    def add_knowledge(self, cell, count):
        """
        Called when the Minesweeper board tells us, for a given
        safe cell, how many neighboring cells have mines in them.

        This function should:
            1) mark the cell as a move that has been made
            2) mark the cell as safe
            3) add a new sentence to the AI's knowledge base
               based on the value of `cell` and `count`
            4) mark any additional cells as safe or as mines
               if it can be concluded based on the AI's knowledge base
            5) add any new sentences to the AI's knowledge base
               if they can be inferred from existing knowledge
        """
        #raise NotImplementedError
        self.moves_made.add(cell)
        self.mark_safe(cell)
        cells = self.neighbour_cells(cell, count)
        if cells:
            self.knowledge.append(Sentence(cells, count))
        #print("Knowledge:")

        for sentence_A in self.knowledge:
            #Marking safe cells
            safe_cells = sentence_A.known_safes()
            for safe_cell in safe_cells:
                self.mark_safe(safe_cell)
            
            #Update knowledge when a subset/superset is found
            if sentence_A.count is not 0:    
                for sentence_B in self.knowledge:
                    if not sentence_A == sentence_B and sentence_B.count is not 0:
                        if sentence_A.cells.issubset(sentence_B.cells):
                            sentence_B.cells.difference_update(sentence_A.cells)
                            sentence_B.count -= sentence_A.count
                        if sentence_A.cells.issuperset(sentence_B.cells):
                            sentence_A.cells.difference_update(sentence_B.cells)
                            sentence_A.count -= sentence_B.count
            
            #Removing known mines from the sentence
            for mine in self.mines:
                sentence_A.mark_mine(mine)

            #Marking mine cells in the sentence
            mine_cells = sentence_A.known_mines()
            for mine_cell in mine_cells:
                self.mark_mine(mine_cell)

            #Marking again safe cells for the sentence
            safe_cells = sentence_A.known_safes()
            for safe_cell in safe_cells:
                self.mark_safe(safe_cell)
        
        self.safes.difference_update(self.moves_made)

        #for sentence in self.knowledge:
            #print(sentence)
        #print("Safe Cells: ", self.safes)
        #print("Mine Cells: ", self.mines)



    def make_safe_move(self):
        """
        Returns a safe cell to choose on the Minesweeper board.
        The move must be known to be safe, and not already a move
        that has been made.

        This function may use the knowledge in self.mines, self.safes
        and self.moves_made, but should not modify any of those values.
        """
        #raise NotImplementedError
        #self.safes.difference_update(self.moves_made)
        if len(self.safes):
            return self.safes.pop()
        return None

    def make_random_move(self):
        """
        Returns a move to make on the Minesweeper board.
        Should choose randomly among cells that:
            1) have not already been chosen, and
            2) are not known to be mines
        """
        #raise NotImplementedError
        # Return None when no cells to be revealed
        if len(self.mines) + len(self.moves_made) is self.height * self.width:
            return None
        # Move randomly
        while True: #len(self.mines) != mines:
            i = random.randrange(self.height)
            j = random.randrange(self.width)
            if (i,j) not in self.mines and (i,j) not in self.moves_made:
                #print(f"Move: {i},{j}")
                return (i,j)
    
    #Below are additional Functions
    def neighbour_cells(self, cell, count):
        """
        Returns a set of neighbouring cells for the given cell
        """
        cells = set()
        # Loop over all cells within one row and column
        for i in range(cell[0] - 1, cell[0] + 2):
            for j in range(cell[1] - 1, cell[1] + 2):

                # Generate neighbour cells excluding safe cells and cells already moved
                if 0 <= i < self.height and 0 <= j < self.width:
                    if (i,j) not in self.safes and (i,j) not in self.moves_made:
                        cells.add((i,j))
        return cells


            

