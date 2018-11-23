#!/usr/bin/env python

# data_analysis.py
# Patrick Tung, Sylvia Lee (Nov 22, 2018)

# Description: This script takes in the cleaned titanic datasets and fits a
#              decision tree to predict which passengers survived the Titanic.
#              This includes cross validating decision trees to determine
#              the value for hyperparameters. It then returns the top three
#              most important features.

# Usage: python data_analysis.py <cleaned_train.csv path> <cleaned_test.csv path> <output_folder path/>
# Example: python data_analysis.py data/cleaned/cleaned_train.csv data/cleaned/cleaned_test.csv results/

import argparse
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.tree import DecisionTreeClassifier
from sklearn.model_selection import cross_val_score
import pickle

parser = argparse.ArgumentParser()
parser.add_argument("training_data")
parser.add_argument("testing_data")
parser.add_argument("output_folder")
args = parser.parse_args()

def main():
    # Read data
    titanic_train = pd.read_csv(args.training_data, index_col = 0)
    titanic_test = pd.read_csv(args.testing_data, index_col = 0)

    # Split data into feature and target dataframes
    Xtrain, ytrain = split_data(titanic_train)
    Xtest, ytest = split_data(titanic_test)

    # Cross Validation to find the best max_depth for decision classification tree
    best_depth = cross_validate(Xtrain, ytrain)

    # Create decision tree and fit model
    tree = fit(Xtrain, ytrain, best_depth)

    # Predicting with train and test set
    train_prediction = predict(tree, Xtrain, titanic_train)
    test_prediction = predict(tree, Xtest, titanic_test)

    # Get accuracies of train and test set
    accuracies_df = pd.DataFrame(columns = ["set", "n_total", "n_correct_pred", "n_incorrect_pred", "accuracy"])
    accuracies_df.loc[0] = get_accuracies(train_prediction, "train")
    accuracies_df.loc[1] = get_accuracies(test_prediction, "test")

    # Rank the most predictive features
    features = list(Xtrain)
    feature_rank_df = feature_rank(tree, features)

    # Export files
    pickle.dump(tree, open(args.output_folder + "classification_tree_model.sav", "wb"))
    train_prediction.to_csv(args.output_folder + "train_prediction.csv")
    test_prediction.to_csv(args.output_folder + "test_prediction.csv")
    accuracies_df.to_csv(args.output_folder + "classification_accuracies.csv")
    feature_rank_df.to_csv(args.output_folder + "feature_ranks.csv")



# Description: split the data sets into a X-feature set and y-target sets
# Parameter:   data(dataframe) = dataframe with target being in the last column named "Survived"
# Return:      X(dataframe) = dataframe containing feature columns
#              y(dataframe) = dataframe containing the target column
def split_data(data):
    X = data.iloc[:, 0:-1]
    y = data.Survived
    return(X, y)


# Description: Find the best max_depth hyperparameter by 10-fold cross valiation
# Parameter:   Xtrain(dataframe) = dataframe containing the training feature columns
#              ytrain(dataframe) = dataframe containing the training target column
# Return:      best_depth(integer) = the max_depth that gave the best accuracies
def cross_validate(Xtrain,ytrain):
    max_depths = range(1, 50)

    accuracies = []
    for depth in max_depths:
        tree = DecisionTreeClassifier(max_depth=depth)
        cross_vals = cross_val_score(tree, Xtrain, ytrain, cv=10)
        accuracies.append(cross_vals.mean())

    best_depth = max_depths[np.argmax(accuracies)]
    return(best_depth)


# Description: create decision classification tree
# Parameter:   Xtrain(dataframe) = dataframe containing the training feature columns
#              ytrain(dataframe) = dataframe containing the training target column
#              best_depth(integer) = the max_depth that gave the best accuracies
# Return:      tree(DecisionTreeClassifier object) = classification tree model
def fit(Xtrain, ytrain, best_depth):
    tree = DecisionTreeClassifier(max_depth=best_depth)
    tree.fit(Xtrain,ytrain)
    return(tree)


# Description: predict targets from feature set using the classification tree
# Parameter:   tree(DecisionTreeClassifier object) = classification tree model
#              feature_set(dataframe) = dataframe containing the feature columns
#              whole_set(dataframe) = dataframe containing the feature and target columns
# Return:      tree_predict(dataframe) = dataframe with an addition prediction column
#                                        appended to the whole_set dataframe
def predict(tree, feature_set, whole_set):
    predictions = tree.predict(feature_set)
    tree_predict = whole_set.copy()
    tree_predict["Prediction"] = predictions
    return(tree_predict)


# Description: evaluate accuracies of the predictions be comparing the targets and the predictions
# Parameter:   df(dataframe) = dataframe with an addition prediction column
#                                        appended to the whole_set dataframe
#              set_name(string) = name of the set being evaluated ("train" or "test")
# Return:      (list) = list containing the set name(str),
#                       total number of predicted samples(int), number of correct predictions(int),
#                       number of incorrect predictions(int), prediction accuracy(float)
def get_accuracies(df, set_name):
    correct_predictions = df.Survived[df.Survived == df.Prediction].sum()
    incorrect_predictions = df.Survived[df.Survived != df.Prediction].sum()
    total = correct_predictions + incorrect_predictions
    accuracy = round(correct_predictions / total, 4)
    return([set_name, total, correct_predictions, incorrect_predictions, accuracy])



# Description: rank the features from the most predictive to the least predictive
# Parameter:   tree(DecisionTreeClassifier object) = classification tree model
#              features(list) = list of feature names(str)
# Return:      feature_rank_df(dataframe) = dataframe that contains the rank, feature
#              name and importance measure in ascending order. Rank of 1 is most predictive
def feature_rank(tree, features):
    importances = tree.feature_importances_
    importance_indices = importances.argsort()[::-1]

    feature_rank_df = pd.DataFrame(columns = ['Rank', 'Feature', 'Importance'])

    for i in range(len(features)):
        feature_rank_df.loc[i] = [i+1, features[importance_indices[i]], importances[importance_indices[i]]]

    return(feature_rank_df)

if __name__ == "__main__":
    main()
