from copy import deepcopy
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
        # If the number of cells equal to the mine count, they are all mines
        if self.count == len(self.cells) and self.count > 0:
            return self.cells

        return set()         


    def known_safes(self):
        """
        Returns the set of all cells in self.cells known to be safe.
        """
        if self.count == 0: # A cell can only be safe if there are 0 count of mines.
            return self.cells

        return set()

    def mark_mine(self, cell):
        """
        Updates internal knowledge representation given the fact that
        a cell is known to be a mine.
        """
        if cell in self.cells:
            self.count -= 1
            self.cells.remove(cell)
        else:
            pass

    def mark_safe(self, cell):
        """
        Updates internal knowledge representation given the fact that
        a cell is known to be safe.
        """
        if cell in self.cells:
            self.cells.remove(cell)
        else:
            pass


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

        self.moves_made.add(cell) # mark the cell as a move that has been made
        self.mark_safe(cell) # mark the cell as safe
        
        neighbors = set() # Create a set to store undefined cell 


        # Looping around the eight cells around the cell
        for i in range(cell[0]-1, cell[0]+2): # x and y coordinates of the cell and cells around the cell
            for j in range(cell[1]-1, cell[1]+2): 

                # Preclude the cell itself
                if (i,j) == cell:
                    continue
                    
                if (i,j) in self.safes:
                    continue

                if (i,j) in self.mines:
                    count -= 1
                    continue

                # Check to see if the cell is within the board and undetermined
                elif 0 <= i < self.height and 0 <= j < self.width:
                    if (i,j) not in self.moves_made and (i,j) not in self.safes and (i,j) not in self.mines:
                        neighbors.add((i,j))

        if len(neighbors) > 0:
            self.knowledge.append(Sentence(neighbors, count)) # Adding new sentences to the knowledge base

        # A loop that checkes through the sentences in knowledge to see whether the cells are mines or safes
        for sentences in self.knowledge:
            if sentences.count == 0:  # If the mine count is 0, then all of the cells are safe
                copyCells = deepcopy(sentences.cells) # Make sures any changes to the board cells copy do not influence the original set 
                for cells in copyCells:
                    self.mark_safe(cells)
            elif sentences.count == len(sentences.cells): # Likewise, they are mines if the count is equal to the length of the cells
                copyCells = deepcopy(sentences.cells)
                for cells in copyCells:
                    self.mark_mine(cells)

        # Also checkes if some sentences are subsets of others
        for sentence1 in self.knowledge:

            for sentence2 in self.knowledge:
                if sentence1.count == sentence2.count: # Skip if the sentences are the same
                    continue

                if len(sentence1.cells) != 0 and len(sentence2.cells)!=0: # An empty set needs to be rule out since it is a subset of every set

                    if sentence1.cells.issubset(sentence2.cells): 
                        combinedCells = sentence1.cells-sentence2.cells
                        combinedCounts = sentence1.count-sentence2.count # Draw new inferences into the KB by subtracting

                        if Sentence(combinedCells,combinedCounts) not in self.knowledge: # Don't repeat the sentences
                            self.knowledge.append(Sentence(combinedCells, combinedCounts)) # Construct a new sentence
                
                    elif sentence2.cells.issubset(sentence1.cells): 
                        combinedCells = sentence2.cells-sentence1.cells
                        combinedCounts = sentence2.count-sentence1.count

                        if Sentence(combinedCells,combinedCounts) not in self.knowledge:
                            self.knowledge.append(Sentence(combinedCells, combinedCounts))
        
            

    def make_safe_move(self):
        """
        Returns a safe cell to choose on the Minesweeper board.
        The move must be known to be safe, and not already a move
        that has been made.

        This function may use the knowledge in self.mines, self.safes
        and self.moves_made, but should not modify any of those values.
        """

        for safeMoves in self.safes:
            if safeMoves not in self.moves_made and safeMoves not in self.mines:
                return safeMoves # Return a safe cell
        
        return None


    def make_random_move(self):
        """
        Returns a move to make on the Minesweeper board.
        Should choose randomly among cells that:
            1) have not already been chosen, and
            2) are not known to be mines
        """
        for i in range(self.height): 
            for j in range(self.width):
                if (i,j) not in self.moves_made and (i,j) not in self.mines:
                        return (i,j)
        
        return None
