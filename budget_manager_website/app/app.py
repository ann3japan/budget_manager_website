from typing import Optional
from bson import json_util, ObjectId
from datetime import datetime
from flask import Flask, render_template, request, redirect, send_from_directory, flash, session, url_for
from flask_wtf import FlaskForm
from werkzeug.security import generate_password_hash, check_password_hash
from wtforms import StringField, PasswordField, SubmitField, IntegerField, SelectField
from wtforms.validators import Length, EqualTo, InputRequired, Optional, NumberRange
from flask_bootstrap import Bootstrap 
from flask_pymongo import PyMongo
import json
from uuid import uuid4
from os import environ

app = Flask(__name__)

app.config["MONGO_URI"] = f"mongodb://{environ.get('MONGO_HOST')}/wad_Budget_Manager"
bootstrap = Bootstrap(app)
mongo = PyMongo(app)
app.secret_key = 'secr3t_k1yuch@'


class SignUpForm(FlaskForm):
    login = StringField('Login', validators=[InputRequired(message="LOGIN REQUIRED"), Length(min=3, max=25, message="LOGIN MUST BE BETWEEN 3 AND 25 CHARACTERS")])
    password = PasswordField('Password', validators=[InputRequired(message="PASSWORD REQUIRED"), Length(min=8, max=30, message="PASSWORD MUST BE BETWEEN 8 AND 30 CHARACTERS")])
    password_retype = PasswordField('Retype password', validators=[InputRequired(message="RETYPE OF PASSWORD REQUIRED"), EqualTo('password', message="PASSWORDS MUST BE EQUAL")])
    submit = SubmitField('Sign Up')

class AuthForm(FlaskForm):
    login = StringField('Login', validators=[InputRequired(message="LOGIN REQUIRED")])
    password = PasswordField('Password', validators=[InputRequired(message="PASSWORD REQUIRED")])
    submit = SubmitField('Log In')

class IncomeForm(FlaskForm):
    income_category = SelectField('Category', choices=['Wages', 'Cashback', 'Other'])

    description = StringField('Description', validators=[Optional()])
    amount = IntegerField('Amount', validators=[InputRequired(message="AMOUNT REQUIRED"), NumberRange(min=0, max=0xffffffff)])
    submit = SubmitField('Add Transaction')

class OutcomeForm(FlaskForm):
    outcome_category = SelectField('Category', choices=['Groceries', 'Services', 'Food', 'Drugs', 'Other'])
    description = StringField('Description', validators=[Optional()])
    amount = IntegerField('Amount', validators=[InputRequired(message="AMOUNT REQUIRED"), NumberRange(min=0, max=0xffffffff)])
    submit = SubmitField('Add Transaction')

@app.route('/', methods=['GET', 'POST'])
def index():
    return render_template('index.html')


@app.route('/auth', methods=['GET', 'POST'])
def auth():
    form = AuthForm()
    login = form.login.data
    password = form.password.data

    if 'login' in session:
        return redirect('/profile')

    if request.method == 'GET':
        return render_template('auth.html', form=form)

    else:
        user = mongo.db.users.find_one({'login':login})

        if user and check_password_hash(user['password'], password):
            session['login'] = user.get('login')
            session['user_id'] = user.get('user_id')
            return redirect('/profile')
        else:
            flash('wrong creds! Try again :(')
            return redirect('/auth')


@app.route('/signup', methods=['GET', 'POST'])
def signup():

    form = SignUpForm()
    login = form.login.data
    password = form.password.data
    password_retype = form.password_retype.data

    if request.method == 'GET':
        return render_template('signup.html', form=form)

    else:
        if mongo.db.users.count_documents({'login':login}) !=0:
            flash('Login already exist')
            return redirect('/signup')
        elif password_retype != password:
            flash('Password doesnt match, try harder')
            return redirect('/signup')    
        else:
            mongo.db.users.insert_one({
                'user_id':str(uuid4()),
                'login':login,
                'password':generate_password_hash(password)
                })
            return redirect('/auth')

