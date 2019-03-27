import management.models.manager as manager
import management.models.turk as turk
from food.models.common import BoxGroup
from management.helpers import MINUTE, mode
from management.models.smart_model import ManyOf, OneOf
from management.qualifications import locale, min_approval, min_completed


class Input(manager.Input):
    box_groups = ManyOf(BoxGroup)


class Output(manager.Output):
    box_group = OneOf(BoxGroup)


class Job(turk.Job):
    box_groups = ManyOf(BoxGroup)


class Response(turk.Response):
    box_group = OneOf(BoxGroup)

    def validate(self):
        self.raw = self.box_group_id
        if self.box_group_id == '':
            return 'No vote provided'
        self.box_group = BoxGroup.objects.get(id=self.box_group_id)
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
    duplication = 3

    # Advertising
    qualifications = [min_approval(98), min_completed(100), locale('US')]
    keywords = ['picture', 'vote', 'box', 'food']
    title = 'Pick which set of boxes matches the foods on a plate'
    description = 'Help us figure out how many different foods are on the same plate.'

    #########
    # LOGIC #
    #########
    def setup(self):
        pass

    def work(self):

        for input in self.assigned:
            self.new_job(box_groups=input.box_groups.all(), from_input=input)

        for job in self.completed_jobs:
            if self.duplication > 1:
                choices = [
                    response.box_group for response in job.valid_responses
                ]
                bg = mode(choices)
            else:
                bg = job.valid_response.box_group

            self.finish(box_group=bg, from_job=job)
