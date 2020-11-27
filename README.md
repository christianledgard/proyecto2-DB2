# Proyecto 2 - Base de Datos 2
Franco, Ledgard & Reátegui - CS UTEC

## Introducción
### Objetivo del proyecto

Hoy en día las bases de datos son indispensables en nuestra sociedad. En ese contexto, resulta necesario una forma estructurada de manejar grandes volúmenes de información y hacer búsquedas en ella. En este proyecto nosotros nos enfocaremos en la elaboración de un **índice invertido** de tipo Block-Sorted, el cual será usado como estructura que funcione de soporte para un motor de búsqueda basada en contenido.

### Descripción del dominio de datos

En este proyecto utilizaremos como dataset un conjunto de decenas de miles de Tweets, en los cuales se realizarán las búsquedas e inserciones. Consideramos que es una cantidad adecuada de tuplas para realizar todas nuestras pruebas, validaciones, test y experimentos. 

## Funcionamiento

### Preprocesamiento

Para preprocesar los tweets, usamos la librería `nltk` de Python. Para cada archivo con tweets, generamos los tokens, removemos los tokens del stoplist y finalmente aplicamos STEMMING para tomar únicamente la raíz de cada palabra. La función que realiza esta labor sobre los textos de un tweet se llama `preprocesamiento`.

Este proceso es clave para construir un índice invertido eficiente y relevante. Asimismo, el hallar las raizes de las palabras nos permite que nuestra búsqueda sea más precisa, cubriendo así una mayor cantidad de tweets relevantes.

### Construcción del Índice

A continuación, describiremos las funciones que componen a `bsb_index_construction`, que se encarga de construir el índice.

La función `procesar_index` se encarga de aplicar el preprocesamiento descrito anteriormente, y de hallar el índice invertido de un archivo con tweets. Nótese que se procesa uno a uno cada archivo de tweets con el objetivo de que no se cargue toda la información directamente a memoria principal. Por otro lado, en dicha función aprovechamos para calcular la cantidad de tweets totales en todos los documentos para poder hallar el TF-IDF posteriormente.

Esta función halla el índice invertido de la siguiente manera. Mientras que recorremos los tweets, vamos guardando en un diccionario las palabras preprocesadas como valor, y el ID del tweet en el que aparecen como llave. Asimismo, vamos guardando en una lista estas palabras, debido a que serán utilizadas posteriormente para hallar la frecuencia de las palabras en todos los archivos. Una vez tengamos estos datos, podemos proceder a hallar el índice invertido del archivo procesado usando la función `generar_index`.

En dicha función recorremos todas las palabras de nuestros tweets para después hallar la coindicendia de la palabra en todos los demás tweets. Esto lo hacemos recorriendo todos los elementos del `index_list` y agregando un contador `+1` cada vez que dicha palabra es encontrada. Finalmente, ordenamos nuestro índice de manera alfabética decreciente para luego realizar el respectivo merge a de los bloques.

Hasta el momento, se ha descrito cómo hallar el índice invertido de un solo archivo. Después de haber generado el índice invertido de cada archivo de tweets, procedemos a partir todos estos archivos en bloques de tamaño similar. La función que realiza esta función se llama `generate_index_blocks`. A partir de los índices invertidos hallados en el paso anterior, partimos en una cantidad de bloques (archivos) predefinida por el usuario los índices invertidos. Vamos llenando bloque a bloque, cargando uno por vez a memoria principal. Una vez se haya llenado un bloque, lo ordenamos y lo escribimos en memoria secundaria.

A partir de los índices invertidos de tamaño similar y ordenados del paso anterior, realizamos el merge de cada uno de esos bloques, usando la función `merge_all_blocks`. Esta función realiza el merge tal como se describe en la diapositiva 45 de la clase de Text Document Retrieval. Va cargando bloque a bloque los inputs, compara los inputs, y lo pasa al bloque de output en memoria principal. Nótese que esta función hace uso de memoria secundaria, y carga como mucho 3 bloques a memoria secundaria por vez (2 bloques de input y 1 de output). Una vez se llena este bloque de output, se escribe a memoria secundaria. Se realiza esta operación log2(bloques_totales) veces para realizar el merge satisfactoriamente, ya que en cada iteración se va ordenando un subgrupo de bloques. Una vez se han realizado todas las iteraciones, la función termina satisfactoriamente, habiendo ordenado los bloques del índice invertido de menor a mayor en base al término. Estos bloques se encuentran en la carpeta `sorted_blocks`.

Con todo esto, se da por terminada la construcción del índice invertido usando BSBI.

Generar el índice invertido (antes del merge) toma **```O(n * t^2)```**, donde n es la cantidad de documentos totales y t es la cantidad de términos máxima en todos los documentos.

