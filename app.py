from flask import Flask, render_template, request, redirect
from flask import session, g, url_for, flash
import sqlite3
import os
import re
import datetime

app = Flask(__name__)
status_msg = " "


# run and create database

@app.route('/', methods=['GET', 'POST'])
def index():
    return redirect("/blog_home")


# blog index page
@app.route('/blog_home', methods=['GET', 'POST'])
def blog_home():
    global status_msg

    if request.method == "GET":
        con = sqlite3.connect('blog.db')
        blog_data = con.execute("SELECT * FROM Blog WHERE visibility = 'Yes' ORDER BY entry_date DESC")
        cat_query = '''Select Distinct category from Blog;'''
        cat_data = con.execute(cat_query).fetchall()
        blog_row = [
            dict(id=row[0], category=row[1], title=row[6], body=row[2], created=row[4], modified=row[5], v=row[9], author=row[3])
            for row in blog_data.fetchall()
        ]
        # print cat_data

        con.commit()
        con.close()
    return render_template('blog.html', status_msg=status_msg, blogger=blog_row, category=cat_data)

@app.route('/post/<cat>', methods=['GET', 'POST'])
def category(cat):
    global status_msg
    con = sqlite3.connect('blog.db')
    blog_query = '''Select * from Blog where visibility='Yes' and category = '%s' ;''' % cat
    comment_query = '''Select * from Comment;'''
    blog_data = con.execute(blog_query)
    comment_data = con.execute(comment_query)
    blog_row = [dict(id=row[0], title=row[6], body=row[2], created=row[4], modified=row[5], category=row[1], author=row[3]) for row in blog_data.fetchall()]
    comment_row = [dict(id=row[0], author=row[2], comment=row[1], created=row[3], modified=row[4], blog_id=row[5]) for row in comment_data.fetchall()]
    cat_query = '''Select Distinct category from Blog;'''
    cat_data = con.execute(cat_query).fetchall()
    # print blog_row
    # print comment_row
    c = 0
    for x in comment_row:
        for y in blog_row:
            if x['blog_id'] == y['id']:
                c+=1

    jquery = ''' select Blog.id, Blog.category, Blog.blog_body, Blog.author, Blog.entry_date, Blog.mod_date, 
    Blog.blog_title, Blog.visibility, Comment.id, Comment.blog_id, Comment.c_body, Comment.c_by, Comment.c_entry_date, 
    Comment.c_mod_date from Blog left join Comment on Blog.id = Comment.blog_id where Blog.visibility='Yes' and Blog.id = Comment.blog_id and category = '%s' order by Blog.id;''' %cat
    run_query = con.execute(jquery)

    n = con.execute(jquery).fetchall()
    all_data = [dict(a=row[0], b=row[1], c=row[3], d=row[4], e=row[5], f=row[6], g=row[7], h=row[8], i=row[9], ccomment=row[10], cauthor=row[11], ccreated=row[12]
                    ) for row in run_query.fetchall()]
    cnt = 0
    # print n
    for zz in all_data:
        # print zz
        cnt+=1
    con.commit()
    con.close()
    return render_template('dashboard/category_post.html', data=blog_row, count=c, newdata=all_data, category=cat_data)


@app.route('/login', methods=['GET', 'POST'])
def login():
    global status_msg
    con = sqlite3.connect('blog.db')
    cat_query = '''Select Distinct category from Blog;'''
    cat_data = con.execute(cat_query).fetchall()
    if request.method == "POST":
        loginStat = 'SELECT COUNT(id) FROM Account where username = "%s" AND password = "%s";' % (request.form['username'],request.form['password'])
        login = con.execute(loginStat).fetchone();

        if login[0]>0:
            session['logged_in'] = True
            session['username'] = request.form['username']
            return redirect('/admin/dashboard')
        else:
            status_msg = 'Username & Password is Invalid'
        con.commit()
        con.close()
    return render_template('login.html', msg=status_msg, category=cat_data)

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    global status_msg
    cuser = ""
    cpass = ""
    c_email = ""
    if request.method == "POST":
        if 'cusername' in request.form and 'cpassword' in request.form and 'cemail' in request.form:
            cuser = request.form['cusername']
            cpass = request.form['cpassword']
            c_email = request.form['cemail']
            con = sqlite3.connect('blog.db')
            query = '''INSERT INTO Account (username, password, email)
                                VALUES ("%s", "%s", "%s");''' % (
            cuser, cpass, c_email)
            con.execute(query)
            con.commit()
            con.close()
            status_msg = 'Account is created'
    return render_template('login.html', msg=status_msg)

