from flask import Flask, g, request, jsonify
from database import get_db
from functools import wraps



app = Flask(__name__)


api_username = 'admin'
api_password = 'pass'

def protected(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.authorization
        if auth and auth.username == api_username and auth.password == api_password:
            return f(*args, **kwargs)
        return jsonify({'message' : 'Authentication failed!'}), 403
    return decorated

@app.teardown_appcontext
def close_db(error):
    if hasattr(g, 'sqlite_db'):
        g.sqlite_db.close()

# GET all members
@app.route('/member', methods=['GET'])
@protected
def get_members():
    db = get_db()
    user_cur = db.execute('select id, name, email, level from members')
    users = user_cur.fetchall()

    all_users = []

    for user in users:
        user_dict = {}
        user_dict['id'] = user['id']
        user_dict['name'] = user['name']
        user_dict['email'] = user['email']
        user_dict['level'] = user['level']

        all_users.append(user_dict)

    return jsonify({'members ' : all_users})

# GET One member
@app.route('/member/<int:member_id>', methods=['GET'])
@protected
def get_member(member_id):

    try:
        db = get_db()
        user_cur = db.execute('select id, name, email, level from members where id = ?', [member_id])
        user = user_cur.fetchone()
        return jsonify({'user' : \
                        {'id': user['id'], 'name' : user['name'], \
                        'email' : user['email'], 'level' : user['level']}})
    except TypeError as err:
        print(err)
        return jsonify({'message' : f'User Not Found', \
                        'Error Message' : f'Server says: {err}' }), 404

# POST one member
@app.route('/member', methods=['POST'])
@protected
def add_member():

    new_user_data = request.get_json()

    name = new_user_data['name']
    email = new_user_data['email']
    level = new_user_data['level']
    # Inject new user to DB
    db = get_db()
    db.execute('INSERT INTO members (name, email, level) VALUES (?,?,?)', [name, email, level])
    db.commit()

    # Retrieve new member added as response 
    user_cur = db.execute('SELECT id, name, email, level FROM members WHERE name = ?', [name])
    new_user = user_cur.fetchone()
    
    return jsonify({'user': \
                {'id' : new_user['id'], 'name': new_user['name'], \
                'email' : new_user['email'], 'level' : new_user['level']}})

# PUT/PATCH updates a member by id
@app.route('/member/<int:member_id>', methods=['PUT', 'PATCH'])
@protected
def edit_member(member_id):

    new_user_data = request.get_json()

    name = new_user_data['name']
    email = new_user_data['email']
    level = new_user_data['level']

    # Update user by Id
    db = get_db()
    db.execute('UPDATE members SET name = ?, email = ?, level = ? WHERE id = ?', \
                [name, email, level, member_id])
    db.commit()

    # Retrieve updated users to show as response
    user_cur = db.execute('SELECT id, name, email, level FROM members WHERE id = ?', [member_id])
    user = user_cur.fetchone()

    return jsonify({'User' : \
                    {'id' : user['id'], 'name' : user['name'], \
                    'email' : user['email'], 'level' : user['level']}})

# DELETE delete one member
@app.route('/member/<int:member_id>', methods=['DELETE'])
@protected
def delete_member(member_id):

    db = get_db()
    db.execute('DELETE FROM members WHERE id = ?', [member_id])
    db.commit()
    return jsonify({'message': f'The member {member_id} has been deleted!'})


if __name__ == '__main__':
    app.run(debug=True)

