import click
import json
import utils
from datetime import datetime, timedelta

DATETIME_FORMAT = "%y-%b-%d %H:%M"

UTF_LEFT = b'\xc3\xa0K'
UTF_UP = b'\xc3\xa0H'
UTF_RIGHT = b'\xc3\xa0M'
UTF_DOWN = b'\xc3\xa0P'
UTF_ENTER = b'\r'

BANNER = """
-------------------------------------------------------------
------ WELCOME TO KEMPERLIFT v1.0 (%s) ---------
-------------------------------------------------------------
""" % datetime.now().strftime(DATETIME_FORMAT)

def view_exercises():
    with open('data/exercises.json', 'r') as file:
        exercises = json.load(file)

    print('\tEXERCISE DATA:\n')

    print(json.dumps(exercises, indent=4))

    input('\npress enter to return to menu...')

def view_muscle_groups():
    with open('data/muscleGroups.json', 'r') as file:
        data = json.load(file)

    print('\tMUSCLE GROUP DATA:\n')

    print(json.dumps(data, indent=4))

    input('\npress enter to return to menu...')

""" STATES = YEAR_SELECT, MONTH_SELECT, DAY_SELECT, HOUR_SELECT, MINUTE_SELECT, CHOICES_SELECT """
def create_session():
    with open('data/exercises.json', 'r') as file:
        exercises = json.load(file)

    choices = []
    date = (datetime.now() + timedelta(days=1)).replace(minute=0)
    states = ['YEAR_SELECT', 'MONTH_SELECT', 'DAY_SELECT', 'HOUR_SELECT', 'MINUTE_SELECT', 'CHOICES_SELECT', 'FINISHED']
    stateid = 0

    while True:
        state = states[stateid]
        click.clear()
        click.echo(BANNER)

        click.echo('\tNEW SESSION (%s):\n' % states[stateid])
        click.echo('\tDate:\t%s' % date.strftime("%y %b %d"))
        click.echo('\tTime:\t%s' % date.strftime("%H:%M"))
        click.echo('\tExercises:')
        for choice in choices:
            click.echo('\t\t%s' % choice)

        click.echo()
        if state == 'YEAR_SELECT':
            click.echo('\tSelect Year (ENTER=%d | ARROWS): ' % date.year, nl=False)
            recv = click.getchar().encode('utf-8')
            if recv == UTF_DOWN or recv == UTF_LEFT:
                date = date.replace(year=date.year - 1)
            elif recv == UTF_UP or recv == UTF_RIGHT:
                date = date.replace(year=date.year + 1)
            elif recv == UTF_ENTER:
                stateid += 1

        elif state == 'MONTH_SELECT':
            click.echo('\tSelect Month (ENTER=%s | ARROWS): ' % date.strftime("%b"), nl=False)
            recv = click.getchar().encode('utf-8')
            if recv == UTF_DOWN or recv == UTF_LEFT:
                date = utils.add_months(date, -1)
            elif recv == UTF_UP or recv == UTF_RIGHT:
                date = utils.add_months(date, 1)
            elif recv == UTF_ENTER:
                stateid += 1

        elif state == 'DAY_SELECT':
            click.echo('\tSelect Day (ENTER=%d | ARROWS): ' % date.day, nl=False)
            recv = click.getchar().encode('utf-8')
            if recv == UTF_DOWN or recv == UTF_LEFT:
                date = utils.add_days(date, -1)
            elif recv == UTF_UP or recv == UTF_RIGHT:
                date = utils.add_days(date, 1)
            elif recv == UTF_ENTER:
                stateid += 1

        elif state == 'HOUR_SELECT':
            click.echo('\tSelect Hour (ENTER=%d | ARROWS): ' % date.hour, nl=False)
            recv = click.getchar().encode('utf-8')
            if recv == UTF_DOWN or recv == UTF_LEFT:
                date = date - timedelta(hours=1)
            elif recv == UTF_UP or recv == UTF_RIGHT:
                date = date + timedelta(hours=1)
            elif recv == UTF_ENTER:
                stateid += 1

        elif state == 'MINUTE_SELECT':
            click.echo('\tSelect Minute (ENTER=%d | ARROWS): ' % date.minute, nl=False)
            recv = click.getchar().encode('utf-8')
            if recv == UTF_DOWN or recv == UTF_LEFT:
                date = date - timedelta(minutes=15)
            elif recv == UTF_UP or recv == UTF_RIGHT:
                date = date + timedelta(minutes=15)
            elif recv == UTF_ENTER:
                stateid += 1

        elif state == 'CHOICES_SELECT':
            for i in range(len(exercises)):
                click.echo('\t\t(%d) - %s' % (i + 1, list(exercises.keys())[i]))
            click.echo('\n\tSelect Next Exercise (ENTER=FINISHED | #): ', nl=False)
            recv = input()
            if recv.isdigit() and 0 < int(recv) < len(exercises):
                choices.append(list(exercises.keys())[int(recv) - 1])
            elif recv == '':
                stateid += 1

        elif state == 'FINISHED':
            click.pause('\n\t<<< Finalized new session of %d exercises on %s...' % (len(choices),
                                                                                    date.strftime(DATETIME_FORMAT)))
            return

def enter_session():
    pass

""" STATES = LIST_VIEW, SESSION_VIEW """
def view_history():
    pass

ACTIONS = {
    "Enter Session": enter_session,
    "Create New Session": create_session,
    "View History": view_history,
    "View Exercises": view_exercises,
    "View Muscle Groups": view_muscle_groups
}

def select_option(options):
    for i in range(len(options)):
        print('\t%d. - %s' % (i + 1, options[i]))

    print()

    response = input('\tSELECT ACTION (%d - %d): ' % (1, len(options)))

    return options[int(response) - 1]

class MainApp:
    def __init__(self):
        pass

    def run(self):
        input_str = ""
        while input_str != "exit":
            click.clear()
            click.echo(BANNER)

            response = select_option(list(ACTIONS.keys()))

            if response:
                ACTIONS[response]()
            else:
                click.echo('\npress enter to return to menu')



if __name__ == '__main__':
    app = MainApp()
    app.run()