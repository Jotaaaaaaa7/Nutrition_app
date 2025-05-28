from typing import List, Optional, Text, Dict
from datetime import date
import enum
import os


from sqlalchemy import (
    create_engine,  Column, Integer, String, Text, Date, Numeric, Enum, ForeignKey, CheckConstraint, JSON
)
from sqlalchemy.orm import declarative_base, foreign, relationship
from sqlalchemy.orm import relationship, sessionmaker, Session
from pydantic import BaseModel, field_validator, model_validator, Field
from contextlib import contextmanager



# ----------------------
# Database configuration
# ----------------------
DATABASE_URL = "sqlite:///./data/food.db"
engine = create_engine(
    DATABASE_URL, connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Context manager para manejar sesiones automáticamente
@contextmanager
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()




def init_db():
    # Eliminamos todas las tablas existentes
    Base.metadata.drop_all(bind=engine)
    print("Tablas eliminadas correctamente.")

    # Creamos las tablas nuevamente
    Base.metadata.create_all(bind=engine)
    print("Tablas creadas correctamente.")

# ----------------------
# Enum definitions
# ----------------------
class ComponentTypeEnum(str, enum.Enum):
    food = "food"
    recipe = "recipe"


# ----------------------
# SQLAlchemy models
# ----------------------
class FoodDB(Base):
    __tablename__ = "foods"
    id = Column(Integer, primary_key=True, autoincrement=True)
    category = Column(String, nullable=True)  # Categoría opcional
    name = Column(String, unique=True, nullable=False)    # Único
    unit = Column(Integer, nullable=True, default=None)  # Unidad por defecto
    market = Column(String, nullable=True)  # Mercado opcional
    nutrients = Column(JSON, nullable=False)


    recipe_items = relationship("RecipeItemDB", back_populates="food")
    meal_items = relationship(
        "MealItemDB",
        primaryjoin="and_(foreign(MealItemDB.component_id)==FoodDB.id, MealItemDB.component_type=='food')",
        viewonly=True
    )

class RecipeDB(Base):
    __tablename__ = "recipes"
    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True, nullable=False)
    description = Column(Text, nullable=True)
    nutrients = Column(JSON, nullable=False)

    # Modificar la relación para incluir cascade
    items = relationship("RecipeItemDB", back_populates="recipe", cascade="all, delete-orphan")
    meal_items = relationship(
        "MealItemDB",
        primaryjoin="and_(foreign(MealItemDB.component_id)==RecipeDB.id, MealItemDB.component_type=='recipe')",
        cascade="all, delete-orphan"
    )

class RecipeItemDB(Base):
    __tablename__ = "recipe_items"
    recipe_id = Column(
        Integer,
        ForeignKey("recipes.id", ondelete="CASCADE"),
        primary_key=True
    )
    food_id = Column(
        Integer,
        ForeignKey("foods.id", ondelete="RESTRICT"),
        primary_key=True
    )
    quantity_g = Column(Numeric, nullable=False)

    recipe = relationship("RecipeDB", back_populates="items")
    food = relationship("FoodDB", back_populates="recipe_items")


class MealDB(Base):
    __tablename__ = "meals"
    id = Column(Integer, primary_key=True)
    meal_date = Column(Date, nullable=False)
    nutrients = Column(JSON, nullable=False)

    items = relationship("MealItemDB", back_populates="meal", cascade="all, delete-orphan")

class MealItemDB(Base):
    __tablename__ = "meal_items"
    meal_id = Column(
        Integer,
        ForeignKey("meals.id", ondelete="CASCADE"),
        primary_key=True
    )
    component_type = Column(Enum(ComponentTypeEnum), primary_key=True)
    component_id = Column(Integer, primary_key=True)
    quantity = Column(Numeric, nullable=False)

    meal = relationship("MealDB", back_populates="items")



# ----------------------
# Pydantic schemas
# ----------------------

class Nutrients(BaseModel):
    kcal: float = Field(..., description="Kcal / 100 gr")
    protein_g: float = Field(..., description="Protein / 100 gr")
    fat_g: float = Field(..., description="Fat / 100 gr")
    carbs_g: float = Field(..., description="Carbs / 100 gr")

    @model_validator(mode="after")
    def validate_nutrients(cls, values):
        for key in ['kcal', 'protein_g', 'fat_g', 'carbs_g']:
            value = getattr(values, key, None)
            if value is None or value < 0:
                raise ValueError(f"{key} must be non-negative")
        return values