@app.route('/addIncome', methods=['POST', 'GET'])
def addIncome():
    # TODO
    # make auth check with decorators?
    form = IncomeForm()
    income_amount = 0
    income_list = []

    if request.method == "GET" or not session.get('login'):
        if 'login' in session:
            try:
                show_amount = int(request.args.get('show'))
            except:
                show_amount = 5
            income_entries = mongo.db.income.find({
                    "user_id": session.get('user_id')
                },
                sort=[("_id",-1)],
                # limit=show_amount
            )
            for item in income_entries:
                income_list.append(json.loads(json.dumps(item,default=json_util.default)))
                income_amount += item.get('amount')
            return render_template('addIncome.html', form=form, income=income_amount, income_entries=income_list, show_next=show_amount+5, show_before=show_amount-5) #, scroll=True)
        else:
            return redirect(url_for('auth'))
    
    # description = form.description.data
    # amount = form.amount.data
    # expense = mongo.db.budget.insert_one({
    #     "user_id": session.get('user_id'),
    #     "description": description,
    #     "amount": amount
    # })
    # return redirect(url_for('index'))

    income_category = form.income_category.data
    description = form.description.data
    amount = form.amount.data


    income_result = mongo.db.income.insert_one({
        "user_id": session.get('user_id'),
        "datetime": datetime.now().strftime("%d.%m.%Y %H:%M"),
        'income_category': income_category,
        "description": description,
        "amount": amount
    })
    
    flash('The income was successfully created!')
    return redirect(url_for('addIncome'))

@app.route('/addOutcome', methods=['POST', 'GET'])
def addOutcome():
    # TODO
    # make auth check with decorators?
    form = OutcomeForm()
    outcome_list = []
    if request.method == "GET" or not session.get('login'):
        if 'login' in session:
            try:
                show_amount = int(request.args.get('show'))
            except:
                show_amount = 5
            # sort = (request.args.get('sort'), request.args.get('sortBy')) if request.args.get('sort') else ()
            outcome_entries = mongo.db.outcome.find({
                    "user_id": session.get('user_id')
                },
                sort=[("_id",-1)],
                # limit=show_amount
            )
            for item in outcome_entries:
                outcome_list.append(json.loads(json.dumps(item,default=json_util.default)))
            return render_template('addOutcome.html', form=form, outcome_entries=outcome_list, show_next=show_amount+5, show_before=show_amount-5) #, scroll=True)
        else:
            return redirect(url_for('index'))
    
    outcome_category = form.outcome_category.data
    description = form.description.data
    amount = form.amount.data

    # outcome_amount = 0
    outcome_list = []

    outcome_result = mongo.db.outcome.insert_one({
        "user_id": session.get('user_id'),
        "outcome_category": outcome_category,
        "datetime": datetime.now().strftime("%d.%m.%Y %H:%M"),
        "description": description,
        "amount": amount
    })

    outcome_entries = mongo.db.outcome.find({
            "user_id": session.get('user_id')
        },
        sort=[("_id",-1)],
        limit=5
    )
    for item in outcome_entries:
        outcome_list.append(json.loads(json.dumps(item,default=json_util.default)))
        # outcome_amount += item.get('amount')

    flash('The expense line was successfully created!') 
    return redirect(url_for('addOutcome'))

@app.route('/profile', methods=['GET', 'POST'])
def profile():
    income_amount = 0
    outcome_amount = 0
    income_list = []
    if not session.get('login'):
        return redirect('/auth')
    income_entries = mongo.db.income.find({
        "user_id": session.get('user_id')
    })
    for item in income_entries:
        income_list.append(json.loads(json.dumps(item,default=json_util.default)))
        income_amount += item.get('amount')
    outcome_entries = mongo.db.outcome.find({
        "user_id": session.get('user_id')
    })
    for item in outcome_entries:
        outcome_amount += item.get('amount')

    return render_template('profile.html', income=income_amount, outcome=outcome_amount, income_entries=income_list, username=session.get('login'))
        

@app.route('/history')
def history():
    # TODO
    # login_required
    if not session.get('login'):
        return redirect('/auth')
    result_list = []
    income_entries = mongo.db.income.find({
        "user_id": session.get('user_id')
        },
        sort=[("_id",-1)],
        # limit=show
    )
    for item in income_entries:
        temp = json.loads(json.dumps(item,default=json_util.default))
        temp.update({"category":temp.get('income_category'), "type":"history-income"})
        result_list.append(temp)

    outcome_entries = mongo.db.outcome.find({
        "user_id": session.get('user_id')
        },
        sort=[("_id",-1)],
        # limit=show
    )
    for item in outcome_entries:
        temp = json.loads(json.dumps(item,default=json_util.default))
        temp.update({"category":temp.get('outcome_category'), "type":"history-outcome"})
        result_list.append(temp)
    # from IPython import embed; embed()
    return render_template('history.html', username=session.get('login'), history_list=sorted(result_list, key=lambda d: d['datetime'], reverse=True)) # [:show], show_before=show-5, show_next=show+5)


@app.route('/logout', methods=['POST', 'GET'])
def logout():
    if 'login' in session:
        session.pop('login', None)
        return render_template('index.html')
    else:
        return render_template('index.html')

if __name__ == "__main__":
    app.run(host='localhost', port=5000, debug=True)
