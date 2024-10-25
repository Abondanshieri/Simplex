def ingresar_datos():
    num_vars = int(input("Ingrese la cantidad de variables en la función objetivo: "))
    num_restricciones = int(input("Ingrese la cantidad de restricciones: "))

    print("\nIngrese los coeficientes de la función objetivo:")
    funcion_objetivo = [-float(input(f"Coeficiente de x{i+1}: ")) for i in range(num_vars)]

    restricciones = []
    desigualdades = []
    
    for i in range(num_restricciones):
        print(f"\nIngrese los coeficientes de la restricción {i+1}:")
        restriccion = [float(input(f"Coeficiente de x{j+1}: ")) for j in range(num_vars)]
        lado_derecho = float(input("Ingrese el lado derecho (b) de la restricción: "))

        # Control de desigualdades
        desigualdad = input("Ingrese el tipo de desigualdad (<=, >=, =): ")
        if desigualdad == ">=" and lado_derecho < 0:
            # Si el lado derecho es negativo, se multiplican ambos lados por -1 para cambiar el signo
            restriccion = [-x for x in restriccion]
            lado_derecho = -lado_derecho
            desigualdad = "<="  # Se invierte la desigualdad

        restricciones.append(restriccion + [lado_derecho])
        desigualdades.append(desigualdad)

    return num_vars, num_restricciones, funcion_objetivo, restricciones, desigualdades

def mostrar_formulacion(num_vars, num_restricciones, funcion_objetivo, restricciones, desigualdades):
    print("\nEsta es la formulación del problema:")
    print("Función Objetivo: Max Z = " + " + ".join([f"{-funcion_objetivo[i]}x{i+1}" for i in range(num_vars)]))

    for i in range(num_restricciones):
        restriccion_str = " + ".join([f"{restricciones[i][j]}x{j+1}" for j in range(num_vars)])
        print(f"Restricción {i+1}: {restriccion_str} {desigualdades[i]} {restricciones[i][-1]}")

    decision = input("\n¿Desea reescribir la formulación? (s/n): ")
    return decision.lower() == "s"

def mostrar_formulacion_convertida(num_vars, num_restricciones, funcion_objetivo, restricciones):
    print("\nEsta es la formulación convertida:")
    print("Función Objetivo: Max Z = " + " + ".join([f"{funcion_objetivo[i]}x{i+1}" for i in range(len(funcion_objetivo)-1)]))

    for i in range(num_restricciones):
        restriccion_str = " + ".join([f"{restricciones[i][j]}x{j+1}" for j in range(len(restricciones[i])-1)])
        print(f"Restricción {i+1}: {restriccion_str} = {restricciones[i][-1]}")

    decision = input("\n¿Desea volver a la formulación inicial? (s/n): ")
    return decision.lower() == "s"

def convertir_a_forma_estandar(num_vars, num_restricciones, funcion_objetivo, restricciones, desigualdades):
    # Agregar variables de holgura y convertir todas las restricciones en igualdades
    for i in range(num_restricciones):
        var_holgura = [0] * num_restricciones
        if desigualdades[i] == "<=":
            var_holgura[i] = 1  # Agregar variable de holgura
        elif desigualdades[i] == ">=":
            var_holgura[i] = -1  # Agregar variable de exceso
        restricciones[i] = restricciones[i][:num_vars] + var_holgura + [restricciones[i][-1]]

    funcion_objetivo += [0] * num_restricciones + [0]  # Añadir variables de holgura a la función objetivo
    restricciones.append(funcion_objetivo)

    return restricciones

def imprimir_tabla_simplex(tableau, iteracion):
    print(f"\nIteración {iteracion}:")
    headers = [f"x{i+1}" for i in range(len(tableau[0])-1-len(tableau))] + \
              [f"s{i+1}" for i in range(len(tableau)-1)] + ["b"]
    print(" | ".join(headers))
    for i, fila in enumerate(tableau):
        if i == len(tableau) - 1:
            fila_name = "z "
        else:
            fila_name = f"s{i+1}"
        fila_str = [f"{fila[j]:.2f}" for j in range(len(fila))]
        print(f"{fila_name} | " + " | ".join(fila_str))

def buscar_columna_pivote(tableau):
    fila_objetivo = tableau[-1]
    columna_pivote = min(range(len(fila_objetivo)-1), key=lambda i: fila_objetivo[i])
    if fila_objetivo[columna_pivote] >= 0:
        return -1
    return columna_pivote

def buscar_fila_pivote(tableau, columna_pivote):
    filas = len(tableau) - 1
    cocientes = []
    for i in range(filas):
        elemento_columna = tableau[i][columna_pivote]
        if elemento_columna > 0:
            cocientes.append(tableau[i][-1] / elemento_columna)
        else:
            cocientes.append(float('inf'))
    if all(c == float('inf') for c in cocientes):
        return -1
    fila_pivote = cocientes.index(min(cocientes))
    return fila_pivote

def pivote(tableau, fila_pivote, columna_pivote):
    pivot_element = tableau[fila_pivote][columna_pivote]
    tableau[fila_pivote] = [x / pivot_element for x in tableau[fila_pivote]]
    for i in range(len(tableau)):
        if i != fila_pivote:
            factor = tableau[i][columna_pivote]
            tableau[i] = [a - factor * b for a, b in zip(tableau[i], tableau[fila_pivote])]

def simplex():
    num_vars, num_restricciones, funcion_objetivo, restricciones, desigualdades = ingresar_datos()

    # Mostrar formulación inicial
    if mostrar_formulacion(num_vars, num_restricciones, funcion_objetivo, restricciones, desigualdades):
        return simplex()  # Volver a ingresar datos si el usuario elige corregir

    # Convertir a forma estándar y mostrar la formulación convertida
    tableau = convertir_a_forma_estandar(num_vars, num_restricciones, funcion_objetivo, restricciones, desigualdades)
    if mostrar_formulacion_convertida(num_vars, num_restricciones, funcion_objetivo, restricciones):
        return simplex()  # Volver a la formulación original si el usuario lo desea

    # Realizar las iteraciones del método simplex
    iteracion = 0
    imprimir_tabla_simplex(tableau, iteracion)
    while True:
        columna_pivote = buscar_columna_pivote(tableau)
        if columna_pivote == -1:
            break
        fila_pivote = buscar_fila_pivote(tableau, columna_pivote)
        if fila_pivote == -1:
            print("\nSolución ilimitada detectada.")
            return
        pivote(tableau, fila_pivote, columna_pivote)
        iteracion += 1
        imprimir_tabla_simplex(tableau, iteracion)

    imprimir_resultados_ajustado(tableau, num_vars, num_restricciones)

def imprimir_resultados_ajustado(tableau, num_vars, num_restricciones):
    filas = len(tableau) - 1
    columnas = len(tableau[0]) - 1

    print("\nSolución óptima:")

    valores = {f"x{i+1}": 0 for i in range(num_vars)}
    valores.update({f"s{i+1}": 0 for i in range(num_restricciones)})

    for i in range(num_restricciones):
        columna = [tableau[j][i] for j in range(num_restricciones)]
        if columna.count(1) == 1 and columna.count(0) == (num_restricciones - 1):
            fila = columna.index(1)
            valores[f"x{i+1}"] = tableau[fila][-1]

    for i in range(num_vars):
        print(f"Variable x{i+1} = {valores[f'x{i+1}']:.2f}")

    print(f"Valor óptimo de la función objetivo: {tableau[-1][-1]:.2f}")

# Ejecutar el simplex
simplex()
