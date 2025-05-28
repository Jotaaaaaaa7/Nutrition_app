import logging
from typing import List, Dict
from datetime import date
from fastapi import FastAPI, HTTPException, Path, Body
from fastapi.responses import JSONResponse

from db_config import (
    Food, Recipe, Meal,
    create_food, get_foods, get_food_by_id, update_food, delete_food,
    create_recipe, get_recipes, get_recipe_by_id, update_recipe, delete_recipe,
    create_meal, get_meals, get_meal_by_id, update_meal, delete_meal,
    get_recipe_with_ingredients, get_recipes_with_ingredients,
    get_meals_with_items, get_meal_with_items, get_meals_by_date,
)

# uvicorn api:app --reload

# ---------------------- Logger Setup ----------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(name)s - %(message)s"
)
logger = logging.getLogger("db_logger")

# ---------------------- FastAPI App ----------------------
app = FastAPI(
    title="API de Nutrición y Alimentos",
    description="""
    Esta API permite gestionar un sistema completo de seguimiento nutricional:
    
    * **Alimentos**: Información detallada de alimentos y sus valores nutricionales
    * **Recetas**: Combinaciones de alimentos con cálculo automático de nutrientes
    * **Comidas**: Registro diario de consumo con análisis nutricional
    
    Utilice los endpoints organizados por categorías para gestionar su dieta diaria.
    """,
    version="1.0.0",
    openapi_tags=[
        {
            "name": "alimentos",
            "description": "Operaciones con alimentos y sus valores nutricionales",
        },
        {
            "name": "recetas",
            "description": "Gestión de recetas y sus ingredientes",
        },
        {
            "name": "comidas",
            "description": "Registro y consulta de comidas diarias",
        },
    ]
)


@app.get("/",
    tags=["alimentos", "recetas", "comidas"],
    summary="Bienvenida a la API de Nutrición",
    description="Esta API permite gestionar alimentos, recetas y comidas diarias."
)
def api_welcome():
    """
    Bienvenido a la API de Nutrición y Alimentos.

    Utilice los endpoints para gestionar alimentos, recetas y comidas diarias.
    Consulte la documentación para más detalles sobre cada operación.
    """
    return JSONResponse(
        content={
            "message": "Bienvenido a la API de Nutrición y Alimentos",
            "version": "1.0.0",
            "description": "Gestión de alimentos, recetas y comidas diarias"
        },
        status_code=200
    )



# ---------------------- Food Endpoints ----------------------

@app.post("/foods",
    response_model=Food,
    tags=["alimentos"],
    summary="Crear nuevo alimento",
    description="Crea un alimento con su información nutricional completa."
)
def api_create_food(food: Food = Body(..., description="Datos del alimento a crear")):
    """
    Crea un nuevo alimento con la siguiente información:

    - **name**: Nombre del alimento (debe ser único)
    - **category**: Categoría del alimento
    - **nutrients**: Valores nutricionales por 100g
    - **unit**: Peso en gramos de una unidad (opcional)
    - **market**: Mercado donde se encuentra (opcional)
    """
    try:
        return create_food(food)
    except Exception as e:
        logger.exception("Error al crear alimento")
        raise HTTPException(status_code=500, detail=f"Error al crear alimento: {str(e)}")

@app.get("/foods",
    tags=["alimentos"],
    summary="Listar todos los alimentos",
    description="Obtiene un listado de todos los alimentos registrados."
)
def api_get_foods():
    """
    Devuelve todos los alimentos con su información nutricional completa.
    """
    try:
        return get_foods()
    except Exception as e:
        logger.exception("Error al recuperar alimentos")
        raise HTTPException(status_code=500, detail="Error al recuperar alimentos")

@app.get("/foods/{food_id}",
    tags=["alimentos"],
    summary="Obtener alimento por ID",
    description="Busca y devuelve la información de un alimento específico."
)
def api_get_food_by_id(
    food_id: int = Path(..., title="ID del alimento", description="ID único del alimento", ge=1)
):
    """
    Recupera la información completa de un alimento según su ID.
    """
    try:
        food = get_food_by_id(food_id)
        if not food:
            raise HTTPException(status_code=404, detail=f"Alimento con ID {food_id} no encontrado")
        return food
    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Error al recuperar alimento id={food_id}")
        raise HTTPException(status_code=500, detail="Error al recuperar alimento")

