from flask import Flask, redirect, render_template, flash, session,request
from flask_debugtoolbar import DebugToolbarExtension

from models import db, connect_db, CollabBoard, CollabList, CollabCard, User
from forms import boardForm, listForm, cardForm, UserForm, LoginForm
from sqlalchemy.exc import IntegrityError
from sqlalchemy import asc
import requests
import json
import os
import re

uri = os.getenv("DATABASE_URL",'postgresql:///stock') 
if uri.startswith("postgres://"):
   uri = uri.replace("postgres://", "postgresql://", 1)


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = uri
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = True

app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'hellosecret')
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False

app.app_context().push()

debug = DebugToolbarExtension(app)

connect_db(app)
db.create_all()

s_code = {"AL": "01", "AK": "54", "AZ": "02", "AR": "03", "CA": "04", 
        "CO": "05", "CT": "06", "DC": "08", "DE": "07", "FL": "09", "GA": "10", 
          "HI": "52", "ID": "11", "IL": "12", "IN": "13", "IA": "14", "KS": "15", 
          "KY": "16", "LA": "17", "ME": "18", "MD": "19",
          "MA": "20", "MI": "21", "MN": "22", "MS": "23", "MO": "24",
           "MT": "25", "NE": "26", "NV": "27", "NH": "28", "NJ": "29",
          "NM": "30", "NY": "36", "NC": "32", "ND": "33", "OH": "34", "OK": "35", 
          "OR": "36", "PA": "37", "RI": "38", "SC": "39",
          "SD": "40", "TN": "41", "TX": "42", "UT": "43", "VT": "44", "VA": "45", 
          "WA": "46", "WV": "47", "WI": "48", "WY": "49"}

##############################################################################
# register
# login
# logout
@app.route('/')
def inital_page():
    return render_template('initial.html')

