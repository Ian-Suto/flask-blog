from flask_restful import reqparse

user_post_parser = reqparse.RequestParser()
user_post_parser.add_argument('username', type=str, required=True)
user_post_parser.add_argument('password', type=str, required=True)

post_get_parser = reqparse.RequestParser()
post_get_parser.add_argument('page', type=int, location=['args', 'headers'])
post_get_parser.add_argument('user', type=str, location=['args', 'headers'])

post_post_parser = reqparse.RequestParser()
post_post_parser.add_argument(
    'title',
    type=str,
    required=True,
    help='Title required',
    location=['json', 'values']
)
post_post_parser.add_argument(
    'text',
    type=str,
    required=True,
    help='Body text is required',
    location=['json', 'values']
)
post_post_parser.add_argument(
    'tags',
    type=str,
    action='append',
    location=['json', 'values']
)

post_put_parser = reqparse.RequestParser()
post_put_parser.add_argument(
    'title',
    type=str,
    location=['json', 'values']
)
post_put_parser.add_argument(
    'text',
    type=str,
    location=['json', 'values']
)
post_put_parser.add_argument(
    'tags',
    type=str,
    action='append',
    location=['json', 'values']
)

comment_get_parser = reqparse.RequestParser()
comment_get_parser.add_argument('page', type=int, location=['args', 'headers'])
comment_get_parser.add_argument('user', type=str, location=['args', 'headers'])

comment_post_parser = reqparse.RequestParser()
comment_post_parser.add_argument(
    'text',
    type=str,
    required=True,
    help='Text is required',
    location=['json', 'values']
)
comment_post_parser.add_argument(
    'name',
    type=str,
    required=True,
    help='Name is required',
    location=['json', 'values']
)

comment_put_parser = reqparse.RequestParser()
comment_put_parser.add_argument(
    'text',
    type=str,
    location=['json', 'values']
)
comment_post_parser.add_argument(
    'name',
    type=str,
    location=['json', 'values']
)