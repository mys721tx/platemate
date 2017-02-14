import sys

LOGGING_LEVEL = 10

FOOD_CONTROL = 40
MANAGER_CONTROL = 30
TURK_CONTROL = 25
LOOP_CONTROL = 20
LOOP_SETUP = 30

CONTENT_TYPE_WARNING = 15

TURK_WARNING = 50

def log(message,level):
    if level >= LOGGING_LEVEL:
        print message
        sys.stdout.flush()
