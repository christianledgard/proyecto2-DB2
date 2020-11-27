# Proyecto 2 - Base de Datos 2
Franco, Ledgard & Reátegui - CS UTEC

# Introducción
## Objetivo del proyecto

Hoy en día las bases de datos son indispensables en nuestra sociedad. En ese contexto, resulta necesario una forma estructurada de manejar grandes volúmenes de información y hacer búsquedas en ella. En este proyecto nosotros nos enfocaremos en la elaboración de un **índice invertido** de tipo Block-Sorted, el cual será usado como estructura que funcione de soporte para un motor de búsqueda basada en contenido.

## Descripción del dominio de datos

En este proyecto utilizaremos como dataset un conjunto de decenas de miles de Tweets, en los cuales se realizarán las búsquedas e inserciones. Consideramos que es una cantidad adecuada de tuplas para realizar todas nuestras pruebas, validaciones, test y experimentos. 

## Resultados que se esperan obtener

El resultado que se desea obtener es un motor de búsqueda para consultas textuales que funcione de forma óptima con una complejidad de tiempo de búsqueda **```O(1)```** y una complejidad de **```O(1)```** para las inserciones.

# Funcionamiento

## Preprocesamiento

Para preprocesar los tweets, usamos la librería `nltk` de Python. Para cada archivo con tweets, generamos los tokens, removemos los tokens del stoplist y finalmente aplicamos STEMMING para tomar únicamente la raíz de cada palabra.

Una vez se preprocese cada tweet de un archivo, como se detalló en el párrafo anterior, se genera el índice invertido a partir de estos tokens. Nótese que se procesa uno a uno cada archivo de tweets con el objetivo de que no se cargue toda la información directamente a memoria principal.

## Construcción del Índice 


## Inserción de nuevo Tweet

## Consultas


# Frontend 

La vista del motor de búsqueda es la siguiente:

![Alt_text](https://i.ibb.co/TR2CFWf/Captura-de-Pantalla-2020-11-24-a-la-s-17-11-40.png)

En ella se introduce la consulta textual y la cantidad de documentos que el usuario desee recuperar en su consulta, en el caso particular y poco probable de que ingrese un número mayor al total de documentos de toda la colección entonces se retorna la colección completa.

# Pruebas de uso y presentación

Link del vídeo: https://drive.google.com/drive/folders/1nxsXNLaz6i0adopcGK6Cm60ZCn4pUPak?usp=sharing
