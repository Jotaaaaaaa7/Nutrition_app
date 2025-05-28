import pandas as pd
from db_config import create_food, Food, create_recipe, create_meal, Recipe, Meal, init_db

data = pd.read_csv('data/alimentos.csv')




#! Reseteamos la DB
init_db()


# * Rellennamos con los aliemntos scrappeados (alimentos.csv)

for index, row in data.iterrows():

    unit = float(row['Unidad (g)']) if pd.notna(row['Unidad (g)']) else None
    print(unit, type(unit))

    food = Food(
        name=row['Alimento'],
        category=row['Categoría'],
        nutrients={
            'kcal': row['Calorías'],
            'protein_g': row['Proteínas'],
            'fat_g': row['Grasa'],
            'carbs_g': row['Carbohidratos'],
        },
        unit=unit,
        market=row.get('Marca / Supermercado', None)
    )

    created_food = create_food(food)



# rellenamos con 8 recetas de ejemplo

recipes_payloads = [
{
  "name": "Ensalada Mediterránea",
  "description": "Ensalada fresca con tomate, lechuga, aceitunas y queso",
  "ingredient_quantities": {
    "Tomate": 200,
    "Lechuga": 150,
    "Aceitunas": 50,
    "Queso de Burgos": 100,
    "Aceite de oliva": 20
  }
},
    {
      "name": "Pasta con Verduras",
      "description": "Pasta salteada con calabacín, pimiento y tomate",
      "ingredient_quantities": {
        "Pasta": 200,
        "Calabacín": 150,
        "Pimiento": 100,
        "Tomate": 150,
        "Aceite de oliva": 15,
        "Cebolla": 50
      }
    },
    {
      "name": "Pollo al Horno con Patatas",
      "description": "Pollo asado con guarnición de patatas y hierbas",
      "ingredient_quantities": {
        "Pollo deshuesado": 300,
        "Patata cocida": 250,
        "Cebolla": 50,
        "Aceite de oliva": 20,
      }
    },
    {
      "name": "Tortilla de Patatas",
      "description": "Tortilla tradicional española con patatas y cebolla",
      "ingredient_quantities": {
        "Huevo entero": 180,
        "Patata cocida": 350,
        "Cebolla": 80,
        "Aceite de oliva": 30
      }
    },
    {
      "name": "Arroz con Mariscos",
      "description": "Arroz con gambas, mejillones y calamares",
      "ingredient_quantities": {
        "Arroz blanco": 200,
        "Gambas": 150,
        "Mejillón": 150,
        "Calamar, Sepia": 100,
        "Tomate": 100,
        "Cebolla": 50,
        "Pimiento": 50,
        "Aceite de oliva": 15
      }
    },
    {
      "name": "Lentejas Estofadas",
      "description": "Guiso tradicional de lentejas con verduras",
      "ingredient_quantities": {
        "Lentejas": 200,
        "Zanahoria": 100,
        "Cebolla": 80,
        "Tomate": 100,
        "Pimiento": 50,
        "Aceite de oliva": 20
      }
    },
    {
      "name": "Hamburguesa Casera",
      "description": "Hamburguesa de ternera con guarnición de verduras",
      "ingredient_quantities": {
        "Ternera, bistec": 200,
        "Cebolla": 50,
        "Tomate": 100,
        "Lechuga": 30,
        "Pan de trigo, blanco": 120,
        "Queso en porciones": 40
      }
    },
    {
      "name": "Crema de Verduras",
      "description": "Crema suave de calabacín, zanahoria y patata",
      "ingredient_quantities": {
        "Calabacín": 200,
        "Zanahoria": 100,
        "Patata cocida": 150,
        "Cebolla": 80,
        "Aceite de oliva": 15
      }
    }
]


for recipe in recipes_payloads:

    recipe = Recipe(
        name=recipe['name'],
        description=recipe['description'],
        ingredient_quantities=recipe['ingredient_quantities']
    )

    created_recipe = create_recipe(
        recipe
    )






# * rellenamos con 2 comidas de ejemplo

meals_payloads = [
    {
      "meal_date": "2025-05-28",
      "recipes": ["Lentejas Estofadas", "Ensalada Mediterránea"],
      "foods": [
        {"Pan de trigo, integral": 60},
        {"Yogurt natural": 125},
      ]
    },
    {
      "meal_date": "2025-05-28",
      "recipes": ["Crema de Verduras"],
      "foods": [
        {"Pan de molde, integral. Pan tostado": 40},
      ]
    }
]

for meal in meals_payloads:

    meal = Meal(
        meal_date=meal['meal_date'],
        recipes=meal['recipes'],  # Lista de nombres de recetas
        foods=meal['foods']  # Lista de diccionarios con alimentos y cantidades
    )

    created_meal = create_meal(
        meal
    )
    print(f"Comida creada para fecha: {created_meal.meal_date}")
    print(f"Nutrientes totales: {created_meal.nutrients}")