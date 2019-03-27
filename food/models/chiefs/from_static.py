import glob
import os
import random

from django.conf import settings
from django.db.models import CharField
from PIL import Image

import management.models.manager as manager
from food.models import identify, measure, tag
from food.models.common import IngredientList, Photo
from management.models.smart_model import OneOf


class Output(manager.Output):
    ingredient_list = OneOf(IngredientList)

class Manager(manager.Manager):

    photoset = CharField(max_length=100)

    def setup(self):
        self.hire(tag.draw_maybe_vote, 'tag')
        self.hire(identify.describe_match_maybe_vote, 'identify')
        self.hire(measure.estimate, 'measure')

        # Loop over each photo in the folder
        photo_search = os.path.join(settings.STATIC_DOC_ROOT, 'uploaded', self.photoset, '*.jpg')
        photos = []
        for path in glob.glob(photo_search):

            # Original image
            filename = os.path.basename(path)
            original = Image.open(path)

            # Resize it to 400px wide (usually 300 high)
            width, height = original.size
            new_size = 400, int(height * 400.0 / width)
            smaller = original.resize(new_size, Image.ANTIALIAS)

            # Save it to photos directory
            out_dir = os.path.join(settings.STATIC_DOC_ROOT, 'photos', self.photoset)
            try:
                os.makedirs(out_dir)
            except os.error:
                pass

            out_path = os.path.join(out_dir, filename)
            smaller.save(out_path)

            # Build a photo object
            print "photoset:", self.photoset
            url = '%s/static/photos/%s/%s' % (settings.URL_PATH, self.photoset, filename)
            photos += [Photo.factory(photo_url=url)]

        random.shuffle(photos)
        for photo in photos:
            self.employee('tag').assign(photo=photo)

    def work(self):
        for output in self.employee('tag').finished:
            for box in output.box_group.boxes.all():
                self.employee('identify').assign(box=box)

        for output in self.employee('identify').finished:
            for ingredient in output.ingredient_list.ingredients.all():
                self.employee('measure').assign(ingredient=ingredient)

        for output in self.employee('measure').finished:
            self.finish(ingredient=output.ingredient)
