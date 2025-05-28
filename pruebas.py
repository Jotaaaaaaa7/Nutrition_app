from db_config import (
    Food, Recipe, Meal, Nutrients,
    create_food, create_recipe, create_meal,
    get_meal_by_id, get_meals, update_meal, delete_meal, calculate_total_nutrients, init_db
)
from datetime import date


init_db()

def test_meal_crud():
    try:
        # 1. Crear alimentos de prueba
        print("\n1. Creando alimentos de prueba...")
        test_foods = [
            Food(
                name="Lentejas",
                nutrients=Nutrients(
                    kcal=116, protein_g=9, fat_g=0.4,
                    carbs_g=20, fiber_g=8, chol_mg=0
                )
            ),
            Food(
                name="Pan",
                nutrients=Nutrients(
                    kcal=265, protein_g=9, fat_g=3.2,
                    carbs_g=49, fiber_g=2.7, chol_mg=0
                )
            ),
            Food(
                name="Huevo",
                nutrients=Nutrients(
                    kcal=155, protein_g=13, fat_g=11,
                    carbs_g=1.1, fiber_g=0, chol_mg=373
                )
            )
        ]

        print(f'Macros de : {test_foods[0].name} -> {test_foods[0].nutrients.kcal} kcal, {test_foods[0].nutrients.protein_g} g proteína, {test_foods[0].nutrients.fat_g} g grasa, {test_foods[0].nutrients.carbs_g} g carbohidratos, {test_foods[0].nutrients.fiber_g} g fibra, {test_foods[0].nutrients.chol_mg} mg colesterol')
        print(f'Macros de : {test_foods[1].name} -> {test_foods[1].nutrients.kcal} kcal, {test_foods[1].nutrients.protein_g} g proteína, {test_foods[1].nutrients.fat_g} g grasa, {test_foods[1].nutrients.carbs_g} g carbohidratos, {test_foods[2].nutrients.fiber_g} g fibra, {test_foods[1].nutrients.chol_mg} mg colesterol')
        print(f'Macros de : {test_foods[2].name} -> {test_foods[2].nutrients.kcal} kcal, {test_foods[2].nutrients.protein_g} g proteína, {test_foods[2].nutrients.fat_g} g grasa, {test_foods[2].nutrients.carbs_g} g carbohidratos, {test_foods[2].nutrients.fiber_g} g fibra, {test_foods[2].nutrients.chol_mg} mg colesterol')

        created_foods = []
        for food in test_foods:
            created_food = create_food(food)
            created_foods.append(created_food)
            print(f"Alimento creado: {created_food.name}")

        # 2. Crear recetas de prueba
        print("\n2. Creando recetas de prueba...")
        test_recipes = [
            Recipe(
                name="Lentejas con huevo",
                description="Lentejas estofadas con huevo cocido",
                ingredient_quantities={
                    "Lentejas": 200,
                    "Huevo": 50
                }
            ),
            Recipe(
                name="Tostada de huevo",
                description="Huevo revuelto sobre pan tostado",
                ingredient_quantities={
                    "Pan": 30,
                    "Huevo": 60
                }
            )
        ]



        created_recipes = []
        for recipe in test_recipes:
            created_recipe = create_recipe(recipe)
            created_recipes.append(created_recipe)
            print(f"Receta creada: {created_recipe.name}")

        # 3. Crear comida con cantidades específicas
        print("\n3. Creando comida...")
        meal = Meal(
            meal_date=date.today(),
            recipes=["Lentejas con huevo"],  # Solo el nombre de la receta
            foods=[{"Pan": 50}]  # 50 gramos de pan
        )

        created_meal = create_meal(meal)
        print(f"Comida creada para fecha: {created_meal.meal_date}")
        print(f"Nutrientes totales: {created_meal.nutrients}")

        # 4. Obtener comida por ID
        print("\n4. Obteniendo comida por ID...")
        found_meal = get_meal_by_id(created_meal.id)
        print(f"Comida encontrada para fecha: {found_meal.meal_date}")
        print(f"Nutrientes: {found_meal.nutrients}")

        # 5. Actualizar comida con diferentes cantidades
        print("\n5. Actualizando comida...")
        updated_meal = Meal(
            meal_date=date.today(),
            recipes=[
                "Lentejas con huevo",
                "Tostada de huevo"
            ],
            foods=[
                {"Pan": 75},  # Aumentamos a 75g de pan
                {"Huevo": 25}  # Añadimos 25g de huevo extra
            ]
        )

        updated = update_meal(created_meal.id, updated_meal)
        print(f"Comida actualizada para fecha: {updated.meal_date}")
        print(f"Nuevos nutrientes: {updated.nutrients}")

        # 6. Listar todas las comidas
        print("\n6. Listando todas las comidas...")
        all_meals = get_meals()
        for meal in all_meals:
            print(f"- Comida del {meal.meal_date}: {meal.nutrients}")

        # 7. Eliminar comida
        print("\n7. Eliminando comida...")
        deleted = delete_meal(created_meal.id)
        print(f"Comida eliminada: {deleted}")

    except Exception as e:
        print(f"\nError: {str(e)}")

if __name__ == "__main__":
    test_meal_crud()