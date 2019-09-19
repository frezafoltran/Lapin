from datetime import datetime
from flask import render_template, flash, redirect, url_for, request, g, \
    jsonify, current_app
from flask_login import current_user, login_required
from flask_babel import _, get_locale
from guess_language import guess_language
from app import db
from app.main.forms import EditProfileForm, PostForm, \
   SearchForm, URLfyForm, GraphPathForm
from app.models import User, Post
from app.translate import translate
from app.main import bp
from app.main.helpers import path_exists, \
    random_edges, build_graph



@bp.before_app_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        db.session.commit()
        g.search_form = SearchForm()
    g.locale = str(get_locale())


@bp.route('/', methods = ['GET', 'POST'])
def main():
    return render_template('algos/algos_main.html')

@bp.route('/index', methods=['GET','POST'])
@login_required
def index():

    form = PostForm()
    if form.validate_on_submit():
        language = guess_language(form.post.data)
        if language == 'UNKNOWN' or len(language) > 5:
            language = ''
        post = Post(body=form.post.data, author=current_user, language=language)
        db.session.add(post)
        db.session.commit()
        flash(_('Your idea is posted!'))
        return redirect(url_for('main.index'))
    page = request.args.get('page', 1, type=int)
    posts = current_user.followed_posts().paginate(
        page, current_app.config['POSTS_PER_PAGE'], False)

    if posts.has_next:
        next_url = url_for('main.index', page=posts.next_num)
    else:
        next_url = None

    if posts.has_prev:
        prev_url = url_for('main.index', page=posts.prev_num)
    else:
        prev_url = None

    return render_template('index.html', title=_('Home Page'), form=form, posts=posts.items, next_url=next_url, prev_url=prev_url)

@bp.route('/user/<username>')
@login_required
def user(username):
    user = User.query.filter_by(username=username).first_or_404()
    page = request.args.get('page', 1, type=int)
    posts = user.posts.order_by(Post.timestamp.desc()).paginate(
        page, current_app.config['POSTS_PER_PAGE'], False)


    if posts.has_next:
        next_url = url_for('main.user', username=user.username, page=posts.next_num)
    else:
        next_url = None

    if posts.has_prev:
        prev_url = url_for('main.user', username=user.username,  page=posts.prev_num)
    else:
        prev_url = None

    return render_template('user.html', user=user, posts=posts.items, next_url=next_url, prev_url=prev_url)


