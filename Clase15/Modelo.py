class Medicamento:
    
    def __init__(self):
        self.__nombre="" 
        self.__dosis=0         

    def AsignarNombre(self,n):
        self.__nombre=n 

    def AsignarDosis(self,a):
        self.__dosis=a 

    def VerNombre(self):
        return self.__nombre 

    def VerDosis(self):
        return self.__dosis 

class Paciente:
    
    def __init__(self):
        self.__nombre="" 
        self.__cedula=0 
        self.__medicamentos = {} 

    def AsignarNombre(self,n):
        self.__nombre=n 

    def AsignarCedula(self,c):
        self.__cedula=c 
    #metodo para verificar medicamentos
    def TieneMedicamento(self,nombre):
        return nombre.lower() in self.__medicamentos 
    #metodo para asignar todos los medicamentos
    def AsignarMedicamentos(self,medicamentos):
        self.__medicamentos = medicamentos 
    #metodo para asignar un solo medicamento
    def AsignarMedicamento(self,m):
        self.__medicamentos[m.VerNombre().lower()] = m 

    def VerNombre(self):
        return self.__nombre 

    def VerCedula(self):
        return self.__cedula 


class Servicio:
    def __init__(self):
        self.__pacientes = {} 
    
    def AgregarPaciente(self,n,c,medicamentos):
        #creo el objeto
        p = Paciente() 
        p.AsignarNombre(n) 
        p.AsignarCedula(c) 
        p.AsignarMedicamentos(medicamentos) 
        #guardo el paciente. LA CLAVE ES LA CEDULA
        self.__pacientes[c] = p 

    def VerificarPaciente(self, c):
        return c in self.__pacientes 
    
    def AgregarMedicamento(self,c, nm, dm):
        #creo el objeto
        m = Medicamento() 
        m.AsignarNombre(nm) 
        m.AsignarDosis(dm) 
        
        #recuperar el paciente del diccionario
        paciente = self.__pacientes[c] 
        #asignarle al paciente el nuevo medicamento
        paciente.AsignarMedicamento(m) 
        #vuelvo a guardar el paciente
        # self.__pacientes[c] = paciente 
    
    def VerificarMedicamento(self, c, nm):
        #recuperar el paciente del diccionario
        paciente = self.__pacientes[c] 
        return paciente.TieneMedicamento(nm) 
