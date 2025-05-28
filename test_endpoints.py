import requests
import json
from datetime import date
import time
import sys
from db_config import init_db

# Configuración base
BASE_URL = "http://localhost:8000"
headers = {"Content-Type": "application/json"}


reset_db = 1    # 1 para resetear los valores de la base de datos, 0 para no resetear
if reset_db:
    init_db()



# Colores para la terminal
class Color:
    VERDE = '\033[92m'
    AMARILLO = '\033[93m'
    ROJO = '\033[91m'
    RESET = '\033[0m'

# -------------------- PAYLOADS PARA PRUEBAS --------------------

# Payloads para alimentos
ALIMENTO_MANZANA = {
    "name": "Manzana verde",
    "category": "Frutas",
    "nutrients": {
        "kcal": 52.0,
        "protein_g": 0.3,
        "fat_g": 0.2,
        "carbs_g": 14.0
    },
    "unit": 180,
    "market": "Mercadona"
}

ALIMENTOS_RECETA = [
    {
        "name": "Tomate",
        "category": "Verduras y hortalizas",
        "nutrients": {"kcal": 22.0, "protein_g": 1.0, "fat_g": 0.0, "carbs_g": 4.0},
        "unit": 123
    },
    {
        "name": "Ajo",
        "category": "Verduras y hortalizas",
        "nutrients": {"kcal": 139.0, "protein_g": 7.0, "fat_g": 0.0, "carbs_g": 28.0},
        "unit": 5
    },
    {
        "name": "Aceite de oliva",
        "category": "Aceites",
        "nutrients": {"kcal": 900.0, "protein_g": 0.0, "fat_g": 100.0, "carbs_g": 0.0}
    },
    {
        "name": "Pan",
        "category": "Cereales",
        "nutrients": {"kcal": 265.0, "protein_g": 8.0, "fat_g": 1.0, "carbs_g": 58.0},
        "unit": 30
    }
]

# Payload para receta
RECETA_SALSA = {
    "name": "Salsa de tomate casera",
    "description": "Salsa de tomate tradicional",
    "ingredient_quantities": {
        "Tomate": 500,
        "Ajo": 10,
        "Aceite de oliva": 20
    }
}

# Payload para comida (la fecha se actualiza al ejecutar)
def get_comida_payload(receta_nombre):
    return {
        "meal_date": date.today().isoformat(),
        "recipes": [receta_nombre],
        "foods": [{"Pan": 60}]
    }

# -------------------- FUNCIONES DE UTILIDAD --------------------

def imprimir_respuesta(descripcion, respuesta, esperado=200):
    """Imprime información sobre la respuesta de manera formateada"""
    estado = respuesta.status_code
    color = Color.VERDE if estado == esperado else Color.ROJO

    print(f"\n{color}[{estado}] {descripcion}{Color.RESET}")
    if respuesta.status_code < 300:
        try:
            json_data = respuesta.json()
            print(json.dumps(json_data, indent=2, ensure_ascii=False))
            return json_data
        except:
            print(respuesta.text)
            return respuesta.text
    else:
        print(f"{Color.AMARILLO}{respuesta.text}{Color.RESET}")
        return None

def obtener_id_por_nombre(tipo, nombre):
    """Busca el ID de un elemento por su nombre"""
    time.sleep(0.5)  # Pequeña pausa para que la API procese la creación
    respuesta = requests.get(f"{BASE_URL}/{tipo}")
    if respuesta.status_code == 200:
        elementos = respuesta.json()
        for elemento in elementos:
            if isinstance(elemento, dict) and elemento.get("name") == nombre:
                return elemento.get("id")
    return None

def endpoint_fallido(nombre, respuesta=None):
    """Muestra un mensaje de error para un endpoint fallido"""
    print(f"{Color.ROJO}❌ Endpoint fallido: {nombre}{Color.RESET}")
    if respuesta:
        print(f"{Color.ROJO}Respuesta: {respuesta.status_code} - {respuesta.text}{Color.RESET}")
    return False

# -------------------- PRUEBAS DE ALIMENTOS --------------------

