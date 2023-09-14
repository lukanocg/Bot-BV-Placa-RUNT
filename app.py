#!/usr/bin/env python
# encoding: utf-8
from clsConfig import clsConfig
from clsScraping import clsScraping
import os, sys, time
import multiprocessing

# Función para procesar registros en paralelo
def fnProcesarInvestigacionBienes( app_config_gen, dataInvestigacionBienes, dataUsuarios ):
    oClsScraping = clsScraping()
    wTiempoEjecucion = oClsScraping.fnProcesarCedulas( dataInvestigacionBienes, dataUsuarios ) 
    
    if wTiempoEjecucion != app_config_gen.wTiempoEsperaBtn:
        app_config_gen.wBtnOculto = True
    #fin if 
#fnProcesarInvestigacionBienes

if __name__ == "__main__":
    os.system('cls')
    app_config_gen = clsConfig()
    wLog = app_config_gen.fnIncializarLog()
    wTiempoEjecucion = app_config_gen.wTiempoEjecucion
    wNroProcesos = 4

    while True:
        # Variables
        driver = None 
        
        try:
            os.system('cls')
            app_config_gen.fnImprimirTitulo(f"Proceso [::INICIO SESION::] ejecutandose {app_config_gen.fnConvertirFechaHora(app_config_gen.fnConfigFecha('FHA'),'-','/')}")
            wLog.info(f"Proceso INICIO [::CONSULTA VEHICULO::].")
            
            # Listado de las cedulas pendientes a consultar
            objDatosCedulas = app_config_gen.fnEjecutarApiPost("BusquedaRadicacion/ConsultaInvBienes", {})
            if objDatosCedulas['Code'] == 200:
                # Listado de usuarios
                objDatosUsuarios = app_config_gen.fnEjecutarApiPost("BusquedaRadicacion/ConsultaUsuariosInvBienes", {})
                if objDatosUsuarios['Code'] == 200:
                    if len(objDatosCedulas['Data']) > 0:
                        if len(objDatosUsuarios['Data']) > 0:
                            # Dividiendo datos
                            registros_por_proceso = [objDatosCedulas['Data'][i::wNroProcesos] for i in range(wNroProcesos)]
                            usuarios_por_proceso = [objDatosUsuarios['Data'][i::wNroProcesos] for i in range(wNroProcesos)]
                            
                            # Crear y ejecutar los procesos en paralelo
                            procesos = []
                            for i in range(wNroProcesos):
                                proceso = multiprocessing.Process(target=fnProcesarInvestigacionBienes, args=(app_config_gen, registros_por_proceso[i],usuarios_por_proceso[i],))
                                procesos.append(proceso)
                                proceso.start()
                            #fin for

                            # Esperar a que todos los procesos terminen
                            for proceso in procesos:
                                proceso.join()
                            #fin for

                            #Si el boton "Consulta Generales" no se encuentra sale del bucle
                            if app_config_gen.wBtnOculto:
                                wTiempoEjecucion = app_config_gen.wTiempoEsperaBtn
                                continue
                            #fin if
                            
                            # Procesar Cedulas con incidencias de errores
                            while True:
                                objDatosCedulasIncidencias = app_config_gen.fnEjecutarApiPost("BusquedaRadicacion/ConsultaInvBienesConIncidencias", {})
                                objDatosUsuarios = app_config_gen.fnEjecutarApiPost("BusquedaRadicacion/ConsultaUsuariosInvBienes", {})
                                
                                if objDatosCedulasIncidencias['Code'] == 200:
                                    if len(objDatosCedulasIncidencias['Data']) > 0:
                                        if len(objDatosUsuarios['Data']) > 0:
                                            # Dividiendo datos
                                            registros_por_proceso = [objDatosCedulasIncidencias['Data'][i::wNroProcesos] for i in range(wNroProcesos)]
                                            usuarios_por_proceso = [objDatosUsuarios['Data'][i::wNroProcesos] for i in range(wNroProcesos)]
                                            
                                            # Crear y ejecutar los procesos en paralelo
                                            procesos = []
                                            for i in range(wNroProcesos):
                                                proceso = multiprocessing.Process(target=fnProcesarInvestigacionBienes, args=(app_config_gen, registros_por_proceso[i],usuarios_por_proceso[i]))
                                                procesos.append(proceso)
                                                proceso.start()
                                            #fin for

                                            # Esperar a que todos los procesos terminen
                                            for proceso in procesos:
                                                proceso.join()
                                            #fin for
                                            
                                            #Si el boton "Consulta Generales" no se encuentra sale del bucle
                                            if app_config_gen.wBtnOculto:
                                                wTiempoEjecucion = app_config_gen.wTiempoEsperaBtn
                                                break
                                            #fin if
                                        else:
                                            app_config_gen.fnImprimir("No se encontraron usuarios activos.")
                                            break
                                        #fin if  
                                    else:
                                        break
                                    #fin if 
                                else:
                                    app_config_gen.fnImprimir(f"ERROR LISTADO-CEDULAS: {objDatosCedulasIncidencias['Message']}")
                                    wLog.error(f"ERROR LISTADO-CEDULAS: {objDatosCedulasIncidencias['Message']}")
                                #fin if
                            #fin while
                        else:
                            app_config_gen.fnImprimir("No se encontraron usuarios activos.")
                        #fin if                         
                    else:
                        app_config_gen.fnImprimir("No se encontraron cedulas a consultar.")
                    #fin if  
                else:
                    app_config_gen.fnImprimir(f"ERROR LISTADO-CEDULAS: {objDatosUsuarios['Message']}")
                    wLog.error(f"ERROR LISTADO-CEDULAS: {objDatosUsuarios['Message']}")
                #fin if
            else:
                app_config_gen.fnImprimir(f"ERROR LISTADO-USUARIOS: {objDatosCedulas['Message']}")
                wLog.error(f"ERROR LISTADO-USUARIOS: {objDatosCedulas['Message']}")
            #fin if  
        except:
            app_config_gen.fnImprimir(f"Error: {sys.exc_info()[1]}")
            wLog.error(sys.exc_info()[1])
            pass
        finally:
            if driver != None:
                driver.quit()
                driver = None
            #fin if
            
            if int(wTiempoEjecucion) > 0:
                os.system('cls')
                wTiempo = (int(wTiempoEjecucion)/60)
                wTiempoDes = str(int(wTiempo)) +" min" if wTiempo < 60 else str( int(wTiempo/60) ) + " hora(s)"
                app_config_gen.fnImprimir(f"TERMINO: {app_config_gen.fnConvertirFechaHora(app_config_gen.fnConfigFecha('FHA'),'-','/')} - PROCESO SE EJECUTARÁ NUEVAMENTE EN {wTiempoDes}.")
                time.sleep(int(wTiempoEjecucion))
            else:
                app_config_gen.fnImprimirTitulo(f"Proceso Culminado {app_config_gen.fnConvertirFechaHora(app_config_gen.fnConfigFecha('FHA'),'-','/')}")
                wLog.info(f"Proceso Culminado.")
                break
            #fin if 
        #fin try
    #fin while 
# fin if
