import smartbeds.vars as v
import unittest
import json
from mysql.connector import connect
from smartbeds.utils import get_sql_config
from smartbeds import start


class ParametrizedTestCase(unittest.TestCase):
    """ TestCase classes that want to be parametrized should
        inherit from this class.
    """
    def __init__(self, methodName='runTest', param=None):
        super(ParametrizedTestCase, self).__init__(methodName)
        self.param = param

    @staticmethod
    def parametrize(testcase_klass, param=None):
        """ Create a suite containing all tests taken from the given
            subclass, passing them the parameter 'param'.
        """
        testloader = unittest.TestLoader()
        testnames = testloader.getTestCaseNames(testcase_klass)
        suite = unittest.TestSuite()
        for name in testnames:
            suite.addTest(testcase_klass(name, param=param))
        return suite


class ApiTest(ParametrizedTestCase):

    def test_smartbed(self):
        api = API.get_instance()
        self._name = self.param['name']
        self._desc = self.param['description']
        self._func = self.param['func']
        self._input = self.param['input']
        self._output = self.param['output']
        self._excepts = self.param['excepts']

        print("\nTest:", self._name)
        print("\nTest:", self._desc)

        funcion = "api."+self._func+"("
        first = True
        for i in self._input:
            if type(i) == str:
                i = "\""+i+"\""
            if first:
                funcion += i
                first = False
            else:
                funcion += ","+i
        funcion += ")"
        try:

            result = eval(funcion)
            #Si no ha saltado excepción es fallo
            if self._excepts is not None:
                self.fail("La excepción no ha saltado")

            if type(result) == tuple:
                result = list(result)
                # Si la salida esperada se ponen igual el resultado
                for i in range(len(self._output)):
                    if self._output[i] is None:  # Salida aleatoria
                        result[i] = None

            self.assertEqual(result, self._output)
        except Exception as ex:
            if type(ex).__name__ != self._excepts:
                self.fail("Excepción no esperada")


def generateSuiteOfTests():
    suite = unittest.TestSuite()
    with open('smartbeds/test/tests.json', 'r') as f:
        tests = json.load(f)
        for test in tests['tests']:
            suite.addTest(ParametrizedTestCase.parametrize(ApiTest, param=test))
    return suite


if __name__ == '__main__':

    start()
    from smartbeds.api import API

    with open("smartbeds/test/test_database.sql") as file:
        query = file.read()
        queries = query.split(";")
        v.db = connect(**get_sql_config())
        for q in queries:
            try:
                cursor = v.db.cursor()
                cursor.execute(q)
                v.db.commit()
                cursor.close()
            except:
                print(q)
    suites = generateSuiteOfTests()
    for suite in suites:
        unittest.TextTestRunner(verbosity=3).run(suite)