class Food(BaseModel):
    name: str = Field(..., description="Food name")
    category: Optional[str] = Field(None, description="Food category")
    nutrients: Nutrients = Field(..., description="Nutritional values")
    unit: Optional[float] = Field(None, description="Cantiadd en gramos de 1 unidad de producto")
    market: Optional[str] = Field(None, description="Market where the food is available")

    @field_validator('name')
    def validate_name(cls, v):
        if not v:
            raise ValueError("Name cannot be empty")
        return v


    class Config:
        from_attributes = True



class Recipe(BaseModel):
    name: str = Field(..., description="Recipe name")
    description: Optional[str] = Field(..., description="Recipe description")
    ingredient_quantities: Dict[str, float] = Field(
        ..., description="Dictionary with food names and quantity in grams"
    )

    @field_validator('ingredient_quantities')
    def validate_ingredient_quantities(cls, v):
        if not isinstance(v, dict):
            raise ValueError("ingredient_quantities must be a dictionary")
        for key, value in v.items():
            if not isinstance(key, str) or not isinstance(value, (int, float)):
                raise ValueError(f"Invalid ingredient entry: {key}: {value}")
            if value <= 0:
                raise ValueError(f"Quantity for '{key}' must be positive")
        return v

    @field_validator('name')
    def validate_name(cls, v):
        if not v.strip():
            raise ValueError("Name cannot be empty")
        return v

    class Config:
        from_attributes = True






class RecipeItem(BaseModel):
    recipe_id: int = Field(..., description="Recipe ID")
    food_id: int = Field(..., description="Food ID")
    quantity_g: float = Field(..., description="Quantity in grams")

    @field_validator('quantity_g')
    def positive_quantity(cls, v):
        if v <= 0:
            raise ValueError("quantity_g must be positive")
        return v

    class Config:
        from_attributes = True

class Meal(BaseModel):
    meal_date: date = Field(..., description="Date of the meal")
    recipes: List[str] = Field(..., description="Lista de recetas en la comida")
    foods: List[Dict[str, float]] = Field(..., description="Lista de diccionarios {nombre_alimento: cantidad_gramos}")

    @field_validator('meal_date')
    def validate_meal_date(cls, v):
        if not isinstance(v, date):
            raise ValueError("meal_date debe ser una fecha")
        return v

    @field_validator('foods')
    def validate_foods(cls, v):
        if not isinstance(v, list):
            raise ValueError("foods debe ser una lista")
        for item in v:
            if not isinstance(item, dict) or len(item) != 1:
                raise ValueError("Cada alimento debe ser un diccionario con un solo par nombre:cantidad")
            for food_name, quantity in item.items():
                if not isinstance(food_name, str) or not isinstance(quantity, (int, float)) or quantity <= 0:
                    raise ValueError(f"Cantidad inválida para '{food_name}'")
        return v


class MealItem(BaseModel):
    meal_id: int = Field(..., description="Meal ID")
    component_type: ComponentTypeEnum = Field(..., description="Type of component (food or recipe)")
    component_id: int = Field(..., description="ID of the component")
    quantity: float = Field(..., description="Quantity in grams")

    @field_validator('quantity')
    def positive_quantity(cls, v):
        if v <= 0:
            raise ValueError("quantity must be positive")
        return v

    @field_validator('component_type')
    def validate_component_type(cls, v):
        if not isinstance(v, ComponentTypeEnum):
            raise ValueError("component_type must be 'food' or 'recipe'")
        return v

    @field_validator('component_id')
    def positive_component_id(cls, v):
        if v <= 0:
            raise ValueError("component_id must be positive")
        return v

    class Config:
        from_attributes = True




# ---------------------- CRUD para FoodDB ----------------------
def create_food(food: Food):
    with get_db() as db:
        db_food = FoodDB(name=food.name, category=food.category, unit=food.unit,  nutrients=food.nutrients.model_dump())
        db.add(db_food)
        db.commit()
        db.refresh(db_food)
        return db_food


