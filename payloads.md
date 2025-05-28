// --------------------- ALIMENTOS (FOODS) ---------------------

// POST /foods - Crear manzana
{
    "name": "Manzana",
    "nutrients": {
        "kcal": 52,
        "protein_g": 0.3,
        "carbs_g": 14,
        "fat_g": 0.2,
        "fiber_g": 2.4,
        "chol_mg": 0
    },
    "unit": 150,
    "market": "Mercadona"
}

// POST /foods - Crear plátano
{
    "name": "Plátano",
    "nutrients": {
        "kcal": 89,
        "protein_g": 1.1,
        "carbs_g": 22.8,
        "fat_g": 0.3,
        "fiber_g": 2.6,
        "chol_mg": 0
    },
    "unit": 120
}

// POST /foods - Crear pan integral
{
    "name": "Pan Integral",
    "nutrients": {
        "kcal": 265,
        "protein_g": 8.8,
        "carbs_g": 47.5,
        "fat_g": 3.2,
        "fiber_g": 7.0,
        "chol_mg": 0
    },
    "unit": 30
}

// POST /foods - Crear tomate
{
    "name": "Tomate",
    "nutrients": {
        "kcal": 22,
        "protein_g": 1,
        "carbs_g": 4,
        "fat_g": 0,
        "fiber_g": 2,
        "chol_mg": 0
    },
    "unit": 100
}

// PUT /foods/1 - Actualizar manzana
{
    "name": "Manzana Verde",
    "nutrients": {
        "kcal": 50,
        "protein_g": 0.3,
        "carbs_g": 13,
        "fat_g": 0.2,
        "fiber_g": 2.4,
        "chol_mg": 0
    },
    "unit": 140,
    "market": "Carrefour"
}

// --------------------- RECETAS (RECIPES) ---------------------

// POST /recipes - Crear ensalada de frutas
{
    "name": "Ensalada de Frutas",
    "description": "Una ensalada fresca y saludable",
    "ingredient_quantities": {
        "Manzana Verde": 100,
        "Plátano": 100
    }
}

// POST /recipes - Crear tostada
{
    "name": "Tostada de Plátano",
    "description": "Tostada con plátano machacado",
    "ingredient_quantities": {
        "Pan Integral": 60,
        "Plátano": 80
    }
}

// PUT /recipes/1 - Actualizar receta
{
    "name": "Ensalada de Frutas Tropical",
    "description": "Una ensalada fresca con frutas tropicales",
    "ingredient_quantities": {
        "Manzana Verde": 120,
        "Plátano": 150
    }
}

// --------------------- COMIDAS (MEALS) ---------------------

// POST /meals - Crear desayuno
{
    "meal_date": "2024-05-25",
    "recipes": ["Ensalada de Frutas Tropical"],
    "foods": [
        {"Pan Integral": 60}
    ]
}

// POST /meals - Crear merienda
{
    "meal_date": "2024-05-26",
    "recipes": ["Tostada de Plátano"],
    "foods": [
        {"Plátano": 120}
    ]
}

// PUT /meals/1 - Actualizar comida
{
    "meal_date": "2024-05-25",
    "recipes": ["Ensalada de Frutas Tropical"],
    "foods": [
        {"Manzana Verde": 75},
        {"Plátano": 50}
    ]
}

// --------------------- VALIDACIÓN ---------------------

// POST /foods - Probar validación (valor negativo)
{
    "name": "Alimento Inválido",
    "nutrients": {
        "kcal": -10,
        "protein_g": 5,
        "carbs_g": 10,
        "fat_g": 2,
        "fiber_g": 1,
        "chol_mg": 0
    }
}

// POST /recipes - Probar ingrediente inexistente
{
    "name": "Receta Inválida",
    "description": "Esta receta debería fallar",
    "ingredient_quantities": {
        "Ingrediente Inexistente": 100
    }
}

// POST /meals - Probar receta inexistente
{
    "meal_date": "2024-05-26",
    "recipes": ["Receta Inexistente"],
    "foods": [
        {"Manzana Verde": 100}
    ]
}