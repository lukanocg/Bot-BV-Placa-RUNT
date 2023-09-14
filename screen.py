from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
from time import sleep
import pytesseract

import cv2
import numpy as np

def btnCancelar():
    wait_modal = WebDriverWait(driver, 30)
    element_btn_message = wait_modal.until(EC.visibility_of_element_located((By.XPATH, '//*[@id="dlgConsulta"]/div/div/div[2]/div/button')))
    element_btn_message.click()

if __name__ == "__main__":
    # Variables Seleccionadas
    op_sel_1 = ["NACIONAL", "EXTRANJERO", "DIPLOMATICO"]
    op_sel_2 = ["Placa y Propietario", "VIN (Número único de identificación)", "SOAT", "PVO (Planilla de viaje ocasional)", "Guía de movilidad", "RTM"]
    op_sel_2_1 = ["Placa", "VIN (Número único de identificación)", "SOAT", "PVO (Planilla de viaje ocasional)", "RTM"]
    op_sel_3 = ["Carnet Diplomático", "Cédula Ciudadania", "Cédula de Extranjería", "NIT", "Pasaporte", "Registro Civil", "Tarjeta de Identidad"]
    
    # Variables Mensajes
    error_modal_vacio = "Por favor verifique el valor ingresado en los campos resaltados en rojo."
    error_modal_invalido = "La imagen no coincide con el valor ingresado, por favor verifiquela e intente nuevamente."

    # Ruta del sw OCR
    pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
    # Parametrizar el navegador web
    service = Service(executable_path=r'C:\Program Files\Google\Chrome\Application\chromedriver.exe')
    driver = webdriver.Chrome(service=service)
    # Enlace
    url = 'https://www.runt.com.co/consultaCiudadana/#/consultaVehiculo'
    driver.get(url)
    sleep(1)

    # Identificar y llenar input
    wait_input = WebDriverWait(driver, 10)

    # Select Procedencia
    op_select_1 = Select(driver.find_element(By.XPATH, '/html/body/div[1]/div/div[1]/div[2]/div[1]/div[2]/div[1]/div[2]/div[2]/div/div/div[1]/div[2]/div/select'))
    op_select_1.select_by_visible_text(op_sel_1[0])
    # Select Consulta por
    op_select_2 = Select(driver.find_element(By.XPATH, '//*[@id="tipoConsulta"]'))
    op_select_2.select_by_visible_text(op_sel_2[0])
    # Input Nro Placa
    element_noplaca = wait_input.until(EC.presence_of_element_located((By.XPATH, '//*[@id="noPlaca"]')))
    element_noplaca.send_keys("KVX878")
    # Select Tipo de documento
    op_select_3 = Select(driver.find_element(By.XPATH, '/html/body/div[1]/div/div[1]/div[2]/div[1]/div[2]/div[1]/div[3]/div[2]/div/div/form/div[4]/div/select'))
    op_select_3.select_by_visible_text(op_sel_3[1])
    # Input Nro dpocumento
    element_nodocumento = wait_input.until(EC.presence_of_element_located((By.NAME, 'noDocumento')))
    element_nodocumento.send_keys("1099213631")

    # Identificar imagen captcha y tomar screenshot
    image_element = wait_input.until(EC.presence_of_element_located((By.ID, 'imgCaptcha')))
    image_element.screenshot('screenshot.png')

    # Procesar imagen
    image = cv2.imread("C:/laragon/www/screenshot.png")
    image = cv2.blur(image, (2, 2))
    ret, image = cv2.threshold(image, 15, 245, cv2.THRESH_BINARY)
    image = cv2.dilate(image, np.ones((3, 3), np.uint8))
    image = cv2.erode(image, np.ones((2, 2), np.uint8))
    filename = 'saved.png'
    cv2.imwrite(filename, image)
    cv2.waitKey(0)

    # Extraer texto de imagen procesada
    extracted_text = pytesseract.image_to_string('C:\laragon\www\saved.png')
    
    # Identificar input del captcha y llenar
    element_txtcaptcha= wait_input.until(EC.presence_of_element_located((By.ID, 'captchatxt')))
    element_txtcaptcha.send_keys(extracted_text.strip())
    print(extracted_text.strip())

    # Identificar boton para hacer consulta
    element_btn = wait_input.until(EC.visibility_of_element_located((By.XPATH, '/html/body/div[1]/div/div[1]/div[2]/div[1]/div[2]/div[1]/div[3]/div[2]/div/div/form/div[9]/button')))
    element_btn.click()

    try :
        wait_resultado = WebDriverWait(driver, 30)
        #element_resultado = wait_resultado.until(EC.visibility_of_element_located((By.XPATH, '/html/body/div[1]/#div/div[1]/div[2]/div[1]/div[2]/div[1]/div[1]/div/div[1]/h2')))
        element_resultado = driver.find_element(By.XPATH, '/html/body/div[1]/div/div[1]/div[2]/div[1]/div[2]/div[1]/div[1]/div/div[1]/h2')
    except NoSuchElementException:
        print("false")
    print("true")

    
    
    #try:
    #    wait_resultado = WebDriverWait(driver, 30)
    #    element_resultado = wait_resultado.until(EC.visibility_of_element_located((By.XPATH, '/html/body/div[1]/#div/div[1]/div[2]/div[1]/div[2]/div[1]/div[1]/div/div[1]/h2')))
    #        
    #    span_text_resultado = element_resultado.text
    #    if span_text_resultado == "Consulta Automotores":
    #        print("a")
    #    elif span_text_resultado != "Consulta Automotores":
    #        print("b")
    #except :
    #    # En caso de error, controlar mensaje de modal
    #    wait_modal = WebDriverWait(driver, 30)
    #    element_message = wait_modal.until(EC.visibility_of_element_located((By.XPATH, '//*[@id="msgConsulta"]')))
    #    span_text = element_message.text
    #    # Validar texto y en caso de error ejecutarlo de nuevo
    #    if span_text == error_modal_vacio :
    #        print("vacio")
    #        btnCancelar()
    #    elif span_text == error_modal_invalido:
    #        print("no valido")
    #        btnCancelar()            
    #    elif span_text != error_modal_vacio or span_text != error_modal_invalido:
    #        print("OK")
        
    driver.quit()