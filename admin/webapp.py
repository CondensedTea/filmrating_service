from flask import Flask, redirect, request, url_for
from flask_admin import Admin, AdminIndexView, BaseView, expose
from flask_admin.contrib.sqla import ModelView
from sqlalchemy import func
from werkzeug.wrappers import Response

from filmrating.models.database import Film, Review, User
from filmrating.session import create_session

app = Flask(__name__)

app.secret_key = 'secret'


class CustomIndexView(AdminIndexView):
    @expose('/')
    def index(self) -> Response:
        with create_session() as session:
            (films,) = session.query(func.count(Film.id)).one()
            (reviews,) = session.query(func.count(Review.id)).one()
            return self.render('index.html', films=films, reviews=reviews)


class ReviewsView(BaseView):
    @expose('/')
    def index(self) -> Response:
        with create_session() as session:
            users = session.query(User).all()
            return self.render('user_list.html', userlist=users)

    @expose('/<user_id>')
    def user_page(self, user_id: int) -> Response:
        with create_session() as session:
            user_reviews = (
                session.query(Film.name, Film.year, Review.text, Review.id, Review.rating)
                .join(Review, Film.id == Review.film_id)
                .filter(Review.user_id == user_id)
                .all()
            )
            return self.render('user_page.html', review_list=user_reviews)

    @expose('/review/<review_id>')
    def preview_review(self, review_id: int) -> Response:
        with create_session() as session:
            review = session.query(Review).filter(Review.id == review_id).one()
            return self.render('review_edit_form.html', review=review)

    @expose('/update_review/<review_id>')
    def update_review(self, review_id: int) -> Response:
        with create_session() as session:
            new_review = request.args.get('review_text')
            review = session.query(Review).filter(Review.id == review_id).one()
            review.text = new_review
            return redirect(url_for('users.user_page', user_id=review.user_id), code=302)


admin = Admin(
    app,
    name='filmrating admin panel',
    template_mode='bootstrap3',
    index_view=CustomIndexView(name='Старт', url='/'),
)
with create_session() as s:
    admin.add_view(ModelView(Film, s, name='Фильмы'))
admin.add_view(ReviewsView(name='Пользователи', endpoint='users'))
