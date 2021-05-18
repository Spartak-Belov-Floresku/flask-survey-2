from flask import Flask, request, render_template, redirect, flash, session
from flask_debugtoolbar import DebugToolbarExtension

from surveys import satisfaction_survey as survey
from surveys import surveys

app = Flask(__name__)
app.config['SECRET_KEY'] = "helloworld"
DebugToolbarExtension(app)


'''run home page'''
@app.route('/')
def home():

    '''create list of serveys'''
    surveys_list = []
    for k, v in surveys.items():
        surveys_list.append([v.title, v.instructions, k])

    '''process a new survey'''
    title = survey.title
    instructions = survey.instructions
    return render_template("index.html", surveys_list = surveys_list)


'''check which survey does user prefer'''
@app.route('/survey/<name_of_survey>')
def user_survey(name_of_survey):

    user_survey = surveys.get(f'{name_of_survey}', False)

    '''check if user already took servey if so redirect to finished page'''
    if session.get(f'responses_{name_of_survey}'):
        responses = session.get(f'responses_{name_of_survey}')
        if len(responses) == len(user_survey.questions):
            session['survey'] = name_of_survey
            return redirect('/finished')

    '''check if user is trying to manipulate with url'''
    if not user_survey:
        return redirect('/')

    session['survey'] = name_of_survey
    return redirect(f'/questions/1')


'''run servey page'''
@app.route('/questions/<int:number>')
def questions_servey(number):

    '''check if user is trying to manipulate the url to go to the survey without selecting survey'''
    if not session.get('survey', False):
        return redirect('/')

    name_of_survey = session['survey']

    '''check if session responses exists if not setup session'''
    if session.get(f'responses_{name_of_survey}'):
        responses = session.get(f'responses_{name_of_survey}')
    else:
        responses = []
        session[f'responses_{name_of_survey}'] = responses

    '''check if user requests the correct number of the question if not change to correct number'''
    if number != len(responses)+1:

        msg = f'You are trying to get the invalid number {number} for the question. Your question number is {len(responses)+1}'
        flash(msg, 'warning')

        number = len(responses)+1

    user_survey = surveys.get(f'{name_of_survey}')

    '''check if user already finished servey and tries to get question page'''
    if len(responses) == len(user_survey.questions):
        return redirect('/finished')

    question_number = number
    title = f'Question # {question_number}'

    question = user_survey.questions[number-1].question
    choices = user_survey.questions[number-1].choices

    return render_template('survey.html', title = title, question = question, choices = choices, question_number = question_number)


'''process POST request'''
@app.route('/answer', methods=["POST"])
def answer():

    name_of_survey = session['survey']
    user_survey = surveys.get(f'{name_of_survey}')

    '''get adta from user responce'''
    answer = request.form['answer']
    num = int(request.form['question'])+1

    '''append answer of the user to the session'''
    responses = session[f'responses_{name_of_survey}']
    responses.append(answer)
    session[f'responses_{name_of_survey}'] = responses

    '''check if user finished servey if not rederect to the correct question'''
    if len(responses) < len(user_survey.questions):
        url = f'/questions/{num}'
    else:
        url = '/finished'

    return redirect(url)


'''if survey is finished sends the user to finished page'''
@app.route('/finished')
def finished():

    '''check if user is trying to manipulate the url to go to the finished page without survey'''
    name_of_survey = session.get('survey', False)

    if not name_of_survey:
        return redirect('/')

    user_survey = surveys.get(f'{name_of_survey}')

    '''check if user does not finish servey and rederect to the correct question'''
    if session.get(f'responses_{name_of_survey}'):
        responses = session[f'responses_{name_of_survey}']
        num = len(responses)
    else:
        num = 0
    
    if num < len(user_survey.questions):
        return redirect(f'/questions/{num+1}')
    else:

        '''setup list of questions of the servey to send with responses'''
        sur = []
        for i in range(len(user_survey.questions)):
            sur.append(user_survey.questions[i].question)

        return render_template('finished.html', responses = responses, sur = sur)

    

    
