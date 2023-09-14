from clsConfig import clsConfig
import sys
class clsApi:

    def __init__( self ):
        self.app_config = clsConfig()
        self.log        = self.app_config.fnIncializarLog()
    #fin if
    
    def fnDesactivarUsuario( self, wIdCedula ):
        datEnviar = '{"ID" : "'+ str(wIdCedula) + '"}' 
        self.app_config.fnEjecutarApiPost("BusquedaRadicacion/DesabilitarUsuarioInvBienes",  datEnviar.encode('utf-8'))
        
        return False 
    #fnDesactivarUsuario
    
    def fnGuardandoIncidencia( self, wCedula, wIdCedula, wErrorBusqueda , wDetalleError, wEstado  ):
        wMsjError = ""
        try:
            datEnviar = '{"Id" : "'+ str(wIdCedula) + '"'
            datEnviar+= ', "ErrorBusqueda": "'+ str(wErrorBusqueda) + '"'
            datEnviar+= ', "DetalleError": "'+ str(wDetalleError) + '"'
            datEnviar+= ', "Estado": "'+ str(wEstado) + '" }' 
            self.app_config.fnEjecutarApiPost("BusquedaRadicacion/GuardandoIcidenciaInvBienes",  datEnviar.encode('utf-8')) 
        except:
            wMsjError = sys.exc_info()[1]            
            self.app_config.fnImprimir(f"{wCedula} - Ocurrio un incoveniente al guardar incidencia, Revisar Log.",7)
            self.log.error(f"Cedula: {wCedula} - JSON:{ datEnviar} - MSJ ERROR: {wMsjError}")
            pass
        #fin try
    #fnGuardandoIncidencia
    
    def fnGuardarDetalleBienes( self, contador, id, cedula, ciudad, matricula, direccion ):
        wMsjError = ""
        try:
            datEnviar = '{"IdInvestigacionBienes" : "'+ str(id) + '", '
            datEnviar+= '"Ciudad" : "'+ ciudad + '", '
            datEnviar+= '"Matricula" : "'+ matricula+ '", '
            datEnviar+= '"Direccion" : "'+ direccion.replace('"','').replace('\\',' ') + '" }' 
            objRptaInvBienes = self.app_config.fnEjecutarApiPost("BusquedaRadicacion/CrearDetalleInvBienes",  datEnviar.encode('utf-8'))
            
            if objRptaInvBienes['Code'] == 200:
                self.app_config.fnImprimir(f"{cedula} - Se guardo exitosamente - Item [{contador}]", 5)
            else:
                wMsjError = objRptaInvBienes['Message']
                self.app_config.fnImprimir(f"{cedula} - Ocurrio un incoveniente al guardar detalle, Revisar Log.", 7)
                self.log.error(f"Cedula: {cedula} - JSON:{ datEnviar} - ERROR DETALLE: {objRptaInvBienes['Message']}")
            #fin if
        except:
            wMsjError = sys.exc_info()[1]            
            self.app_config.fnImprimir(f"{cedula} - Ocurrio un incoveniente en la funcion guardar detalle, Revisar Log.", 7)
            self.log.error(f"Cedula: {cedula} - JSON:{ datEnviar} - MSJ ERROR: {wMsjError}")
            pass
        #fin try
        
        return wMsjError, (contador+1)
    #fnGuardarDetalleBienes
    