def get_food_by_id(food_id: int):
    with get_db() as db:
        return db.query(FoodDB).filter(FoodDB.id == food_id).first()


def get_foods():
    with get_db() as db:
        return db.query(FoodDB).all()


def update_food(food_id: int, updated_data: Food):
    with get_db() as db:
        db_food = db.query(FoodDB).filter(FoodDB.id == food_id).first()
        if not db_food:
            raise ValueError("Food not found")
        db_food.name = updated_data.name
        db_food.category = updated_data.category  # Añadir categoría
        db_food.nutrients = updated_data.nutrients.model_dump()  # Corregir .dict() a .model_dump()
        db_food.unit = updated_data.unit  # Añadir estos campos que faltaban
        db_food.market = updated_data.market
        db.commit()
        db.refresh(db_food)
        return db_food


def delete_food(food_id: int):
    with get_db() as db:
        db_food = db.query(FoodDB).filter(FoodDB.id == food_id).first()
        if db_food:
            db.delete(db_food)
            db.commit()
            return True
        return False

def get_food_and_nutrients(food_id, quantity):
    with get_db() as db:
        food = db.query(FoodDB).filter(FoodDB.id == food_id).first()
        if not food:
            raise ValueError("Food not found")

        # Calcular los nutrientes para la cantidad especificada
        nutrients = {key: (value * quantity) / 100 for key, value in food.nutrients.items()}
        return {
            "name": food.name,
            "nutrients": nutrients,
            "quantity_g": quantity
        }


# ---------------------- CRUD para RecipeDB ----------------------
def calculate_total_nutrients(items: List[Dict]) -> Dict:
    total = {"kcal": 0, "protein_g": 0, "fat_g": 0, "carbs_g": 0}
    for item in items:
        nutrients = item["nutrients"]
        qty = item["quantity"]
        for key in total:
            total[key] += (nutrients[key] * qty) / 100

    print(f"Total Nutrients: {total}")
    return total



def get_recipe_with_ingredients(recipe_id: int):
    with get_db() as db:
        # Obtener la receta con sus items
        db_recipe = db.query(RecipeDB).filter(RecipeDB.id == recipe_id).first()
        if not db_recipe:
            raise ValueError("Recipe not found")

        # Obtener los ingredientes con sus cantidades
        ingredients = db.query(RecipeItemDB, FoodDB)\
            .join(FoodDB)\
            .filter(RecipeItemDB.recipe_id == recipe_id)\
            .all()

        # Construir el resultado
        result = {
            "id": db_recipe.id,
            "name": db_recipe.name,
            "description": db_recipe.description,
            "nutrients": db_recipe.nutrients,
            "ingredients": [
                {
                    "food_name": food.name,
                    "quantity_g": float(item.quantity_g),
                    "nutrients": food.nutrients
                }
                for item, food in ingredients
            ]
        }
        return result

def get_recipes_with_ingredients():
    with get_db() as db:
        # Obtener todas las recetas con sus items
        recipes = db.query(RecipeDB).all()
        result = []
        for db_recipe in recipes:
            ingredients = db.query(RecipeItemDB, FoodDB)\
                .join(FoodDB)\
                .filter(RecipeItemDB.recipe_id == db_recipe.id)\
                .all()

            recipe_data = {
                "id": db_recipe.id,
                "name": db_recipe.name,
                "description": db_recipe.description,
                "nutrients": db_recipe.nutrients,
                "ingredients": [
                    {
                        "food_name": food.name,
                        "quantity_g": float(item.quantity_g),
                        "nutrients": food.nutrients
                    }
                    for item, food in ingredients
                ]
            }
            result.append(recipe_data)
        return result


def create_recipe(recipe: Recipe):
    with get_db() as db:
        items = []
        for food_name, quantity in recipe.ingredient_quantities.items():
            food = db.query(FoodDB).filter(FoodDB.name == food_name).first()
            if not food:
                raise ValueError(f"Food '{food_name}' not found")
            items.append({"nutrients": food.nutrients, "quantity": quantity})

        nutrients = calculate_total_nutrients(items)
        db_recipe = RecipeDB(name=recipe.name, description=recipe.description, nutrients=nutrients)
        db.add(db_recipe)
        db.commit()

        for food_name, quantity in recipe.ingredient_quantities.items():
            food = db.query(FoodDB).filter(FoodDB.name == food_name).first()
            db.add(RecipeItemDB(recipe_id=db_recipe.id, food_id=food.id, quantity_g=quantity))

        db.commit()
        db.refresh(db_recipe)
        return db_recipe


