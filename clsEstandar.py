"""
    Autor: GrupoJC
    Fecha Creación: 17/01/2023
"""
from datetime import datetime 

class clsEstandar:   
    
    def fnObtenerArchivoSegunExtension(self, pFicheros, pExtension01, pExtension02 ):
        return [fichero.name for fichero in pFicheros if fichero.is_file() and (fichero.name.endswith(pExtension01) or fichero.name.endswith(pExtension02))]
    #fnObtenerArchivoSegunExtension

    def fnConfigFecha(self, pTipo):
        """Configuración de fechas

        Args:
            pTipo (text): Condicion de fechas 
            
        Returns:
            text: Retorna valor segun la condición.
        """
        match pTipo:
            case 'AA' : return datetime.now().year                           #AÑO ACTUAL
            case 'FA' : return datetime.now().strftime('%Y-%m-%d')           #FECHA ACTUAL
            case 'HA' : return datetime.now().strftime('%H:%M:%S')           #HORA ACTUAL
            case 'FHA': return datetime.now().strftime('%Y-%m-%d %H:%M:%S')  #FECHA HORA ACTUAL
        #math
    #fnConfigFecha
    

    def fnConvertirFecha( self, pFecha, pSeparadorAnt = '/', pSeparadorAct = '-' ):
        """Retornar la fecha convertida"""

        return pSeparadorAct.join(pFecha.split(pSeparadorAnt)[::-1])
    #fnFecConvertir
    
    def fnConvertirFechaHora( self, pFechaHora, pSeparadorAnt = '/', pSeparadorAct = '-' ):
        """Retornar la fecha hora convertida"""

        if pFechaHora:
            wFecha,wHora = pFechaHora.split(' ')
            return self.fnConvertirFecha( wFecha, pSeparadorAnt, pSeparadorAct ) + ' ' + wHora
        return ''
    #fnFecConvertir

    def fnImprimir( self, pMensaje, pCantidad = 2 ):
        """Imprimir

        Args:
            pMensaje (text): Descripción del mensaje a imprimir en pantalla
            pCantidad (int, optional): cantidad de separador de espacio por defecto es 2.
        """
        print((' '*pCantidad) + '- '+pMensaje)
    #fnImprimir

    def fnImprimirTitulo(self, pTitulo ):
        """Imprimiendo titulo personalizado 
        Args:
            pTitulo (text): Descripción del titulo del proceso RPA
        """
        self.fnImprimir("----------------------------------------------------------------------------------------------------")
        self.fnImprimir( (" "*round((100-len(pTitulo))/2) ) + pTitulo.upper() )
        self.fnImprimir("----------------------------------------------------------------------------------------------------")
    #fnImprimirTitulo

    def fnSaltoLinea( self ):
        """Imprimir Salto de linea """
        print("\n" )
    #fnSaltoLineafnImprimir