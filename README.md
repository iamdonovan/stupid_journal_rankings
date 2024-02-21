# stupid journal rankings

This program takes a list of journal names and SJR categories, and generates a spreadsheet of corresponding rankings,
percentiles, and quartile rankings for each journal in each category.

## setup

After cloning the repository to your computer, use `conda` to create an environment using the **environment.yml** file:

```
conda env create -f environment.yml
```

This will create a new environment with the necessary packages. Alternatively, you can install the packages listed 
in **environment.yml** by hand.


## usage

To run the program, you will need a spreadsheet of journal names (`'Journal'`; preferably matching the names used by 
SJR) and corresponding SJR category codes (`'Scimago Category'`).

Run the program from the repository directory as follows:

```commandline
    python stupid_journal_rankings.py <spreadsheet>
```

This will create a new file, **stupid_journal_rankings.csv**, that contains the rankings, percentiles, and quartile
rankings for each journal in each category.
