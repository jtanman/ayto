# James Tan

# ayto.py

import numpy as np
import pandas as pd
import csv
import itertools
import time
import os.path

DATA_FILE = 'data.csv'
MATCH_LOAD = 'matches'
MATCH_SAVE = 'matches'
PROB_FILE = 'probs.csv'
GUESS_FILE = 'matchup_guess.csv'

BOYS = {
    'Andre':    0,
    'Derrick':  1,
    'Edward':   2,
    'Hayden':   3,
    'Jaylan':   4,
    'Joey':     5,
    'Michael':  6,
    'Mike':     7,
    'Osvaldo':  8,
    'Ozzy':     9,
    'Tyler':    10,
}

GIRLS = {
    'Alicia':   0,
    'Carolina': 1,
    'Casandra': 2,
    'Gianna':   3,
    'Hannah':   4,
    'Kam':      5,
    'Kari':     6,
    'Kathryn':  7,
    'Shannon':  8,
    'Taylor':   9,
    'Tyranny':  10,
}

BOYS_REV = dict((v, k) for k, v in BOYS.items())
GIRLS_REV = dict((v, k) for k, v in GIRLS.items())


NUM_PLAYERS = len(BOYS)


def gen_combinations():
    """Generate all combinations for AYTO"""
    start = time.time()
    permutations = list(itertools.permutations(range(NUM_PLAYERS)))
    permutations = pd.DataFrame(permutations)
    end = time.time()

    print 'Generating permutations took %.2f' % (end - start)
    return permutations


def read_csv(filename, matches):
    """Read csv file with results from truth booth and matchup ceremony"""

    with open(filename, 'rb') as csvfile:
        csvreader = csv.reader(csvfile)
        while True:
            try:
                row = next(csvreader)
                header = row[0]
                if header == '':
                    continue
                elif header.isdigit():
                    matches = parse_matchup_ceremony(csvreader, header,
                                                     matches)
                elif header == 'Guess':
                    guess_matchup_ceremony(csvreader, header, matches)
                elif (header == 'Yes') | (header == 'No'):
                    matches = parse_truth_booth(csvreader, header, matches)
                else:
                    print 'Header not recognized'
                    break
            except csv.Error:
                print "Error"
            except StopIteration:
                print "End of file"
                break

    return matches


def parse_truth_booth(csvreader, header, matches):
    """Parses truth booth data from csv"""
    start = time.time()
    orig_len = len(matches)
    row = next(csvreader)
    name_a = row[0].strip()
    name_b = row[1].strip()
    boy = BOYS[name_a] if name_a in BOYS else BOYS[name_b]
    girl = GIRLS[name_a] if name_a in GIRLS else GIRLS[name_b]

    # tuple code
    # if header=='Yes':
    #     # matches = [elem for elem in matches if elem[boy] == girl]
    #     matches = matches[
    # elif header=='No':
    #     # matches = [elem for elem in matches if elem[boy] != girl]
    # else:
    #     print 'Invalid header for truth booth ceremony'

    # # np array code
    # if header == 'Yes':
    #     matches = matches[matches[:, boy] == girl]
    # elif header == 'No':
    #     matches = matches[matches[:, boy] != girl]
    # else:
    #     print 'Invalid header for truth booth ceremony'

    # pandas code
    if header == 'Yes':
        matches = matches[matches[boy] == girl]
    elif header == 'No':
        matches = matches[matches[boy] != girl]
    else:
        print 'Invalid header for truth booth ceremony'

    post_len = len(matches)

    print 'Truth booth of {result} with {name_a} and {name_b} eliminated {n} '\
        '({percent:.2f}%) matches from {orig} to {post}'.format(
            result=header,
            name_a=name_a,
            name_b=name_b,
            n=orig_len - post_len,
            percent=float(orig_len - post_len) * 100 / orig_len,
            orig=orig_len,
            post=post_len
        )
    end = time.time()
    print 'Truth booth took %.2f' % (end - start)

    return matches


def parse_matchup_ceremony(csvreader, header, matches):
    """Parses truth booth data from csv"""

    start = time.time()
    orig_len = len(matches)
    matchups = {}
    for i in xrange(NUM_PLAYERS):
        row = next(csvreader)
        name_a = row[0].strip()
        name_b = row[1].strip()
        boy = BOYS[name_a] if name_a in BOYS else BOYS[name_b]
        girl = GIRLS[name_a] if name_a in GIRLS else GIRLS[name_b]
        matchups[boy] = girl

    # count similar matchups
    count_matchups = np.zeros(orig_len)
    for i in xrange(NUM_PLAYERS):
        girl = matchups[i]
        count_matchups = np.where(matches[i] == girl, 1, 0) + count_matchups

    # filter matchups with different number of correct
    matches = matches[count_matchups == int(header)]
    post_len = len(matches)

    end = time.time()
    print 'Matchup ceremony of {result} eliminated {n} '\
        '({percent:.2f}%) matches from {orig} to {post}'.format(
            result=header,
            n=orig_len - post_len,
            percent=float(orig_len - post_len) * 100 / orig_len,
            orig=orig_len,
            post=post_len
        )
    print 'Matchup ceremony took %.2f' % (end - start)

    return matches

def findProb(matches):
    """Creates spreadsheet of probabilities from remaining possibilities"""

    df_prob = pd.DataFrame(index=range(NUM_PLAYERS))

    for i in xrange(NUM_PLAYERS):
        df_prob = pd.concat([df_prob, pd.DataFrame(matches[i].value_counts(), columns=[i])], axis=1)
    # df_prob = df_prob.fillna(0)
    df_prob = df_prob / len(matches)

    df_prob = df_prob.rename(index=GIRLS_REV, columns=BOYS_REV)
    df_prob.to_csv(PROB_FILE)


def guess_matchup_ceremony(csvreader, header, matches):
    """Generate distribution of matchups
    based on a guess for the matchup ceremony"""

    start = time.time()
    orig_len = len(matches)
    matchups = {}
    for i in xrange(NUM_PLAYERS):
        row = next(csvreader)
        name_a = row[0].strip()
        name_b = row[1].strip()
        boy = BOYS[name_a] if name_a in BOYS else BOYS[name_b]
        girl = GIRLS[name_a] if name_a in GIRLS else GIRLS[name_b]
        matchups[boy] = girl

    # count similar matchups
    count_matchups = np.zeros(orig_len)
    for i in xrange(NUM_PLAYERS):
        girl = matchups[i]
        count_matchups = np.where(matches[i] == girl, 1, 0) + count_matchups

    df_prob = pd.DataFrame(
        index=range(NUM_PLAYERS+1),
        data=pd.Series(count_matchups).value_counts(),
        columns=['prob']
    )

    df_prob = df_prob / orig_len
    df_prob.to_csv(GUESS_FILE)


def main():
    """Run load/generation of all matches and read csv to apply filters"""
    if os.path.isfile(MATCH_LOAD):
        matches = pd.read_pickle(MATCH_LOAD)

    else:
        matches = gen_combinations()

    matches = read_csv(DATA_FILE, matches)
    findProb(matches)

    matches.to_pickle(MATCH_SAVE)

if __name__ == '__main__':
    main()


















