class Libro: 
  def __init__(self, titulo, autor, num_paginas, anio_publicacion): 
    self.titulo = titulo 
    self.autor = autor 
    self.num_paginas = num_paginas 
    self.anio_publicacion = anio_publicacion

class Libro: 
  def __init__(self, titulo, autor, num_paginas, anio_publicacion): 
    self.titulo = titulo 
    self.autor = autor 
    self.num_paginas = num_paginas 
    self.anio_publicacion = anio_publicacion 
  def info_libro(self): 
return f"Título: {self.titulo}, Autor: {self.autor}, Páginas: {self. 
num_paginas}, Año: {self.anio_publicacion}"

class Libro: 
  def __init__(self, titulo, autor, num_paginas, anio_publicacion): 
    self.titulo = titulo 
    self.autor = autor 
    self.num_paginas = num_paginas 
    self.anio_publicacion = anio_publicacion 
  def info_libro(self): 
    return f"Título: {self.titulo}, Autor: {self.autor}, Páginas: {self.num_pagi 
    nas}, Año: {self.anio_publicacion}" 
mi_libro = Libro("Cien años de soledad", "Gabriel García Márquez", 417, 1967) 
print(mi_libro.info_libro())
