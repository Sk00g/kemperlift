import click
import json
import utils
import calendar
from datetime import datetime, timedelta

DATETIME_FORMAT = "%Y-%b-%d %H:%M"
DATETIME_FULL_FORMAT = "%Y-%b-%d %H:%M:%S"

UTF_LEFT = b'\xc3\xa0K'
UTF_UP = b'\xc3\xa0H'
UTF_RIGHT = b'\xc3\xa0M'
UTF_DOWN = b'\xc3\xa0P'
UTF_ENTER = b'\r'

BANNER = """
-------------------------------------------------------------
------ WELCOME TO KEMPERLIFT v1.0 (%s) -------
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
    states = ['YEAR_SELECT', 'MONTH_SELECT', 'DAY_SELECT',
              'HOUR_SELECT', 'MINUTE_SELECT', 'CHOICES_SELECT', 'FINISHED']
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
            click.echo('\tSelect Year (ENTER=%d | ARROWS): ' %
                       date.year, nl=False)
            recv = click.getchar().encode('utf-8')
            if recv == UTF_DOWN or recv == UTF_LEFT:
                date = date.replace(year=date.year - 1)
            elif recv == UTF_UP or recv == UTF_RIGHT:
                date = date.replace(year=date.year + 1)
            elif recv == UTF_ENTER:
                stateid += 1

        elif state == 'MONTH_SELECT':
            click.echo('\tSelect Month (ENTER=%s | ARROWS): ' %
                       date.strftime("%b"), nl=False)
            recv = click.getchar().encode('utf-8')
            if recv == UTF_DOWN or recv == UTF_LEFT:
                date = utils.add_months(date, -1)
            elif recv == UTF_UP or recv == UTF_RIGHT:
                date = utils.add_months(date, 1)
            elif recv == UTF_ENTER:
                stateid += 1

        elif state == 'DAY_SELECT':
            click.echo('\tSelect Day (ENTER=%d | ARROWS): ' %
                       date.day, nl=False)
            recv = click.getchar().encode('utf-8')
            if recv == UTF_DOWN or recv == UTF_LEFT:
                date = utils.add_days(date, -1)
            elif recv == UTF_UP or recv == UTF_RIGHT:
                date = utils.add_days(date, 1)
            elif recv == UTF_ENTER:
                stateid += 1

        elif state == 'HOUR_SELECT':
            click.echo('\tSelect Hour (ENTER=%d | ARROWS): ' %
                       date.hour, nl=False)
            recv = click.getchar().encode('utf-8')
            if recv == UTF_DOWN or recv == UTF_LEFT:
                date = date - timedelta(hours=1)
            elif recv == UTF_UP or recv == UTF_RIGHT:
                date = date + timedelta(hours=1)
            elif recv == UTF_ENTER:
                stateid += 1

        elif state == 'MINUTE_SELECT':
            click.echo('\tSelect Minute (ENTER=%d | ARROWS): ' %
                       date.minute, nl=False)
            recv = click.getchar().encode('utf-8')
            if recv == UTF_DOWN or recv == UTF_LEFT:
                date = date - timedelta(minutes=15)
            elif recv == UTF_UP or recv == UTF_RIGHT:
                date = date + timedelta(minutes=15)
            elif recv == UTF_ENTER:
                stateid += 1

        elif state == 'CHOICES_SELECT':
            for i in range(len(exercises)):
                click.echo('\t\t(%d) - %s' %
                           (i + 1, list(exercises.keys())[i]))
            click.echo(
                '\n\tSelect Next Exercise (ENTER=FINISHED | #): ', nl=False)
            recv = input()
            if recv.isdigit() and 0 < int(recv) <= len(exercises):
                choices.append(list(exercises.keys())[int(recv) - 1])
            elif recv == '':
                stateid += 1

        elif state == 'FINISHED':
            click.pause('\n\t<<< Finalized new session of %d exercises on %s...' % (len(choices),
                                                                                    date.strftime(DATETIME_FORMAT)))
            with open('data/sessions.json', 'r') as file:
                sessions = json.load(file)
            with open('data/sessions.json', 'w') as file:
                sid = hash(
                    frozenset([date.strftime(DATETIME_FORMAT), *choices]))
                sessions.append(dict(
                    id=sid,
                    timeScheduled=date.strftime(DATETIME_FORMAT),
                    timeStarted="", timeFinished="",
                    status='PENDING',
                    exercises=choices,
                    completions={}
                ))
                json.dump(sessions, file)
            return


""" STATES = SELECT_SESSION, SELECT_EXERCISE, SELECT_REPS, SELECT_WEIGHT"""


def enter_session():
    with open('data/sessions.json', 'r') as file:
        sessions = json.load(file)
        sessions.sort(key=lambda s: datetime.strptime(
            s['timeScheduled'], DATETIME_FORMAT))

    with open('data/exercises.json', 'r') as file:
        exercise_data = json.load(file)

    with open('data/sessionHistory.json', 'r') as file:
        session_history = json.load(file)

    state = 'SELECT_SESSION'
    matched_session = None
    active_session = None
    active_exercise = None
    next_exercise_id = 0

    while True:
        click.clear()
        click.echo(BANNER)

        if active_session:
            click.echo('\tACTIVE SESSION (%s):' %
                       active_session['timeScheduled'])
            click.echo('\tStarted:\t%s' % active_session['timeStarted'])
            elapsed = datetime.now() - \
                datetime.strptime(
                    active_session['timeStarted'], DATETIME_FULL_FORMAT)
            click.echo('\tDuration:\t%s:%s\n' %
                       (int(elapsed.seconds / 60), elapsed.seconds % 60))

            complete_exercises = [
                complete_ex for complete_ex in active_session['completions']]
            exercises = active_session['exercises']
            for i in range(len(exercises)):
                weight_suggestion = ''
                if exercise_data[exercises[i]]['usesWeight']:
                    for sid in range(len(session_history)):
                        session = session_history[-(sid + 1)]
                        if exercises[i] in session['completions']:
                            weight_suggestion = [rep['weight'] for rep in session['completions'][exercises[i]]['sets']]
                            break
                click.echo('\t\t(%d) - %s \t%s \t%s' % (i + 1,
                                                   exercises[i],
                                                   weight_suggestion,
                                                   '*COMPLETE*' if exercises[i] in complete_exercises else ''))

            for exercise in active_session['completions']:
                click.echo('\n\tExercise:\t%s (%d)' % (
                    exercise, len(active_session['completions'][exercise])))
                for i in range(len(active_session['completions'][exercise]['sets'])):
                    aset = active_session['completions'][exercise]['sets'][i]
                    click.echo('\t\tSet %s: %s' %
                               (i + 1, aset['reps']), nl=False)
                    click.echo('\t\t%s lbs' %
                               aset['weight'] if aset['weight'] else '')

        click.echo('\n')

        if state == 'SELECT_SESSION':
            for i in range(len(sessions)):
                day_id = datetime.strptime(
                    sessions[i]['timeScheduled'], DATETIME_FORMAT).weekday()
                day_name = calendar.weekheader(9).split()[day_id]
                click.echo('\t\t%d. - %s %s (%d)' % (i + 1,
                                                     day_name,
                                                     sessions[i]['timeScheduled'],
                                                     len(sessions[i]['exercises'])))
            click.echo('\n\tActivate Session (ENTER=(1) | #): ', nl=False)
            recv = input()
            if recv.isdigit() and 0 < int(recv) <= len(sessions):
                matched_session = sessions[int(recv) - 1]
            elif recv == '':
                matched_session = sessions[0]

            if matched_session:
                active_session = matched_session.copy()
                active_session['timeStarted'] = datetime.now().strftime(
                    DATETIME_FULL_FORMAT)
                state = 'SELECT_EXERCISE'

        elif state == 'SELECT_EXERCISE':
            complete_exercises = [
                complete_ex for complete_ex in active_session['completions']]
            if len(complete_exercises) == len(active_session['exercises']):
                state = 'FINISHED'
                continue

            exercises = active_session['exercises']
            click.echo('\tBegin Exercise (ENTER=(1) | END | #): ', nl=False)
            recv = input()

            active_exercise = None
            if recv.isdigit() and 0 < int(recv) <= len(exercises):
                active_exercise = exercises[int(recv) - 1]
                next_exercise_id = int(recv) - 1
            elif recv == '':
                active_exercise = exercises[next_exercise_id]

            if active_exercise:
                active_session['completions'][active_exercise] = dict(
                    timeStarted=datetime.now().strftime(DATETIME_FULL_FORMAT),
                    timeFinished="",
                    sets=[]
                )
                state = 'SELECT_WEIGHT' if exercise_data[active_exercise]['usesWeight'] else 'SELECT_REPS'

            elif recv.lower() == 'end':
                state = 'FINISHED'
                continue

        elif state == 'SELECT_WEIGHT':
            click.echo(
                '\n\tComplete Exercise (ENTER=NEXT | #=Weight): ', nl=False)
            recv = input()
            if recv.isdigit() and 0 < int(recv) <= 100:
                active_session['completions'][active_exercise]['sets'].append(
                    dict(reps=None, weight=int(recv)))
                state = 'SELECT_REPS'
            elif recv == '':
                active_session['completions'][active_exercise]['timeFinished'] = datetime.now().strftime(
                    DATETIME_FULL_FORMAT)
                next_exercise_id += 1
                state = 'SELECT_EXERCISE'

        elif state == 'SELECT_REPS':
            click.echo(
                "\n\tComplete Exercise (ENTER=NEXT | #=REPS): ", nl=False)
            recv = input()
            if recv.isdigit() and 0 < int(recv) <= 1000:
                current_set = active_session['completions'][active_exercise]['sets'][-1] if \
                    active_session['completions'][active_exercise]['sets'] else None
                if not current_set or current_set['reps']:
                    active_session['completions'][active_exercise]['sets'].append(
                        dict(reps=int(recv), weight=None))
                else:
                    current_set['reps'] = int(recv)

                if exercise_data[active_exercise]['usesWeight']:
                    state = 'SELECT_WEIGHT'
                else:
                    state = 'SELECT_REPS'
            elif recv == '':
                active_session['completions'][active_exercise]['timeFinished'] = datetime.now().strftime(
                    DATETIME_FULL_FORMAT)
                next_exercise_id += 1
                state = 'SELECT_EXERCISE'

        elif state == 'FINISHED':
            click.pause('\n\t<<< Finalized session completion on %s...' %
                        active_session['timeStarted'])
            active_session['timeFinished'] = datetime.now().strftime(
                DATETIME_FULL_FORMAT)

            with open('data/sessionHistory.json', 'r') as file:
                session_history = json.load(file)
            with open('data/sessionHistory.json', 'w') as file:
                session_history.append(active_session)
                json.dump(session_history, file)

            with open('data/sessions.json', 'w') as file:
                sessions.remove(matched_session)
                json.dump(sessions, file)

            return


""" STATES = LIST_VIEW, SESSION_VIEW """


def view_history():
    with open('data/sessionHistory.json', 'r') as file:
        sessions = json.load(file)
        sessions.sort(key=lambda s: datetime.strptime(
            s['timeStarted'], DATETIME_FULL_FORMAT))
        sessions.reverse()

    state = 'LIST_VIEW'
    selection = None

    while True:
        click.clear()
        click.echo(BANNER)

        if state == 'LIST_VIEW':
            for i in range(len(sessions)):
                start_time = datetime.strptime(
                    sessions[i]['timeStarted'], DATETIME_FULL_FORMAT)
                end_time = datetime.strptime(
                    sessions[i]['timeFinished'], DATETIME_FULL_FORMAT)
                duration = end_time - start_time
                day_id = datetime.strptime(
                    sessions[i]['timeStarted'], DATETIME_FULL_FORMAT).weekday()
                day_name = calendar.weekheader(5).split()[day_id].upper()
                click.echo('\t%d. %s %s (SCHED: %s) Duration: %s (%d)' % (i + 1,
                                                                          day_name,
                                                                          sessions[i]['timeStarted'][:-2],
                                                                          sessions[i]['timeScheduled'],
                                                                          '%s:%s' % (
                                                                              int(duration.seconds / 60), duration.seconds % 60),
                                                                          len(sessions[i]['completions'])))
            click.echo('\n\tView Session (ENTER=MENU | #): ', nl=False)
            recv = input()
            if recv.isdigit() and 0 < int(recv) <= len(sessions):
                selection = sessions[int(recv) - 1]
                state = 'SESSION_VIEW'
            elif recv == '':
                return

        elif state == 'SESSION_VIEW':
            click.echo(json.dumps(selection, indent=4))
            click.echo('\n\t<<< Press any key to return to list')
            click.getchar()
            selection = None
            state = 'LIST_VIEW'


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
