import os
import argparse
import urllib
import time
import pandas as pd


def _download_rank_sheet(code, year=None):
    os.makedirs('rank_sheets', exist_ok=True)

    this_url = f"https://www.scimagojr.com/journalrank.php?category={code}&out=xls"
    time.sleep(60) # be nice and wait 1 minute before we try to download a sheet

    if year is not None:
        this_url += f"&year={year}"
        outname = f"{code}-{year}.csv"
        print(f"Downloading sheet for code {code}, {year} from scimagojr.com")
    else:
        outname = f"{code}.csv"
        print(f"Downloading sheet for code {code} from scimagojr.com")

    urllib.request.urlretrieve(this_url, os.path.join('rank_sheets', outname))


def _get_index(journal, rank_sheet, sheetname):
    try:
        return rank_sheet.loc[rank_sheet['Title'].str.lower() == journal.lower()].index[0]
    except IndexError as e:
        print(f"Unable to find {journal} in {code}.")
        return None


def _get_quartiles(df):
    df.loc[(df['Percentile'] < 0.25), 'Quartile'] = 'Q1'
    df.loc[(0.25 <= df['Percentile']) & (df['Percentile'] < 0.5), 'Quartile'] = 'Q2'
    df.loc[(0.5 <= df['Percentile']) & (df['Percentile'] < 0.75), 'Quartile'] = 'Q3'
    df.loc[0.75 <= df['Percentile'], 'Quartile'] = 'Q4'

    return df


def _argparser():
    parser = argparse.ArgumentParser(
        description="Find Stupid Journal Rankings given a list of journals with Scimago categories.",
        formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('journallist', action='store', type=str,
                        help='the spreadsheet of journal names and categories')
    parser.add_argument('-y', '--years', action='store', type=int, nargs='+', default=None,
                        help='the years to use for the rankings (defaults to current year)')

    # TODO: add a flag/routine to update the journal list based on the codes we find
    return parser


def main():
    parser = _argparser()
    args = parser.parse_args()

    journal_data = pd.read_excel(args.journallist)
    rank_output = pd.DataFrame()

    if args.years is None:
        years = [None]
    else:
        years = args.years

    for _, row in journal_data.iterrows():
        for year in years:

            code = row['Scimago Category']

            if year is None:
                sheetname = f"{code}.csv"
            else:
                sheetname = f"{code}-{year}.csv"

            if not os.path.exists(os.path.join('rank_sheets', sheetname)):
                _download_rank_sheet(code, year=year)

            rank_sheet = pd.read_csv(os.path.join('rank_sheets', sheetname), delimiter=';', decimal=',')

            ind = len(rank_output)  # get current length of data frame

            rank_output.loc[ind, 'Journal'] = row['Journal']
            rank_output.loc[ind, 'SubjectArea'] = row['Subject Area']
            rank_output.loc[ind, 'Category'] = row['Category']

            rank_ind = _get_index(row['Journal'], rank_sheet, sheetname)

            rank_output.loc[ind, 'Rank'] = rank_sheet.loc[rank_ind, 'Rank']
            rank_output.loc[ind, 'CategorySize'] = len(rank_sheet)

            rank_output.loc[ind, 'Year'] = year

            rank_output.loc[ind, 'Percentile'] = rank_output.loc[ind, 'Rank'] / rank_output.loc[ind, 'CategorySize']

            rank_output.loc[ind, 'SJR'] = float(rank_sheet.loc[rank_ind, 'SJR'])
            rank_output.loc[ind, '2YearCites'] = float(rank_sheet.loc[rank_ind, 'Cites / Doc. (2years)'])
            rank_output.loc[ind, 'RefsPerDoc'] = float(rank_sheet.loc[rank_ind, 'Ref. / Doc.'])

    rank_output = _get_quartiles(rank_output)

    rank_output.to_csv('stupid_journal_rankings.csv', index=False)


if __name__ == "__main__":
    main()