@app.put("/foods/{food_id}",
    tags=["alimentos"],
    summary="Actualizar alimento",
    description="Modifica los datos de un alimento existente."
)
def api_update_food(
    food_id: int = Path(..., title="ID del alimento", description="ID único del alimento", ge=1),
    food: Food = Body(..., description="Nuevos datos del alimento")
):
    """
    Actualiza la información de un alimento existente, incluyendo sus valores nutricionales.
    """
    try:
        return update_food(food_id, food)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.exception(f"Error al actualizar alimento id={food_id}")
        raise HTTPException(status_code=500, detail="Error al actualizar alimento")

@app.delete("/foods/{food_id}",
    tags=["alimentos"],
    summary="Eliminar alimento",
    description="Elimina permanentemente un alimento de la base de datos."
)
def api_delete_food(
    food_id: int = Path(..., title="ID del alimento", description="ID único del alimento", ge=1)
):
    """
    Elimina un alimento según su ID. Esta operación no se puede deshacer.
    """
    try:
        if delete_food(food_id):
            return {"mensaje": f"Alimento con ID {food_id} eliminado correctamente"}
        raise HTTPException(status_code=404, detail=f"Alimento con ID {food_id} no encontrado")
    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Error al eliminar alimento id={food_id}")
        raise HTTPException(status_code=500, detail="Error al eliminar alimento")

# ---------------------- Recipe Endpoints ----------------------

