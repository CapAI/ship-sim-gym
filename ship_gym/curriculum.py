from enum import Enum

class LessonCondition(Enum):
    STEPS = 0,
    REWARD = 1

class Lesson(object):

    def __init__(self, param_dict):

        self.param_dict = param_dict

    def pass_lesson(self, val_dict):

        for k,v in self.param_dict.items():

            if val_dict[k] < v:
                return False

        return True


class Curriculum(object):

    def __init__(self, values, conditions, repeat_condition=1):
        self.lesson = 0
        self.repeat_reached = 0

        self.conditions = conditions
        self.repeat_condition = repeat_condition

        self.values = values

    def __int__(self):
        return int(self.values[self.lesson])

    def __float__(self):
        return self.values[self.lesson]

    def progress(self, val):

        if self.lesson < len(self.conditions):
            if val > self.conditions[self.lesson]:
                self.repeat_reached += 1
                if self.repeat_reached > self.repeat_condition:
                    self.lesson += 1
                    self.repeat_reached = 0
                    return True

        return False


    # @property
    # def param_names(self):
    #     s = set()
    #     for lesson in self.lessons:
    #         s.update(lesson.keys())
    #
    #     return s
    #
    # def pass_lesson(self, val):
    #
    #
    #
    # def get_lesson_params(self):