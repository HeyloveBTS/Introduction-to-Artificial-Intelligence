from logic import *

AKnight = Symbol("A is a Knight")
AKnave = Symbol("A is a Knave")

BKnight = Symbol("B is a Knight")
BKnave = Symbol("B is a Knave")

CKnight = Symbol("C is a Knight")
CKnave = Symbol("C is a Knave")

# Puzzle 0
# A says "I am both a knight and a knave."
knowledge0 = And(
    # TODO
    Or(AKnight, AKnave), Not(And(AKnight, AKnave)), # A is either a knight or knave, but cannot be both in the same time
    Biconditional(AKnave, Not(And(AKnight, AKnave))) # A is a knave because A is lying
)

# Puzzle 1
# A says "We are both knaves."
# B says nothing.
knowledge1 = And(
    # TODO
    Or(AKnight, AKnave), Not(And(AKnight, AKnave)), 
    Or(BKnight, BKnave), Not(And(BKnave, BKnight)), # B cannot be both knave and knight in the same time

    # Either A is telling the truth, or A is a knave
    Implication(AKnave, Not(And(AKnave, BKnave))), 
    Implication(AKnight, And(AKnave, BKnave)), 

    Implication(AKnave, BKnight) # If A is a knave, then B is knight
)

# Puzzle 2
# A says "We are the same kind."
# B says "We are of different kinds."
knowledge2 = And(
    # TODO
    Or(AKnight, AKnave), Not(And(AKnight, AKnave)), 
    Or(BKnight, BKnave), Not(And(BKnave, BKnight)),

    Biconditional(AKnight, And(AKnight, BKnight)), # A and B is the same kind and A is telling the truth (if A is a knight) are biconditional
    Biconditional(AKnave, Or(And(BKnight, AKnave), And(BKnave, AKnight))), # In the contrast if A is a knave

    Biconditional(BKnight,And(BKnight, AKnave)),
    Biconditional(BKnave, And(AKnave, BKnave)) # B is a knave and both A and B is a knave are biconditional
)

# Puzzle 3
# A says either "I am a knight." or "I am a knave.", but you don't know which.
# B says "A said 'I am a knave'."
# B says "C is a knave."
# C says "A is a knight."
knowledge3 = And(
    # TODO
    Or(AKnave, AKnight), Not(And(AKnave, AKnight)),
    Or(BKnight, BKnave), Not(And(BKnave, BKnight)),
    Or(CKnight, CKnave), Not(And(CKnave, CKnight)), # C cannot be both knight and knave in the same time

    # Either way A is a knight or knave, A would say 'I am a knight', so B is lying
    Implication(Or(AKnave,AKnight), BKnave),

    Implication(BKnave, CKnight), # If B is a knave, then C is a knight
    Implication(CKnight, AKnight) # If C is a knight, then what C said the true

)


def main():
    symbols = [AKnight, AKnave, BKnight, BKnave, CKnight, CKnave]
    puzzles = [
        ("Puzzle 0", knowledge0),
        ("Puzzle 1", knowledge1),
        ("Puzzle 2", knowledge2),
        ("Puzzle 3", knowledge3)
    ]
    for puzzle, knowledge in puzzles:
        print(puzzle)
        if len(knowledge.conjuncts) == 0:
            print("    Not yet implemented.")
        else:
            for symbol in symbols:
                if model_check(knowledge, symbol):
                    print(f"    {symbol}")


if __name__ == "__main__":
    main()
