from rest_framework import serializers

from .models import Movie, Review, Rating, Actor


class FilterReviewListSerializer(serializers.ListSerializer):
    """Фильтр комментарией, только parents"""

    def to_representation(self, data):  # data это queryset
        data = data.filter(parent=None) # фильтруем и находим только те записи у которых parent none
        return super().to_representation(data)


class MovieListSerializer(serializers.ModelSerializer):
    """Список фильмов"""

    rating_user = serializers.BooleanField()
    middle_star = serializers.IntegerField()

    class Meta:
        model = Movie
        fields = ("id", "title", "tagline", "category", "rating_user", "middle_star")


class ReviewCreateSerializer(serializers.ModelSerializer):
    "Добавление отзыва"

    class Meta:
        model = Review
        fields = "__all__"


class RecursiveSerializer(serializers.Serializer):
    """Вывод рекурсивно children"""

    def to_representation(self, value):
        serializer = self.parent.parent.__class__(value, context=self.context)
        return serializer.data


class ActorListSerializer(serializers.ModelSerializer):
    """Вывод списка актеров и режисеров"""

    class Meta:
        model = Actor
        fields = "__all__"


class ActorDetailSerializer(serializers.ModelSerializer):
    """Вывод полного описания актера или режисера"""

    class Meta:
        model = Actor
        fields = "__all__"


class ReviewSerializer(serializers.ModelSerializer):
    "Вывод отзыва"

    children = RecursiveSerializer(many=True)

    class Meta:
        list_serializer_class = FilterReviewListSerializer
        model = Review
        fields = ("id", "name", "text", "children")


class MovieDetailSerializer(serializers.ModelSerializer):
    """Полный фильм"""

    category = serializers.SlugRelatedField(slug_field='name', read_only=True)
    # read_only это поле только для чтения  slug_field - получет имя
    directors = ActorListSerializer(read_only=True, many=True)
    actors = ActorListSerializer(read_only=True, many=True)
    genres = serializers.SlugRelatedField(slug_field='name', read_only=True, many=True)
    reviews = ReviewSerializer(many=True)

    class Meta:
        model = Movie
        exclude = ('draft', )  # Выводить все кроме draft


class CreateRatingSerializer(serializers.ModelSerializer):
    """Добавление рейтинга пользователем"""

    class Meta:
        model = Rating
        fields = ("star", "movie")

    def create(self, validated_data):
        rating, _ = Rating.objects.update_or_create(
            ip=validated_data.get('ip', None), # validated_data эо сериализатор с клиентской стороны
            movie=validated_data.get('movie', None),
            defaults={'star': validated_data.get("star")} # и обновлять мы будем поле star
        )
        return rating
