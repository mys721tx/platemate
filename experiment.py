import sys

from food.models.chiefs import from_static
from management.run import run

photoset = sys.argv[1]
mode = sys.argv[-1]

run(
    chief_module=from_static,
    args={'photoset': photoset, 'sandbox': (mode != 'real')},
    operation=photoset,
)
