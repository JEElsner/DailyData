'''
Jonathan Elsner
2020

Records various statistics about the user's day, in hopes of better
understanding what contributes to the user's overall mood on a given day,
to promote positive lifestyle changes.
'''

import json
import os
import random as rand
from datetime import date, datetime
from os import path, system
from pathlib import Path as PathObject

from ConsoleQuestionPrompts import questions

# The path to the configuration JSON file containing all of the settings and
# questions
config_file = './journaler_config.json'

# Load the config file and parse the settings
with open(config_file, 'r') as file:
    cfg = json.load(file)

    # Prepend act_ for 'activity' to each activity question header.
    # This is done to reduce the possibility of duplicates and make it more
    # clear what those columns represent.
    cfg['activity_questions'] = {'act_{e}'.format(e=k):
                                 'Did you {activity} today?'.format(
                                     activity=v)
                                 for k, v in cfg['activity_questions'].items()}

    # Prepend evt_ for 'event' to each event question header. This is done for
    # the same reasons listed above.
    cfg['event_questions'] = {'evt_{a}'.format(
        a=k): v for k, v in cfg['event_questions'].items()}

    # Add all activity and event columns to the master list of columns
    cfg['columns'] += list(cfg['activity_questions'].keys()) + \
        list(cfg['event_questions'].keys())

    # Check for duplicate column names
    if len(set(cfg['columns'])) != len(cfg['columns']):
        raise ValueError('Duplicate column names')

# Construct the path to the CSV file that will store today's entry
data_file = cfg['data_folder'] + str(date.today().year) + cfg['data_suffix']

# Get the timezone for later recording
timezone = datetime.now().astimezone().tzinfo


def main():
    '''
    Take the user's input for the day's statistics and record them. Open the
    journalling program if specified in the configuration file.
    '''

    # Verify data file exists, and create it if it doesn't
    if not path.exists(data_file):
        # Verify that parent folder of data file exists, or create it
        if not path.exists(cfg['data_folder']):
            os.makedirs(cfg['data_folder'])

        # Create data file
        with open(data_file, 'w') as f:
            f.write(cfg['delimiter'].join(cfg['columns']) + '\n')

    with open(data_file, mode='r+') as file:
        try:
            # Read in the headers to verify they match the data about to be
            # recorded.
            headers = next(file).strip().split(cfg['delimiter'])

            # Make sure the headers match the data recorded
            if headers != cfg['columns']:
                raise ValueError(
                    'File columns do not match recording columns:\nFile: {f}\nExpected: {e}'.format(f=headers, e=cfg['columns']))
        except StopIteration:
            pass

        # Get the user's input about their statistics
        entry = record()

        # Make sure the kind of data recieved from the user matches what is expected
        if list(entry.keys()) != cfg['columns']:
            raise ValueError(
                'Recorded information does not match expected data columns\nRecorded: {r}\nExpected: {e}'.format(r=entry.keys(), e=cfg['columns']))

        # Start the journalling program
        if cfg['journal']:
            time = open_journal(entry['journal_day'])
            entry['journal_time'] = time.total_seconds()

        # Write today's data to the file
        file.write(cfg['delimiter'].join([str(i)
                                          for i in entry.values()]) + '\n')


def record():
    '''
    Ask questions to the user, returning their responses as a dictionary that
    maps a key word for the question to the user's response.

    Returns

        dict with string keys for each question with a coresponding response.
    '''

    # Create the dictionary storing the responses
    entry = {c: None for c in cfg['columns']}

    # Greet the user
    # Kindness counts :)
    print(cfg['greeting'], cfg['name'] + '!')

    # Verify the date, and allow the user to change it
    # This is useful if the user is journalling after midnight, and wants the
    # data to be recorded for the previous day
    prompt = 'You are journalling for the date of ' + \
        str(date.today()) + ' is that correct? Press enter or type \'yes\' if it' + \
        ' is, or enter the correct date in the form yyyy-mm-dd.\n> '

    # Custom function to parse the user's response to the date question
    def parse_date_response(response: str):
        # If the date is correct, the user either responds with yes or inputs
        # nothing
        if len(response) == 0 or response.lower()[0] == 'y':
            return date.today()  # The current date is good, return it
        else:
            # If the current date is not the desired date, parse the user's
            # input for the correct date
            try:
                return date.fromisoformat(response)
            except:
                # If the passed date was bad, return None so the question is
                # asked again
                return None

    # Ask the question about the date
    entry['journal_day'] = questions.ask_question(prompt, in_bounds=lambda x: x is not None,
                                                  cast=parse_date_response)

    # Record the actual date and time of recording, even if it differs from the
    # nominal journal date
    entry['time'] = datetime.now(timezone)

    # Ask the user how their day was relative to yesterday. Later it is asked
    # how their day was on a fixed, absolute scale. I think this question is
    # important however, for data redundancy and validity. Also it can be hard
    # to quantify how good a day is on an absolute scale, and its nice to have
    # something to reference.
    prompt = 'Today was _________ yesterday.'
    choices = ['much worse than',
               'worse than',
               'the same as',
               'better than',
               'much better than'
               ]
    entry['relative_score'] = questions.option_question(
        prompt, choices, range(-2, 3))

    # All of these are pretty self explanatory
    # Ask the user a question, and record their response in the dictionary
    prompt = 'how focused were you today?\n> '
    entry['focus'] = questions.range_question(prompt)

    prompt = 'how proactive were you today?\n> '
    entry['proactivity'] = questions.range_question(prompt)

    prompt = 'how stressed were you today?\n> '
    entry['stress'] = questions.range_question(prompt)

    prompt = 'how good of a day was today?\n> '
    entry['score'] = questions.range_question(prompt)

    # Ask the user a subset of several questions and record their responses
    entry.update(questions.ask_some(cfg['activity_questions'],
                                    cfg['activity_questions_count']))

    entry.update(questions.ask_some(cfg['event_questions'],
                                    cfg['event_questions_count']))

    # Allow the user a little more freedom in expressing the quality of their day
    prompt = 'Input any keywords for today. For example, things that happened today.\n> '
    entry['keywords'] = questions.ask_question(prompt).replace('`', '')

    # Return the user's responses
    return entry


def open_journal(date: date):
    '''
    Open the user's desired journal program

    Arguments

        date    The current date so to open the corresponding journal file for
                the month

    Returns

        a datetime.timedelta instance representing the amount of time the user
        used their journalling program
    '''

    # Construct the path to the journal file
    journal_path = cfg['journal_folder'] + \
        date.strftime('%Y-%m') + cfg['journal_suffix']

    # Create the file if it does not exist
    PathObject(cfg['journal_folder']).mkdir(parents=True, exist_ok=True)
    if not path.exists(journal_path):
        open(journal_path, 'w')

    # Record when the user started editing their journal entry
    start = datetime.now()

    # Open the journal file with the associated program in the OS
    system('start /WAIT ' + journal_path)

    # Return the duration of time the user spent editing their journal
    return datetime.now() - start


if __name__ == '__main__':
    main()