def probar_alimentos():
    print(f"\n{Color.AMARILLO}===== PRUEBAS DE ALIMENTOS ====={Color.RESET}")
    endpoints_ok = 0

    # 1. Crear un nuevo alimento (POST /foods)
    print("\n🔄 Probando: POST /foods")
    respuesta = requests.post(f"{BASE_URL}/foods", json=ALIMENTO_MANZANA, headers=headers)
    data = imprimir_respuesta("Crear alimento", respuesta)

    if respuesta.status_code != 200 or not data:
        return endpoint_fallido("POST /foods", respuesta)

    # Buscar el ID del alimento creado
    alimento_id = data.get("id")
    if not alimento_id:
        alimento_id = obtener_id_por_nombre("foods", ALIMENTO_MANZANA["name"])

    if not alimento_id:
        return endpoint_fallido("No se pudo obtener ID del alimento")

    print(f"🆔 ID del alimento creado: {alimento_id}")
    endpoints_ok += 1

    # 2. Obtener todos los alimentos (GET /foods)
    print("\n🔄 Probando: GET /foods")
    respuesta = requests.get(f"{BASE_URL}/foods")
    alimentos = imprimir_respuesta("Listar todos los alimentos", respuesta)

    if respuesta.status_code != 200 or not alimentos:
        return endpoint_fallido("GET /foods", respuesta)

    print(f"📊 Número de alimentos: {len(alimentos)}")
    endpoints_ok += 1

    # 3. Obtener alimento por ID (GET /foods/{id})
    print(f"\n🔄 Probando: GET /foods/{alimento_id}")
    respuesta = requests.get(f"{BASE_URL}/foods/{alimento_id}")
    alimento = imprimir_respuesta(f"Obtener alimento por ID ({alimento_id})", respuesta)

    if respuesta.status_code != 200 or not alimento:
        return endpoint_fallido(f"GET /foods/{alimento_id}", respuesta)

    print(f"✅ Alimento recuperado: {alimento.get('name')}")
    endpoints_ok += 1

    # 4. Actualizar alimento (PUT /foods/{id})
    alimento_actualizado = ALIMENTO_MANZANA.copy()
    alimento_actualizado["name"] = "Manzana Granny Smith"
    alimento_actualizado["unit"] = 175

    print(f"\n🔄 Probando: PUT /foods/{alimento_id}")
    respuesta = requests.put(f"{BASE_URL}/foods/{alimento_id}", json=alimento_actualizado, headers=headers)
    resultado = imprimir_respuesta(f"Actualizar alimento ({alimento_id})", respuesta)

    if respuesta.status_code != 200 or not resultado:
        return endpoint_fallido(f"PUT /foods/{alimento_id}", respuesta)

    print(f"✏️ Alimento actualizado a: {resultado.get('name')}")
    endpoints_ok += 1

    # 5. Eliminar alimento (DELETE /foods/{id})
    print(f"\n🔄 Probando: DELETE /foods/{alimento_id}")
    respuesta = requests.delete(f"{BASE_URL}/foods/{alimento_id}")
    resultado = imprimir_respuesta(f"Eliminar alimento ({alimento_id})", respuesta)

    if respuesta.status_code != 200:
        return endpoint_fallido(f"DELETE /foods/{alimento_id}", respuesta)

    print(f"🗑️ Alimento eliminado correctamente")
    endpoints_ok += 1

    print(f"{Color.VERDE}✅ Todos los endpoints de alimentos ({endpoints_ok}/5) funcionaron correctamente{Color.RESET}")
    return True

# -------------------- PRUEBAS DE RECETAS --------------------

