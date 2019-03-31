from django.core.exceptions import ObjectDoesNotExist

import management.models.manager as manager
import management.models.turk as turk
from food.models.common import IngredientList
from management.helpers import MINUTE, mode
from management.models.smart_model import ManyOf, OneOf
from management.qualifications import locale, min_approval, min_completed


class Input(manager.Input):
    ingredient_lists = ManyOf(IngredientList)


class Output(manager.Output):
    ingredient_list = OneOf(IngredientList)


class Job(turk.Job):
    ingredient_lists = ManyOf(IngredientList)


class Response(turk.Response):
    ingredient_list = OneOf(IngredientList)

    def validate(self):
        self.raw = self.ingredients_choice
        if self.ingredients_choice in ['', ' ', None]:
            return "No choice of ingredients provided"
        try:
            self.ingredient_list = IngredientList.objects.get(
                pk=self.ingredients_choice
            )
        except ObjectDoesNotExist:
            return "Invalid choice entered"

        return True


class Manager(manager.Manager):

    ################
    # HIT SETTINGS #
    ################

    # Batching
    batch_size = 2
    max_wait = 5 * MINUTE

    # Payment
    reward = .04
    duplication = 5

    # Advertising
    qualifications = [min_approval(98), min_completed(200), locale('US')]
    keywords = ['picture', 'identify', 'food', 'database', 'match', 'vote']
    title = 'Pick which list of ingredients best matches a photo'
    description = 'Select the list of ingredients that best matches the highlighted portion of a picture'

    #########
    # LOGIC #
    #########
    def work(self):

        for input in self.assigned:
            self.new_job(
                ingredient_lists=input.ingredient_lists.all(),
                from_input=input,
            )

        for job in self.completed_jobs:

            if self.duplication > 1:
                choices = [
                    response.ingredient_list for response in job.valid_responses
                ]
                il = mode(choices)
            else:
                il = job.valid_response.ingredient_list

            self.finish(ingredient_list=il, from_job=job)
