import mysql.connector as connector

class API:
    """
    Clase con las funciones de la API de SmartBeds
    """

    def __init__(self,db : connector):
        self._db = db

    def auth(self, nick: str,password: str) -> str:
        """
        Comprueba que el usuario y la contraseña
        son correctas.

        Parameters
        ----------
        nick : string
            nombre introducido por el usuario
        password : string
            contraseña introducida por el usuario

        Returns
        -------
        string 
            token de sesión del usuario
        
        Raises
        ------
        BadCredentialsError
            si la relación nick-password no existe
        """
        pass

    def beds(self, token: str) -> list:
        """
        Lista de camas disponibles para
        el usuario asociado al token

        Parameters
        ----------
        token : string
            identificación del usuario
        
        Returns
        -------
        list
            lista con los nombres de las camas disponibles
        
        Raises
        ------
        BadCredentialsError
            si el token no está asociado a ningún usuario
        """
        pass

    def bed(self, token : str, bedname: str) -> str:
        """
        Solicita el namespace
        donde los datos de la cama se
        difunden.

        Parameters
        ----------
        token : string
            identificacion del usuario
        bedname : string
            identificación de la cama

        Returns
        -------
        string 
            espacio de nombres donde se difuenden los datos de la cama

        Raises
        ------
        BadCredentialsError
            si el token no está asociado a ningún usuario
        ElementNotExistsError
            si la cama no existe
        PermissionsError
            si la cama no es accesible para el usuario
        """
        pass

    def users(self, token : str) -> list:
        """
        Solicita la lista de usuarios

        Parameters
        ----------
        token : string
            identificacion del usuario

        Return
        ------
        list
            nicknames de todos los usuarios

        Raises
        ------
        BadCredentialsError
            si el token no está asociado a ningún usuario
        PermissionsError
            si el usuario no tiene rol de administrador
        """
        pass
        
    def useradd(self, token : str, nick : str, password : str):
        """
        Crea un nuevo usuario

        Parameters
        ----------
        token : string
            identificacion del usuario
        nick : string
            nombre del nuevo usuario
        password : string
            contraseña del nuevo usuario

        Raises
        ------
        BadCredentialsError
            si el token no está asociado a ningún usuario
        PermissionsError
            si el usuario no tiene rol de administrador
        UsernameExistsError
            si el nombre de usuario existía con anterioridad.
        """
        pass

    def usermod(self, token : str, nick : str, password : str, oldpass = None):
        """
        Cambia la contraseña del usuario

        Parameters
        ----------
        token : string
            identificacion del usuario
        nick : string
            nombre del usuario a modificar la contraseña
        password : string
            contraseña nueva
        oldpass : string optional
            contraseña antigua, solo necesaria si no es administrador

        Raises
        ------
        BadCredentialsError
            si el token no está asociado a ningún usuario o la contraseña anterior es distinta
        PermissionsError
            si no es administrador y el usuario a cambiar es distinto al asociado con el token
        ElementNotExistsError
            si el usuario no existe
        """
        pass

    def userdel(self, token : str, nick : str):
        """
        Borra un usuario

        Parameters
        ----------
        token : string
            identificacion del usuario
        nick : string
            nombre del usuario a borrar

        Raises
        ------
        BadCredentialsError
            si el token no está asociado a ningún usuario
        PermissionsError
            si el usuario no tiene rol de administrador
        ElementNotExistsError
            si el usuario no existe
        """
        pass

    def bedadd(self, token : str, bedparams : dict):
        """
        Crea una nueva cama

        Parameters
        ----------
        token : string
            identificacion del usuario
        bedparams : dict
            attributos de las camas cuya clave es la columna
            de la tabla

        Raises
        ------
        BadCredentialsError
            si el token no está asociado a ningún usuario
        PermissionsError
            si el usuario no tiene rol de administrador
        BedExistsError
            si algúno de los parámetros identificativos de la cama
            existe ya como son el nombre, el identificador o el par
            ip-puerto
        """
        pass

    def bedmod(self, token : str, bedparams : dict):
        """
        Modifica una cama

        Parameters
        ----------
        token : string
            identificacion del usuario
        bedparams : dict
            attributos de las camas cuya clave es la columna
            de la tabla

        Raises
        ------
        BadCredentialsError
            si el token no está asociado a ningún usuario
        PermissionsError
            si el usuario no tiene rol de administrador
        BedExistsError
            si algúno de los parámetros identificativos de la cama
            existe ya como son el nombre, el identificador o el par
            ip-puerto en otra cama diferente
        ElementNotExistsError
            si la cama no existe
        """
        pass

    def beddel(self, token : str, bedname : str):
        """
        Borra una cama

        Parameters
        ----------
        token : string
            identificacion del usuario
        bedname : string
            nombre que identifica a la cama

        Raises
        ------
        BadCredentialsError
            si el token no está asociado a ningún usuario
        PermissionsError
            si el usuario no tiene rol de administrador
        ElementNotExistsError
            si la cama no existe
        """
        pass

    def bedgetperm(self, token : str) -> list:
        """
        Obtiene la lista de permisos

        Parameters
        ----------
        token : string
            identificacion del usuario

        Returns
        -------
        list
            lista con los pares usuario-cama

        Raises
        ------
        BadCredentialsError
            si el token no está asociado a ningún usuario
        PermissionsError
            si el usuario no tiene rol de administrador
        """
        pass
    
    def bedmodperm(self, token : str, bedname : str, username : str) -> bool:
        """
        Obtiene la lista de permisos

        Parameters
        ----------
        token : string
            identificacion del usuario
        bedname : string
            identificador de la cama a modificar
        username : string
            identificar del tercero a modificar permisos

        Returns
        -------
        boolean
            verdadero si se ha creado un permiso, falso si se ha roto

        Raises
        ------
        BadCredentialsError
            si el token no está asociado a ningún usuario
        PermissionsError
            si el usuario no tiene rol de administrador
        ElementNotExistsError
            si la cama o el usuario no existe
        """
        pass

class SmartBedError(Exception):
    pass

class BadCredentialsError(SmartBedError):
    pass

class ElementNotExistsError(SmartBedError):
    pass

class PermissionsError(SmartBedError):
    pass

class BedExistsError(SmartBedError):
    pass

class UsernameExistsError(SmartBedError):
    pass