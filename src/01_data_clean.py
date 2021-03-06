#!/usr/bin/env python

# 01_clean_data.py
# Patrick Tung, Sylvia Lee (Nov 22, 2018)

# Description: This script takes in the raw titanic datasets and clean it for
#              future analyses. Cleaning includes removing un-need data, fill NaN elements
#              and joined gender_submission.csv with test.csv

# Usage: python 01_data_clean.py <train.csv path> <test.csv path> <gender_submission.csv path>
#        <clean_train.csv path> <clean_test.csv path> <clean_total.csv path>
# Example: python 01_data_clean.py data/raw/train.csv data/raw/test.csv data/raw/gender_submission.csv
#          data/cleaned/cleaned_train.csv data/cleaned/cleaned_test.csv

import argparse
import pandas as pd
import numpy as np

parser = argparse.ArgumentParser()
parser.add_argument('training_data')
parser.add_argument('testing_data')
parser.add_argument('gender_submission')
parser.add_argument('cleaned_train')
parser.add_argument("cleaned_test")
args = parser.parse_args()

def main():
    # Read in raw data
    titanic_train = pd.read_csv(args.training_data, index_col = 0)
    titanic_test = pd.read_csv(args.testing_data, index_col = 0)
    gender_submission = pd.read_csv(args.gender_submission, index_col = 0)
    print("Raw data imported")


    # Drop columns that we are not interested in
    titanic_train = titanic_train.loc[:,["Pclass", "Sex", "Age", "SibSp", "Parch", "Fare", "Survived"]]
    titanic_test = titanic_test.loc[:,["Pclass", "Sex", "Age", "SibSp", "Parch", "Fare"]]

    # Add Survived column to test data
    titanic_test = titanic_test.join(gender_submission)

    # Process data
    fillNAN([titanic_train, titanic_test])
    process_sex([titanic_train, titanic_test])
    print("Finished cleaning")

    # Export data
    titanic_train.to_csv(args.cleaned_train)
    titanic_test.to_csv(args.cleaned_test)
    print("Clean data exported")

# Calculate statistical center of "age" and "fare"
def calcNAN(df):
    return {'Age': df.Age.mean(), 'Fare': df.Fare.median()}

# Replace NaN values in df with statistical center of column variable
def fillNAN(df):
    values = calcNAN(df[0])
    for i in df:
        i.fillna(value=values, inplace = True)

# Replace Sex to 1 or 0
def process_sex(df):
    for i in df:
        i["Sex"] = i["Sex"].map({"male": 1, "female": 0})

if __name__ == "__main__":
    main()

# UNIT TESTS
# ==========

# Toy dataset to check functions
unit_train_df = pd.DataFrame({'Age': [1, 2, 3, np.NaN, 5, 4], 'Fare': [2, np.NaN, 4, 5, 7, 21], 'Sex': ["male", "female", "female", "male", "male", "male"]})

# Unit test for calcNAN()
assert calcNAN(unit_train_df) == {"Age": np.mean(unit_train_df.Age), "Fare": np.nanmedian(unit_train_df.Fare)}, 'The Age or Fare is incorrect.'
assert len(calcNAN(unit_train_df)) == 2, 'Incorrect number of variables returned'

# Unit test for fillNAN()
fillNAN([unit_train_df])
assert unit_train_df.isnull().values.any() == False, 'NaN values not replaced'
assert unit_train_df.Age[3] == np.mean(unit_train_df.Age), 'Age NaN value not replaced correctly'
assert unit_train_df.Fare[1] == np.nanmedian(unit_train_df.Fare), 'Fare NaN value not replaced correctly'

# Unit test for process_sex()
process_sex([unit_train_df])
assert pd.api.types.is_numeric_dtype(unit_train_df['Sex']) == True, 'Strings not converted to numbers'
assert np.sum(unit_train_df.Sex) == 4, 'Incorrect number of males and females'
assert list(unit_train_df.Sex) == [1, 0, 0, 1, 1, 1], "Males and females wrongly assigned"
