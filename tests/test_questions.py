# This is literally just to test if the module ConsoleQuestionPrompts is installed
# and working properly

from ConsoleQuestionPrompts import questions

if __name__ == '__main__':
    response = questions.ask_question(
        'What is the answer to life, the universe, and everything? ')

    if response == '42':
        print('Correct!')
    else:
        print('Incorrect!')
