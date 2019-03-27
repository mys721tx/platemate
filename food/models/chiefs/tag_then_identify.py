import glob
import os

from django.conf import settings
from django.db.models import CharField

import management.models.manager as base
from food.models import identify, tag
from food.models.common import Box, IngredientList, Photo
from management.models.smart_model import OneOf


class Output(base.Output):
    photo = OneOf(Photo)
    box = OneOf(Box)
    ingredient_list = OneOf(IngredientList)


class Manager(base.Manager):

    photoset = CharField(max_length=100)

    def setup(self):
        self.hire(tag.draw_maybe_vote, 'tag')
        self.hire(identify.describe_match_maybe_vote, 'identify')

        photo_search = os.path.join(
            settings.STATIC_DOC_ROOT, 'photos', self.photoset, '*.jpg')
        for path in glob.glob(photo_search):
            filename = os.path.basename(path)
            url = '%s/static/photos/%s/%s' % (
                settings.URL_PATH,
                self.photoset,
                filename
            )
            photo = Photo.factory(photo_url=url)
            self.employee('tag').assign(photo=photo)

    def work(self):

        for output in self.employee('tag').finished:
            for box in output.box_group.boxes.all():
                self.employee('identify').assign(photo=output.photo, box=box)

        for output in self.employee('identify').finished:
            self.finish(
                photo=output.photo,
                box=output.box,
                ingredient_list=output.ingredient_list
            )
