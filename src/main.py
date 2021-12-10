import re
import itertools
import numpy as np

class App():
    def __init__(self) -> None:
        pass

    def analyze_equations(self, equations) -> dict:
        equations_computer_format = []
        for equation in equations:
            x = self.convert_equation_to_computer_format(equation)
            equations_computer_format.append(x)

        variables_all = [x["variables"] for x in equations_computer_format]
        variables_unique = set((itertools.chain(*variables_all)))

        cleaned_equations = []
        for equation in equations_computer_format:
            x = self.fill_missing_terms(equation, variables_unique)
            cleaned_equations.append(equation)

        is_unsolvable = self.is_set_of_equations_unsolvable(variables_unique, cleaned_equations)

        assert is_unsolvable == False, "This set of equations is not solvable"

        return cleaned_equations

    def fill_missing_terms(self, equation, all_variables) -> dict:
        if all_variables == equation['variables']:
            return equation

        for var in all_variables:
            if var not in equation["variables"]:
                equation['terms'].append({
                    "coefficient": 0.0,
                    "variable": var
                })
                equation['variables'].append(var)

        equation['terms'] = sorted(equation['terms'], key=lambda x: x["variable"])

        return equation
            

    def is_set_of_equations_unsolvable(self, variables, equations) -> bool:
        # This set is for sure NOT solvable with this method when there isn't enough equations
        if len(variables) < len(equations):
            return True
        
        return False

    def convert_equation_to_computer_format(self, equation) -> dict:
        coefficients = re.findall(r'[.\,\0-9\-\+]+', equation)

        # Replacing ',' with dots, so that user can also use commas for decimal numbers
        coefficients = [x.replace(',', '.') for x in coefficients]

        try:
            coefficients = [float(x) for x in coefficients]
        except TypeError:
            raise TypeError(f"Given equation is the wrong format, equation = {equation}")

        # Last 'coefficient' should be the term without any variable - constant
        constant = coefficients[-1]
        coefficients = coefficients[:-1]

        variables = re.findall(r'[a-z]', equation)

        assert len(variables) == len(coefficients), f"Given equation is the wrong format, equation = {equation}"

        # Matching variables to their coefficients
        # It should be done as soon as possible to ensure nothing is mixed up later
        terms = []
        for coefficient, var in zip(coefficients, variables):
            terms.append({
                    "coefficient": coefficient, 
                    "variable": var,
                }
            )

        variables = sorted(variables)
        terms = sorted(terms, key=lambda x: x['variable'])

        converted_equation = {
            "equation_string": equation,
            "variables": variables,
            "terms": terms,
            "constant": constant,
        }

        return converted_equation

    def get_matrices(self, equations) -> dict:
        variables = np.array((equations[0]['variables']))

        coefficients_all = []
        for equation in equations:
            row = [x['coefficient'] for x in equation['terms']]
            coefficients_all.append(row)

        coefficients = np.array(coefficients_all)

        constants_all = [x['constant'] for x in equations]
        constants = np.array(equations)

        matrices = {
            "coefficients": coefficients,
            "variables": variables,
            "constants": constants,
        }

        return matrices
        

if __name__ == "__main__":
    app = App()

    equations = [
        "-100x+50z-2.1y+55t=0",
        "-340x-2.1y=22",
        "-550x-1.1y+34t=44",
        "-66x+66z-0.1y+0t=111",
    ]

    equations = app.analyze_equations(equations)

    app.get_matrices(equations)