@bp.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm(current_user.username)
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.about_me = form.about_me.data
        db.session.commit()
        flash(_('Your profile changes have been saved.'))
        return redirect(url_for('main.edit_profile'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.about_me.data = current_user.about_me
    return render_template('edit_profile.html', title='Edit Profile', form=form)


@bp.route('/follow/<username>')
@login_required
def follow(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash(_('User %(username) not found', username=username))
        return redirect(url_for('main.index'))

    if user == current_user:
        flash(_('You cannot follow yourself!'))
        return redirect(url_for('main.user', username=username))

    current_user.follow(user)
    db.session.commit()
    flash(_('You are now following %(username)', username=username))
    return redirect(url_for('main.user', username=username))

@bp.route('/unfollow/<username>')
@login_required
def unfollow(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash(_('User %(username) not found.', username=username))
        return redirect(url_for('main.index'))
    if user == current_user:
        flash(_('You cannot unfollow yourself!'))
        return redirect(url_for('main.user', username=username))
    current_user.unfollow(user)
    db.session.commit()
    flash(_('You are not following %(username).', username=username))
    return redirect(url_for('main.user', username=username))

@bp.route('/explore')
@login_required
def explore():
    page = request.args.get('page', 1, type=int)
    posts=Post.query.order_by(Post.timestamp.desc()).paginate(
        page, current_app.config['POSTS_PER_PAGE'], False)
    if posts.has_next:
        next_url = url_for('main.explore', page=posts.next_num)
    else:
        next_url = None

    if posts.has_prev:
        prev_url = url_for('main.explore', page=posts.prev_num)
    else:
        prev_url = None
    return render_template('index.html', title=_('Explore'), posts=posts.items, next_url=next_url, prev_url=prev_url)


@bp.route('/translate', methods=['POST'])
@login_required
def translate_text():
    return jsonify({'text': translate(request.form['text'],
                                      request.form['source_language'],
                                      request.form['dest_language'])})

@bp.before_app_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        db.session.commit()
        g.search_form = SearchForm()
    g.locale = str(get_locale())

@bp.route('/search')
@login_required
def search():
    if not g.search_form.validate():
        return redirect(url_for('main.explore'))
    page = request.args.get('page', 1, type=int)
    posts, total = Post.search(g.search_form.q.data, page,
                               current_app.config['POSTS_PER_PAGE'])

    next_url = url_for('main.search', q=g.search_form.q.data, page=page + 1) \
        if total > page * current_app.config['POSTS_PER_PAGE'] else None
    prev_url = url_for('main.search', q=g.search_form.q.data, page=page - 1) \
        if page > 1 else None
    return render_template('search.html', title=_('Search'), posts=posts,
                           next_url=next_url, prev_url=prev_url)

@bp.route('/user/<username>/popup')
@login_required
def user_popup(username):
    user = User.query.filter_by(username=username).first_or_404()
    return render_template('user_popup.html', user=user)


@bp.route('/algos')
def algos():
    return render_template('algos/algos_main.html')

@bp.route('/algos/data_structures_questions')
def algos_data_structures_questions():
    return render_template('algos/data_structures_questions.html')


@bp.route('/algos/arrays_and_strings/<q_num>', methods=['GET', 'POST'])
def algos_arrays_and_strings(q_num):
    #TODO maybe implement a lookup
    if q_num == '0':
        return render_template('algos/arrays_and_strings/arrays_and_strings_main.html')

    else:
        return render_template('algos/arrays_and_strings/question_' + str(q_num) + '.html')



@bp.route('/algos/linked_lists/<q_num>', methods=['GET', 'POST'])
def algos_linked_lists(q_num):

    if q_num == '0':
        return render_template('algos/linked_lists/linked_lists_main.html')

    else:
        return render_template('algos/linked_lists/question_' + str(q_num) + '.html')


@bp.route('/algos/stacks_and_queues/<q_num>', methods=['GET', 'POST'])
def algos_stacks_and_queues(q_num):

    if q_num == '0':
        return render_template('algos/stacks_and_queues/stacks_and_queues_main.html')

    else:
        return render_template('algos/stacks_and_queues/question_' + str(q_num) + '.html')


@bp.route('/algos/trees_and_graphs/<q_num>', methods=['GET', 'POST'])
def algos_trees_and_graphs(q_num):

    if q_num == '0':
        return render_template('algos/trees_and_graphs/trees_and_graphs_main.html')

    elif q_num == '1':

        form = GraphPathForm()

        if form.validate_on_submit():

            edges = form.curr_graph.data
            edges_vec = [0]*len(edges)
            for i in range(len(edges)):
                edges_vec[i] = int(edges[i])

            p_info = ['Angela', 'Joao', 'Elvira', 'Ringo', 'Pedro',
                'Carol', 'Sofia', 'Jude']

            for i in range(len(p_info)):
                if p_info[i] == form.p1.data:
                    p1_index = i
                if p_info[i] == form.p2.data:
                    p2_index = i

            graph = build_graph(edges_vec)

            path_bool = path_exists(p1_index, p2_index, graph)


            return render_template('algos/trees_and_graphs/question_' + str(q_num) + '.html', edges=edges,
                                   edges_vec=edges_vec, form=form, path_bool=path_bool, anchored=1)

        [edges, edges_vec] = random_edges()

        return render_template('algos/trees_and_graphs/question_' + str(q_num) + '.html', edges=edges,
                               edges_vec=edges_vec, form=form, path_bool=-1)

    else:
        return render_template('algos/trees_and_graphs/question_' + str(q_num) + '.html')


@bp.route('/algos/bit_manipulation/<q_num>', methods=['GET', 'POST'])
def algos_bit_manipulation(q_num):

    if q_num == '0':
        return render_template('algos/bit_manipulation/bit_manipulation_main.html')

    else:
        return render_template('algos/bit_manipulation/question_' + str(q_num) + '.html')

@bp.route('/algos/math/<q_num>', methods=['GET', 'POST'])
def algos_math(q_num):

    if q_num == '0':
        return render_template('algos/math/math_main.html')

    else:
        return render_template('algos/math/question_' + str(q_num) + '.html')


@bp.route('/algos/object_oriented_design/<q_num>', methods=['GET', 'POST'])
def algos_object_oriented_design(q_num):

    if q_num == '0':
        return render_template('algos/object_oriented_design/object_oriented_design_main.html')

    else:
        return render_template('algos/object_oriented_design/question_' + str(q_num) + '.html')

@bp.route('/algos/moderate/<q_num>', methods=['GET', 'POST'])
def algos_moderate(q_num):

    if q_num == '0':
        return render_template('algos/moderate/moderate_main.html')

    else:
        return render_template('algos/moderate/question_' + str(q_num) + '.html')

@bp.route('/algos/hard/<q_num>', methods=['GET', 'POST'])
def algos_hard(q_num):

    if q_num == '0':
        return render_template('algos/hard/hard_main.html')

    else:
        return render_template('algos/hard/question_' + str(q_num) + '.html')


@bp.route('/algos/recursion_and_dynamic_programming/<q_num>', methods=['GET', 'POST'])
def algos_recursion_and_dynamic_programming(q_num):

    if q_num == '0':
        return render_template('algos/recursion_and_dynamic_programming/recursion_and_dynamic_programming_main.html')

    else:
        return render_template('algos/recursion_and_dynamic_programming/question_' + str(q_num) + '.html')

@bp.route('/algos/sorting/<q_num>', methods=['GET', 'POST'])
def algos_sorting(q_num):

    if q_num == '0':
        return render_template('algos/sorting/sorting_main.html')

    else:
        return render_template('algos/sorting/question_' + str(q_num) + '.html')


@bp.route('/algos/', methods=['GET', 'POST'])
@bp.route('/algos/<search_query>', methods=['GET', 'POST'])
def search_clean(search_query):


    return render_template('algos/algos_main.html', search_query=search_query)