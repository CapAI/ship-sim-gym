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

    def __init__(self, values, conditions):
        self.lesson = 0
        self.conditions = conditions
        self.values = values

    def __int__(self):
        return int(self.values[self.lesson])

    def __float__(self):
        return self.values[self.lesson]

    def progress(self, val):

        if self.lesson < len(self.conditions):
            if val > self.conditions[self.lesson]:
                self.lesson += 1
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