from django.contrib.auth.validators import UnicodeUsernameValidator
from django.core.validators import RegexValidator
from rest_framework.serializers import (
    CharField,
    EmailField,
    IntegerField,
    ModelSerializer,
    SlugRelatedField,
    ValidationError,
)

from reviews.models import (
    Category,
    Comment,
    Genre,
    GenreTitle,
    Review,
    Title,
    User,
)


class CategorySerializer(ModelSerializer):
    class Meta:
        model = Category
        fields = ('name', 'slug')


class GenreSerializer(ModelSerializer):
    class Meta:
        model = Genre
        fields = ('name', 'slug')


class TitleSerializer(ModelSerializer):
    category = CategorySerializer()
    genre = GenreSerializer(many=True)
    rating = IntegerField(source='reviews__score__avg', read_only=True)

    class Meta:
        model = Title
        fields = '__all__'


class TitleCreateUpdateSerializer(ModelSerializer):
    category = SlugRelatedField(
        queryset=Category.objects.all(), slug_field='slug', required=True
    )
    genre = SlugRelatedField(
        queryset=Genre.objects.all(),
        slug_field='slug',
        many=True,
        required=True,
    )
    description = CharField(required=False)

    class Meta:
        model = Title
        fields = '__all__'
        read_only_fields = ('rating',)

    def create(self, validated_data):
        category = validated_data.pop('category')
        genres = validated_data.pop('genre')
        title = Title.objects.create(**validated_data, category=category)
        for genre in genres:
            genre = Genre.objects.get(slug=genre.slug)
            GenreTitle.objects.create(genre=genre, title=title)
        return title


class ReviewSerializer(ModelSerializer):
    author = SlugRelatedField(slug_field='username', read_only=True)

    class Meta:
        model = Review
        fields = ('id', 'text', 'author', 'score', 'pub_date')

    def validate(self, data):
        if self.context['request'].method != 'POST':
            return data
        user = self.context['request'].user
        title_id = self.context['request'].parser_context['kwargs']['title_id']
        if Review.objects.filter(author=user, title__id=title_id).exists():
            raise ValidationError(
                'Это ошибка, вызванная тем, что нельзя оставлять'
                'два отзыва на одно произведение'
            )
        return data


class CommentSerializer(ModelSerializer):
    author = SlugRelatedField(slug_field='username', read_only=True)

    class Meta:
        model = Comment
        fields = ('id', 'text', 'author', 'pub_date')


class UserSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = (
            'username',
            'email',
            'first_name',
            'last_name',
            'bio',
            'role',
        )


class ProfileSerializer(UserSerializer):
    role = CharField(read_only=True)


class SignUpSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = ('username', 'email')

    username = CharField(
        max_length=150,
        validators=[
            UnicodeUsernameValidator(),
            RegexValidator(
                regex=r'^(?!me$).*$',
                message='Использовать "me" в качестве username запрещено',
            ),
        ],
    )
    email = EmailField(max_length=254)

    def create(self, validated_data):
        existing_user_by_username = User.objects.filter(
            username=validated_data.get('username')
        ).first()
        existing_user_by_email = User.objects.filter(
            email=validated_data.get('email')
        ).first()
        if any([existing_user_by_username, existing_user_by_email]):
            if existing_user_by_username == existing_user_by_email:
                return existing_user_by_username
            raise ValidationError(
                'Email уже зарегистрирован для другого пользователя.'
            )
        return User.objects.create(**validated_data)


class TokenSerializer(ModelSerializer):
    username = CharField()
    confirmation_code = CharField(required=True)

    class Meta:
        model = User
        fields = ('username', 'confirmation_code')
