import flask
from app import app
from models import Article, User, db

app.secret_key = b'a\xdb\xd2\x13\x93\xc1\xe9\x97\xef2\xe3\x004U\xd1Z'

class TestApp:
    '''Flask API in app.py'''

    def setup_method(self):
        """Set up test data before each test"""
        with app.app_context():
            # Create a user if none exists
            if not User.query.first():
                user = User(username="testuser")
                db.session.add(user)
                db.session.commit()

            # Create a member-only article if none exists
            if Article.query.filter_by(is_member_only=True).count() == 0:
                article = Article(
                    title="Test Member Only Article",
                    content="This is the content of the member-only article.",
                    preview="This is a preview of the article.",
                    minutes_to_read=5,
                    is_member_only=True,
                    author="Test Author",
                    user_id=1  # Assuming the user with ID 1 exists
                )
                db.session.add(article)
                db.session.commit()

    def test_can_only_access_member_only_while_logged_in(self):
        '''allows logged in users to access member-only article index at /members_only_articles.'''
        with app.test_client() as client:
            client.get('/clear')

            # Ensure a user is logged in
            user = User.query.first()
            client.post('/login', json={'username': user.username})

            # Check that the logged-in user can access member-only articles
            response = client.get('/members_only_articles')
            assert(response.status_code == 200)

            # Log out the user
            client.delete('/logout')

            # Ensure unauthorized access after logout
            response = client.get('/members_only_articles')
            assert(response.status_code == 401)

    def test_member_only_articles_shows_member_only_articles(self):
        '''only shows member-only articles at /members_only_articles.'''
        with app.test_client() as client:
            client.get('/clear')

            # Log in as user
            user = User.query.first()
            client.post('/login', json={'username': user.username})

            # Get the member-only articles and verify the content
            response_json = client.get('/members_only_articles').get_json()
            for article in response_json:
                assert article['is_member_only'] == True

    def test_can_only_access_member_only_article_while_logged_in(self):
        '''allows logged in users to access full member-only articles at /members_only_articles/<int:id>.'''
        with app.test_client() as client:
            client.get('/clear')

            # Log in as user
            user = User.query.first()
            client.post('/login', json={'username': user.username})

            # Retrieve an article id
            article_id = Article.query.filter_by(is_member_only=True).first().id

            # Ensure logged-in user can access the full member-only article
            response = client.get(f'/members_only_articles/{article_id}')
            assert(response.status_code == 200)

            # Log out and ensure unauthorized access is denied
            client.delete('/logout')
            response = client.get(f'/members_only_articles/{article_id}')
            assert(response.status_code == 401)
