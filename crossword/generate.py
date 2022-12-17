import queue
import sys

from crossword import *



class CrosswordCreator():

    def __init__(self, crossword):
        """
        Create new CSP crossword generate.
        """
        self.crossword = crossword
        self.domains = {
            var: self.crossword.words.copy()
            for var in self.crossword.variables
        }

    def letter_grid(self, assignment):
        """
        Return 2D array representing a given assignment.
        """
        letters = [
            [None for _ in range(self.crossword.width)]
            for _ in range(self.crossword.height)
        ]
        for variable, word in assignment.items():
            direction = variable.direction
            for k in range(len(word)):
                i = variable.i + (k if direction == Variable.DOWN else 0)
                j = variable.j + (k if direction == Variable.ACROSS else 0)
                letters[i][j] = word[k]
        return letters

    def print(self, assignment):
        """
        Print crossword assignment to the terminal.
        """
        letters = self.letter_grid(assignment)
        for i in range(self.crossword.height):
            for j in range(self.crossword.width):
                if self.crossword.structure[i][j]:
                    print(letters[i][j] or " ", end="")
                else:
                    print("█", end="")
            print()

    def save(self, assignment, filename):
        """
        Save crossword assignment to an image file.
        """
        from PIL import Image, ImageDraw, ImageFont
        cell_size = 100
        cell_border = 2
        interior_size = cell_size - 2 * cell_border
        letters = self.letter_grid(assignment)

        # Create a blank canvas
        img = Image.new(
            "RGBA",
            (self.crossword.width * cell_size,
             self.crossword.height * cell_size),
            "black"
        )
        font = ImageFont.truetype("assets/fonts/OpenSans-Regular.ttf", 80)
        draw = ImageDraw.Draw(img)

        for i in range(self.crossword.height):
            for j in range(self.crossword.width):

                rect = [
                    (j * cell_size + cell_border,
                     i * cell_size + cell_border),
                    ((j + 1) * cell_size - cell_border,
                     (i + 1) * cell_size - cell_border)
                ]
                if self.crossword.structure[i][j]:
                    draw.rectangle(rect, fill="white")
                    if letters[i][j]:
                        w, h = draw.textsize(letters[i][j], font=font)
                        draw.text(
                            (rect[0][0] + ((interior_size - w) / 2),
                             rect[0][1] + ((interior_size - h) / 2) - 10),
                            letters[i][j], fill="black", font=font
                        )

        img.save(filename)

    def solve(self):
        """
        Enforce node and arc consistency, and then solve the CSP.
        """
        self.enforce_node_consistency()
        self.ac3()
        return self.backtrack(dict())

    def enforce_node_consistency(self):
        """
        Update `self.domains` such that each variable is node-consistent.
        (Remove any values that are inconsistent with a variable's unary
         constraints; in this case, the length of the word.)
        """
        for variables in self.domains.keys(): # Review and iterates all the variables in the domain 
            var_length = variables.length 
            for word in self.crossword.words: # Iterates all the words in the domain
                if len(word) != var_length:
                    # Remove any values that are inconsistent with a variable's length
                    self.domains[variables].remove(word) 

    def revise(self, x, y):
        """
        Make variable `x` arc consistent with variable `y`.
        To do so, remove values from `self.domains[x]` for which there is no
        possible corresponding value for `y` in `self.domains[y]`.

        Return True if a revision was made to the domain of `x`; return
        False if no revision was made.
        """        
        revised = False
       
        if self.crossword.overlaps[x,y] is None:
            return False
        else: # We only pay attention if there is an overlap 
            x_overlap, y_overlap = self.crossword.overlaps[x,y] # Unpack the overlapping integers
            
            # Iterates words in x's and y's domains
            for x in self.domains[x_overlap]:
                for y in self.domains[y_overlap]:
                
                    if x[x_overlap] != y[y_overlap]: #If no words in y's domain are consistent with any words in x's domain 
                        self.domains[x_overlap].remove(x) # Removing the word from the domain
                        revised = True

                    else:
                        break # No need to check if both words have the same letter overlapped in the same position
        
        return revised


    def ac3(self, arcs=None):
        """
        Update `self.domains` such that each variable is arc consistent.
        If `arcs` is None, begin with initial list of all arcs in the problem.
        Otherwise, use `arcs` as the initial list of arcs to make consistent.

        Return True if arc consistency is enforced and no domains are empty;
        return False if one or more domains end up empty.
        """
        if arcs is None:
            queue = [] # Initialize a list
            # Adding arcs to the queue
            for x in self.domains.keys():
                for y in self.domains.keys():
                    if x != y: # Each arc is a tuple of x and a different variable of y
                        queue.append((x,y))
        else:
            for x,y in arcs: # Use arcs to initialize a list to make consistent
                if self.revise(x,y):
                    if len(self.domains[x]) == 0:
                        return False # Return false if I remove everything from the x's domain

                    # Add additional arcs to the queue to ensure that other arcs stay consistent
                    for z in self.crossword.neighbors(x):
                        if z != y:
                            queue.append(tuple(z,x))

        return True



    def assignment_complete(self, assignment):
        """
        Return True if `assignment` is complete (i.e., assigns a value to each
        crossword variable); return False otherwise.
        """
        for var in self.domains:
            if var not in assignment:
                return False

        return True



    def consistent(self, assignment):
        """
        Return True if `assignment` is consistent (i.e., words fit in crossword
        puzzle without conflicting characters); return False otherwise.
        """
        for var in assignment:
            word = assignment[var]
            if var.length != len(word): # Checking if every value has the right length
                return False
            
            words = []
            if var not in words:
                words.append(var)
            else:
                return False # Checking if every value is distinct
            
            # Checking to see if there are conflicts between neighboring variables
            for neighbors in self.crossword.neighbors(var):
                if neighbors in assignment:
                    x_overlap, y_overlap = self.crossword.overlaps[var,neighbors]
                    if assignment[var][x_overlap] != assignment[neighbors][y_overlap]:
                        return False

        return True # Return true if the assignment met all the consistent requirements

    def order_domain_values(self, var, assignment):
        """
        Return a list of values in the domain of `var`, in order by
        the number of values they rule out for neighboring variables.
        The first value in the list, for example, should be the one
        that rules out the fewest values among the neighbors of `var`.
        """
        values = {}
        neighbors = self.crossword.neighbors(var)

        for variable in self.domains[var]:
            remove = 0
            # Rule out any variable already present in the assignment
            if variable in assignment:
                continue

            for neighbor in neighbors:
                # Rule out any neighbor already present in the assignment
                if neighbor in assignment:
                    continue
                else:
                    # Iterate through the overlaps between the variable and neighbors
                    for var_neighbor in neighbors:
                        if variable in self.domains[var_neighbor]:
                            remove += 1 # Counting the number of values ruled out for neighboring unassigned variables
                            
            # Add the values and the number of values they rule out for neighboring variables to the list.
            values[variable] = remove 

        # Sorting the remaining variables in the ascending order
        return sorted(values, key= lambda key: values[key])


    def select_unassigned_variable(self, assignment):
        """
        Return an unassigned variable not already part of `assignment`.
        Choose the variable with the minimum number of remaining values
        in its domain. If there is a tie, choose the variable with the highest
        degree. If there is a tie, any of the tied variables are acceptable
        return values.
        """
        choice = None
        
        # iterating through unassigned variables
        for variable in self.crossword.variables - set(assignment):
            if choice is None:
                choice = variable
            else:
                if len(self.domains[variable]) < len(self.domains[choice]):
                    choice = variable # Replace our choice if the variable has fewer number of remaining values in its domain
                elif len(self.crossword.neighbors(variable)) < len(self.crossword.neighbors(choice)):
                    choice = variable # Replace our choice with the variable that has the largests degrees

        return choice

    def backtrack(self, assignment):
        """
        Using Backtracking Search, take as input a partial assignment for the
        crossword and return a complete assignment if possible to do so.

        `assignment` is a mapping from variables (keys) to words (values).

        If no assignment is possible, return None.
        """

        # return the assignment if it's completed 
        if self.assignment_complete(assignment):
            return assignment
        # selects any of the variables that do not have an assignment yet
        var = self.select_unassigned_variable(assignment)
        for value in self.order_domain_values(var,assignment):
            assignment[var] = value
            if self.consistent(assignment):
                result = self.backtrack(assignment)
                if result is not None:
                    return result
            # If the resulting value is failure, then the latest assignment is removed
            assignment.pop(var)
        return None



def main():

    # Check usage
    if len(sys.argv) not in [3, 4]:
        sys.exit("Usage: python generate.py structure words [output]")

    # Parse command-line arguments
    structure = sys.argv[1]
    words = sys.argv[2]
    output = sys.argv[3] if len(sys.argv) == 4 else None

    # Generate crossword
    crossword = Crossword(structure, words)
    creator = CrosswordCreator(crossword)
    assignment = creator.solve()

    # Print result
    if assignment is None:
        print("No solution.")
    else:
        creator.print(assignment)
        if output:
            creator.save(assignment, output)


if __name__ == "__main__":
    main()
