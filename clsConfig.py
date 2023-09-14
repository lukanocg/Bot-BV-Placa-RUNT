"""
    Autor: GrupoJC
    Fecha Creación: 17/01/2023
"""
import configparser, requests, logging
from clsEstandar import clsEstandar
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait 
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
import os

class clsConfig( clsEstandar ):
    def __init__( self ):
        self.aDataConfig = configparser.ConfigParser() 
        self.fnConfigVariables( )
        
        #self.wERROR = {
        #     'SISTEMA_MANTENIMIENTO'     : 'Sistema en modo mantenimiento, estamos trabajando para habilitar el servicio'
        #    ,'SISTEMA_NO_FUNCIONA'       : 'Esta página no funciona\nLa página certificados.supernotariado.gov.co no puede procesar esta solicitud ahora.\nHTTP ERROR 500\nVolver a cargar'
        #    ,'SOLO_CEDULAS_NUMERICAS'    : 'Lo sentimos pero para Cedula de Ciudadania solo se permiten valores Numericos.\nAceptar'            
        #    ,'MODAL_VACIO'               : 'Aceptar'
        #    ,'TIEMPO_EXCEDIDO'           : 'Lo sentimos, ha excedido el tiempo máximo de inactividad de 15 minutos, por favor presione el botón aceptar para actualizar.'
        #}
        #
        #self.wERROR_BLOQUEAR_USUARIOS = {                    
        #     'USUARIO_BLOQUEADO'         : 'Lo sentimos pero ha excedido la cantidad máxima de consultas con tarifa gratuita por día'
        #    ,'USUARIO_NO_ENCONTRADO'     : 'Lo sentimos pero la información ingresada no corresponde a un usuario de la plataforma'
        #    ,'USUARIO_INACTIVO'          : 'Lo sentimos pero el usuario con el que intenta ingresar está Inactivo, por favor utilice la función de recordar contraseña o contacte al administrador de la plataforma'
        #    ,'INFORMACION_NO_ENCONTRADA' : 'La informacion ingresada no coincide con ningun usuario registrado.'
        #}
        #
        #self.wBtnOculto = False
        
    #__init__

    def fnConfigVariables( self ):
        """
        Configuración de variables        
        """
        #self.aDataConfig.read('C:\ROBOT\CONFIG\config-investigacionBienes.ini')
        self.aDataConfig.read('C:\laragon\www\estructura\config.ini')
        self.wChromeDriver   = self.aDataConfig.get("config", "chromedriver")
        self.wRutaApi        = self.aDataConfig.get("api", "ruta")
        
        #DATOS DE COMBOS EN LINEA  
        self.wRutaLog     = self.aDataConfig.get("consultaVehiculo", "ruta_log").strip() 
        self.wPagConsumir = self.aDataConfig.get("consultaVehiculo", 'pagina_consumir').strip()  
        self.wTiempoEjecucion = self.aDataConfig.get("consultaVehiculo", 'tiempo_ejecucion').strip()  
        self.wTiempoEsperaBtn = self.aDataConfig.get("consultaVehiculo", 'tiempo_espera_btn').strip()  
    #FIN fnConfigVariables
    
    def fnIncializarLog( self ):
        """Inicializar configuración de log

        Returns:
            _type_: _description_
        """ 
        logger = logging.getLogger( 'logInvestigacionBienes' )
        logger.setLevel(logging.DEBUG)
        
        if not os.path.exists( self.wRutaLog.replace( self.wRutaLog.split('\\')[-1] , '') ):
            self.fnCrearDirectorio( self.wRutaLog.replace( self.wRutaLog.split('\\')[-1] , '')   )
        #fin if
        
        file_handler = logging.FileHandler( self.wRutaLog )
        file_handler.setLevel(logging.DEBUG)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s') 
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
        
        return logger  
    #fin if 
    
    def fnCrearDirectorio(self, pRutaDirectorio ):
        os.makedirs( pRutaDirectorio )
    #fnCreandoDirectorio
    
    def fnAbrirPagina( self, wUrlPagina ):
        """Abriendo Pagina

        Args:
            wUrlPagina (text): _description_

        Returns:
            _type_: _description_
        """
        options = webdriver.ChromeOptions()
        options.add_argument("disable-infobars")
        options.add_argument('--ignore-certificate-errors')
        options.add_argument("--start-maximized")
        options.add_argument("--disable-extensions") 
        options.add_argument("--disable-blink-features=AutomationControlled") 
        options.add_experimental_option("excludeSwitches", ["enable-automation","enable-logging"])
        options.add_experimental_option('useAutomationExtension', False)
        options.add_experimental_option('prefs', {
            "disable-notifications": True,
            "profile.password_manager_enabled": False,
            "profile.default_content_setting_values.automatic_downloads": 1,
            "profile.default_content_setting_values.notifications": 2, 
            "plugins.always_open_pdf_externally": True,
            "download.directory_upgrade":True,
            "download.prompt_for_download":False})
        options.add_experimental_option('detach', True)

        driver = webdriver.Chrome( self.wChromeDriver, chrome_options=options)
        #driver = webdriver.Chrome( options=options )
        try:
            wait = WebDriverWait(driver, 5)
            driver.set_page_load_timeout(40)
            driver.get(wUrlPagina)
        except TimeoutException:
            driver.quit()
            driver = None
            pass 
        #fin driver
        return driver, wait
    #fnAbrirPagina

    def fnEjecutarApiGet(self, pFuncionApi, pDataGet = {}, pRetornarJson = True ):
        """Ejecutamos el request metodo GET"""

        try:
            data = requests.get(url = (self.wRutaApi+pFuncionApi), params = pDataGet)
            if pRetornarJson:
                return data.json()
            #fin if
            return {'success': True, 'message' : "Se ejecutó exitosamente" }
        except requests.HTTPError as e:
            return {'success': False, 'message' : e }
        #fin try
    #fnEjecutarApiGet

    def fnEjecutarApiPost(self, pFuncionApi, pDataPost, pRetornarJson = True ):
        """Ejecutamos el request metodo POST"""
        try:
            data = requests.post(url = (self.wRutaApi+pFuncionApi), data = pDataPost, headers= {'Content-Type': 'application/json;  charset=utf-8'})
            if pRetornarJson:
                return data.json()
            #fin if
            return {'success': True, 'message' : "Se ejecutó exitosamente" }
        except requests.HTTPError as e:
            return {'success': False, 'message' : e }
        #fin try
    #fnEjecutarApiPost

#clsConfig