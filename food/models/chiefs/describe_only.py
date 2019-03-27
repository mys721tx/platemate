import management.models.manager as base
from food.models import identify
from food.models.common import Box, Photo, IngredientList
from management.models.smart_model import OneOf


class Output(base.Output):
    photo = OneOf(Photo)
    box = OneOf(Box)
    ingredient_list = OneOf(IngredientList)

class Manager(base.Manager):

    def setup(self):
        self.hire(identify.describe, 'describe')

    def work(self):
        pass
