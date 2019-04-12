from mysql.connector.connection import MySQLConnection
from mysql.connector.errors import  IntegrityError
import random, string
from hashlib import sha512
from base64 import b64encode

from sql import *
from sql.aggregate import *
from sql.conditionals import *

class API:
    """
    Clase con las funciones de la API de SmartBeds
    """

    SIZE = 32

    def __init__(self, db: MySQLConnection):
        self._db = db
        self._db.autocommit = False

        self._users = Table('Users')
        self._beds = Table('Beds')
        self._user_bed = Table('Users_Beds')

    def auth(self, nick: str, password: str) -> str:
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

        self.__check_password(nick, password)

        token = self.__update_token(nick)

        self._db.commit()
        return token

    def __check_password(self, nick, password):
        """
        Comprueba si la contraseña es correcta

        :param nick: nombre de usuario
        :param password: contraseña
        :raise BadCredentialsError: si la combinación no es correcta
        """
        hashed = sha512(password.encode('utf-8')).digest()
        based = b64encode(hashed).decode('utf-8')

        query = self._users.select(Count(Literal("*")))
        query.where = (self._users.nickname == nick) & (self._users.password == based)

        cursor = self._db.cursor()
        cursor.execute(*tuple(query))

        if cursor.fetchone() is None:
            self._db.rollback()
            raise BadCredentialsError("La combinación de nombre de usuario y contraseña no coinciden")
        cursor.close()

    def __update_token(self, nick):
        """
        Genera un nuevo token para la sesión

        :param nick: nombre del usuario
        :return: nuevo token
        """
        again = True
        while again:
            try:
                token = self.__generateToken(API.SIZE)

                hashed = sha512(token.encode('utf-8')).digest()
                based = b64encode(hashed).decode('utf-8')

                query = self._users.update(columns=[self._users.token], values=[based], where=self._users.nick == nick)

                cursor = self._db.cursor()
                cursor.execute(*tuple(query))
                again = False
                cursor.close()
            except IntegrityError:
                pass

        return token

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
        user = self.__getUserByToken(token)

        if user['rol'] == "admin":
            query = self._beds.select(self._beds.bed_name)
        else:
            join = self._beds.join(self._user_bed)
            join.condition = join.right.IDB == self._beds.IDB
            query = join.select(self._beds.bed_name)
            query.where = join.right.IDU == user['IDU']

        cursor = self._db.cursor()
        cursor.execute(*tuple(query))

        names = [n for (n) in cursor]
        cursor.close()
        return names

    def bed(self, token: str, bedname: str) -> str:
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

    def users(self, token: str) -> list:
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
        
    def useradd(self, token: str, nick: str, password: str):
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

    def bedadd(self, token: str, bedparams: dict):
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
        user = self.__getUserByToken(token)
        if user['rol'] != 'admin':
            raise PermissionsError('Orden válida solo para administrador')

        try:
            columns, values = self.__getParamsFromDict("self._beds", bedparams)
            query = self._beds.insert(columns=columns, values=values)

            cursor = self._db.cursor()
            cursor.execute(*tuple(query))
            cursor.close()
            self._db.commit()
        except IntegrityError as err:
            self._db.rollback()
            raise BedExistsError(str(err))

    def bedmod(self, token: str, bedparams: dict):
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

    def __generateToken(self, size: int) -> str:
        """
        Genera un token del tamaño size

        Parameters
        ----------
        size : int
            tamaño del token a generar

        Returns
        -------
        string
            token alfanumérico
        """
        token = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(size))
        return token

    def __getUserByToken(self, token) -> dict:
        """
        Obtiene los datos del usuario

        :param token: identificador del usuario
        :return: datos del usuario
        :raise BadCredentialsError: si el token no está ligado a ningún usuario
        """
        hashed = sha512(token.encode('utf-8')).digest()
        based = b64encode(hashed).decode('utf-8')

        query = self._users.select()
        query.where = self._users.token == based

        cursor = self._db.cursor(dictionary=True)
        cursor.execute(*tuple(query))
        user = cursor.fetchone()
        if user is None:
            raise BadCredentialsError('Token no válido para ningún usuario')
        cursor.close()
        return user

    def __getParamsFromDict(self, table, params):
        """
        Obtiene los parámetros válidos para sql-python

        :param params: diccionario con los parámetros
        :return: tupla columnas, valores
        """
        columns = []
        values = []
        for c,v in params.items():
            columns.append(eval(table+"."+c))
            values.append(v)

        return columns, values


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
