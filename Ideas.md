Generador de LNK:

# Diseño
## Problema con automatización de attachements
Antes de generar el LNK definitivo tengo que generar uno Dummy con el comando de los attachements configurado como si fuese el real. Esto se debe a que uso el tamaño del LNK en el comando para extraer los ficheros y como el tamaño depende directamente del comando primero tengo que escribir el fichero con placeholders en vez de tamaño, calcular el tamaño y luego substituir los placeholders.
Los placeholders tienen que tener el mismo tamaño que tendrán los numeros en el comando real, ya que si cambiamos el comando luego, cambiará el tamaño también.
Lo bueno es que los placeholders siguen un orden "lógocio en el comando" y se puede automatizar. El comando es tal que así:
```
<PREMISAS> $File= gc $lnkpath -Encoding Byte -TotalCount size(AllPrevious+Attachment) -ReadCount size(AllPrevious+Attachment); sc $Path ([byte[]] $File ^| select -Skip size(PreviousToAttachment)) -Encoding Byte
```
Entonces cada placeholder tiene sentido, en el comando Get-Content (GC) va el tamaño de todo lo anterior + el del fichero incluido y en el comando Set-Content (SC) va el tamaño de todo lo anterior para saltarselo.

Entonces ya lo tenemos todo, los PLACEHOLDERS SE PUEDEN PONER FÁCIL. 
Hay dos casos extra que es cuando se pone al principio de todo qeu se ponee l tamaño inicial pero esto se puede tratar como outlier.

Ahora tengo que pensar como guardo la info de los placeholders en un sitio para calcularla luego... YO había pensado en un SET, o en algo indexado por "keys", de esta forma cada attachement tendrá su placeholder indexado por su key:
- 0 el generico total.
- 10 primer placeholder primer tamaño
- 11 primer placeholder, segundo tipo tamaño
- 20 segundo "
- 21 segundo "
...
De hecho, con este tipo de indexación no hace falta ningún tipo de estructura MAP, solo con una array para acordarse de los PlaceHolders ya está... Pero bueno mejor guardar el tamaño para no hacer mil calculos después. Usamos un diccionario.

Esta forma de indexar placeholders tiene un defecto: Solo puedo poner 9 attachments... Pero creo que es suficiente la verdad...

Tengo otra idea para poner más attachments, hacerlo secuencial e incrementar de 2 en 2 el numero de attachment, es decir
- 00000 generico 
- 01 -> Primer attachment primer placeholder
- 02 -> Primer attachment segundo placeholder 
- 03 -> Segundo attachment, primer placeholder 
- 04 -> Segundo attachment, segundo placehodler.
-> Si empezamos a numerar los attachment en 0, esto es att Num + Placeholder position... Hago esto.
Asi puedo hacer muchos más número... Voy a hacer eso.

# Error:
Me está fallando al crear el LNK al ejecutar "shortcut.TargetPath" dice que es Unknown, pero tiene este objeto y funciona bien!! 
Parece ser qiue es porque tengo carácteres en UNICODE??? https://stackoverflow.com/questions/57179274/python3-6-create-win32-shortcut-with-unicode

Esto tiene varias soluciones, con la de activar el UNICODE funciona... Pero en el PC del trabajo no lo tuve que hacer...

No sé en qué momento tengo caracteres no válidos en ASCII, porque la pregunta usa carácteres en japonés peor yo no...

# TODO
- Poder definir el path donde guardar ficheros extraidos.
- Encriptar ficheros -> FIcheros config para clave y tal...
- Default attachment?? QUe sea capaz de crear uno y añadirlo
- Definir el WindowStyle del LNK
- Con tantos parámetros lo mejor sería usar un Config file y pasarselo... Un JSON... Así más fácil añadir también ficheros a acoplar y donde exportarlos y claves encriptación y más items asociados a estos. Y booleanos y demás.
- Rethink loops to improve efficiency. Maybe size calculation and placeholder replacement can be done at the same time...
- Can I combine a command with attachment files???- Ficheros incrustados por defecto los abrirá... pero estaría bien poner opción para definir el comportamiento...


Esto hace algo parecido: https://github.com/tommelo/lnk2pwn/tree/master