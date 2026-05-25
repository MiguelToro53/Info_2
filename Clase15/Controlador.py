from Modelo import Servicio
from Vistas import VentanaPrincipal
import sys
from PyQt5.QtWidgets import QApplication

class Coordinador(object):
    #como el coordindor enlaza el modelo con la vista debe
    #tener acceso a objetos de ambas clases
    def __init__(self, vista, sistema):
        self.__mi_vista = vista 
        self.__mi_sistema = sistema 
    #La idea es que la vista pase los datos que quiere guardar en
    #el modelo, este metodo se encarga de verificar que si se puedan
    #guardar y en caso de que si se pueda se guardan

    def RecibirInfoPaciente(self,n,c,medicamentos):
        #verificamos que el paciente no exista
        if self.__mi_sistema.VerificarPaciente(c) == True:
            return "Ya el paciente existe!" 
        else:
            #si no existe lo agrega
            self.__mi_sistema.AgregarPaciente(n,c,medicamentos) 
            return "Paciente agregado ..." 

    def AgregarMedicamento(self,c,n,d):
        #verifico que exista el paciente
        if self.__mi_sistema.VerificarPaciente(c) == False:
            return "El paciente no existe. No se puede agregar medicamento" 
        else:
            if self.__mi_sistema.VerificarMedicamento(c,n) == True:
                return "El paciente ya tiene el medicamento" 
            else:
                self.__mi_sistema.AgregarMedicamento(c,n,d) 
                return "Medicamento agregado"


# Código cliente
def main():
    app = QApplication(sys.argv)
    mi_vista = VentanaPrincipal() 
    mi_sistema = Servicio() 
    mensajero1 = Coordinador(mi_vista, mi_sistema) 
    mi_vista.asignarCoordinador(mensajero1) 
    mi_vista.show() 
    sys.exit(app.exec_())     

if __name__=='__main__':
    main()  