def get_recipe_by_id(recipe_id: int):
    with get_db() as db:
        return db.query(RecipeDB).filter(RecipeDB.id == recipe_id).first()


def get_recipes():
    with get_db() as db:
        return db.query(RecipeDB).all()


def update_recipe(recipe_id: int, updated_data: Recipe):
    with get_db() as db:
        db_recipe = db.query(RecipeDB).filter(RecipeDB.id == recipe_id).first()
        if not db_recipe:
            raise ValueError("Recipe not found")

        db.query(RecipeItemDB).filter(RecipeItemDB.recipe_id == recipe_id).delete()
        items = []
        for food_name, quantity in updated_data.ingredient_quantities.items():
            food = db.query(FoodDB).filter(FoodDB.name == food_name).first()
            if not food:
                raise ValueError(f"Food '{food_name}' not found")
            items.append({"nutrients": food.nutrients, "quantity": quantity})
            db.add(RecipeItemDB(recipe_id=recipe_id, food_id=food.id, quantity_g=quantity))

        db_recipe.name = updated_data.name
        db_recipe.description = updated_data.description
        db_recipe.nutrients = calculate_total_nutrients(items)
        db.commit()
        db.refresh(db_recipe)
        return db_recipe


def delete_recipe(recipe_id: int):
    with get_db() as db:
        try:
            # Primero eliminamos las referencias en meal_items
            db.query(MealItemDB).filter(
                MealItemDB.component_id == recipe_id,
                MealItemDB.component_type == ComponentTypeEnum.recipe
            ).delete()

            # Luego eliminamos la receta (los items se eliminarán automáticamente)
            db_recipe = db.query(RecipeDB).filter(RecipeDB.id == recipe_id).first()
            if db_recipe:
                db.delete(db_recipe)
                db.commit()
                return True
            return False
        except Exception as e:
            db.rollback()
            raise ValueError(f"Error al eliminar la receta: {str(e)}")


def get_recipe_with_nutrients(recipe_id: int, quantity):
    with get_db() as db:
        recipe = db.query(RecipeDB).filter(RecipeDB.id == recipe_id).first()
        if not recipe:
            raise ValueError("Recipe not found")

        # Calcular los nutrientes para la cantidad especificada
        nutrients = {key: (value * quantity) / 100 for key, value in recipe.nutrients.items()}
        return {
            "name": recipe.name,
            "nutrients": nutrients,
            "quantity_g": quantity
        }


# ---------------------- CRUD para MealDB ----------------------

def create_meal(meal: Meal):
    with get_db() as db:
        items = []
        # Procesar recetas (se mantienen como unidades)
        for recipe in meal.recipes:
            db_recipe = db.query(RecipeDB).filter(RecipeDB.name == recipe).first()
            if not db_recipe:
                raise ValueError(f"Receta '{recipe}' no encontrada")
            items.append({"nutrients": db_recipe.nutrients, "quantity": 100})

        # Procesar alimentos con sus cantidades específicas
        for food_dict in meal.foods:
            food_name = list(food_dict.keys())[0]
            quantity = food_dict[food_name]
            db_food = db.query(FoodDB).filter(FoodDB.name == food_name).first()
            if not db_food:
                raise ValueError(f"Alimento '{food_name}' no encontrado")
            items.append({"nutrients": db_food.nutrients, "quantity": quantity})

        nutrients = calculate_total_nutrients(items)
        db_meal = MealDB(meal_date=meal.meal_date, nutrients=nutrients)
        db.add(db_meal)
        db.commit()

        # Guardar componentes de la comida
        for recipe in meal.recipes:
            db_recipe = db.query(RecipeDB).filter(RecipeDB.name == recipe).first()
            db.add(MealItemDB(
                meal_id=db_meal.id,
                component_type=ComponentTypeEnum.recipe,
                component_id=db_recipe.id,
                quantity=100
            ))

        for food_dict in meal.foods:
            food_name = list(food_dict.keys())[0]
            quantity = food_dict[food_name]
            db_food = db.query(FoodDB).filter(FoodDB.name == food_name).first()
            db.add(MealItemDB(
                meal_id=db_meal.id,
                component_type=ComponentTypeEnum.food,
                component_id=db_food.id,
                quantity=quantity
            ))

        db.commit()
        db.refresh(db_meal)
        return db_meal


