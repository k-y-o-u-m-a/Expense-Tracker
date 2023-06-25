from flask import Flask, render_template, request, redirect, url_for
from flask_login import LoginManager, login_user, logout_user, current_user, login_required, UserMixin

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Initialize Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)

#User class for authentication
class User(UserMixin):
    def __init__(self, id):
        self.id = id


@login_manager.user_loader
def load_user(user_id):
    # Find the user with the given id
    user = next((user for user in users if user['username'] == user_id), None)
    
    if user:
        # Create a User object with the user's id
        return User(user['username'])
    
    return None  # User not found


# Initialize empty data structures
expenses = []
friend_totals = {}
users = [
    {'username': 'user1', 'password': 'password1'},
    {'username': 'user2', 'password': 'password2'}
]

@app.route('/')
@login_required
def index():
    return render_template('index.html', expenses=expenses, friend_totals=friend_totals)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Check if the provided credentials match a user in the list
        for user in users:
            if user['username'] == username and user['password'] == password:
                user_obj = User(username)
                login_user(user_obj)
                return redirect(url_for('index'))

        # Invalid credentials
        return render_template('login.html', error='Invalid username or password', friend_totals=friend_totals)

    return render_template('login.html', friend_totals=friend_totals)



@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))


@app.route('/add_expense', methods=['GET', 'POST'])
def add_expense():
    if request.method == 'POST':
        name = request.form['name']
        price = float(request.form['price'])
        friend = request.form['friend']
        
        expenses.append({'name': name, 'price': price, 'friend': friend})
        
        if friend in friend_totals:
            friend_totals[friend] += price
        else:
            friend_totals[friend] = price
        
        return redirect(url_for('index'))
    
    return render_template('add_expense.html', friends=list(friend_totals.keys()))


@app.route('/edit_expense/<int:index>', methods=['GET', 'POST'])
def edit_expense(index):
    if request.method == 'POST':
        name = request.form['name']
        price = float(request.form['price'])
        friend = request.form['friend']
        
        expense = expenses[index]
        old_friend = expense['friend']
        
        expense['name'] = name
        expense['price'] = price
        expense['friend'] = friend
        
        friend_totals[old_friend] -= expense['price']
        
        if friend in friend_totals:
            friend_totals[friend] += price
        else:
            friend_totals[friend] = price
        
        return redirect(url_for('index'))
    
    expense = expenses[index]
    friends = list(friend_totals.keys())
    
    return render_template('edit_expense.html', expense=expense, friends=friends)


@app.route('/delete_expense/<int:index>')
def delete_expense(index):
    expense = expenses[index]
    friend = expense['friend']
    price = expense['price']
    
    del expenses[index]
    friend_totals[friend] -= price
    
    return redirect(url_for('index'))


@app.route('/add_friend', methods=['POST'])
def add_friend():
    friend_name = request.form['friend_name']
    friend_totals[friend_name] = 0
    return redirect(url_for('index'))


@app.route('/remove_friend/<int:index>')
def remove_friend(index):
    friend = list(friend_totals.keys())[index]
    del friend_totals[friend]
    
    # Remove expenses associated with the friend
    expenses[:] = [expense for expense in expenses if expense['friend'] != friend]
    
    return redirect(url_for('index'))


@app.route('/edit_friend/<int:index>/<new_name>')
def edit_friend(index, new_name):
    friend = list(friend_totals.keys())[index]
    friend_totals[new_name] = friend_totals.pop(friend)
    
    # Update friend name in expenses
    for expense in expenses:
        if expense['friend'] == friend:
            expense['friend'] = new_name
    
    return redirect(url_for('index'))

login_manager.login_view = 'login'
if __name__ == '__main__':
    app.run(debug=True)
