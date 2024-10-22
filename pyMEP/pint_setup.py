import pint

UNITS = pint.UnitRegistry()
Quantity = UNITS.Quantity

unit_definitions = [
    'parts_per_million = 1e-6 fraction = ppm'
]
for ud in unit_definitions:
    UNITS.define(ud)

# If you are pickling and unplicking Quantities within your project,
# you should also define the registry as the application registry
pint.set_application_registry(UNITS)
