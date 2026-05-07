from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException, StaleElementReferenceException
from selenium.webdriver.chrome.service import Service
import time
from calendar import monthrange
import locale

def scrap():
    email = "corozcov@emeal.nttdata.com"
    password = "NR9Xq47KsQqQ!"
    emailXpath = '//*[@autocomplete="username"]'

    moreXpath = "//span[contains(text(),'More') and @class='dropdown-text']"
    logWorkXpath = "//span[contains(text(),'Log work') and @class='trigger-label']"
    timeSpentXpath = '//*[@id="log-work-form-time-logged"]'
    dateStartedXpath = '//*[@id="log-work-form-date-logged-date-picker"]'
    commentXpath = '//body[@id="tinymce"]'
    submitXpath = '//button[@id="log-work-form-submit"]'
    cancelXpath = '//a[@id="log-work-cancel"]'
    iframeXpath = '//iframe[@class="tox-edit-area__iframe"]'
    successXpath = "//div[contains(@class, 'aui-message-success')]"
    

    options = Options()
    options.add_argument("--disable-notifications")
    options.add_argument("--disable-infobars")
    options.add_argument("--disable-popup-blocking")
    options.add_argument("--disable-extensions")
    options.add_argument("--disable-gpu")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--no-sandbox")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--start-maximized")
    options.add_argument("--log-level=3")
    options.add_argument("--ignore-certificate-errors")
    options.add_argument("--ignore-ssl-errors")
    options.add_argument("--allow-insecure-localhost")
    options.add_argument("--remote-debugging-port=9222")

    # Mantener cuenta de Google abierta
    options.add_argument("user-data-dir=Users/calicheorozco/Library/Application Support/Google/Chrome/Default")
    # /Users/calicheorozco/CDriver/chromedriver
    service = Service('/Users/calicheorozco/CDriver/chromedriver')
    driver = webdriver.Chrome(service=service, options=options)
    link = 'https://umane.emeal.nttdata.com/jiraito/projects/BATENARIS/issues'
    ##https://umane.emeal.nttdata.com/jiraito/browse/BATENARIS-576
    # ABRIR EL LINK
    driver.get(link)

    # obtener el mes actual y el siguiente
    locale.setlocale(locale.LC_TIME, "en_US.UTF-8")  # Asegura nombres de meses en inglés

    meses = []
    year = int(time.strftime("%Y"))
    mes_actual = int(time.strftime("%m"))
    meses.append((mes_actual, year))
    if mes_actual == 12:
        meses.append((1, year + 1))
    else:
        meses.append((mes_actual + 1, year))

    dias_laborables = []
    for mes_num, anio in meses:
        mes_nombre = time.strftime("%B", time.strptime(str(mes_num), "%m"))
        dias_en_mes = monthrange(anio, mes_num)[1]
        for i in range(1, dias_en_mes + 1):
            try:
                dia_nombre = time.strftime("%A", time.strptime(f"{anio} {mes_nombre} {i}", "%Y %B %d"))
                if dia_nombre in ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]:
                    dias_laborables.append((i, mes_num, anio, mes_nombre))
            except Exception as e:
                print("No se pudo obtener los dias laborables")
                print(f"Error: {e}")
                break
    # dias festivos, vacacioness
    dias_excepciones = []
    # Filtrar días excepcionales si es necesario
    dias_laborables = [dia for dia in dias_laborables if dia[0] not in dias_excepciones]
    print(f"Dias laborables: {dias_laborables}")

    try:
        WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.XPATH, emailXpath)))
        driver.find_element(By.XPATH, emailXpath).send_keys(u'\ue007')
        print("Se ingresó el email")
        input("Inicia sesión, luego regresa y presiona enter para continuar")
        print("Iniciando script..")
        time.sleep(2)
    except TimeoutException:
        print("Ya está la sesión iniciada")

    for dia, mes_num, anio, mes_nombre in dias_laborables:
        intento = 0  # Contador de intentos
        while True:  # Repetir hasta que se procese el día correctamente
            try:
                intento += 1
                print(f"Intentando procesar el día {dia}/{mes_num}/{anio} (Intento {intento})")
                
                # Esperar y hacer clic en el botón 'More'
                more_button = WebDriverWait(driver, 5).until(
                    EC.element_to_be_clickable((By.XPATH, moreXpath))
                )
                more_button.click()

                # Esperar y hacer clic en 'Log work'
                log_work_button = WebDriverWait(driver, 30).until(
                    EC.element_to_be_clickable((By.XPATH, logWorkXpath))
                )
                log_work_button.click()

                # Llenar el formulario
                WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.XPATH, timeSpentXpath)))
                driver.find_element(By.XPATH, timeSpentXpath).send_keys("8h")
                driver.find_element(By.XPATH, dateStartedXpath).clear()
                mes_abrev = time.strftime("%b", time.strptime(str(mes_num), "%m"))
                driver.find_element(By.XPATH, dateStartedXpath).send_keys(f"{dia:02d}/{mes_abrev}/{anio} 09:00 AM")
                print(f"Se ingresó la fecha {dia:02d}/{mes_num}/{anio} 09:00 AM")

                try:
                    # Manejar el iframe de comentarios
                    iframe = WebDriverWait(driver, 30).until(
                        EC.presence_of_element_located((By.XPATH, iframeXpath))
                    )
                    driver.switch_to.frame(iframe)

                    comments = WebDriverWait(driver, 30).until(
                        EC.presence_of_element_located((By.XPATH, commentXpath))
                    )
                    comments.click()
                    time.sleep(1)
                    comments.send_keys("Customer activities \n User support \n Data migration")
                    print("Se ingresó el comentario")

                    driver.switch_to.default_content()

                except NoSuchElementException:
                    print("No se encontró el elemento de comentarios")

                # Enviar el formulario
                submit_button = WebDriverWait(driver, 30).until(
                    EC.element_to_be_clickable((By.XPATH, submitXpath))
                )
                submit_button.click()
                print(f"Se registró el día {dia}/{mes_num}/{anio}")
                
                # validar que timeSpentXpath haya desaparecido
                WebDriverWait(driver, 30).until_not(
                    EC.presence_of_element_located((By.XPATH, timeSpentXpath))
                )
                # validar que el mensaje de éxito aparezca y luego ya no sea clickable
                WebDriverWait(driver, 30).until(
                    EC.presence_of_element_located((By.XPATH, successXpath))
                )
                WebDriverWait(driver, 30).until_not(
                    EC.element_to_be_clickable((By.XPATH, successXpath))
                )

                
                # esperar 3 segundos
                time.sleep(3)

                # Si es el último día, espera adicionalmente para asegurarte de que se registre correctamente
                if (dia, mes_num, anio, mes_nombre) == dias_laborables[-1]:
                    print("Esperando extra para el último día registrado")
                    time.sleep(5)  # Espera de 5 segundos adicionales en el último día
                    

                # Esperar a que la página se actualice antes de la siguiente iteración

                # Si se procesa correctamente, rompe el ciclo `while`
                break

            except (TimeoutException, StaleElementReferenceException) as e:
                print(f"Error al procesar el día {dia}/{mes_num}/{anio}: {e}")
                if intento >= 10:  # Limitar a 3 intentos para evitar un bucle infinito
                    print(f"No se pudo procesar el día {dia}/{mes_num}/{anio} después de {intento} intentos. Pasando al siguiente día.")
                    break
                print("Reintentando con el mismo día...")

    print("Se terminó de registrar las horas de trabajo exitosamente")
    input("Presiona enter para cerrar el navegador")
    driver.quit()


if __name__ == "__main__":
    scrap()