def probar_recetas():
    print(f"\n{Color.AMARILLO}===== PRUEBAS DE RECETAS ====={Color.RESET}")
    endpoints_ok = 0

    # 0. Crear alimentos necesarios para la receta
    print("\n🔄 Preparando ingredientes para recetas...")
    for i, alimento in enumerate(ALIMENTOS_RECETA):
        print(f"  Creando ingrediente {i+1}/{len(ALIMENTOS_RECETA)}: {alimento['name']}")
        requests.post(f"{BASE_URL}/foods", json=alimento, headers=headers)
        time.sleep(0.2)

    # 1. Crear una nueva receta (POST /recipes)
    print("\n🔄 Probando: POST /recipes")
    respuesta = requests.post(f"{BASE_URL}/recipes", json=RECETA_SALSA, headers=headers)
    data = imprimir_respuesta("Crear receta", respuesta)

    if respuesta.status_code != 200 or not data:
        return endpoint_fallido("POST /recipes", respuesta), None

    # Buscar el ID de la receta creada
    receta_id = data.get("id")
    if not receta_id:
        receta_id = obtener_id_por_nombre("recipes", RECETA_SALSA["name"])

    if not receta_id:
        return endpoint_fallido("No se pudo obtener ID de la receta"), None

    print(f"🆔 ID de la receta creada: {receta_id}")
    endpoints_ok += 1

    # 2. Obtener todas las recetas (GET /recipes)
    print("\n🔄 Probando: GET /recipes")
    respuesta = requests.get(f"{BASE_URL}/recipes")
    recetas = imprimir_respuesta("Listar todas las recetas", respuesta)

    if respuesta.status_code != 200 or not recetas:
        return endpoint_fallido("GET /recipes", respuesta), None

    print(f"📊 Número de recetas: {len(recetas)}")
    endpoints_ok += 1

    # 3. Obtener receta por ID (GET /recipes/{id})
    print(f"\n🔄 Probando: GET /recipes/{receta_id}")
    respuesta = requests.get(f"{BASE_URL}/recipes/{receta_id}")
    receta = imprimir_respuesta(f"Obtener receta por ID ({receta_id})", respuesta)

    if respuesta.status_code != 200 or not receta:
        return endpoint_fallido(f"GET /recipes/{receta_id}", respuesta), None

    print(f"✅ Receta recuperada: {receta.get('name')}")
    endpoints_ok += 1

    # 4. Actualizar receta (PUT /recipes/{id})
    receta_actualizada = RECETA_SALSA.copy()
    receta_actualizada["description"] = "Salsa de tomate casera con ajo"
    receta_actualizada["ingredient_quantities"]["Ajo"] = 15

    print(f"\n🔄 Probando: PUT /recipes/{receta_id}")
    respuesta = requests.put(f"{BASE_URL}/recipes/{receta_id}", json=receta_actualizada, headers=headers)
    resultado = imprimir_respuesta(f"Actualizar receta ({receta_id})", respuesta)

    if respuesta.status_code != 200 or not resultado:
        return endpoint_fallido(f"PUT /recipes/{receta_id}", respuesta), None

    print(f"✏️ Receta actualizada: {resultado.get('name')}")
    endpoints_ok += 1

    receta_nombre = "Salsa de tomate casera" if not resultado else resultado.get('name', "Salsa de tomate casera")

    print(f"{Color.VERDE}✅ 4 endpoints de recetas funcionaron correctamente{Color.RESET}")
    # DELETE se probará después de las comidas para mantener la integridad referencial
    return True, receta_id, receta_nombre

# -------------------- PRUEBAS DE COMIDAS --------------------

