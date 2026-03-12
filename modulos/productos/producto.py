from config.database import obtener_conexion
from rich.console import Console
from rich.table import Table

console = Console()

class Producto:
    def crear(self, nombre, categoria, unidad_medida, precio_venta, precio_costo, codigo_barra=None):
        conn = obtener_conexion()
        try:
            with conn.cursor() as cur:
                cur.execute(
                    """INSERT INTO productos (nombre, categoria, unidad_medida, precio_venta, precio_costo, codigo_barra)
                    VALUES (%s, %s, %s, %s, %s, %s) RETURNING id""",
                    (nombre, categoria, unidad_medida, precio_venta, precio_costo, codigo_barra)
                )
                id_nuevo = cur.fetchone()[0]
                conn.commit() 
                console.print(f"[green]Producto creado con ID {id_nuevo}[/green]")
                return id_nuevo
        except Exception as e:
            conn.rollback()
            console.print(f"[red]Error al crear producto: {e}[/red]")
        finally:
            conn.close()

    def buscar(self, termino):
        conn = obtener_conexion()
        try:
            with conn.cursor() as cur:
                cur.execute(
                    """SELECT id, codigo_barra, nombre, categoria, precio_venta
                    FROM productos
                    WHERE (codigo_barra = %s OR nombre ILIKE %s)
                    AND activo = TRUE""",
                    (termino, f"%{termino}%")
                )
                resultados = cur.fetchall()

                if not resultados:
                    console.print("[yellow]No se encontraron productos[/yellow]")
                    return

                tabla = Table(title="Productos encontrados")
                tabla.add_column("ID")
                tabla.add_column("Código barra")
                tabla.add_column("Nombre")
                tabla.add_column("Categoría")
                tabla.add_column("Precio venta")

                for fila in resultados:
                    tabla.add_row(str(fila[0]), str(fila[1]), fila[2], fila[3], f"${fila[4]}")

                console.print(tabla)
        except Exception as e:
            console.print(f"[red]Error al buscar producto: {e}[/red]")
        finally:
            conn.close()

    def actualizar_precio(self, termino, nuevo_precio):
        conn = obtener_conexion()
        try:
            with conn.cursor() as cur:
                cur.execute(
                    """SELECT id, codigo_barra, nombre, precio_venta
                    FROM productos
                    WHERE (codigo_barra = %s OR nombre ILIKE %s)
                    AND activo = TRUE""",
                    (termino, f"%{termino}%")
                )
                resultados = cur.fetchall()

                if not resultados:
                    console.print("[yellow]No se encontraron productos[/yellow]")
                    return

                if len(resultados) > 1:
                    tabla = Table(title="Productos encontrados")
                    tabla.add_column("ID")
                    tabla.add_column("Nombre")
                    tabla.add_column("Precio actual")
                    for fila in resultados:
                        tabla.add_row(str(fila[0]), fila[2], f"${fila[3]}")
                    console.print(tabla)
                    id_producto = int(input("¿Cuál ID quieres actualizar? "))
                    if not any(fila[0] == id_producto for fila in resultados):
                        console.print("[yellow]ID no válido[/yellow]")
                        return
                else:
                    id_producto = resultados[0][0]

                cur.execute(
                    "UPDATE productos SET precio_venta = %s WHERE id = %s RETURNING nombre, precio_venta",
                    (nuevo_precio, id_producto)
                )
                producto = cur.fetchone()
                conn.commit()
                console.print(f"[green]{producto[0]} actualizado a ${producto[1]}[/green]")

        except Exception as e:
            conn.rollback()
            console.print(f"[red]Error al actualizar precio: {e}[/red]")
        finally:
            conn.close()

    def desactivar(self, termino):
        conn = obtener_conexion()
        try:
            with conn.cursor() as cur:
                cur.execute(
                    """SELECT id, codigo_barra, nombre, activo
                    FROM productos
                    WHERE (codigo_barra = %s OR nombre ILIKE %s)""",
                    (termino, f"%{termino}%")
                )
                resultados = cur.fetchall()

                if not resultados:
                    console.print("[yellow]No se encontraron productos[/yellow]")
                    return

                if len(resultados) > 1:
                    tabla = Table(title="Productos encontrados")
                    tabla.add_column("ID")
                    tabla.add_column("Nombre")
                    tabla.add_column("Estado")
                    for fila in resultados:
                        estado = "activo" if fila[3] else "inactivo"
                        tabla.add_row(str(fila[0]), fila[2], estado)
                    console.print(tabla)
                    id_producto = int(input("¿Cuál ID quieres cambiar? "))
                    if not any(fila[0] == id_producto for fila in resultados):
                        console.print("[yellow]ID no válido[/yellow]")
                        return
                    producto_seleccionado = next(fila for fila in resultados if fila[0] == id_producto)
                else:
                    id_producto = resultados[0][0]
                    producto_seleccionado = resultados[0]

                nuevo_estado = not producto_seleccionado[3]

                cur.execute(
                    "UPDATE productos SET activo = %s WHERE id = %s RETURNING nombre, activo",
                    (nuevo_estado, id_producto)
                )
                producto = cur.fetchone()
                conn.commit()
                estado_texto = "activado" if producto[1] else "desactivado"
                console.print(f"[green]{producto[0]} {estado_texto}[/green]")

        except Exception as e:
            conn.rollback()
            console.print(f"[red]Error al cambiar estado: {e}[/red]")
        finally:
            conn.close()