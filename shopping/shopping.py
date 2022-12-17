import csv
import sys

from sklearn.model_selection import train_test_split
from sklearn.neighbors import KNeighborsClassifier

TEST_SIZE = 0.4


def main():

    # Check command-line arguments
    if len(sys.argv) != 2:
        sys.exit("Usage: python shopping.py data")

    # Load data from spreadsheet and split into train and test sets
    evidence, labels = load_data(sys.argv[1])
    X_train, X_test, y_train, y_test = train_test_split(
        evidence, labels, test_size=TEST_SIZE
    )

    # Train model and make predictions
    model = train_model(X_train, y_train)
    predictions = model.predict(X_test)
    sensitivity, specificity = evaluate(y_test, predictions)

    # Print results
    print(f"Correct: {(y_test == predictions).sum()}")
    print(f"Incorrect: {(y_test != predictions).sum()}")
    print(f"True Positive Rate: {100 * sensitivity:.2f}%")
    print(f"True Negative Rate: {100 * specificity:.2f}%")


def load_data(filename):
    """
    Load shopping data from a CSV file `filename` and convert into a list of
    evidence lists and a list of labels. Return a tuple (evidence, labels).

    evidence should be a list of lists, where each list contains the
    following values, in order:
        - Administrative, an integer
        - Administrative_Duration, a floating point number
        - Informational, an integer
        - Informational_Duration, a floating point number
        - ProductRelated, an integer
        - ProductRelated_Duration, a floating point number
        - BounceRates, a floating point number
        - ExitRates, a floating point number
        - PageValues, a floating point number
        - SpecialDay, a floating point number
        - Month, an index from 0 (January) to 11 (December)
        - OperatingSystems, an integer
        - Browser, an integer
        - Region, an integer
        - TrafficType, an integer
        - VisitorType, an integer 0 (not returning) or 1 (returning)
        - Weekend, an integer 0 (if false) or 1 (if true)

    labels should be the corresponding list of labels, where each label
    is 1 if Revenue is true, and 0 otherwise.
    """

    with open(filename) as file: # Read data in from file
        reader = csv.DictReader(file)
        next(reader)

        evidence = [] # list of all of the evidence for each of the data points
        labels = [] # list of all of the labels for each data point

        # 0-indexed, create a dictionary to map month names to month numbers
        month = {"Jan":0, "Feb":1, "Mar":2, "Apr":3, "May":4, "June":5, "Jul":6, "Aug":7, "Sep":8, "Oct":9, "Nov":10, "Dec":11} 

        for row in reader:

            # Every evidence and label is a list for each customer
            # They are all sorted into the overall evidence and label lists by order.

            evidence.append([
                int(row['Administrative']), float(row['Administrative_Duration']),
                int(row['Informational']), float(row['Informational_Duration']),
                int(row['ProductRelated']), float(row['ProductRelated_Duration']),
                float(row['BounceRates']), float(row['ExitRates']),
                float(row['PageValues']), float(row['SpecialDay']),
                month[row['Month']], int(row['OperatingSystems']),
                int(row['Browser']), int(row['Region']),
                int(row['TrafficType']),
                1 if row['VisitorType'] == 'Returning_Visitor' else 0,
                1 if row['Weekend'] == 'True' else 0
                ]),

            labels.append(1 if row['Revenue']=='TRUE' else 0)

    # Return a tuple
    return (evidence,labels)

def train_model(evidence, labels):
    """
    Given a list of evidence lists and a list of labels, return a
    fitted k-nearest neighbor model (k=1) trained on the data.
    """

    # Create classifier to implement k-nearest neighbors
    model = KNeighborsClassifier(n_neighbors = 1)
    model.fit(evidence,labels) # train model

    return model

def evaluate(labels, predictions):
    """
    Given a list of actual labels and a list of predicted labels,
    return a tuple (sensitivity, specificty).

    Assume each label is either a 1 (positive) or 0 (negative).

    `sensitivity` should be a floating-point value from 0 to 1
    representing the "true positive rate": the proportion of
    actual positive labels that were accurately identified.

    `specificity` should be a floating-point value from 0 to 1
    representing the "true negative rate": the proportion of
    actual negative labels that were accurately identified.
    """
    # Initializing sensitivity and specificity
    sensitivity = float(0)
    specificity = float(0)

    positive = 0
    negative = 0

    # Iterates over actual labels and predictions
    # zip technique discovered at https://docs.python.org/3/library/functions.html#zip
    for labels, predictions in zip(labels, predictions): # labels and predictions should be the same length
        
        # Compute how well our classifier performed
        if labels == 0:
            negative += 1
            if predictions == 0:
                specificity += 1

        elif labels == 1:
            positive += 1
            if predictions == 1:
                sensitivity += 1

    # Evaluate proportion of correct identified positves and negatives
    sensitivity /= positive
    specificity /= negative

    return (sensitivity, specificity)

if __name__ == "__main__":
    main()
