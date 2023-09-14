from clsConfig import clsConfig
from clsApi import clsApi
from selenium.webdriver.common.by import By  
from selenium.webdriver.support.ui import WebDriverWait 
from selenium.webdriver.support import expected_conditions as ec  
from selenium.common.exceptions import WebDriverException
from urllib3.exceptions import NewConnectionError
import time, sys

class clsScraping:
    def __init__( self ):
        self.app_config = clsConfig()
        self.app_api    = clsApi()
        self.log        = self.app_config.fnIncializarLog()
    #fin if
        
    def fnAutenticacion( self, wt, usuario, clave ):
        wt.until(ec.presence_of_element_located((By.XPATH,'//*[@id="formLogin:inpUserLogin"]'))).send_keys(usuario)
        wt.until(ec.presence_of_element_located((By.XPATH,'//*[@id="formLogin:inpPassLogin"]'))).send_keys(clave)
    #fnAutenticacion
    
    def fnIniciarSession( self, dv, wt, cedula, objDatosUsuarios, wDatUsuario ):
        try:
            wMsjError = ""
            self.app_config.fnImprimir(f"{cedula} - Proceso de Inicio de Sesion.",5)
            # Seleccionando Iniciar Sesión
            wt.until(ec.presence_of_element_located((By.XPATH,'/html/body/header/div[1]/div/table/tbody/tr/td[2]/table/tbody/tr/td[1]/button'))).click()
            time.sleep(2)
            
            
            if len(wDatUsuario) == 0:
                wMsjError = "No se encuentró Usuarios activos."
            else:
                if wDatUsuario['Activo'] == False:
                    objDatosUsuarios = [ dato  for dato in objDatosUsuarios  if dato['Activo'] == True and  dato['Id'] != wDatUsuario['Id']]
                    wDatUsuario = objDatosUsuarios[0] if len( objDatosUsuarios ) > 0 else {}
                    #fin if
                #fin if
                
                if len(wDatUsuario) == 0:
                    wMsjError = "No se encuentró Usuarios activos." 
                else: 
                    # Logeo
                    self.fnAutenticacion( wt, wDatUsuario['Usuario'], wDatUsuario['Clave'] ) 
                
                    if dv.find_element(By.XPATH, '//*[@id="formLogin:inpUserLogin"]').get_attribute('value') == '':
                        self.fnAutenticacion( wt, wDatUsuario['Usuario'], wDatUsuario['Clave'] )             
                    #fin if 
                    
                    wt.until(ec.presence_of_element_located((By.XPATH,'//*[@id="formLogin:btnIngresarLogin"]'))).click()
                    time.sleep(2)
                #fin if
            #fin if 
        
        except NewConnectionError as e:
            wMsjError = "Error de conexión: " + str(e)        
        except WebDriverException as e:
            wMsjError =  e
        except:
            wMsjError =  str( sys.exc_info()[1])
            pass
        finally:
            if wMsjError == "":
                wMsjValidacion = wt.until(ec.presence_of_element_located((By.XPATH,'//*[@id="modalDialog"]/div[2]/div[1]/span'))).text
                
                if len(  [ dato for dato in self.app_config.wERROR_BLOQUEAR_USUARIOS if self.app_config.wERROR_BLOQUEAR_USUARIOS[dato] == str(wMsjValidacion).strip() ]  ) > 0:
                    wDatUsuario['Activo'] = self.app_api.fnDesactivarUsuario( wDatUsuario['Id'] ) 
                    wMsjError = wMsjValidacion
                else:
                    self.app_config.fnImprimir(f"{cedula} - Ingreso correctamente.",5)
                #fin if  
                
            #fin if 
        #fin try
        
        return wMsjError, wDatUsuario
    #fnIniciarSession
    
    def fnSolicitar( self, dv, cedula ):
        # Solicitar
        self.app_config.fnImprimir(f"{cedula} - Presionando Solicitar",5)
        wTiempo, wMsjError = 1, ""
        wTiempoMaximo = 0
        wOperativo = False
        while wTiempoMaximo<=4:
            try:
                if dv.find_element(By.XPATH, '/html/body').text == self.app_config.wERROR['SISTEMA_NO_FUNCIONA']:
                    wMsjError = self.app_config.wERROR['SISTEMA_NO_FUNCIONA']
                    break
                # fin if
                
                if dv.find_element(By.XPATH,'//*[@id="timeoutSession"]/div/div/div[2]/label').text == self.app_config.wERROR['TIEMPO_EXCEDIDO']:
                    wMsjError = self.app_config.wERROR['TIEMPO_EXCEDIDO']
                    break
                #fin if  
                
                if 'display: none;' in dv.find_element(By.XPATH, '//*[@id="modalLoading"]').get_attribute('style'): 
                    wOperativo = True
                    break
                #fin if 
                
                if wTiempo == 1 or wTiempo == 30:
                    WebDriverWait(dv, 60).until(ec.presence_of_element_located((By.XPATH,'//*[@id="formQueries:j_idt42"]'))).click()
                    
                    wTiempo=0
                    wTiempoMaximo+=1
                #fin if                
            except:
                pass
            finally:
                time.sleep(1)
                wTiempo +=1
            #fin
        #fin while
        
        if not wOperativo:
            wMsjError = "Ocurrio un incoveniente con la pagina, no se pudo presionar el btn [Solicitar]."
        #fin if 
        
        return wMsjError 
    #fnSolicitar
    
    def fnImprimirErrorCerrarChrome( self, dv, cedula, msjError, cntesp):
        self.app_config.fnImprimir(f"{cedula} - {msjError}", cntesp)
        self.log.error(f"Cedula: {cedula} - MSJ ERROR: {msjError}")
        
        if dv != None:
            dv.quit()
        return None 
    #fnImprimirErrorCerrarChrome
    
    def fnConsultarCedula( self, dv, wt, wCedula, wDatUsuario ):
        try:
            # Variables
            wMsjError  = ''
            wTiempo    = 1
            wOperativo = False
            
            # Consultar cedula
            self.app_config.fnImprimir(f"{wCedula} - Presionando Consultar.",5)
            wt.until(ec.presence_of_element_located((By.XPATH,'//*[@id="formQueries:j_idt58"]'))).send_keys(wCedula)
            wt.until(ec.presence_of_element_located((By.XPATH,'//*[@id="formQueries:j_idt87"]'))).click()
            
            while wTiempo <=180: #maximo 3minutos
                try:
                    if 'display: block;' in dv.find_element(By.XPATH, '//*[@id="modalResultadoTransaccion"]').get_attribute('style'):
                        wOperativo = True
                        break
                    #fin if
                    
                    wMsjValidacion = wt.until(ec.presence_of_element_located((By.XPATH,'//*[@id="modalDialog"]/div[2]/div[1]/span'))).text

                    # Validaciones de mensajes la cual el usuario deberia bloquearse
                    if len(  [ dato for dato in self.app_config.wERROR_BLOQUEAR_USUARIOS if self.app_config.wERROR_BLOQUEAR_USUARIOS[dato] == str(wMsjValidacion).strip() ]  ) > 0:
                        wDatUsuario['Activo'] = self.app_api.fnDesactivarUsuario( wDatUsuario['Id'] ) 
                        wMsjError = wMsjValidacion
                        break
                    #fin if 
                    
                    if wt.until(ec.presence_of_element_located((By.XPATH,'//*[@id="modalDialog"]/div[2]'))).text == self.app_config.wERROR['MODAL_VACIO']:
                        wMsjError = "ERROR VALIDACION: Modal se encuentra vacio."
                        break
                    #fin if
                    
                    if wt.until(ec.presence_of_element_located((By.XPATH,'//*[@id="modalDialog"]/div[2]'))).text == self.app_config.wERROR['SOLO_CEDULAS_NUMERICAS']:
                        wMsjError = "ERROR VALIDACION: Lo sentimos pero para Cedula de Ciudadania solo se permiten valores Numericos."
                        break
                    #fin if
                    
                    if wt.until(ec.presence_of_element_located((By.XPATH,'//*[@id="timeoutSession"]/div/div/div[2]/label'))).text == self.app_config.wERROR['TIEMPO_EXCEDIDO']:
                        wMsjError = self.app_config.wERROR['TIEMPO_EXCEDIDO']
                        break
                    #fin if  
                    
                except:
                    pass
                finally:
                    time.sleep(1)
                    wTiempo+=1
                #fin try
            #fin while 
            
            if not wOperativo and wMsjError == "":
                wMsjError = "Ocurrio un incoveniente al consultar Cedula."
            #fin if 
        except:
            pass
        #fin try
        
        return wMsjError, wDatUsuario
    #fnConsultarCedula
        
    def fnProcesarCedulas( self, wDatosGenerales, wDatosUsuarios ):
        driver = None
        try:
            # Variables
            wCont            = 1
            wDatUsuario      = wDatosUsuarios[0]
            wTiempoEjecucion = self.app_config.wTiempoEjecucion
            
            for datos in wDatosGenerales:
                try:
                    if driver == None:
                        self.app_config.fnImprimir(f"{datos['Cedula']} - Ingresando a la pagina", 5)
                        driver, wait = self.app_config.fnAbrirPagina( self.app_config.wPagConsumir )
                        
                        # Validando pagina en mantenimiento
                        try:
                            if driver.find_element(By.XPATH, '//*[@id="panelMantenimiento"]/div[1]').text == self.app_config.wERROR['SISTEMA_MANTENIMIENTO']: 
                                driver = self.fnImprimirErrorCerrarChrome( driver, datos['Cedula'], self.app_config.wERROR['SISTEMA_MANTENIMIENTO'], 7)
                                self.app_api.fnGuardandoIncidencia( datos['Cedula'], datos['Id'], "SI", self.app_config.wERROR['SISTEMA_MANTENIMIENTO'], 'PENDIENTE' )
                                continue
                            #fin if 
                        except:
                            pass
                        #fin if 
                        
                        if driver == None:
                            msjError = "Se cerro la pagina sin aviso."
                            self.fnImprimirErrorCerrarChrome( None, datos['Cedula'], msjError, 7)
                            self.app_api.fnGuardandoIncidencia( datos['Cedula'], datos['Id'], "SI", msjError, 'PENDIENTE' )
                            continue
                        #fin if 
                        
                        wMsjError, wDatUsuario = self.fnIniciarSession( driver, wait, datos['Cedula'], wDatosUsuarios, wDatUsuario )
                        
                        if wMsjError != "":
                            driver = self.fnImprimirErrorCerrarChrome( driver, datos['Cedula'], wMsjError, 7)
                            
                            if len( wDatUsuario ) == 0:
                                break
                            else: 
                                self.app_api.fnGuardandoIncidencia( datos['Cedula'], datos['Id'], "SI", wMsjError, 'PENDIENTE' )
                                continue
                            #fin if
                        #fin if 
                                                
                        # Consultas Generales
                        self.app_config.fnImprimir(f"{datos['Cedula']} - Presionando Consulta Generales.",5)
                        
                        # esperando que se activen los botones
                        wTiempo = 1
                        while wTiempo<=180:
                            try:
                                if len(driver.find_elements(By.XPATH,'/html/body/div[2]/div[2]/span[2]/div/div[1]/div[2]/div') ) > 0:
                                    time.sleep(2)
                                    break
                                #fin if
                            except:
                                pass
                            finally:
                                wTiempo+=1
                                time.sleep(1)
                            #fin try 
                        #fin while
                        
                        # validando si existe la opcion de "Consulta Generales"
                        ele_cons_general = [ div.text for div in driver.find_elements(By.XPATH,'/html/body/div[2]/div[2]/span[2]/div/div[1]/div[2]/div') if str(div.text).strip() == 'Consultas Generales' ]
                        if len(ele_cons_general) > 0:
                            WebDriverWait(driver, 60).until(ec.presence_of_element_located((By.XPATH,'//*[@id="linkConsultas"]'))).click()
                        else:
                            driver = self.fnImprimirErrorCerrarChrome( driver, datos['Cedula'], "No se encontro la opcion de [Consulta Generales]", 7) 
                            wTiempoEjecucion = self.app_config.wTiempoEsperaBtn #4horas
                            break
                        #fin if 
                    #fin if
                        
                    # Cedula
                    wMsjError = self.fnSolicitar( driver, datos['Cedula'] )
                    if wMsjError != "":
                        driver = self.fnImprimirErrorCerrarChrome( driver, datos['Cedula'], wMsjError, 7 ) 
                        self.app_api.fnGuardandoIncidencia( datos['Cedula'], datos['Id'], "SI", wMsjError, 'PENDIENTE' )
                        continue
                    #fin if 
                    
                    # Consultar
                    wMsjError, wDatUsuario = self.fnConsultarCedula( driver, wait, datos['Cedula'], wDatUsuario )
                    if wMsjError != '':
                        driver = self.fnImprimirErrorCerrarChrome( driver, datos['Cedula'], wMsjError, 7)
                        self.app_api.fnGuardandoIncidencia( datos['Cedula'], datos['Id'], "SI", wMsjError, 'PENDIENTE' )                        
                        continue
                    #fin if 
                    
                    # Validando errores
                    try: 
                        wMsjValidacion = wait.until(ec.presence_of_element_located((By.XPATH,'//*[@id="modalDialog"]/div[2]/div[1]/span'))).text                
                        if len(  [ dato for dato in self.app_config.wERROR_BLOQUEAR_USUARIOS if self.app_config.wERROR_BLOQUEAR_USUARIOS[dato] == str(wMsjValidacion).strip() ]  ) > 0:
                            # Desactivando al usuario
                            wDatUsuario['Activo'] = self.app_api.fnDesactivarUsuario( wDatUsuario['Id'] )
                            driver = self.fnImprimirErrorCerrarChrome( driver, datos['Cedula'], self.app_config.wERROR_BLOQUEAR_USUARIOS['USUARIO_BLOQUEADO'], 7)
                            self.app_api.fnGuardandoIncidencia( datos['Cedula'], datos['Id'], "SI", wMsjError, 'PENDIENTE' )                            
                            continue                                             
                        #fin if 
                        
                        if driver.find_element(By.XPATH,'//*[@id="timeoutSession"]/div/div/div[2]/label').text == self.app_config.wERROR['TIEMPO_EXCEDIDO']:
                            driver = self.fnImprimirErrorCerrarChrome( driver, datos['Cedula'], self.app_config.wERROR['TIEMPO_EXCEDIDO'], 7)
                            self.app_api.fnGuardandoIncidencia( datos['Cedula'], datos['Id'], "SI", wMsjError, 'PENDIENTE' )                            
                            continue
                        #fin if 
                    except:
                        pass
                    #fin try
                    
                    if len(driver.find_elements(By.XPATH, '//*[@id="formModalResultado:consultas_data"]/tr')) > 0:
                        # Variables                        
                        wContador     = 0 
                        wCntRegistros = len(driver.find_elements(By.XPATH, '//*[@id="formModalResultado:consultas_data"]/tr'))
                        
                        self.app_config.fnImprimir(f"{datos['Cedula']} - Recorriendo Resultado Transacción",5)
                        for dataTr in driver.find_elements(By.XPATH, '//*[@id="formModalResultado:consultas_data"]/tr'):
                            try:
                                wItem = dataTr.find_elements(By.XPATH, 'td')[0].text
                                
                                if wItem == 'La consulta realizada a las oficinas de registro no arrojo ningún resultado para los parametros ingresados':
                                    wCntRegistros = 0
                                    self.app_config.fnImprimir(f"{datos['Cedula']} - RPTA RESULTADO: {wItem}",7)
                                    break
                                #fin if 
                                
                                self.app_config.fnImprimir(f"{datos['Cedula']} - Registrando Detalle {wItem}",5)
                                
                                wMsjError, wContador = self.app_api.fnGuardarDetalleBienes( wContador, datos['Id'], datos['Cedula'], (dataTr.find_elements(By.XPATH, 'td')[1].text), (dataTr.find_elements(By.XPATH, 'td')[2].text), (dataTr.find_elements(By.XPATH, 'td')[3].text) )
                                if wMsjError!= "" :
                                    break
                                #fin if  
                            except:
                                self.app_config.fnImprimir(f"{datos['Cedula'] } - Ocurrio un incoveniente en el proceso de guardar detalle, Revisar Log.",7)
                                self.log.error(f"Cedula: {datos['Cedula'] } - ERROR DETALLE: {sys.exc_info()[1]}")
                                pass
                            #fin try
                        #fin for 
                        
                        if wCntRegistros == 0:
                            self.app_api.fnGuardandoIncidencia( datos['Cedula'], datos['Id'], "NO", "", 'SIN DATOS' )
                        elif wContador != wCntRegistros:
                            self.app_api.fnGuardandoIncidencia( datos['Cedula'], datos['Id'], "SI", "Registros Guardados diferentes al portal", 'PENDIENTE' )
                        else:
                            self.app_api.fnGuardandoIncidencia( datos['Cedula'], datos['Id'], "NO", "", 'PROCESADO' )
                        #fin if 
                        
                        time.sleep(1)
                    else:
                        self.app_api.fnGuardandoIncidencia( datos['Cedula'], datos['Id'], "NO", "", 'SIN DATOS' )
                        self.app_config.fnImprimir(f"{datos['Cedula']} - No se encontro registros.",7)
                    #fin if 
                                                        
                    driver.refresh()
                    time.sleep(1)  
                except:
                    self.app_api.fnGuardandoIncidencia( datos['Cedula'], datos['Id'], "SI", "Ocurrio un tipo de error en la pagina", 'PENDIENTE' )
                    driver = self.fnImprimirErrorCerrarChrome( driver, datos['Cedula'], str( sys.exc_info()[1]), 7)  
                    pass
                finally:
                    wCont+=1
                #fin try
            #fin for
        except:
            pass
        finally:
            if driver != None:
                driver.quit()
                driver = None
            #fin if
        #fin try
        
        return wTiempoEjecucion
    #fnProcesarCedulas