def probar_comidas(receta_nombre, receta_id):
    print(f"\n{Color.AMARILLO}===== PRUEBAS DE COMIDAS ====={Color.RESET}")
    endpoints_ok = 0

    # 1. Crear una nueva comida (POST /meals)
    print("\n🔄 Probando: POST /meals")
    comida_payload = get_comida_payload(receta_nombre)
    respuesta = requests.post(f"{BASE_URL}/meals", json=comida_payload, headers=headers)
    data = imprimir_respuesta("Crear comida", respuesta)

    if respuesta.status_code != 200 or not data:
        return endpoint_fallido("POST /meals", respuesta)

    # Buscar el ID de la comida creada
    comida_id = data.get("id")
    fecha_actual = comida_payload["meal_date"]

    if not comida_id:
        # Intentar obtener el ID de la comida buscando por fecha
        respuesta_fecha = requests.get(f"{BASE_URL}/meals/date/{fecha_actual}")
        if respuesta_fecha.status_code == 200:
            comidas = respuesta_fecha.json()
            if comidas and isinstance(comidas, list) and len(comidas) > 0:
                comida_id = comidas[0].get("id")

    if not comida_id:
        return endpoint_fallido("No se pudo obtener ID de la comida")

    print(f"🆔 ID de la comida creada: {comida_id}")
    endpoints_ok += 1

    # 2. Obtener todas las comidas (GET /meals)
    print("\n🔄 Probando: GET /meals")
    respuesta = requests.get(f"{BASE_URL}/meals")
    comidas = imprimir_respuesta("Listar todas las comidas", respuesta)

    if respuesta.status_code != 200 or not comidas:
        return endpoint_fallido("GET /meals", respuesta)

    print(f"📊 Número de comidas: {len(comidas)}")
    endpoints_ok += 1

    # 3. Obtener comida por ID (GET /meals/{id})
    print(f"\n🔄 Probando: GET /meals/{comida_id}")
    respuesta = requests.get(f"{BASE_URL}/meals/{comida_id}")
    comida = imprimir_respuesta(f"Obtener comida por ID ({comida_id})", respuesta)

    if respuesta.status_code != 200 or not comida:
        return endpoint_fallido(f"GET /meals/{comida_id}", respuesta)

    endpoints_ok += 1

    # 4. Obtener comidas por fecha (GET /meals/date/{date})
    print(f"\n🔄 Probando: GET /meals/date/{fecha_actual}")
    respuesta = requests.get(f"{BASE_URL}/meals/date/{fecha_actual}")
    comidas_fecha = imprimir_respuesta(f"Obtener comidas por fecha ({fecha_actual})", respuesta)

    if respuesta.status_code != 200 or not comidas_fecha:
        return endpoint_fallido(f"GET /meals/date/{fecha_actual}", respuesta)

    print(f"📆 Comidas encontradas en la fecha: {len(comidas_fecha)}")
    endpoints_ok += 1

    # 5. Actualizar comida (PUT /meals/{id})
    comida_actualizada = comida_payload.copy()
    comida_actualizada["foods"].append({"Tomate": 50})

    print(f"\n🔄 Probando: PUT /meals/{comida_id}")
    respuesta = requests.put(f"{BASE_URL}/meals/{comida_id}", json=comida_actualizada, headers=headers)
    resultado = imprimir_respuesta(f"Actualizar comida ({comida_id})", respuesta)

    if respuesta.status_code != 200 or not resultado:
        return endpoint_fallido(f"PUT /meals/{comida_id}", respuesta)

    endpoints_ok += 1

    # 6. Eliminar comida (DELETE /meals/{id})
    print(f"\n🔄 Probando: DELETE /meals/{comida_id}")
    respuesta = requests.delete(f"{BASE_URL}/meals/{comida_id}")
    resultado = imprimir_respuesta(f"Eliminar comida ({comida_id})", respuesta)

    if respuesta.status_code != 200:
        return endpoint_fallido(f"DELETE /meals/{comida_id}", respuesta)

    print(f"🗑️ Comida eliminada correctamente")
    endpoints_ok += 1

    # 7. Eliminar también la receta utilizada (DELETE /recipes/{id})
    print(f"\n🔄 Probando: DELETE /recipes/{receta_id}")
    respuesta = requests.delete(f"{BASE_URL}/recipes/{receta_id}")
    resultado = imprimir_respuesta(f"Eliminar receta de prueba ({receta_id})", respuesta)

    if respuesta.status_code != 200:
        return endpoint_fallido(f"DELETE /recipes/{receta_id}", respuesta)

    print(f"🗑️ Receta eliminada correctamente")
    endpoints_ok += 1 # Para el DELETE de receta

    print(f"{Color.VERDE}✅ Todos los endpoints de comidas ({endpoints_ok-1}/6) funcionaron correctamente{Color.RESET}")
    print(f"{Color.VERDE}✅ DELETE /recipes también funcionó correctamente{Color.RESET}")
    return True

# -------------------- EJECUCIÓN PRINCIPAL --------------------

if __name__ == "__main__":
    print(f"{Color.AMARILLO}INICIANDO PRUEBAS COMPLETAS DE LA API DE NUTRICIÓN{Color.RESET}")
    print(f"URL: {BASE_URL}")
    print(f"Fecha: {date.today().isoformat()}")

    try:
        # Verificamos que la API esté funcionando
        print("\n🔄 Verificando conexión con la API...")
        respuesta = requests.get(f"{BASE_URL}")
        if respuesta.status_code < 200 or respuesta.status_code >= 300:
            raise requests.exceptions.ConnectionError("La API no respondió correctamente")
        print(f"{Color.VERDE}✓ API disponible{Color.RESET}")

        # Ejecutamos las pruebas en secuencia
        exitoso_alimentos = probar_alimentos()
        if exitoso_alimentos:
            exitoso_recetas, receta_id, receta_nombre = probar_recetas()
            if exitoso_recetas and receta_id and receta_nombre:
                exitoso_comidas = probar_comidas(receta_nombre, receta_id)
                if exitoso_comidas:
                    print(f"\n{Color.VERDE}✅ TODAS LAS PRUEBAS COMPLETADAS EXITOSAMENTE{Color.RESET}")
                    sys.exit(0)

        print(f"\n{Color.ROJO}❌ ALGUNAS PRUEBAS FALLARON{Color.RESET}")
        sys.exit(1)

    except requests.exceptions.ConnectionError:
        print(f"{Color.ROJO}❌ ERROR: No se pudo conectar con la API en {BASE_URL}{Color.RESET}")
        print("Asegúrate de que el servidor esté en ejecución con 'uvicorn api:app --reload'")
        sys.exit(2)
    except Exception as e:
        print(f"{Color.ROJO}❌ ERROR INESPERADO: {str(e)}{Color.RESET}")
        sys.exit(3)