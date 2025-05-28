import os
import csv
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

CATEGORIA_IDS = ['cat-19', 'cat-10', 'cat-20', 'cat-16', 'cat-8', 'cat-13', 'cat-14',
                 'cat-18', 'cat-15', 'cat-12', 'cat-9', 'cat-17', 'cat-21', 'cat-11']

CSV_FILENAME = "data/alimentos.csv"

def setup_driver():
    options = webdriver.ChromeOptions()
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option("useAutomationExtension", False)
    options.add_argument("user-agent=Mozilla/5.0")
    options.add_argument("--start-maximized")
    driver = webdriver.Chrome(options=options)
    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    driver.get("https://www.labdeiters.com/nutricalculadora/")
    return driver

def scroll_hasta_elemento(driver, elemento):
    driver.execute_script("arguments[0].scrollIntoView();", elemento)
    time.sleep(0.5)

def poner_gramos(input_elem, valor):
    input_elem.clear()
    input_elem.send_keys(str(valor))
    input_elem.send_keys(Keys.TAB)

def get_values(driver):
    return {
        'kcal': driver.find_element(By.ID, 'energia').text,
        'prot': driver.find_element(By.ID, 'proteinas').text,
        'fat': driver.find_element(By.ID, 'grasas').text,
        'carbs': driver.find_element(By.ID, 'azucar').text,
        'fiber': driver.find_element(By.ID, 'fibra').text,
        'chol': driver.find_element(By.ID, 'colesterol').text
    }

def inicializar_csv():
    if not os.path.exists(CSV_FILENAME):
        with open(CSV_FILENAME, mode='w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['Categoría', 'Alimento', 'Calorías', 'Proteínas', 'Grasa', 'Carbohidratos', 'Fibra', 'Colesterol'])
        print(f"📁 Archivo CSV creado: {CSV_FILENAME}")

def cargar_alimentos_existentes():
    existentes = set()
    if os.path.exists(CSV_FILENAME):
        with open(CSV_FILENAME, mode='r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                existentes.add(row['Alimento'].strip().lower())
    return existentes

def agregar_a_csv(fila):
    with open(CSV_FILENAME, mode='a', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow([
            fila['categoria'],
            fila['alimento'],
            fila['kcal'],
            fila['prot'],
            fila['fat'],
            fila['carbs'],
            fila['fiber'],
            fila['chol']
        ])

def procesar_categoria(driver, cat_id, alimentos_existentes):
    cabecera_xpath = f'//*[@id="{cat_id}"]/div[1]'
    cuerpo_xpath = f'//*[@id="{cat_id}"]/div[2]'
    prev_input = None

    try:
        cabecera = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, cabecera_xpath))
        )
        scroll_hasta_elemento(driver, cabecera)
        categoria_nombre = cabecera.text.strip()
        print(f"\n🟢 Procesando categoría: {categoria_nombre}")
        cabecera.click()
        time.sleep(1)

        cuerpo = driver.find_element(By.XPATH, cuerpo_xpath)
        alimentos = cuerpo.find_elements(By.CLASS_NAME, 'alimento')

        for alimento in alimentos:
            try:
                label = alimento.find_element(By.TAG_NAME, 'label')
                input_elem = alimento.find_element(By.TAG_NAME, 'input')
                nombre_alimento = label.text.strip()

                if nombre_alimento.lower() in alimentos_existentes:
                    print(f"⏩ Ya registrado: {nombre_alimento} (se omite)")
                    continue

                if prev_input:
                    poner_gramos(prev_input, 0)
                    time.sleep(1)

                poner_gramos(input_elem, 100)
                time.sleep(1.5)
                valores = get_values(driver)

                print(f"🍽 Alimento: {nombre_alimento}")
                print(f"    🔥 kcal:  {valores['kcal']}     💪 prot:  {valores['prot']}     🧈 grasa: {valores['fat']}")
                print(f"    🍞 carb:  {valores['carbs']}    🥦 fibra: {valores['fiber']}    ❤️ col:   {valores['chol']}")


                fila = {
                    'categoria': categoria_nombre,
                    'alimento': nombre_alimento,
                    **valores
                }

                agregar_a_csv(fila)
                alimentos_existentes.add(nombre_alimento.lower())  # Actualizar el set para evitar duplicados
                prev_input = input_elem

            except Exception as e:
                print(f"❌ Error con alimento: {e}")
                continue

        if prev_input:
            poner_gramos(prev_input, 0)
            time.sleep(1)

        cabecera.click()
        time.sleep(0.5)

    except Exception as e:
        print(f"❌ Error en categoría {cat_id}: {e}")

def main():
    inicializar_csv()
    alimentos_existentes = cargar_alimentos_existentes()
    driver = setup_driver()

    for cat_id in CATEGORIA_IDS:
        procesar_categoria(driver, cat_id, alimentos_existentes)

    driver.quit()
    print("\n✅ Scraping completado. Datos actualizados en alimentos.csv")

if __name__ == "__main__":
    main()