@app.route('/register', methods=['GET', 'POST'])
def register_user():
    form = UserForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        email = form.email.data
        first_name = form. first_name.data
        last_name = form.last_name.data
        city =  form.city.data
        state = form.state.data
        new_user = User.register(username, password, email, first_name, last_name, city, state)
        db.session.add(new_user)
        try:
            db.session.commit()
        except IntegrityError:
            form.username.errors.append('Username taken.  Please pick another')
            return render_template('register.html', form=form)
        session['user_id'] = new_user.id
        session['username'] = new_user.username
        return redirect(f"/{session['username']}/board")

    return render_template('register.html', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login_user():
    form = LoginForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        user = User.authenticate(username, password)
        if user:
            flash(f"Welcome Back, {user.username}!")
            session['username'] = user.username
            session['user_id'] = user.id
            return redirect(f"/{session['username']}/board")
        else:
            form.username.errors = ['Invalid username/password.']

    return render_template('login.html', form=form)

@app.route('/logout')
def logout_user():
    session.pop('username')
    session.pop('user_id')
    flash("Goodbye!", "info")
    return redirect('/')
##############################################################################
# profile
@app.route('/profile')
def profile():
    if 'username' not in session:
        return redirect('/')
    username = session['username']
    return redirect(f'/{username}/profile')

@app.route("/<username>/profile")
def show_profile(username):
    user = User.query.filter_by(username=username).first()
    return render_template('profile.html', user=user)

@app.route("/<username>/profile/edit-profile")
def edit_profile_form(username):
    user = User.query.filter_by(username=username).first()
    return render_template('edit-profile.html', user=user)

@app.route("/<username>/profile/edit-profile/edited", methods=['POST'] )
def editprofile(username):
    if 'username' not in session or username != session['username']:
        flash("Please login first!")
        return redirect('/')
    curr_user = User.query.filter_by(username=username).first()
    first_name = request.form["first_name"]
    last_name = request.form["last_name"]
    email = request.form["last_name"]
    city = request.form["city"]
    state = request.form["state"]
    curr_user.first_name = first_name
    curr_user.last_name = last_name
    curr_user.email = email
    curr_user.city = city
    curr_user.state = state
    db.session.add(curr_user)
    db.session.commit()
    return redirect(f'/{username}/profile')
##############################################################################
# Homepage with Board and weather
@app.route("/<username>/board", methods=['GET', 'POST'])
def root(username):
    """Main page."""
    if 'username' not in session or username != session['username']:
        flash("Please login first!")
        return redirect('/')
    user = User.query.filter_by(username=username).first()
    city = user.city
    state = user.state
    state_code = s_code[state]
    weather_res = requests.get("http://api.openweathermap.org/data/2.5/weather",
        params = {
            "q": f"{city}, us",
            "appid": api_key,
            "units": "metric"
        })
    weather = weather_res.json()
    # if weather["message"] == "city not found":
    #     weather_res = requests.get("http://api.openweathermap.org/data/2.5/weather",
    #     params = {
    #         "q": "Los Angeles, us",
    #         "appid":"c69ce1abd18c0eae09db094b5f772100"
    #     })
    #     weather = weather_res.json()
    boards = CollabBoard.query.filter_by(user_id=user.id, archive="f").all()

    return render_template('homepage.html', boards=boards, weather=weather)

##############################################################################
# Board
@app.route("/<username>/create-board", methods=['GET', 'POST'])
def createboard(username):
    """Create Board."""
    if 'username' not in session or username != session['username']:
        flash("Please login first!")
        return redirect('/')
    form = boardForm()
    if form.validate_on_submit():
        name = form.name.data
        user_id = session['user_id']
        new_board = CollabBoard(name=name, user_id=user_id)
        db.session.add(new_board)
        db.session.commit()
        # board = CollabBoard.query.filter_by(name=name).first()
        return redirect(f'/{username}/board/{new_board.id}')
    return render_template('create-board.html', form=form)


@app.route("/<username>/board/<int:board_id>", methods=['GET', 'POST'])
def show_board(username,board_id):
    """Show Board, List."""
    if 'username' not in session or username != session['username']:
        flash("Please login first!")
        return redirect('/')
    # user = User.query.filter_by(username=username).first()
    user_id = session['user_id']
    board = CollabBoard.query.get(board_id)
    lists = [lists for lists in board.colists]
    dic={}
    for lists in board.colists:
        dic[lists.id] = lists
    keys = list(dic.keys())
    keys.sort()
    return render_template('show-board.html', board=board, dic=dic, keys=keys)

@app.route("/<username>/board/<int:board_id>/delete")
def delete_board(username,board_id):
    """Delete Board."""
    if 'username' not in session or username != session['username']:
        flash("Please login first!")
        return redirect('/')
    user = User.query.filter_by(username=username).first()
    board = CollabBoard.query.get(board_id)
    db.session.delete(board)
    db.session.commit()
    return redirect(f'/{username}/board')

@app.route("/<username>/board/<int:board_id>/archive")
def save_board(username,board_id):
    """Save Board."""
    if 'username' not in session or username != session['username']:
        flash("Please login first!")
        return redirect('/')
    board = CollabBoard.query.get(board_id)
    board.archive = True
    db.session.commit()
    return redirect(f'/{username}/board')

##############################################################################
# List
@app.route("/<username>/board/<int:board_id>/create-list", methods=['GET', 'POST'])
def createlist(username,board_id):
    """Create List."""
    if 'username' not in session or username != session['username']:
        return redirect('/')
    form = listForm()
    if form.validate_on_submit():
        name = form.name.data
        user_id = session['user_id']
        new_list = CollabList(name=name,boards_id=board_id,user_id=user_id )
        # session['board_id'] = board_id
        db.session.add(new_list)
        db.session.commit()
        # curr_list = CollabList.query.filter_by(boards_id=board_id, name=name).first()
        # list_id = curr_list.json().id
        # session['list_id'] = list_id
        return redirect(f'/{username}/board/{board_id}')
    return render_template('create-list.html', form=form)

@app.route("/<username>/board/<int:board_id>/list/<int:list_id>/edit", methods=['GET', 'POST'])
def edit_list_form(username,board_id,list_id):
    """Create List."""
    if 'username' not in session or username != session['username']:
        return redirect('/')
    board = CollabBoard.query.get(board_id)
    list = CollabList.query.get(list_id)
    return render_template('edit-list.html', username=username, board=board, list=list)

@app.route("/<username>/board/<int:board_id>/list/<int:list_id>/edit/edited", methods=['GET', 'POST'])
def editlist(username,board_id, list_id):
    """Edit List Name."""
    curr_list = CollabList.query.get(list_id)
    list_name = request.form["name"]
    curr_list.name = list_name
    db.session.add(curr_list)
    db.session.commit()
    return redirect(f'/{username}/board/{board_id}')

##############################################################################
# Card
@app.route("/<username>/board/<int:board_id>/list/<int:list_id>/create-card", methods=['GET', 'POST'])
def createcard(username, board_id, list_id):
    """Create Card."""
    if 'username' not in session or username != session['username']:
        flash("Please login first!")
        return redirect('/')
    form = cardForm()
    if form.validate_on_submit():
        name = form.name.data
        description = form.description.data
        deadline = form.deadline.data
        user_id = session['user_id']
        new_card = CollabCard(name=name,description=description, deadline=deadline,lists_id=list_id, boards_id=board_id, user_id=user_id )

        db.session.add(new_card)
        db.session.commit()
        return redirect(f'/{username}/board/{board_id}')
    return render_template('create-card.html', form=form)


@app.route("/<username>/board/<int:board_id>/list/<int:list_id>/card/<int:card_id>/edit", methods=['GET', 'POST'])
def edit_card_form(username,board_id,list_id,card_id):
    """Create List."""
    if 'username' not in session or username != session['username']:
        return redirect('/')
    board = CollabBoard.query.get(board_id)
    list = CollabList.query.get(list_id)
    card = CollabCard.query.get(card_id)
    return render_template('edit-card.html', username=username, board=board, list=list, card=card)

@app.route("/<username>/board/<int:board_id>/list/<int:list_id>/card/<int:card_id>/edited", methods=['GET', 'POST'])
def editcard(username,board_id, list_id,card_id):
    """Edit List Name."""
    curr_card = CollabCard.query.get(card_id)
    card_name = request.form["name"]
    card_description = request.form["description"]
    card_deadline = request.form["deadline"]
    curr_card.name = card_name
    curr_card.description=card_description
    curr_card.deadline=card_deadline
    db.session.commit()
    return redirect(f'/{username}/board/{board_id}')

@app.route("/<username>/board/<int:board_id>/list/<int:list_id>/card/<int:card_id>/move", methods=['GET', 'POST'])
def move_card_form(username,board_id, list_id,card_id):
    """Move_card_form."""
    user = User.query.filter_by(username=username).first()
    board = CollabBoard.query.get(board_id)
    list = CollabList.query.get(list_id)
    card= CollabCard.query.get(card_id)
    lists = CollabList.query.filter(CollabList.id > list_id, CollabList.boards_id==board_id, CollabList.user_id == user.id).all()
    return render_template('move-card.html', username=username, board=board, list=list, card=card, lists=lists)

@app.route("/<username>/board/<int:board_id>/list/<int:list_id>/card/<int:card_id>/moved", methods=['GET', 'POST'])
def move_card(username,board_id, list_id,card_id):
    """Edit List Name."""
    user = User.query.filter_by(username=username).first()
    curr_card = CollabCard.query.get(card_id)
    list_name = request.form.getlist('checklist')[0]
    lists= CollabList.query.filter(CollabList.name == list_name,CollabList.boards_id==board_id, CollabList.user_id == user.id).first()
    lists_id = lists.id
    curr_card.lists_id = lists_id
    db.session.commit()
    return redirect(f'/{username}/board/{board_id}')



##############################################################################
# Archive
@app.route("/archive", methods=['GET', 'POST'])
def go_archive():
    if 'username' not in session:
        return redirect('/')
    username = session['username']
    return redirect(f'/{username}/archive')

@app.route("/<username>/archive", methods=['GET', 'POST'])
def show_archive(username):
    user = User.query.filter_by(username=username).first()
    boards = CollabBoard.query.filter_by(user_id=user.id, archive="t").all()
    return render_template('archive.html',boards=boards)

@app.route("/<username>/archive/<int:board_id>/archive", methods=['GET', 'POST'])
def board_archive(username,board_id):
    """Show Board, List."""
    if 'username' not in session or username != session['username']:
        flash("Please login first!")
        return redirect('/')
    board = CollabBoard.query.get(board_id)
    lists = [lists for lists in board.colists]
    return render_template('archive-lists.html', board=board, lists=lists)