Por otro lado, el merge toma **```O(p log(b))```**, donde p es la cantidad de palabras totales en el índice invertido y b es la cantidad de bloques totales.

### Cálculo del TF-IDF

A partir de los bloques mergeados con la construcción del BSBI, podemos proceder a hallar el TF-IDF usando la función `calculate_tf_idf`. Nosotros decidimos guardar el DF y el TF dentro del índice invertido de cada término. Es por ello, que para hallar el TF-IDF, simplemente debemos iterar a través de cada bloque y calcular el TF-IDF de cada documento de cada término. Un ejemplo abajo:

`"hagamosl": [df: 2, [[1038525060129148928, tf: 1, tf-idf: ], [1038525060129148428, tf: 1, tf-idf: ]]]`
`tf-idf = log10(1 + tf) * log10(total_documents / df)`

Nuevamente, estamos cargando bloque por bloque a memoria principal, y una vez hallamos el TF-IDF de todo el bloque, escribimos este resultado en la carpeta `sorted_blocks`.

Asimismo, aprovechamos para calcular la norma de cada documento, y lo guardamos en `documents_norm.json`.

Esta operación toma **```O(nd)```**, donde n es la cantidad de términos distintos del índice invertido, y d es la cantidad máxima de documentos asociados a cada término.

### Resumen de tiempos de ejecución

En definitiva, la operación más costosa es generar el índice invertido, ya que esta operación toma **```O(n * t^2)```**, donde n es la cantidad de documentos totales y t es la cantidad de términos máxima en todos los documentos, lo cual es asintóticamente mayor que el merge **```O(p log(b))```**, donde p es la cantidad de palabras totales en el índice invertido y b es la cantidad de bloques totales) y el cálculo del TF-IDF **```O(nd)```**, donde n es la cantidad de términos distintos del índice invertido, y d es la cantidad máxima de documentos asociados a cada término.

## Frontend

La vista del motor de búsqueda es la siguiente:

![Alt_text](https://i.ibb.co/gj6Rtpw/Captura-de-Pantalla-2020-11-27-a-la-s-11-07-16.png)

Dicho motor cuenta con 2 fucionalidades. La primera es agregar varios archivos JSON con diversos tweets. Estos archivos deberán de contener el cuerpo, ID y fecha del respectivo tweet. Luego, el usuario procederá a seleccionar la cantidad de bloques a dividir dicho índice. Cabe recalcar que el usuario podrá seleccionar entre diversas potencias de dos, ya que realizaremos un merge en nuestro backend. Finalmente, podrá seleccionar "Agregar" para cargarlos, una vez que precione dicho botón, el sistema realizará toda la lógica necesaria para obtener nuestros vectores normalizados.

La segunda funcionalidad es realizar la consulta textual. En ella, el usuario ingresa un conjunto de palabras en lenguaje natural y la cantidad de resultados que desea recuperar en su consulta, en el caso particular y poco probable de que ingrese un número mayor al total de documentos de toda la colección, se retornará la colección completa.

Cabe recalcar que para dicha consulta de tweets estamos utilizando el protocolo REST a nuestro servidor. Esto nos permite una mayor flexibilidad y escalabilidad al mostrar los resultados finales.



### Búsqueda

Para realizar las consultas se está tomando en cuenta la similitud de coseno normalizada. El algoritmo que describe dicho proceso es el siguiente:

```Python
class Query(Q,K):
    scores[N]=0
    norm[N]=load NormFile

    words=preprocess(Q)
    for each word in words:
        documents= binarySearch(word)
        for doc in documents:
            scores[doc]+= tf-idf
    
    for each d in scores:
        scores[d]=scores[d]/norm[d]
    
    sort(scores)

    return top K scores in scores
```

El costo de la consulta es  **```N lg N```**, una complejidad en accesos a memoria secundaria y tiempo de ejecución bastante buena.

### Carga de archivos
Para realizar la carga de archivos, primero limpiamos los directorios utilizados para dicho procesamiento de índices y almacenamiento tweets. Luego, guardamos los archivos cargados por el usuario al directorio ```clean``` para luego inicializar nuestra clase INDEX con los números de bloques previamente ingresados por el usuario. Finalmente, procesamos la data, y si el proceso fue realizado sin inconvenietes, mostramos un mensaje de éxito. Luego de ello, el usuario podrá realizar las consultas sin inconvenietes sobre la data ya caragada.


## Pruebas de uso y presentación
Las pruebas de uso se encuentran en el siguiente video: 
[Link del video](https://drive.google.com/drive/folders/1nxsXNLaz6i0adopcGK6Cm60ZCn4pUPak?usp=sharing)
