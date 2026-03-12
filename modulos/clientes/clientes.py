from config.database import obtener_conexion
from rich.console import Console
from rich.table import Table

console = Console()

class Cliente:
    
    def crear(self, nombre):
        conn = obtener_conexion()
        try:
            with conn.cursor() as cur:
                cur.execute(
                    "INSERT INTO clientes (nombre) VALUES (%s) RETURNING id",
                    (nombre,)
                )
                id_nuevo = cur.fetchone()[0]
                conn.commit()
                console.print(f"[green]Cliente '{nombre}' registrado con ID {id_nuevo}[/green]")
        except Exception as e:
            conn.rollback()
            console.print(f"[red]Error al crear cliente: {e}[/red]")
        finally:
            conn.close()
    
    def buscar(self, termino):
        conn = obtener_conexion()
        try:
            with conn.cursor() as cur:
                cur.execute(
                    """SELECT id, nombre, activo
                    FROM clientes
                    WHERE nombre ILIKE %s""",
                    (f"%{termino}%",)
                )
                resultados = cur.fetchall()

                if not resultados:
                    console.print("[yellow]No se encontraron clientes[/yellow]")
                    return

                tabla = Table(title="Clientes encontrados")
                tabla.add_column("ID")
                tabla.add_column("Nombre")
                tabla.add_column("Estado")
                for fila in resultados:
                    estado = "activo" if fila[2] else "inactivo"
                    tabla.add_row(str(fila[0]), fila[1], estado)
                console.print(tabla)

        except Exception as e:
            console.print(f"[red]Error al buscar cliente: {e}[/red]")
        finally:
            conn.close()
    
    def desactivar(self, termino):
        conn = obtener_conexion()
        try:
            with conn.cursor() as cur:
                cur.execute(
                    """SELECT id, nombre, activo
                    FROM clientes
                    WHERE nombre ILIKE %s""",
                    (f"%{termino}%",)
                )
                resultados = cur.fetchall()

                if not resultados:
                    console.print("[yellow]No se encontraron clientes[/yellow]")
                    return

                if len(resultados) > 1:
                    tabla = Table(title="Clientes encontrados")
                    tabla.add_column("ID")
                    tabla.add_column("Nombre")
                    tabla.add_column("Estado")
                    for fila in resultados:
                        estado = "activo" if fila[2] else "inactivo"
                        tabla.add_row(str(fila[0]), fila[1], estado)
                    console.print(tabla)
                    id_cliente = int(input("¿Cuál ID quieres cambiar? "))
                    if not any(fila[0] == id_cliente for fila in resultados):
                        console.print("[yellow]ID no válido[/yellow]")
                        return
                    cliente_seleccionado = next(fila for fila in resultados if fila[0] == id_cliente)
                else:
                    id_cliente = resultados[0][0]
                    cliente_seleccionado = resultados[0]

                nuevo_estado = not cliente_seleccionado[2]
                cur.execute(
                    "UPDATE clientes SET activo = %s WHERE id = %s RETURNING nombre, activo",
                    (nuevo_estado, id_cliente)
                )
                cliente = cur.fetchone()
                conn.commit()
                estado_texto = "activado" if cliente[1] else "desactivado"
                console.print(f"[green]{cliente[0]} {estado_texto}[/green]")

        except Exception as e:
            conn.rollback()
            console.print(f"[red]Error al cambiar estado: {e}[/red]")
        finally:
            conn.close()