@app.post("/recipes",
    tags=["recetas"],
    summary="Crear nueva receta",
    description="Crea una receta con ingredientes y calcula automáticamente sus valores nutricionales."
)
def api_create_recipe(recipe: Recipe = Body(..., description="Datos de la receta a crear")):
    """
    Crea una nueva receta especificando:

    - **name**: Nombre de la receta (único)
    - **description**: Descripción o instrucciones
    - **ingredient_quantities**: Diccionario de ingredientes con cantidades en gramos

    El sistema calcula automáticamente los valores nutricionales totales.
    """
    try:
        db_recipe = create_recipe(recipe)
        return get_recipe_with_ingredients(db_recipe.id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.exception("Error al crear receta")
        raise HTTPException(status_code=500, detail="Error al crear receta")

@app.get("/recipes",
    tags=["recetas"],
    summary="Listar todas las recetas",
    description="Obtiene un listado de todas las recetas con sus ingredientes y valores nutricionales."
)
def api_get_recipes():
    """
    Devuelve todas las recetas registradas, incluyendo ingredientes, cantidades y valores nutricionales.
    """
    try:
        return get_recipes_with_ingredients()
    except Exception as e:
        logger.exception("Error al recuperar recetas")
        raise HTTPException(status_code=500, detail="Error al recuperar recetas")

@app.get("/recipes/{recipe_id}",
    tags=["recetas"],
    summary="Obtener receta por ID",
    description="Busca y devuelve una receta específica con todos sus detalles."
)
def api_get_recipe_by_id(
    recipe_id: int = Path(..., title="ID de la receta", description="ID único de la receta", ge=1)
):
    """
    Recupera una receta completa según su ID, incluyendo ingredientes y valores nutricionales.
    """
    try:
        recipe = get_recipe_with_ingredients(recipe_id)
        if not recipe:
            raise HTTPException(status_code=404, detail=f"Receta con ID {recipe_id} no encontrada")
        return recipe
    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Error al recuperar receta id={recipe_id}")
        raise HTTPException(status_code=500, detail="Error al recuperar receta")

@app.put("/recipes/{recipe_id}",
    tags=["recetas"],
    summary="Actualizar receta",
    description="Modifica los datos de una receta existente y recalcula sus valores nutricionales."
)
def api_update_recipe(
    recipe_id: int = Path(..., title="ID de la receta", description="ID único de la receta", ge=1),
    recipe: Recipe = Body(..., description="Nuevos datos de la receta")
):
    """
    Actualiza una receta existente con nuevos ingredientes y cantidades.
    Se recalculan automáticamente los valores nutricionales.
    """
    try:
        update_recipe(recipe_id, recipe)
        return get_recipe_with_ingredients(recipe_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.exception(f"Error al actualizar receta id={recipe_id}")
        raise HTTPException(status_code=500, detail="Error al actualizar receta")

@app.delete("/recipes/{recipe_id}",
    tags=["recetas"],
    summary="Eliminar receta",
    description="Elimina permanentemente una receta de la base de datos."
)
def api_delete_recipe(
    recipe_id: int = Path(..., title="ID de la receta", description="ID único de la receta", ge=1)
):
    """
    Elimina una receta según su ID. Esta operación no se puede deshacer.
    """
    try:
        if delete_recipe(recipe_id):
            return {"mensaje": f"Receta con ID {recipe_id} eliminada correctamente"}
        raise HTTPException(status_code=404, detail=f"Receta con ID {recipe_id} no encontrada")
    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Error al eliminar receta id={recipe_id}")
        raise HTTPException(status_code=500, detail="Error al eliminar receta")

# ---------------------- Meal Endpoints ----------------------

@app.post("/meals",
    tags=["comidas"],
    summary="Registrar nueva comida",
    description="Registra una comida para una fecha específica con alimentos y recetas consumidos."
)
def api_create_meal(meal: Meal = Body(..., description="Datos de la comida a registrar")):
    """
    Registra una nueva comida especificando:

    - **meal_date**: Fecha de consumo
    - **recipes**: Lista de nombres de recetas incluidas
    - **foods**: Lista de alimentos con sus cantidades en gramos

    El sistema calcula automáticamente los valores nutricionales totales.
    """
    try:
        db_meal = create_meal(meal)
        return get_meal_with_items(db_meal.id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.exception("Error al crear comida")
        raise HTTPException(status_code=500, detail="Error al crear comida")

@app.get("/meals",
    tags=["comidas"],
    summary="Listar todas las comidas",
    description="Obtiene un listado de todas las comidas registradas con sus componentes."
)
def api_get_meals():
    """
    Devuelve todas las comidas registradas, incluyendo fecha, componentes y valores nutricionales.
    """
    try:
        return get_meals_with_items()
    except Exception as e:
        logger.exception("Error al recuperar comidas")
        raise HTTPException(status_code=500, detail="Error al recuperar comidas")

@app.get("/meals/{meal_id}",
    tags=["comidas"],
    summary="Obtener comida por ID",
    description="Busca y devuelve una comida específica con todos sus componentes."
)
def api_get_meal_by_id(
    meal_id: int = Path(..., title="ID de la comida", description="ID único de la comida", ge=1)
):
    """
    Recupera una comida completa según su ID, incluyendo todos sus componentes y nutrientes.
    """
    try:
        meal = get_meal_with_items(meal_id)
        if not meal:
            raise HTTPException(status_code=404, detail=f"Comida con ID {meal_id} no encontrada")
        return meal
    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Error al recuperar comida id={meal_id}")
        raise HTTPException(status_code=500, detail="Error al recuperar comida")

@app.get("/meals/date/{meal_date}",
    tags=["comidas"],
    summary="Buscar comidas por fecha",
    description="Devuelve todas las comidas registradas para una fecha específica."
)
def api_get_meals_by_date(
    meal_date: str = Path(..., title="Fecha", description="Fecha en formato YYYY-MM-DD")
):
    """
    Busca todas las comidas registradas para una fecha específica.
    La fecha debe tener formato YYYY-MM-DD.
    """
    try:
        meals = get_meals_by_date(meal_date)
        if not meals:
            raise HTTPException(status_code=404, detail=f"No hay comidas registradas para la fecha {meal_date}")
        return meals
    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Error al recuperar comidas para fecha={meal_date}")
        raise HTTPException(status_code=500, detail="Error al recuperar comidas por fecha")

@app.put("/meals/{meal_id}",
    tags=["comidas"],
    summary="Actualizar comida",
    description="Modifica los datos de una comida existente y recalcula sus valores nutricionales."
)
def api_update_meal(
    meal_id: int = Path(..., title="ID de la comida", description="ID único de la comida", ge=1),
    meal: Meal = Body(..., description="Nuevos datos de la comida")
):
    """
    Actualiza una comida existente con nuevos componentes.
    Se recalculan automáticamente los valores nutricionales.
    """
    try:
        update_meal(meal_id, meal)
        return get_meal_with_items(meal_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.exception(f"Error al actualizar comida id={meal_id}")
        raise HTTPException(status_code=500, detail="Error al actualizar comida")

@app.delete("/meals/{meal_id}",
    tags=["comidas"],
    summary="Eliminar comida",
    description="Elimina permanentemente una comida de la base de datos."
)
def api_delete_meal(
    meal_id: int = Path(..., title="ID de la comida", description="ID único de la comida", ge=1)
):
    """
    Elimina una comida según su ID. Esta operación no se puede deshacer.
    """
    try:
        if delete_meal(meal_id):
            return {"mensaje": f"Comida con ID {meal_id} eliminada correctamente"}
        raise HTTPException(status_code=404, detail=f"Comida con ID {meal_id} no encontrada")
    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Error al eliminar comida id={meal_id}")
        raise HTTPException(status_code=500, detail="Error al eliminar comida")