@app.route('/admin/dashboard', methods=['GET', 'POST'])
def dashboard():
    global status_msg
    if 'logged_in' not in session:
        return redirect('/login')
    con = sqlite3.connect('blog.db')
    query = '''SELECT * FROM Blog WHERE author='%s' ORDER BY id ASC;''' % (session['username'])
    blog_data = con.execute(query)
    post_count = 0
    published_count = 0
    unpub_count = 0

    blog_row = [
        dict(id=row[0], category=row[1], body=row[2], visibility=row[9])
        for row in blog_data.fetchall()
    ]
    # checking no of post
    for x in blog_row:
        if x > 0:
            post_count+=1
        if x['visibility'] == 'Yes':
            published_count+=1
        if x['visibility'] == 'No':
            unpub_count+=1
    con.commit()
    con.close()
    return render_template('dashboard/index.html', blog=blog_row, count=post_count, v_count=published_count, nv_count=unpub_count)


# Post Page
@app.route('/admin/post', methods=['GET', 'POST'])
def post():
    global status_msg
    if 'logged_in' not in session:
        return redirect('/login')
    con = sqlite3.connect('blog.db')
    query = '''SELECT * FROM Blog WHERE author='%s' ORDER BY id ASC;''' % (session['username'])
    blog_data = con.execute(query)
    blog_row = [
        dict(id=row[0], title=row[6], body=row[2], created=row[4], modified=row[5], v=row[9], category=row[1])
        for row in blog_data.fetchall()
    ]
    con.commit()
    con.close()
    return render_template('dashboard/post.html', blog=blog_row)


# Adding Post
@app.route('/admin/post/new', methods=['GET', 'POST'])
def new_post():
    global status_msg
    if 'logged_in' not in session:
        return redirect('/login')
    n_title = ""
    n_visibility = ""
    n_content = ""
    n_category = ""
    n_author = ""
    c_date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    if not ('title' in request.form and 'visi' in request.form and 'content' in request.form):
        status_msg = ""
        return render_template('dashboard/post_new.html', status_msg=status_msg)
    elif 'title' in request.form and 'visi' in request.form and 'content' in request.form:
        n_title = request.form['title']
        n_visibility = request.form['visi']
        n_content = request.form['content']
        n_category = request.form['category']
        n_author = session['username']
    else:
        status_msg = "Please fill the form completly"
        return render_template('dashboard/post_new.html', status_msg=status_msg)
    con = sqlite3.connect('blog.db')
    query = '''INSERT INTO Blog (blog_title, visibility, blog_body, entry_date, category, author)
                        VALUES ("%s", "%s", "%s", "%s", "%s", "%s");''' % (
        n_title, n_visibility, n_content, c_date, n_category, n_author)
    con.execute(query)
    con.commit()
    con.close()
    return render_template('dashboard/post_new.html')


# Ediging Post
@app.route('/admin/post/edit', methods=['GET', 'POST'])
def post_edit():
    global status_msg
    if 'logged_in' not in session:
        return redirect('/login')
    con = sqlite3.connect('blog.db')
    query = '''SELECT * FROM Blog WHERE id=%s;''' % request.form['blog_id']
    post_data = con.execute(query)
    post_row = [
        dict(id=row[0], title=row[6], visibility=row[9], category=row[1], body=row[2], modified=row[5], created=row[4])
        for row in post_data.fetchall()
    ]
    con.commit()
    con.close()
    return render_template('dashboard/post_edit.html', postedit=post_row)


# Update Post
@app.route('/admin/post/update', methods=['GET', 'POST'])
def post_update():
    global status_msg
    if 'logged_in' not in session:
        return redirect('/login')
    n_title = ""
    n_visibility = ""
    n_content = ""
    n_category = ""
    m_date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    if not ('title' in request.form and 'visi' in request.form and 'content' in request.form):
        status_msg = ""
        return render_template('dashboard/post_new.html', status_msg=status_msg)
    elif 'title' in request.form and 'visi' in request.form and 'content' in request.form:
        n_title = request.form['title']
        n_visibility = request.form['visi']
        n_content = request.form['content']
        n_category = request.form['category']
        n_postid = request.form['post_id']
    else:
        status_msg = "Please fill the form completly"
        return render_template('dashboard/post_new.html', status_msg=status_msg)
    con = sqlite3.connect('blog.db')
    query = '''UPDATE Blog 
    SET blog_title='%s',  visibility='%s', blog_body='%s', mod_date='%s', category='%s' 
    WHERE id='%s';''' % (n_title, n_visibility, n_content, m_date, n_category, n_postid)
    con.execute(query)
    con.commit()
    con.close()
    return redirect("/admin/post")


