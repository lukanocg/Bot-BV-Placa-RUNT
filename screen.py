from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
from time import sleep
import pytesseract
import requests
from bs4 import BeautifulSoup
import json
import time, sys
from datetime import datetime

import cv2
import numpy as np

from clsConfig import clsConfig
from clsApi import clsApi

class screen:
    
    def __init__( self ):
        self.app_config = clsConfig()
        self.app_api    = clsApi()
        self.log        = self.app_config.fnIncializarLog()

    global wRutaApi
    wRutaApi = "http://10.164.17.160:8081/api/BusquedaRadicacion/ListadoPlacaBusquedaVehicularRunt"

    def fnEjecutarApiPost(pFuncionApi, pDataPost, pRetornarJson = True ):
            """Ejecutamos el request metodo POST"""
            try:
                data = requests.post(url = (wRutaApi+pFuncionApi), data = pDataPost, headers= {'Content-Type': 'application/json;  charset=utf-8'})
                if pRetornarJson:
                    return data.json()
                #fin if
                return {'success': True, 'message' : "Se ejecutó exitosamente" }
            except requests.HTTPError as e:
                return {'success': False, 'message' : e }
            #fin try
        #fnEjecutarApiPost
        
    def btnCancelar():
        wait_modal = WebDriverWait(driver, 30)
        element_btn_message = wait_modal.until(EC.visibility_of_element_located((By.XPATH, '//*[@id="dlgConsulta"]/div/div/div[2]/div/button')))
        element_btn_message.click()

    if __name__ == "__main__":
        app_api    = clsApi()
        # Variables Seleccionadas
        op_sel_1 = ["NACIONAL", "EXTRANJERO", "DIPLOMATICO"]
        op_sel_2 = ["Placa y Propietario", "VIN (Número único de identificación)", "SOAT", "PVO (Planilla de viaje ocasional)", "Guía de movilidad", "RTM"]
        op_sel_2_1 = ["Placa", "VIN (Número único de identificación)", "SOAT", "PVO (Planilla de viaje ocasional)", "RTM"]
        op_sel_3 = ["Carnet Diplomático", "Cédula Ciudadania", "Cédula de Extranjería", "NIT", "Pasaporte", "Registro Civil", "Tarjeta de Identidad"]
        
        # Variables Mensajes
        error_modal_vacio = "Por favor verifique el valor ingresado en los campos resaltados en rojo."
        error_modal_invalido = "La imagen no coincide con el valor ingresado, por favor verifiquela e intente nuevamente."
        texto_resultado = "No se encontró información registrada en el RUNT."

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
        wait_input = WebDriverWait(driver, 5)

        datEnviar = '{}'
        returned_data = fnEjecutarApiPost("", datEnviar.encode('utf-8'))
        #print(returned_data)
        
        # Opening JSON file
        #f = open('data.json')
        # returns JSON object as
        # a dictionary
        with open('data.json', encoding='utf-8') as fh:
            data = json.load(fh)

        for x in data['Data']:
            id = x['Id']
            tipo_documento = x['TipoDocumento']
            nro_documento = x['NroDocumento']
            placa = x['Placa']
            
            # Select Procedencia
            op_select_1 = Select(driver.find_element(By.XPATH, '/html/body/div[1]/div/div[1]/div[2]/div[1]/div[2]/div[1]/div[2]/div[2]/div/div/div[1]/div[2]/div/select'))
            op_select_1.select_by_visible_text(op_sel_1[0])
            # Select Consulta por
            op_select_2 = Select(driver.find_element(By.XPATH, '//*[@id="tipoConsulta"]'))
            op_select_2.select_by_visible_text(op_sel_2[0])
            # Input Nro Placa
            element_noplaca = wait_input.until(EC.presence_of_element_located((By.XPATH, '//*[@id="noPlaca"]')))
            element_noplaca.send_keys(placa)
            # Select Tipo de documento
            op_select_3 = Select(driver.find_element(By.XPATH, '/html/body/div[1]/div/div[1]/div[2]/div[1]/div[2]/div[1]/div[3]/div[2]/div/div/form/div[4]/div/select'))
            op_select_3.select_by_visible_text(tipo_documento)
            # Input Nro dpocumento
            element_nodocumento = wait_input.until(EC.presence_of_element_located((By.NAME, 'noDocumento')))
            element_nodocumento.send_keys(nro_documento)
        
            # Identificar imagen captcha y tomar screenshot
            image_element = wait_input.until(EC.presence_of_element_located((By.ID, 'imgCaptcha')))
            image_element.screenshot('screenshot'+nro_documento+'.png')
        
            # Procesar imagen
            image = cv2.imread("C:/laragon/www/screenshot"+nro_documento+".png")
            image = cv2.blur(image, (2, 2))
            ret, image = cv2.threshold(image, 15, 245, cv2.THRESH_BINARY)
            image = cv2.dilate(image, np.ones((3, 3), np.uint8))
            image = cv2.erode(image, np.ones((2, 2), np.uint8))
            filename = 'saved'+nro_documento+'.png'
            cv2.imwrite(filename, image)
            cv2.waitKey(0)
                        
            # Extraer texto de imagen procesada
            extracted_text = pytesseract.image_to_string('C:\laragon\www\saved'+nro_documento+'.png')
            
            # Identificar input del captcha y llenar
            element_txtcaptcha= wait_input.until(EC.presence_of_element_located((By.ID, 'captchatxt')))
            element_txtcaptcha.send_keys(extracted_text.strip())
            print(extracted_text.strip())
        
            # Identificar boton para hacer consulta
            element_btn = wait_input.until(EC.visibility_of_element_located((By.XPATH, '/html/body/div[1]/div/div[1]/div[2]/div[1]/div[2]/div[1]/div[3]/div[2]/div/div/form/div[9]/button')))
            element_btn.click()
            
            #Scrapping
            #element_to_scroll_to = driver.find_element(By.XPATH, '/html/body/div[1]/div/div[1]/div[2]/div[1]/div[2]/#div[1]/div[6]/div[1]/h4')
            #driver.execute_script("arguments[0].scrollIntoView();", element_to_scroll_to)

            wait_resultado = WebDriverWait(driver, 3)
            element_resultado = wait_resultado.until(EC.presence_of_element_located((By.XPATH, '/html/body/div[1]/div/div[1]/div[2]/div[1]/div[2]/div[1]/div[1]/div/div[1]/h2')))
            span_text_resultado = element_resultado.text
            
            # 01 columna
            element_marca = wait_resultado.until(EC.presence_of_element_located((By.XPATH, '/html/body/div[1]/div/div[1]/div[2]/div[1]/div[2]/div[1]/div[6]/div[2]/div/div/div/div[1]/div[2]')))
            text_marca = element_marca.text
            print(text_marca)
            
            element_modelo = wait_resultado.until(EC.presence_of_element_located((By.XPATH, '/html/body/div[1]/div/div[1]/div[2]/div[1]/div[2]/div[1]/div[6]/div[2]/div/div/div/div[2]/div[2]')))
            text_modelo = element_modelo.text
                    
            element_nro_serie = wait_resultado.until(EC.presence_of_element_located((By.XPATH, '/html/body/div[1]/div/div[1]/div[2]/div[1]/div[2]/div[1]/div[6]/div[2]/div/div/div/div[3]/div[2]')))
            text_nro_serie = element_nro_serie.text
            
            element_nro_chasis = wait_resultado.until(EC.presence_of_element_located((By.XPATH, '/html/body/div[1]/div/div[1]/div[2]/div[1]/div[2]/div[1]/div[6]/div[2]/div/div/div/div[4]/div[2]')))
            text_nro_chasis = element_nro_chasis.text
            
            element_cilindraje = wait_resultado.until(EC.presence_of_element_located((By.XPATH, '/html/body/div[1]/div/div[1]/div[2]/div[1]/div[2]/div[1]/div[6]/div[2]/div/div/div/div[5]/div[2]')))
            text_cilindraje = element_cilindraje.text
            
            element_tipo_combustible = wait_resultado.until(EC.presence_of_element_located((By.XPATH, '/html/body/div[1]/div/div[1]/div[2]/div[1]/div[2]/div[1]/div[6]/div[2]/div/div/div/div[6]/div[2]')))
            text_tipo_combustible = element_tipo_combustible.text
            
            element_autoridad_transito = wait_resultado.until(EC.presence_of_element_located((By.XPATH, '/html/body/div[1]/div/div[1]/div[2]/div[1]/div[2]/div[1]/div[6]/div[2]/div/div/div/div[7]/div[2]')))
            text_autoridad_transito = element_autoridad_transito.text
            
            element_clasico_antiguo = wait_resultado.until(EC.presence_of_element_located((By.XPATH, '/html/body/div[1]/div/div[1]/div[2]/div[1]/div[2]/div[1]/div[6]/div[2]/div/div/div/div[8]/div[2]')))
            text_clasico_antiguo = element_clasico_antiguo.text
                    
            # 02 columna
            element_linea = wait_resultado.until(EC.presence_of_element_located((By.XPATH, '/html/body/div[1]/div/div[1]/div[2]/div[1]/div[2]/div[1]/div[6]/div[2]/div/div/div/div[1]/div[4]')))
            text_linea = element_linea.text
            
            element_color = wait_resultado.until(EC.presence_of_element_located((By.XPATH, '/html/body/div[1]/div/div[1]/div[2]/div[1]/div[2]/div[1]/div[6]/div[2]/div/div/div/div[2]/div[4]')))
            text_color = element_color.text
            
            element_nro_motor = wait_resultado.until(EC.presence_of_element_located((By.XPATH, '/html/body/div[1]/div/div[1]/div[2]/div[1]/div[2]/div[1]/div[6]/div[2]/div/div/div/div[3]/div[4]')))
            text_nro_motor = element_nro_motor.text
            
            element_nro_vin = wait_resultado.until(EC.presence_of_element_located((By.XPATH, '/html/body/div[1]/div/div[1]/div[2]/div[1]/div[2]/div[1]/div[6]/div[2]/div/div/div/div[4]/div[4]')))
            text_nro_vin = element_nro_vin.text
            
            element_tipo_carroceria = wait_resultado.until(EC.presence_of_element_located((By.XPATH, '/html/body/div[1]/div/div[1]/div[2]/div[1]/div[2]/div[1]/div[6]/div[2]/div/div/div/div[5]/div[4]')))
            text_tipo_carroceria = element_tipo_carroceria.text
            
            element_fecha_matricula_inicial = wait_resultado.until(EC.presence_of_element_located((By.XPATH, '/html/body/div[1]/div/div[1]/div[2]/div[1]/div[2]/div[1]/div[6]/div[2]/div/div/div/div[6]/div[4]')))
            text_fecha_matricula_inicial = element_fecha_matricula_inicial.text
            
            element_gravamenes_propiedad = wait_resultado.until(EC.presence_of_element_located((By.XPATH, '/html/body/div[1]/div/div[1]/div[2]/div[1]/div[2]/div[1]/div[6]/div[2]/div/div/div/div[7]/div[4]')))
            text_gravamenes_propiedad = element_gravamenes_propiedad.text
            
            element_repotenciado = wait_resultado.until(EC.presence_of_element_located((By.XPATH, '/html/body/div[1]/div/div[1]/div[2]/div[1]/div[2]/div[1]/div[6]/div[2]/div/div/div/div[8]/div[4]')))
            text_repotenciado = element_repotenciado.text
            
            ##Datos de Informacion General del Vehiculo
            #data_informacion_general_vehiculo = []
            #data_informacion_general_vehiculo.append({'Id': id, 'Marca': text_marca, 'Modelo': #text_modelo, 'NroSerie': text_nro_serie, 'NroChasis': text_nro_chasis, 'Cilindraje': #text_cilindraje, 'TipoCombustible': text_tipo_combustible, 'AutoridadTransito': #text_autoridad_transito, 'ClasicoAntiguo': text_clasico_antiguo, 'Linea': text_linea, 'Color': #text_color, 'NroMotor': text_nro_motor, 'NroVin': text_nro_vin, 'TipoCarroceria': #text_tipo_carroceria, 'FecMatriculaInicial': text_fecha_matricula_inicial, #'GravemenesPropiedad': text_gravamenes_propiedad, 'Repotenciado': text_repotenciado })
            #
            ## Convert the extracted data to JSON
            #json_informacion_general_vehiculo = json.dumps(data_informacion_general_vehiculo, indent=4)
            ## Print or save the JSON data
            #print(json_informacion_general_vehiculo)
            
            #API Registrar Datos Placa Busqueda Vehicular
            # Define the format of the input date string
            input_format = "%d/%m/%Y"

            # Parse the input date string into a datetime object
            date_object = datetime.strptime(text_fecha_matricula_inicial, input_format)

            # Define the desired output format
            output_format = "%Y-%m-%d %H:%M:%S"

            # Format the datetime object as a string in the desired output format
            formatted_text_fecha_matricula_inicial = date_object.strftime(output_format)

            wContador     = 0 
            wMsjError, wContador = app_api.fnRegistrarDatosPlacaBusquedaVehicular(wContador, id, nro_documento, placa, text_marca, text_modelo, text_nro_serie, text_nro_chasis, text_cilindraje, text_tipo_combustible, text_autoridad_transito, text_clasico_antiguo, text_linea, text_color, text_nro_motor, text_nro_vin, text_tipo_carroceria, formatted_text_fecha_matricula_inicial, text_gravamenes_propiedad, text_repotenciado )    
            
            #Limitaciones a la propiedad
            element_limitaciones = wait_resultado.until(EC.presence_of_element_located((By.XPATH, '/html/body/div[1]/div/div[1]/div[2]/div[1]/div[2]/div[16]/div[1]/h4')))
            driver.execute_script("arguments[0].scrollIntoView();", element_limitaciones)
            element_limitaciones.click()
            
            element_limitaciones_mensaje = wait_resultado.until(EC.presence_of_element_located((By.XPATH, '/html/body/div[1]/div/div[1]/div[2]/div[1]/div[2]/div[16]/div[2]/div/div/div/div')))
            text_limitaciones_mensaje = element_limitaciones_mensaje.text
            
            if( text_limitaciones_mensaje == texto_resultado ):
                print(text_limitaciones_mensaje)
            else:
                element_limitaciones_tabla = wait_resultado.until(EC.presence_of_element_located((By.XPATH, '/html/body/div[1]/div/div[1]/div[2]/div[1]/div[2]/div[16]/div[2]/div/div/div/table')))
                html_table_limitaciones = element_limitaciones_tabla.get_attribute("outerHTML")
                # Parse the HTML using BeautifulSoup
                soup_limitaciones = BeautifulSoup(html_table_limitaciones, 'html.parser')

                # Find the table and iterate through its rows to extract data
                table_limitaciones = soup_limitaciones.find('table')
                data_limitaciones = []
                for row in table_limitaciones.find_all('tr')[1:]:  # Skip the header row
                    columns = row.find_all('td')
                    tipo_limitacion = columns[0].get_text()
                    nro_oficio = columns[1].get_text()
                    entidad_juridica = columns[2].get_text()
                    departamento = columns[3].get_text()
                    municipio = columns[4].get_text()
                    fecha_expedicion_oficio = columns[5].get_text()
                    fecha_registro_sistema = columns[6].get_text()
                    data_limitaciones.append({'identificacion_acreedor': identificacion_acreedor, 'acreedor': acreedor, 'fecha_inscripcion': fecha_inscripcion, 'patrimonio_autonomo': patrimonio_autonomo, 'confecamaras': confecamaras })
                    
                    # Convert the extracted data to JSON
                    json_data_limitaciones = json.dumps(data_limitaciones, indent=4)

                    # Print or save the JSON data
                    print(json_data_limitaciones)
                    
                    # Define the format of the input date string
                    input_format = "%d/%m/%Y"

                    # Parse the input date string into a datetime object
                    date_object = datetime.strptime(fecha_expedicion_oficio, input_format)

                    # Define the desired output format
                    output_format = "%Y-%m-%d %H:%M:%S"

                    # Format the datetime object as a string in the desired output format
                    formatted_text_fecha_expedicion_oficio = date_object.strftime(output_format)
                    
                    # Define the format of the input date string
                    input_format = "%d/%m/%Y"

                    # Parse the input date string into a datetime object
                    date_object = datetime.strptime(fecha_registro_sistema, input_format)

                    # Define the desired output format
                    output_format = "%Y-%m-%d %H:%M:%S"

                    # Format the datetime object as a string in the desired output format
                    formatted_text_fecha_registro_sistema = date_object.strftime(output_format)
                    
                    wContador     = 0 
                    wMsjError, wContador = app_api.fnRegistrarLimitacionPropiedadBusquedaVehicular(wContador, id, nro_documento, placa, tipo_limitacion, nro_oficio, entidad_juridica, departamento, municipio, formatted_text_fecha_expedicion_oficio, formatted_text_fecha_registro_sistema )
        
            # Garantias a favor de
            element_garantias = wait_resultado.until(EC.presence_of_element_located((By.XPATH, '/html/body/div[1]/div/div[1]/div[2]/div[1]/div[2]/div[18]/div[1]/h4')))
            driver.execute_script("arguments[0].scrollIntoView();", element_garantias)
            element_garantias.click()
            
            element_garantias_mensaje = wait_resultado.until(EC.presence_of_element_located((By.XPATH, '/html/body/div[1]/div/div[1]/div[2]/div[1]/div[2]/div[18]/div[2]/div/div/div/div')))
            text_garantias_mensaje = element_garantias_mensaje.text
            if( text_garantias_mensaje == texto_resultado ):
                print(text_garantias_mensaje)
            else:
                element_garantias_tabla = wait_resultado.until(EC.presence_of_element_located((By.XPATH, '/html/body/div[1]/div/div[1]/div[2]/div[1]/div[2]/div[18]/div[2]/div/div/div/table')))
                html_table_garantias = element_garantias_tabla.get_attribute("outerHTML")
                # Parse the HTML using BeautifulSoup
                soup_garantias = BeautifulSoup(html_table_garantias, 'html.parser')

                # Find the table and iterate through its rows to extract data
                table_garantias = soup_garantias.find('table')
                data_garantias = []
                for row in table_garantias.find_all('tr')[1:]:  # Skip the header row
                    columns = row.find_all('td')
                    identificacion_acreedor = columns[0].get_text()
                    acreedor = columns[1].get_text()
                    fecha_inscripcion = columns[2].get_text()
                    patrimonio_autonomo = columns[3].get_text()
                    confecamaras = columns[4].get_text()
                    data_garantias.append({'identificacion_acreedor': identificacion_acreedor, 'acreedor': acreedor, 'fecha_inscripcion': fecha_inscripcion, 'patrimonio_autonomo': patrimonio_autonomo, 'confecamaras': confecamaras })
                    
                    # Convert the extracted data to JSON
                    json_data_garantias = json.dumps(data_garantias, indent=4)

                    # Print or save the JSON data
                    print(json_data_garantias)
                    
                    # Define the format of the input date string
                    input_format = "%d/%m/%Y"

                    # Parse the input date string into a datetime object
                    date_object = datetime.strptime(fecha_inscripcion, input_format)

                    # Define the desired output format
                    output_format = "%Y-%m-%d %H:%M:%S"

                    # Format the datetime object as a string in the desired output format
                    formatted_text_fecha_inscripcion = date_object.strftime(output_format)
                    
                    wContador     = 0 
                    wMsjError, wContador = app_api.fnRegistrarGarantiasFavorDeBusquedaVehicular(wContador, id, nro_documento, placa, identificacion_acreedor, acreedor, formatted_text_fecha_inscripcion, patrimonio_autonomo, confecamaras )
                            
            
            # Wait for some time to let the page load or scroll further if needed
            time.sleep(2)  # Adjust the time as needed

            # Scrape data from the element
            #scraped_data = element_to_scroll_to.text

            #html_table = element_to_scroll_to.get_attribute("outerHTML")
        #Fin del For

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