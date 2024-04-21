import pandas as pd
import csv
import random
import os.path

def convertir_excel_a_csv(nombre_archivo):
    df = pd.read_excel("dataset.xlsx")
    df.to_csv(nombre_archivo, index=False)

def leer_csv(nombre_archivo):
    datos = []
    with open(nombre_archivo, 'r', newline='', encoding="utf-8") as archivo_csv:
        lector_csv = csv.reader(archivo_csv)
        for fila in lector_csv:
            datos.append(fila)
    return datos

def escribir_csv(nombre_archivo, datos):
    with open(nombre_archivo, 'w', newline='', encoding="utf-8") as archivo_csv:
        escritor_csv = csv.writer(archivo_csv)
        for fila in datos:
            escritor_csv.writerow(fila)

def dataset_positivas(historias_usuario, cantidad_historias):
    dataset = []
    contador_historia = 0
    i = 0 # itera cada fila del arreglo de historias de usuario

    while contador_historia < cantidad_historias:
        fila = historias_usuario[i]
        correcto = fila[2]

        if correcto == "Si":
            dataset.append(fila)
            contador_historia += 1
        i += 1
    
    return dataset

def dataset_negativas(historias_usuario, cantidad_historias):
    dataset = []
    contador_historia = 0
    i = 0 # itera cada fila del matriz de historias de usuario

    while contador_historia < cantidad_historias:
        fila = historias_usuario[i]
        correcto = fila[2]

        if correcto == "No":
            dataset.append(fila)
            contador_historia += 1
        i += 1
    
    return dataset

def ordenar(historias_usuario):
    return sorted(historias_usuario, key=lambda x: int(x[0]))

def desordenar(historias_usuario):
    random.shuffle(historias_usuario)

# Elimina las historias de usuario ya utilizadas
def actualizar_historias_usuario(historias_usuario, dataset):
    return [historia for historia in historias_usuario if historia not in dataset]

def crear_dataset(historias_usuario, numero, cantidad, solo_negativas=False):
    if solo_negativas == False:
        cantidad = cantidad / 2
        historias_usuario = verificar_dataset(historias_usuario, cantidad)
        historias_usuario_positivas = dataset_positivas(historias_usuario, cantidad)
        historias_usuario_negativas = dataset_negativas(historias_usuario, cantidad)
        dataset = ordenar(historias_usuario_positivas + historias_usuario_negativas)
    else:
        historias_usuario = verificar_dataset(historias_usuario, cantidad)
        historias_usuario_negativas = dataset_negativas(historias_usuario, cantidad)
        dataset = ordenar(historias_usuario_negativas)

    return dataset

def verificar_dataset(historias_usuario, cantidad):
    historias_positivas_faltantes = cantidad - obtener_cant_positivas(historias_usuario)
    historias_negativas_faltantes = cantidad - obtener_cant_negativas(historias_usuario)

    if historias_positivas_faltantes > 0 or historias_negativas_faltantes > 0:
        dataset_original = leer_csv("dataset.csv")
        desordenar(dataset_original)

        if historias_positivas_faltantes > 0:
            nuevas_positivas = [historia for historia in dataset_original if historia not in historias_usuario and historia[2] == "Si"]
            historias_usuario.extend(nuevas_positivas[:historias_positivas_faltantes])
        
        if historias_negativas_faltantes > 0:
            nuevas_negativas = [historia for historia in dataset_original if historia not in historias_usuario and historia[2] == "No"]
            historias_usuario.extend(nuevas_negativas[:historias_negativas_faltantes])

    return historias_usuario

def leer_dataset(numero):
    return leer_csv(f"dataset_{numero}.csv")

def obtener_cant_positivas(historias_usuario):
    return len([historia for historia in historias_usuario if historia[2] == "Si"])

def obtener_cant_negativas(historias_usuario):
    return len([historia for historia in historias_usuario if historia[2] == "No"])

def crear_o_leer_dataset(numero, historias_usuario, cantidad, solo_negativas=False):
    nombre_archivo = f"dataset_{numero}.csv"

    if os.path.isfile(nombre_archivo):
        return leer_csv(nombre_archivo)
    else:
        nuevo_dataset = crear_dataset(historias_usuario, numero, cantidad, solo_negativas)
        escribir_csv(f"dataset_{numero}.csv", nuevo_dataset)
        return nuevo_dataset

if __name__ == "__main__":
    nombre_archivo = "dataset.csv"

    # convertir_excel_a_csv(nombre_archivo)

    historias_usuario = leer_csv(nombre_archivo)
    desordenar(historias_usuario)

    dataset_1 = crear_o_leer_dataset(1, historias_usuario, 20)
    dataset_2 = crear_o_leer_dataset(2, historias_usuario, 20)

    historias_usuario = actualizar_historias_usuario(historias_usuario, dataset_1)
    historias_usuario = actualizar_historias_usuario(historias_usuario, dataset_2)

    dataset_3 = crear_o_leer_dataset(3, historias_usuario, 20)

    historias_usuario = leer_csv(nombre_archivo)
    desordenar(historias_usuario)
    
    dataset_4 = crear_o_leer_dataset(4, historias_usuario, 10)
    dataset_5 = crear_o_leer_dataset(5, historias_usuario, 10)

    historias_usuario = leer_csv(nombre_archivo)
    desordenar(historias_usuario)
    
    dataset_6 = crear_o_leer_dataset(6, historias_usuario, 20, True)
