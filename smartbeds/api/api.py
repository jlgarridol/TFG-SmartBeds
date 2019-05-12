from mysql.connector import connect
from mysql.connector.errors import IntegrityError
from smartbeds.utils import get_secret_key
import smartbeds.vars as v
import random
import string
from hashlib import sha512
from base64 import b64encode
from sql import *


class API:
    """
    Clase con las funciones de la API de SmartBeds
    """

    SIZE = 32
    _instance = None

    def __init__(self, params: dict):
        if API._instance is not None:
            raise Exception("Ya existe una instancia de la API")

        self._params = params

        self._users = Table('Users')
        self._beds = Table('Beds')
        self._user_bed = Table('Users_Beds')
        self._master_key = get_secret_key()

        API._instance = self

    def _db_context(self):
        if v.db is None:
            v.db = connect(**self._params)
            v.db.autocommit = False
        return v.db

    @classmethod
    def get_instance(cls):
        if API._instance is None:
            raise Exception("No existe una instancia de la API")
        return cls._instance

    def auth(self, nick: str, password: str) -> tuple:
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
        print("Intento de autenticación del usuario:", nick)
        conn = self._db_context()
        print(conn)
        self.__check_password(nick, password)

        token = self.__update_token(nick)
        user = self.__get_user_by_token(token)
        conn.commit()
        
        return token, nick, user['rol']

    def __check_password(self, nick, password):
        """
        Comprueba si la contraseña es correcta

        :param nick: nombre de usuario
        :param password: contraseña
        :raise BadCredentialsError: si la combinación no es correcta
        """
        conn = self._db_context()
        password = API.encrypt(password)

        query = self._users.select()
        query.where = (self._users.nickname == nick) & (self._users.password == password)

        cursor = conn.cursor()
        command = API.prepare_query(query)
        cursor.execute(*command)

        if cursor.fetchone() is None:
            conn.rollback()
            raise BadCredentialsError("La combinación de nombre de usuario y contraseña no coinciden")
        cursor.close()

    def __update_token(self, nick):
        """
        Genera un nuevo token para la sesión

        :param nick: nombre del usuario
        :return: nuevo token
        """
        conn = self._db_context()
        again = True
        while again:
            try:
                token = API.generate_token(API.SIZE)

                token_crypt = API.encrypt(token)

                query = self._users.update(columns=[self._users.token],
                                           values=[token_crypt],
                                           where=self._users.nickname == nick)

                cursor = conn.cursor()
                command = API.prepare_query(query)
                cursor.execute(*command)
                again = False
                cursor.close()
            except IntegrityError:
                pass #Se ha repetido el token, se vuelve a intentar

        return token

    def get_all_beds_info(self):
        """
        Obtiene toda la lista de camas
        con todos sus datos. Recomendado
        para su uso interno de la aplicación

        :return: Lista de camas
        """
        conn = self._db_context()
        query = self._beds.select()

        cursor = conn.cursor(dictionary=True)
        command = API.prepare_query(query)
        cursor.execute(*command)
        lista = list(cursor)
        cursor.close()
        
        return lista

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
        conn = self._db_context()
        if token != self._master_key:
            user = self.__get_user_by_token(token)
        else:
            user = {'rol': "admin"}

        if user['rol'] == "admin":
            query = self._beds.select(self._beds.bed_name)
        else:
            join = self._beds.join(self._user_bed)
            join.condition = join.right.IDB == self._beds.IDB
            query = join.select(self._beds.bed_name)
            query.where = join.right.IDU == user['IDU']

        cursor = conn.cursor()
        command = API.prepare_query(query)
        cursor.execute(*command)

        names = [self.__get_bed(n) for [n] in cursor]
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
            que es el UUID y la MAC

        Raises
        ------
        BadCredentialsError
            si el token no está asociado a ningún usuario
        ElementNotExistsError
            si la cama no existe
        PermissionsError
            si la cama no es accesible para el usuario
        """
        conn = self._db_context()
        if token != self._master_key:
            user = self.__get_user_by_token(token)
        else:
            user = {'rol': "admin"}
        bed = self.__get_bed(bedname)

        #Comprobación de que es accesible
        if user['rol'] != 'admin':
            query = self._user_bed.select()
            query.where = (self._user_bed.IDB == bed['IDB']) & (self._user_bed.IDU == user['IDU'])

            cursor = conn.cursor()
            command = API.prepare_query(query)
            cursor.execute(*command)
            row = cursor.fetchone()
            if row is None:
                raise PermissionsError("La cama no es accesible por el usuario")
            cursor.close()

        namespace = bed['UUID']+"_"+bed['MAC']
        
        return namespace

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
        conn = self._db_context()
        if token != self._master_key:
            user = self.__get_user_by_token(token)
        else:
            user = {'rol': "admin"}
        if user['rol'] != 'admin':
            raise PermissionsError('Orden válida solo para administrador')

        query = self._users.select(self._users.nickname)
        cursor = conn.cursor()
        command = API.prepare_query(query)
        cursor.execute(*command)

        names = [n for [n] in cursor]
        cursor.close()
        
        return names

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
        conn = self._db_context()
        user = self.__get_user_by_token(token)
        if user['rol'] != 'admin':
            raise PermissionsError('Orden válida solo para administrador')

        first_token = API.encrypt(API.generate_token(API.SIZE))
        password = API.encrypt(password)
        query = self._users.insert(
            columns=[self._users.nickname, self._users.password, self._users.token],
            values=[[nick, password, first_token]])

        try:
            cursor = conn.cursor()
            command = API.prepare_query(query)
            cursor.execute(*command)

            cursor.close()
            conn.commit()
        except IntegrityError as err:
            conn.rollback()
            raise UsernameExistsError(str(err))

    def usermod(self, token: str, nick: str, password: str, oldpass=None):
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
        conn = self._db_context()
        user = self.__get_user_by_token(token)
        if user['rol'] != 'admin':

            if user['nickname'] != nick:
                raise PermissionsError('Orden válida solo para administrador')
            elif user['password'] != API.encrypt(oldpass):
                raise BadCredentialsError('Contraseña anterior no válida')
        if self.__get_user_by_name(nick)['password'] == API.encrypt(password):
            #La contraseña es la misma
            return

        try:
            update = self._users.update(columns=[self._users.password],
                                        values=[API.encrypt(password)],
                                        where=self._users.nickname == nick)

            cursor = conn.cursor()
            command = API.prepare_query(update)
            cursor.execute(*command)

            if cursor.rowcount == 0:
                raise ElementNotExistsError("El usuario no existe")

            cursor.close()
            conn.commit()
            
        except Exception:
            conn.rollback()
            
            raise

    def userdel(self, token: str, nick: str):
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
        IllegalOperationError
            si se intenta borrar al usuario administrador
        """
        conn = self._db_context()
        if token != self._master_key:
            user = self.__get_user_by_token(token)
        else:
            user = {'rol': "admin"}
        if user['rol'] != 'admin':
            raise PermissionsError('Orden válida solo para administrador')
        to_del = self.__get_user_by_name(nick)
        if to_del['rol'] == 'admin':
            raise IllegalOperationError("No se puede borrar al usuario administrador")

        try:
            self.__delete(self._users, self._users.nickname == nick, "El usuario no existe")

            conn.commit()
            
        except Exception:
            conn.rollback()
            
            raise

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
        conn = self._db_context()
        if token != self._master_key:
            user = self.__get_user_by_token(token)
        else:
            user = {'rol': "admin"}
        if user['rol'] != 'admin':
            raise PermissionsError('Orden válida solo para administrador')

        try:
            columns, values = self._get_params_from_dict(table="self._beds", params=bedparams)
            query = self._beds.insert(columns=columns, values=[values])

            cursor = conn.cursor()
            command = API.prepare_query(query)
            cursor.execute(*command)
            cursor.close()
            conn.commit()
            
        except IntegrityError as err:
            conn.rollback()
            
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
        conn = self._db_context()
        if token != self._master_key:
            user = self.__get_user_by_token(token)
        else:
            user = {'rol': "admin"}
        self.__get_bed(bedparams['bed_name']) #Comprueba que la cama existe
        if user['rol'] != 'admin':
            raise PermissionsError('Orden válida solo para administrador')

        try:
            columns, values = self._get_params_from_dict("self._beds", bedparams)
            query = self._beds.update(columns=columns,
                                      values=values,
                                      where=self._beds.bed_name == bedparams['bed_name'])

            cursor = conn.cursor()
            command = API.prepare_query(query)
            cursor.execute(*command)
            cursor.close()
            conn.commit()
            
        except IntegrityError as err:
            conn.rollback()
            
            raise BedExistsError(str(err))

    def beddel(self, token: str, bedname: str):
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
        conn = self._db_context()
        if token != self._master_key:
            user = self.__get_user_by_token(token)
        else:
            user = {'rol': "admin"}
        if user['rol'] != 'admin':
            raise PermissionsError('Orden válida solo para administrador')

        try:
            self.__delete(self._beds, self._beds.bedname == bedname, "La cama no existe")

            conn.commit()
            
        except Exception:
            conn.rollback()
            
            raise

    def bedgetperm(self, token: str) -> list:
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
        conn = self._db_context()
        if token != self._master_key:
            user = self.__get_user_by_token(token)
        else:
            user = {'rol': "admin"}
        if user['rol'] != 'admin':
            raise PermissionsError('Orden válida solo para administrador')

        perms = []

        join = self._beds.join(self._user_bed)
        join.condition = join.right.IDB == self._beds.IDB
        join = join.join(self._users)
        join.condition = join.right.IDU == self._user_bed.IDU

        query = join.select(self._beds.bed_name, self._users.nickname)

        cursor = conn.cursor()
        command = API.prepare_query(query)
        cursor.execute(*command)

        for [bedname, username] in cursor:
            perms.append({"username": username, "bed_name": bedname})

        cursor.close()
        
        return perms

    def bedmodperm(self, token: str, bedname: str, username: str) -> bool:
        """
        Modifica los permisos

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
        conn = self._db_context()
        if token != self._master_key:
            user = self.__get_user_by_token(token)
        else:
            user = {'rol': "admin"}
        if user['rol'] != 'admin':
            raise PermissionsError('Orden válida solo para administrador')

        bed = self.__get_bed(bedname)
        user = self.__get_user_by_name(username)

        idu = user['IDU']
        idb = bed['IDB']

        query = self._user_bed.select()
        query.where = (self._user_bed.IDB == idb) & (self._user_bed.IDU == idu)

        cursor = conn.cursor()
        command = API.prepare_query(query)
        cursor.execute(*command)

        if cursor.fetchone() is None:
            self._add_perm(idb, idu)
        else:
            self._remove_perm(idb, idu)

        cursor.close()
        
        conn.commit()

    def _remove_perm(self, idb, idu):
        """
        Elimina una asignación usuario - cama

        :param idb: identificador de la cama
        :param idu: identificador del usuario
        """
        conn = self._db_context()
        delete = self._user_bed.delete(where=(self._user_bed.IDB == idb) & (self._user_bed.IDU == idu))
        cursor = conn.cursor()
        command = API.prepare_query(delete)
        cursor.execute(*command)
        cursor.close()

    def _add_perm(self, idb, idu):
        """
        Crea una asignación usuario - cama

        :param idb: identificador de la cama
        :param idu: identificador del usuario
        """
        conn = self._db_context()
        add = self._user_bed.insert(columns=[self._user_bed.IDB, self._user_bed.IDB],
                                    values=[[idb, idu]])
        cursor = conn.cursor()
        command = API.prepare_query(add)
        cursor.execute(*command)
        cursor.close()

    @classmethod
    def generate_token(cls, size: int) -> str:
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

    @classmethod
    def encrypt(cls, text):
        """
        Encripta un texto

        :param text: texto a encriptar
        :return: texto encriptado
        """
        hashed = sha512(text.encode('utf-8')).digest()
        based = b64encode(hashed).decode('utf-8')
        return based

    def __delete(self, table, where, error="El elemento no existe"):
        """
        Elimina un elemento

        :param table: tabla sobre la que borrar
        :param where: condición de borrado
        :param error: mensaje en caso de error (opcional)
        :raise ElementNotExistsError: si no se borra nada
        """
        conn = self._db_context()
        delete = table.delete(where=where)

        cursor = conn.cursor()
        command = API.prepare_query(delete)
        cursor.execute(*command)

        if cursor.rowcount == 0:
            raise ElementNotExistsError(error)

        cursor.close()

    def __get_user_by_token(self, token) -> dict:
        """
        Obtiene los datos del usuario

        :param token: identificador del usuario
        :return: datos del usuario
        :raise BadCredentialsError: si el token no está ligado a ningún usuario
        """
        conn = self._db_context()
        token = API.encrypt(token)

        query = self._users.select()
        query.where = self._users.token == token

        cursor = conn.cursor(dictionary=True)
        command = API.prepare_query(query)
        cursor.execute(*command)
        user = cursor.fetchone()
        if user is None:
            raise BadCredentialsError('Token no válido para ningún usuario')
        cursor.close()
        return user

    def __get_user_by_name(self, name) -> dict:
        """
        Obtiene los datos del usuario

        :param name: nombre del usuario
        :return: datos del usuario
        :raise ElementNotExistsError: si el usuario no existe
        """
        conn = self._db_context()
        query = self._users.select()
        query.where = self._users.nickname == name

        cursor = conn.cursor(dictionary=True)
        command = API.prepare_query(query)
        cursor.execute(*command)
        user = cursor.fetchone()
        if user is None:
            raise ElementNotExistsError('El usuario no existe')
        cursor.close()
        return user

    def __get_bed(self, bedname) -> dict:
        """
        Obtiene los datos de una cama

        :param bedname: identificador de la cama
        :return: datos de la cama
        """
        conn = self._db_context()
        query = self._beds.select()
        query.where = self._beds.bed_name == bedname

        cursor = conn.cursor(dictionary=True)
        command = API.prepare_query(query)
        cursor.execute(*command)
        bed = cursor.fetchone()
        if bed is None:
            raise ElementNotExistsError('La cama solicitada no existe')
        cursor.close()
        return bed

    @classmethod
    def prepare_query(cls, query):
        command = list(query)
        command[0] = command[0].replace("\"", "")
        return command

    def _get_params_from_dict(self, table, params):
        """
        Obtiene los parámetros válidos para sql-python

        :param table: tabla sobre la que aplicar
        :param params: diccionario con los parámetros
        :return: tupla columnas, valores
        """
        columns = []
        values = []
        for c, v in params.items():
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


class IllegalOperationError(SmartBedError):
    pass
