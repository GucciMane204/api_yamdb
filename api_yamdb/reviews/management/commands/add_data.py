import csv
import os

from django.core.management.base import BaseCommand
from django.conf import settings

from users.models import User
from reviews.models import (
    Title,
    Category,
    Genre,
    Review,
    Comment,
    GenreTitle,
)


class Command(BaseCommand):
    def handle(self, *args, **options):
        csv_files_path = os.path.join(settings.BASE_DIR, 'static/data')
        dir_path = os.path.abspath(csv_files_path)

        file_model_mapping = {
            'users.csv': User,
            'category.csv': Category,
            'genre.csv': Genre,
            'titles.csv': Title,
            'review.csv': Review,
            'comments.csv': Comment,
            'genre_title.csv': GenreTitle,
        }

        for file, model in file_model_mapping.items():
            path = os.path.join(dir_path, file)

            obj_list = []
            with open(path, encoding='utf-8') as csv_file:
                for obj_dict in csv.DictReader(csv_file):
                    if isinstance(model(), Title):
                        category_id = int(obj_dict['category'])
                        category = Category.objects.get(id=category_id)
                        obj_dict['category'] = category
                    if isinstance(model(), (Review, Comment)):
                        author_id = int(obj_dict['author'])
                        author = User.objects.get(id=author_id)
                        obj_dict['author'] = author
                    obj_list.append(model(**obj_dict))
                model.objects.bulk_create(obj_list)

        self.stdout.write(self.style.SUCCESS('Импорт данных выполнен.'))
