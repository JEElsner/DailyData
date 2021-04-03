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
from sys import argv

import ConsoleQuestionPrompts as questions
from DailyData.analyzer import parse_docx

from .. import tracker


class Journaller:

    def __init__(self, tracker_cfg):
        self.cfg: tracker.TrackerConfig = tracker_cfg

        # Prepend act_ for 'activity' to each activity question header.
        # This is done to reduce the possibility of duplicates and make it more
        # clear what those columns represent.
        self.activity_questions = {'act_{e}'.format(e=k):
                                   'Did you {activity} today?'.format(
            activity=v)
            for k, v in self.cfg.activity_questions.items()}

        # Add all activity and event columns to the master list of columns
        self.columns = self.cfg.columns + \
            list(self.activity_questions.keys())

        # Check for duplicate column names
        if len(set(self.columns)) != len(self.columns):
            raise ValueError('Duplicate column names')

        # Construct the path to the CSV file that will store today's entry
        self.data_file = self.cfg.stats_folder.joinpath(
            str(date.today().year) + self.cfg.data_suffix)

        # Get the timezone for later recording
        self.timezone = datetime.now().astimezone().tzinfo

    def record_and_write_to_file(self):
        '''
        Take the user's input for the day's statistics and record them. Open the
        journalling program if specified in the configuration file.
        '''

        # Verify data file exists, and create it if it doesn't
        if not path.exists(self.data_file):
            # Verify that parent folder of data file exists, or create it
            if not path.exists(self.cfg.stats_folder):
                os.makedirs(self.cfg.stats_folder)

            # Create data file
            with open(self.data_file, 'w') as f:
                f.write(self.cfg.delimiter.join(
                    self.columns) + '\n')

        with open(self.data_file, mode='r+') as file:
            try:
                # Read in the headers to verify they match the data about to be
                # recorded.
                headers = next(file).strip().split(self.cfg.delimiter)

                # Make sure the headers match the data recorded
                if headers != self.columns:
                    raise ValueError(
                        'File columns do not match recording columns:\nFile: {f}\nExpected: {e}'.format(f=headers, e=self.columns))
            except StopIteration:
                pass

            # Get the user's input about their statistics
            entry = self.record()

            # Make sure the kind of data recieved from the user matches what is expected
            if list(entry.keys()) != self.columns:
                raise ValueError(
                    'Recorded information does not match expected data columns\nRecorded: {r}\nExpected: {e}'.format(r=entry.keys(), e=self.columns))

            # Start the journalling program
            if self.cfg.open_journal:
                time = self.open_journal(entry['journal_day'])
                entry['journal_time'] = time.total_seconds()

            # Write today's data to the file
            file.write(self.cfg.delimiter.join([str(i)
                                                for i in entry.values()]) + '\n')

    def record(self):
        '''
        Ask questions to the user, returning their responses as a dictionary that
        maps a key word for the question to the user's response.

        Returns

            dict with string keys for each question with a coresponding response.
        '''

        # Create the dictionary storing the responses
        entry = {c: None for c in self.columns}

        # Greet the user
        # Kindness counts :)
        print(self.cfg.greeting, self.cfg.name + '!')

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

        # Sanitization function to ensure properly-formed delimited files
        def sanitize(s: str) -> str:
            return s.replace(self.cfg.delimiter, '')

        # Ask the question about the date
        entry['journal_day'] = questions.ask_question(prompt, in_bounds=lambda x: x is not None,
                                                      cast=parse_date_response)

        # Record the actual date and time of recording, even if it differs from the
        # nominal journal date
        entry['time'] = datetime.now(self.timezone)

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
        entry['prod_work'] = questions.range_question(
            prompt='how much school work did you do today?\n> '
        )

        entry['prod_house'] = questions.range_question(
            prompt='how much house work (cooking, cleaning, etc.) did you do today?\n> '
        )

        entry['prod_self'] = questions.range_question(
            prompt='how much time did you take for yourself?\n> '
        )

        prompt = 'how stressed were you today?\n> '
        entry['stress'] = questions.range_question(prompt)

        entry['bothers'] = questions.ask_question(
            prompt='What bothered you today?\n> ',
            cast=sanitize
        )

        entry['gratefuls'] = questions.ask_question(
            prompt='What are you grateful for today?\n> ',
            cast=sanitize
        )

        prompt = 'how good of a day was today?\n> '
        entry['score'] = questions.range_question(prompt)

        # Ask the user a subset of several questions and record their responses
        entry.update(questions.ask_some(self.activity_questions,
                                        self.cfg.activity_questions_count))

        # Allow the user a little more freedom in expressing the quality of their day
        prompt = 'Input any keywords for today. For example, things that happened today.\n> '
        entry['keywords'] = questions.ask_question(prompt, cast=sanitize)

        # Return the user's responses
        return entry

    def open_journal(self, date: date, create_file=parse_docx.new_doc, header_func=parse_docx.add_header):
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
        journal_path = self.cfg.journal_folder.joinpath(
            date.strftime('%Y-%m') + self.cfg.journal_suffix)

        # Create the file if it does not exist
        self.cfg.journal_folder.mkdir(
            parents=True, exist_ok=True)
        if not path.exists(journal_path):
            create_file(journal_path)

        # Add a new header
        header_func(journal_path, date.strftime('%Y-%m-%d'))

        # Record when the user started editing their journal entry
        start = datetime.now()

        # Open the journal file with the associated program in the OS
        system('start /WAIT ' + str(journal_path.absolute()))

        # Return the duration of time the user spent editing their journal
        return datetime.now() - start