# Delete Post
@app.route('/admin/post/delete', methods=['GET', 'POST'])
def post_delete():
    if 'logged_in' not in session:
        return redirect('/login')

    delete_query = ''' Delete from Blog where
                    id=%s;''' % request.form['blog_id']

    con = sqlite3.connect("blog.db")
    con.execute(delete_query)
    con.commit()
    con.close()
    return redirect("/admin/post")

# Single Post Page
@app.route('/admin/<title>', methods=['GET', 'POST'])
def single(title):
    global status_msg
    con = sqlite3.connect('blog.db')
    blog_query = '''Select * from Blog where visibility='Yes' and blog_title = '%s' ;''' % title
    comment_query = '''Select * from Comment;'''
    cat_query = '''Select Distinct category from Blog;'''
    cat_data = con.execute(cat_query).fetchall()
    blog_data = con.execute(blog_query)
    comment_data = con.execute(comment_query)


    blog_row = [dict(id=row[0], title=row[6], body=row[2], created=row[4], modified=row[5], category=row[1], author=row[3]) for row in blog_data.fetchall()]
    comment_row = [dict(id=row[0], author=row[2], comment=row[1], created=row[3], modified=row[4], blog_id=row[5]) for row in comment_data.fetchall()]
    # print blog_row
    # print comment_row
    c = 0
    for x in comment_row:
        for y in blog_row:
            if x['blog_id'] == y['id']:
                c+=1

    jquery = ''' select Blog.id, Blog.category, Blog.blog_body, Blog.author, Blog.entry_date, Blog.mod_date, 
    Blog.blog_title, Blog.visibility, Comment.id, Comment.blog_id, Comment.c_body, Comment.c_by, Comment.c_entry_date, 
    Comment.c_mod_date from Blog left join Comment on Blog.id = Comment.blog_id where Blog.visibility='Yes' and Blog.id = Comment.blog_id and blog_title = '%s' order by Blog.id;''' %title
    run_query = con.execute(jquery)
    all_data = [dict(a=row[0], b=row[1], c=row[3], d=row[4], e=row[5], f=row[6], g=row[7], h=row[8], i=row[9], ccomment=row[10], cauthor=row[11], ccreated=row[12]
                    ) for row in run_query.fetchall()]
    cnt = 0
    for zz in all_data:
        # print zz
        cnt+=1
    con.commit()
    con.close()
    return render_template('dashboard/single_post.html', data=blog_row, comment_data = comment_row, count=c, newdata=all_data, category=cat_data)


@app.route('/comment', methods=['GET', 'POST'])
def add_comment():
    global status_msg
    comment_author = ""
    comment_email = ""
    comment = ""
    comment_date = ""
    commend_mod = ""
    c_blog_id = ""
    if 'cName' in request.form and 'cEmail' in request.form and 'cMessage' in request.form:
        comment_author = request.form['cName']
        comment_email = request.form['cEmail']
        comment = request.form['cMessage']
        comment_date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        c_blog_id = request.form['blog_id']
    con = sqlite3.connect('blog.db')
    query = '''INSERT INTO Comment (c_body, c_by, c_entry_date, blog_id)
                        VALUES ("%s", "%s", "%s", "%s");'''% (comment, comment_author, comment_date, c_blog_id )
    con.execute(query)
    con.commit()
    con.close()
    return redirect('/admin/'+ request.form['blog_title'])

@app.route('/logout')
def logout():
    session['logged_in'] = False
    return redirect('/')


if __name__ == '__main__':
    app.secret_key = os.urandom(24)
    HOST = os.environ.get('SERVER_HOST', 'localhost')
    try:
        PORT = int(os.environ.get('SERVER_PORT', '5001'))
    except ValueError:
        PORT = 5001
    app.run(HOST, PORT, debug=True)
