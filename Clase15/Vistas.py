from Modelo import Medicamento
import sys
from PyQt5.QtWidgets import QApplication,QMainWindow, QDialog,QMessageBox
from PyQt5.QtGui import QDoubleValidator, QRegExpValidator,QIntValidator
from PyQt5.QtCore import Qt,QRegExp
from PyQt5.uic import loadUi


class VentanaPrincipal(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        loadUi('ventana_principal.ui',self)
        self.setup()

    def setup(self):
        self.boton_ingresar.clicked.connect(self.abrir_ventana_paciente)
        self.boton_agregar.clicked.connect(self.abrir_ventana_AgregarMedicamento)

    def abrir_ventana_paciente(self):
        ventana_paciente=ventanaPaciente(self)
        ventana_paciente.asignarCoordinador(self.__mensajero2)
        self.hide()
        ventana_paciente.show()

    def abrir_ventana_AgregarMedicamento(self):
        ventana_medicamento= ventanaAgregar(self)
        ventana_medicamento.asignarCoordinador(self.__mensajero2)
        self.hide()
        ventana_medicamento.show()

    def asignarCoordinador(self,c):
        self.__mensajero2 = c 

class ventanaPaciente(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        loadUi('ventana_paciente.ui',self)
        self.__mi_ventana_principal = parent
        self.setup()

    def setup(self):
        self.campo_nombre.setValidator(QRegExpValidator(QRegExp("[a-zA-Z ]+")))
        self.campo_cedula.setValidator(QIntValidator())
        self.boton_agregar.clicked.connect(self.abrir_ventana_medicamento)
        self.buttonBox.accepted.connect(self.opcion_aceptar) 
        self.buttonBox.rejected.connect(self.opcion_cancelar)

    def opcion_aceptar(self):
        #1 se recuperan los campos
        nombre = self.campo_nombre.text() 
        cedula = self.campo_cedula.text() 
        #2 Se envia la informacion al controlador
        mensaje = self.__mensajero3.RecibirInfoPaciente(nombre,cedula,self.__medicamentos_paciente_actual)
        if mensaje is True:
            print("Entro aca")
        else:            
            msg = QMessageBox(self)
            msg.setIcon(QMessageBox.Information)
            msg.setText(mensaje)
            msg.setWindowTitle("Resultado de la operacion")
            msg.show()
        #3 se muestra la ventana principal y se oculta la actual
        self.__mi_ventana_principal.show()
        self.hide()

    def opcion_cancelar(self):
        #en esta opcion simplemente se vuelve a mostrar la principal
        #y se oculta la actual
        self.__mi_ventana_principal.show() 
        self.hide()

    def abrir_ventana_medicamento(self):
        ventana_medicamento = ventanaMedicamento(self)
        self.hide()
        ventana_medicamento.show() 

    def asignarCoordinador(self,c):
        self.__mensajero3 = c 

    def recibir_medicamentos(self, medicamentos):
        self.__medicamentos_paciente_actual = medicamentos

class ventanaMedicamento(QDialog):
    def __init__(self, parent=None):
        super(ventanaMedicamento,self).__init__(parent)
        loadUi('ventana_medicamento.ui',self)
        self.__mi_ventana_principal = parent
        self.__medicamentos = {}
        self.setup()

    def setup(self):
        self.campo_nombre.setValidator(QRegExpValidator(QRegExp("[a-zA-Z ]+")))
        soloEntero = QIntValidator()
        self.campo_dosis.setValidator(soloEntero)
        self.boton_agregar.clicked.connect(self.recuperar_info_medicamento)
        self.buttonBox.accepted.connect(self.opcion_aceptar) 
        self.buttonBox.rejected.connect(self.opcion_cancelar)

    def recuperar_info_medicamento(self):
        #1 Se recuperan los campos
        nombre = self.campo_nombre.text() 
        dosis = int(self.campo_dosis.text()) 
        if nombre.lower() not in self.__medicamentos:
            m = Medicamento()
            m.AsignarNombre(nombre) 
            m.AsignarDosis(dosis) 
            self.__medicamentos[nombre.lower()] = m
            mensaje = "Guardado con exito"
        else:# 3 si si esta se muestra el mensaje
            #mostrar mensaje
            mensaje = "Ya se había asignado el medicamento"

        msg = QMessageBox(self)
        msg.setIcon(QMessageBox.Information)
        msg.setText(mensaje)
        #msg.setInformativeText("This is additional information")
        msg.setWindowTitle("Resultado de la operacion")
        msg.show()

        #6 se vuelven a poner en blanco los campos
        self.campo_nombre.setText('')
        self.campo_dosis.setText('')
        
    def opcion_aceptar(self):
        #se retorna el diccionario con lo que se haya guardado
        self.__mi_ventana_principal.recibir_medicamentos(self.__medicamentos)
        self.__mi_ventana_principal.show()
        self.hide()

    def opcion_cancelar(self):
        #se crea un diccionario vacio
        m = {} 
        self.__mi_ventana_principal.recibir_medicamentos(m) 
        self.__mi_ventana_principal.show() 
        self.hide() 
            
class ventanaAgregar(QDialog):
    def __init__(self, parent=None):
        super(ventanaAgregar,self).__init__(parent)
        loadUi('ventana_agregar.ui',self)
        self.__mi_ventana_principal = parent
        self.setup()

    def setup (self):
        self.campo_nombre.setValidator(QRegExpValidator(QRegExp("[a-zA-Z ]+")))
        soloEntero = QIntValidator()
        self.campo_dosis.setValidator(soloEntero)
        self.campo_cedula.setValidator(soloEntero)
        self.boton_anexarMed.accepted.connect(self.agregarDroga)

    def agregarDroga(self):
        cedula= self.campo_cedula.text()
        nombre= self.campo_nombre.text()
        dosis= self.campo_dosis.text() 
        mensaje=self.__mensajero4.AgregarMedicamento(cedula,nombre,dosis)
        msg = QMessageBox(self)
        msg.setIcon(QMessageBox.Information)
        msg.setText(mensaje)
        msg.setWindowTitle("Resultado de la operacion")
        msg.show()
        self.__mi_ventana_principal.show()

    def asignarCoordinador(self,c):
        self.__mensajero4 = c 
