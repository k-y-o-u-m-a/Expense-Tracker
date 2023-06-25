from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

# Initialize empty data structures
expenses = []
friend_totals = {}


@app.route('/')
def index():
    return render_template('index.html', expenses=expenses, friend_totals=friend_totals)


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


if __name__ == '__main__':
    app.run(debug=True)
