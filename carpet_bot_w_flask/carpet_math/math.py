# pylint: disable=missing-module-docstring
# pylint: disable=missing-class-docstring
# pylint: disable=missing-function-docstring

import math
from google_sheet import GoogleSheet


def calculate_carpet_cost(carpet_type, **kwargs):
    """
    Розраховує загальну вартість килима
    на основі його розмірів та кількості мотків.
    """
    # Отримання вартості матеріалів
    gs = GoogleSheet()
    materials = gs.get_material_cost("Вартість матеріалів")
    yarn_usage_multiplier = 1 if kwargs.get('num_skeins', 3) == 2 else 1.5
    yarn_usage_per_100_cm2 = 48 * yarn_usage_multiplier / 300

    # Розрахунок площі килима
    area_calculators = {
                    "Квадратний килим": lambda length, width, **_:
                    length * width,
                    "Круглий килим": lambda diameter, **_:
                    math.pi * ((diameter / 2) ** 2)
                        }

    carpet_area = area_calculators[carpet_type](**kwargs)

    # Розрахунок необхідних матеріалів та вартості
    usage_per_100_cm2 = {
        "Yarn": yarn_usage_per_100_cm2,
        "Fabric": 0.0354,
        "Glue": 0.0354,
        "Lining": 0.0354
    }

    total_cost = 0
    for material, usage in usage_per_100_cm2.items():
        total_cost += (
            math.ceil(carpet_area * usage / 100) * materials.get(material)
            )

    profit_coef = 3
    return total_cost * profit_coef

# print(calculate_carpet_cost(
#     "Квадратний килим", length=100, width=100, num_skeins=3)
#     )
# print(calculate_carpet_cost("Круглий килим", diameter=60, num_skeins=3))
