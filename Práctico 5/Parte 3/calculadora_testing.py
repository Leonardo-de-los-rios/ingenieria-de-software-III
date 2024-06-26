import platform
import unittest

from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select, WebDriverWait


class CalculadoraTests(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        system = platform.system()
        if system == "Windows":
            service = Service(executable_path="chromedriver.exe")
        elif system == "Linux":
            service = Service(executable_path="chromedriver-linux64/chromedriver")
        cls.driver = webdriver.Chrome(service=service)
        cls.driver.get("https://profequiroga.github.io/Calculadora-IS3/")

    # Verifica los elementos del HTML (inputs, buttons, etc.)
    def get_elemento(self, by, value):
        try:
            return self.driver.find_element(by, value)
        except NoSuchElementException:
            return None

    # Verifica si el elemento tiene el atributo especificado
    def verificar_atributo(self, element, attr):
        return element.get_attribute(attr) is not None

    def get_elementos(self):
        return {
            "selectBuild": self.get_elemento(By.ID, "selectBuild"),
            "errorMsgField": self.get_elemento(By.ID, "errorMsgField"),
            "number1Field": self.get_elemento(By.ID, "number1Field"),
            "number2Field": self.get_elemento(By.ID, "number2Field"),
            "selectOperationDropdown": self.get_elemento(
                By.ID, "selectOperationDropdown"
            ),
            "calculateButton": self.get_elemento(By.ID, "calculateButton"),
            "numberAnswerField": self.get_elemento(By.ID, "numberAnswerField"),
            "integerSelect": self.get_elemento(By.ID, "integerSelect"),
            "clearButton": self.get_elemento(By.ID, "clearButton"),
        }

    def verificar_elementos(self, elementos, operacion):
        for nombre, elemento in elementos.items():
            if operacion == 4 and nombre == "integerSelect":
                self.assertTrue(
                    self.verificar_atributo(elemento, "hidden"),
                    f"{nombre} no debería estar visible",
                )
                self.assertTrue(
                    self.verificar_atributo(elemento, "disabled"),
                    f"{nombre} no debería estar habilitado",
                )
                continue
            else:
                self.assertIsNotNone(elemento, f"{nombre} no se encontró en la página")
                self.assertFalse(
                    self.verificar_atributo(elemento, "disabled"),
                    f"{nombre} debería estar habilitado",
                )

            if nombre != "errorMsgField":
                self.assertFalse(
                    self.verificar_atributo(elemento, "hidden"),
                    f"{nombre} debería estar visible",
                )
        return elementos

    def obtener_resultado(self):
        try:
            resultado = WebDriverWait(self.driver, 2).until(
                EC.visibility_of_element_located((By.ID, "numberAnswerField"))
            )
            resultado_obtenido = resultado.get_attribute("value")
            return resultado_obtenido
        except TimeoutException:
            return None

    def clear(self, number_1, number_2, clear):
        number_1.clear()
        number_2.clear()
        clear.click()

    def set_number(self, numero, input):
        if numero:
            input.send_keys(numero)

    def get_resultado_esperado(self, resultado_esperado, operacion, i, integers_only):
        # No activar integers_only para concatenación
        if operacion != 4:
            # Activar integers only en la segunda iteración
            if i == 1:
                integers_only.click()

                if resultado_esperado:
                    resultado_entero = resultado_esperado.split(".")[0]
                    return resultado_entero
        return resultado_esperado

    def verificar_errores(self, error_esperado, error_obtenido):
        if error_obtenido != "" or error_esperado:
            if error_obtenido == "Divide by zero error!":
                self.driver.refresh()
            self.assertEqual(error_obtenido, error_esperado)

    def verificar_resultados(self, resultado_esperado, resultado_obtenido):
        if resultado_esperado or resultado_obtenido:
            self.assertEqual(
                resultado_obtenido,
                resultado_esperado,
                f"La operación debería dar {resultado_esperado}",
            )

    def realizar_operacion(
        self, num_build, numero1, numero2, operacion, resultado_esperado, error_esperado
    ):
        iteraciones = 1 if operacion == 4 else 2

        for i in range(iteraciones):
            elementos = self.get_elementos()

            build = Select(elementos["selectBuild"])
            error_label = elementos["errorMsgField"]
            number_1 = elementos["number1Field"]
            number_2 = elementos["number2Field"]
            operation = Select(elementos["selectOperationDropdown"])
            calculate = elementos["calculateButton"]
            integers_only = elementos["integerSelect"]
            clear = elementos["clearButton"]

            build.select_by_value(str(num_build))
            operation.select_by_value(str(operacion))

            self.verificar_elementos(elementos, operacion)
            self.clear(number_1, number_2, clear)

            self.set_number(numero1, number_1)
            self.set_number(numero2, number_2)

            resultado_esperado_aux = self.get_resultado_esperado(
                resultado_esperado, operacion, i, integers_only
            )

            calculate.click()

            resultado_obtenido = self.obtener_resultado()
            error_obtenido = error_label.text

            self.verificar_errores(error_esperado, error_obtenido)
            self.verificar_resultados(resultado_esperado_aux, resultado_obtenido)

    @classmethod
    def tearDownClass(cls):
        cls.driver.quit()


def generar_prueba(
    build, numero1, numero2, operacion, resultado_esperado, error_esperado
):
    def test(self):
        self.realizar_operacion(
            build, numero1, numero2, operacion, resultado_esperado, error_esperado
        )

    return test


# (number_1, number_2, result, error)
pruebas_suma = [
    ("9999999999", "1", "10000000000", None),
    ("-999999999", "-1", "-1000000000", None),
    ("99999999.9", "0.00000001", "99999999.90000002", None),
    ("-9999999.9", "-0.0000001", "-9999999.900000101", None),
    ("aaaaaaaaaa", "9999999999", None, "Number 1 is not a number"),
    ("??????????", "9999999999", None, "Number 1 is not a number"),
    ("999999999.", "9999999999", "10999999998", None),
    ("9999999999", "aaaaaaaaaa", None, "Number 2 is not a number"),
    ("9999999999", "??????????", None, "Number 2 is not a number"),
    ("9999999999", "999999999.", "10999999998", None),
    ("999999999.", "999999999.", "1999999998", None),
    ("9999999999", None, "9999999999", None),
    ("aaaaaaaaaa", None, None, "Number 1 is not a number"),
    ("??????????", None, None, "Number 1 is not a number"),
    ("999999999.", None, "999999999", None),
    (None, "9999999999", "9999999999", None),
    (None, "aaaaaaaaaa", None, "Number 2 is not a number"),
    (None, "??????????", None, "Number 2 is not a number"),
    (None, "999999999.", "999999999", None),
    (None, None, "0", None),
]

pruebas_resta = [
    ("9999999999", "1", "9999999998", None),
    ("-999999999", "-1", "-999999998", None),
    ("99999999.9", "0.00000001", "99999999.89999999", None),
    ("-9999999.9", "-0.0000001", "-9999999.8999999", None),
    ("aaaaaaaaaa", "9999999999", None, "Number 1 is not a number"),
    ("??????????", "9999999999", None, "Number 1 is not a number"),
    ("999999999.", "9999999999", "-9000000000", None),
    ("9999999999", "aaaaaaaaaa", None, "Number 2 is not a number"),
    ("9999999999", "??????????", None, "Number 2 is not a number"),
    ("9999999999", "999999999.", "9000000000", None),
    ("999999999.", "999999999.", "0", None),
    ("9999999999", None, "9999999999", None),
    ("aaaaaaaaaa", None, None, "Number 1 is not a number"),
    ("??????????", None, None, "Number 1 is not a number"),
    ("999999999.", None, "999999999", None),
    (None, "9999999999", "-9999999999", None),
    (None, "aaaaaaaaaa", None, "Number 2 is not a number"),
    (None, "??????????", None, "Number 2 is not a number"),
    (None, "999999999.", "-999999999", None),
    (None, None, "0", None),
]

pruebas_producto = [
    ("9999999999", "1", "9999999999", None),
    ("-999999999", "-1", "999999999", None),
    ("99999999.9", "0.00000001", "0.999999999", None),
    ("-9999999.9", "-0.0000001", "0.99999999", None),
    ("aaaaaaaaaa", "9999999999", None, "Number 1 is not a number"),
    ("??????????", "9999999999", None, "Number 1 is not a number"),
    ("999999999.", "9999999999", "9999999989000000000", None),
    ("9999999999", "aaaaaaaaaa", None, "Number 2 is not a number"),
    ("9999999999", "??????????", None, "Number 2 is not a number"),
    ("9999999999", "999999999.", "9999999989000000000", None),
    ("999999999.", "999999999.", "999999998000000000", None),
    ("9999999999", None, "0", None),
    ("aaaaaaaaaa", None, None, "Number 1 is not a number"),
    ("??????????", None, None, "Number 1 is not a number"),
    ("999999999.", None, "0", None),
    (None, "9999999999", "0", None),
    (None, "aaaaaaaaaa", None, "Number 2 is not a number"),
    (None, "??????????", None, "Number 2 is not a number"),
    (None, "999999999.", "0", None),
    (None, None, "0", None),
]

pruebas_division = [
    ("9999999999", "1", "9999999999", None),
    ("-999999999", "-1", "999999999", None),
    ("99999999.9", "0.00000001", "9999999990000000", None),
    ("-9999999.9", "-0.0000001", "99999999000000.02", None),
    ("aaaaaaaaaa", "9999999999", None, "Number 1 is not a number"),
    ("??????????", "9999999999", None, "Number 1 is not a number"),
    ("999999999.", "9999999999", "0.09999999991", None),
    ("9999999999", "aaaaaaaaaa", None, "Number 2 is not a number"),
    ("9999999999", "??????????", None, "Number 2 is not a number"),
    ("9999999999", "999999999.", "10.000000009", None),
    ("999999999.", "999999999.", "1", None),
    ("9999999999", None, None, "Divide by zero error!"),
    ("aaaaaaaaaa", None, None, "Number 1 is not a number"),
    ("??????????", None, None, "Number 1 is not a number"),
    ("999999999.", None, None, "Divide by zero error!"),
    (None, "9999999999", "0", None),
    (None, "aaaaaaaaaa", None, "Number 2 is not a number"),
    (None, "??????????", None, "Number 2 is not a number"),
    (None, "999999999.", "0", None),
    (None, None, None, "Divide by zero error!"),
    ("9999999999", "0", None, "Divide by zero error!"),
    ("-999999999", "0", None, "Divide by zero error!"),
    ("99999999.9", "0", None, "Divide by zero error!"),
    ("-9999999.9", "0", None, "Divide by zero error!"),
    ("aaaaaaaaaa", "0", None, "Number 1 is not a number"),
    ("??????????", "0", None, "Number 1 is not a number"),
    ("999999999.", "0", None, "Divide by zero error!"),
    (None, "0", None, "Divide by zero error!"),
]

pruebas_concatenacion = [
    ("0000000000", "9999999999", "00000000009999999999", None),
    ("aaaaaaaaaa", "zzzzzzzzzz", "aaaaaaaaaazzzzzzzzzz", None),
    ("??????????", "!!!!!!!!!!", "??????????!!!!!!!!!!", None),
    ("?1a???a?a?", "!9z!!!z!z!", "?1a???a?a?!9z!!!z!z!", None),
    ("?1a???a?a?", "", "?1a???a?a?", None),
    ("", "?1a???a?a?", "?1a???a?a?", None),
    ("", "", "", None),
]


tests = [
    (0, "suma", pruebas_suma),
    (1, "resta", pruebas_resta),
    (2, "producto", pruebas_producto),
    (3, "division", pruebas_division),
    (4, "concatenacion", pruebas_concatenacion),
]


def test(build, operacion):
    for i, (numero1, numero2, resultado_esperado, error) in enumerate(operacion[2], 1):
        test_name = f"test_{operacion[1]}_build_{build}_caso_{i}"
        test = generar_prueba(
            build, numero1, numero2, operacion[0], resultado_esperado, error
        )
        setattr(CalculadoraTests, test_name, test)


def ingresar_datos():
    build = int(input("Ingresa el build (0 al 9): "))
    operacion = int(
        input(
            "Ingresa la operacion (0: suma, 1: resta, 2: producto, 3: division, 4: concatenacion): "
        )
    )
    return build, operacion


if __name__ == "__main__":
    while True:
        build, operacion = ingresar_datos()
        # Crear suite de pruebas
        suite = unittest.TestSuite()
        test(build, tests[operacion])

        # Agregar pruebas a la suite
        for attr_name in dir(CalculadoraTests):
            if attr_name.startswith("test_"):
                suite.addTest(CalculadoraTests(attr_name))

        # Ejecutar las pruebas de la suite
        runner = unittest.TextTestRunner()
        runner.run(suite)

        # Eliminar las pruebas dinámicamente agregadas
        for attr_name in dir(CalculadoraTests):
            if attr_name.startswith("test_"):
                delattr(CalculadoraTests, attr_name)

        repeat = input("¿Quieres realizar otro test? (s/n): ").strip().lower()
        if repeat != "s":
            break
