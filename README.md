# DailyData
Record data about the day.

## Installation
1. Run `pip install DailyData`
2. Run the command `dailydata --config-file`
3. Open the JSON file returned by the command, and edit the values to your liking
4. Set `"configured"` to `true`


## Use

### Journaller
Use the command `dailydata -j` to start a new journal entry

### Timelog
Use the command `timelog doing [activity]` to record starting an activity. The first time you record doing an activity, you will have to use the switch `-n` to record it. This is necessary so that a different activity isn't recoreded if you accidently type an activity with a typo.

To list your activities, the amount of time you spend doing each, and the percentage of your time you spend on each activity, run `timelog -l`
