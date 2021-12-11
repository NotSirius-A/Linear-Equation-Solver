import re
import itertools
import numpy as np

class EquationsNotSolveable(Exception):
    pass


class Solver():
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

        if is_unsolvable:
            raise EquationsNotSolveable("Not enough equations")

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
        coefficients_raw = [x for x in re.split('[A-Za-z]', equation)]

        coefficients_raw = [x.replace(',', '.').replace('=', '') for x in coefficients_raw]

        coefficients = []
        for x in coefficients_raw:
            if (x == "+") or (x == ''):
                x = 1
            elif x == "-":
                x = -1
            else:
                pass

            coefficients.append(x)

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
        constants = np.array(constants_all)

        matrices = {
            "coefficients": coefficients,
            "variables": variables,
            "constants": constants,
        }

        return matrices

    def get_solution_cramer_method(self, matrices) -> list:
        solution = []

        main_determinant = np.linalg.det(matrices["coefficients"])

        if main_determinant == 0:
            raise EquationsNotSolveable("Main determinant is equal to 0, no solutions or infinetly many solutions exist")

        for index, var in enumerate(matrices['variables']):
            substituted_matrix = matrices["coefficients"].copy()
            substituted_matrix[:, index] = matrices["constants"]

            partial_determinant = np.linalg.det(substituted_matrix)
            
            var_value = (partial_determinant/main_determinant)

            solution.append([var, var_value])

        return solution

    def solve(self, equations) -> dict:
        equations_formatted = self.analyze_equations(equations)

        matrices = self.get_matrices(equations_formatted)

        solution = self.get_solution_cramer_method(matrices)

        rv = {
            "input": {
                "equations_str": equations,
                "equations_formatted": equations_formatted,
                "matrices": matrices,
            },
            "solution": solution,
        }

        return rv 
        

if __name__ == "__main__":  
    solver = Solver()

    num = int(input("How many equations: "))

    equations = []
    for i in range(num):
        x = input(f"{i+1}: ")
        equations.append(x)

    # equations = [
    #     "x-z-2.1y+10t=0",
    #     "-4x-2.1y=22",
    #     "-1x-1.1y+4t=4",
    #     "-6x+16.2z-0.1y+0t=-20",
    # ]

    #[['t', -1.2350579150579164], ['x', -2.3589189189189215], ['y', -5.983011583011583], ['z', -2.1451737451737465]]

    output = solver.solve(equations)
    print(output["solution"])
    