def get_meal_with_items(meal_id: int):
    with get_db() as db:
        # Obtener la comida base
        db_meal = db.query(MealDB).filter(MealDB.id == meal_id).first()
        if not db_meal:
            raise ValueError("Meal not found")

        # Obtener los items de la comida
        items = db.query(MealItemDB).filter(MealItemDB.meal_id == meal_id).all()

        # Construir el resultado
        result = {
            "id": db_meal.id,
            "meal_date": db_meal.meal_date,
            "nutrients": db_meal.nutrients,
            "items": [
                {
                    "component_type": item.component_type,
                    "component_id": item.component_id,
                    "quantity": float(item.quantity)
                }
                for item in items
            ]
        }
        return result

def get_meals_with_items():
    with get_db() as db:
        # Obtener todas las comidas con sus items
        meals = db.query(MealDB).all()
        result = []
        for db_meal in meals:
            items = db.query(MealItemDB).filter(MealItemDB.meal_id == db_meal.id).all()
            meal_data = {
                "id": db_meal.id,
                "meal_date": db_meal.meal_date,
                "nutrients": db_meal.nutrients,
                "items": [
                    {
                        "component_type": item.component_type,
                        "component_id": item.component_id,
                        "quantity": float(item.quantity)
                    }
                    for item in items
                ]
            }
            result.append(meal_data)
        return result


def get_meal_by_id(meal_id: int):
    with get_db() as db:
        return db.query(MealDB).filter(MealDB.id == meal_id).first()


def get_meals():
    with get_db() as db:
        return db.query(MealDB).all()


def update_meal(meal_id: int, updated_data: Meal):
    with get_db() as db:
        db_meal = db.query(MealDB).filter(MealDB.id == meal_id).first()
        if not db_meal:
            raise ValueError("Meal not found")

        # Eliminar todos los items existentes
        db.query(MealItemDB).filter(MealItemDB.meal_id == meal_id).delete()

        items = []

        # Procesar recetas (mantienen cantidad de 100)
        for recipe in updated_data.recipes:
            db_recipe = db.query(RecipeDB).filter(RecipeDB.name == recipe).first()
            if not db_recipe:
                raise ValueError(f"Recipe '{recipe}' not found")
            items.append({"nutrients": db_recipe.nutrients, "quantity": 100})
            db.add(MealItemDB(
                meal_id=meal_id,
                component_type=ComponentTypeEnum.recipe,
                component_id=db_recipe.id,
                quantity=100
            ))

        # Procesar alimentos con sus cantidades específicas
        for food_dict in updated_data.foods:
            food_name = list(food_dict.keys())[0]
            quantity = food_dict[food_name]
            db_food = db.query(FoodDB).filter(FoodDB.name == food_name).first()
            if not db_food:
                raise ValueError(f"Food '{food_name}' not found")
            items.append({"nutrients": db_food.nutrients, "quantity": quantity})
            db.add(MealItemDB(
                meal_id=meal_id,
                component_type=ComponentTypeEnum.food,
                component_id=db_food.id,
                quantity=quantity
            ))

        db_meal.meal_date = updated_data.meal_date
        db_meal.nutrients = calculate_total_nutrients(items)
        db.commit()
        db.refresh(db_meal)
        return db_meal


def delete_meal(meal_id: int):
    with get_db() as db:
        try:
            db_meal = db.query(MealDB).filter(MealDB.id == meal_id).first()
            if db_meal:
                # Los items se eliminarán automáticamente por el cascade
                db.delete(db_meal)
                db.commit()
                return True
            return False
        except Exception as e:
            db.rollback()
            raise ValueError(f"Error al eliminar la comida: {str(e)}")

def get_meals_by_date(meal_date: date):
    with get_db() as db:
        return db.query(MealDB).filter(MealDB.meal_date == meal_date).all()


# ---------------------- Creación de la Base de Datos ----------------------
if __name__ == "__main__":
    init_db()








