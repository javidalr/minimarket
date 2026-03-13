from config.database import obtener_conexion
from rich.console import Console
from rich.table import Table

console = Console()

class Inventario:

    def agregar_stock(self, producto_id, cantidad, fecha_caducidad=None):
        conn = obtener_conexion()
        try:
            with conn.cursor() as cur:
                cur.execute(
                    """INSERT INTO inventario (producto_id, cantidad, fecha_caducidad)
                    VALUES (%s, %s, %s) RETURNING id""",
                    (producto_id, cantidad, fecha_caducidad)
                )
                conn.commit()
                console.print(f"[green]Stock agregado correctamente[/green]")
        except Exception as e:
            conn.rollback()
            console.print(f"[red]Error al agregar stock: {e}[/red]")
        finally:
            conn.close()

    def eliminar_stock(self, producto_id, cantidad):
        conn = obtener_conexion()
        try:
            with conn.cursor() as cur:
                cur.execute(
                    """SELECT id, cantidad, fecha_caducidad
                    FROM inventario
                    WHERE producto_id = %s
                    AND cantidad > 0
                    ORDER BY fecha_caducidad ASC NULLS LAST""",
                    (producto_id,)
                )
                filas = cur.fetchall()

                if not filas:
                    console.print("[yellow]No hay stock para este producto[/yellow]")
                    return

                cantidad_restante = cantidad
                for fila in filas:
                    if cantidad_restante <= 0:
                        break
                    id_fila, stock_fila, fecha = fila
                    if stock_fila <= cantidad_restante:
                        cantidad_restante -= stock_fila
                        cur.execute("DELETE FROM inventario WHERE id = %s", (id_fila,))
                    else:
                        cur.execute(
                            "UPDATE inventario SET cantidad = cantidad - %s WHERE id = %s",
                            (cantidad_restante, id_fila)
                        )
                        cantidad_restante = 0

                conn.commit()
                console.print(f"[green]Stock eliminado correctamente[/green]")
        except Exception as e:
            conn.rollback()
            console.print(f"[red]Error al eliminar stock: {e}[/red]")
        finally:
            conn.close()

    def consultar_stock(self, termino):
        conn = obtener_conexion()
        try:
            with conn.cursor() as cur:
                cur.execute(
                    """SELECT p.nombre, i.cantidad, i.fecha_caducidad, i.fecha_ingreso
                    FROM inventario i
                    JOIN productos p ON p.id = i.producto_id
                    WHERE (p.codigo_barra = %s OR p.nombre ILIKE %s)
                    AND i.cantidad > 0
                    ORDER BY i.fecha_caducidad ASC NULLS LAST""",
                    (termino, f"%{termino}%")
                )
                resultados = cur.fetchall()

                if not resultados:
                    console.print("[yellow]No se encontró stock para este producto[/yellow]")
                    return

                tabla = Table(title="Stock")
                tabla.add_column("Producto")
                tabla.add_column("Cantidad")
                tabla.add_column("Fecha caducidad")
                tabla.add_column("Fecha ingreso")
                for fila in resultados:
                    tabla.add_row(fila[0], str(fila[1]), str(fila[2]) if fila[2] else "-", str(fila[3]))
                console.print(tabla)

        except Exception as e:
            console.print(f"[red]Error al consultar stock: {e}[/red]")
        finally:
            conn.close()

    def alertas_caducidad(self):
        conn = obtener_conexion()
        try:
            with conn.cursor() as cur:
                cur.execute(
                    """SELECT p.nombre, i.cantidad, i.fecha_caducidad
                    FROM inventario i
                    JOIN productos p ON p.id = i.producto_id
                    WHERE i.fecha_caducidad IS NOT NULL
                    AND i.fecha_caducidad <= CURRENT_DATE + INTERVAL '14 days'
                    AND i.cantidad > 0
                    ORDER BY i.fecha_caducidad ASC"""
                )
                resultados = cur.fetchall()

                if not resultados:
                    console.print("[green]No hay productos próximos a vencer[/green]")
                    return

                tabla = Table(title="Alertas de caducidad")
                tabla.add_column("Producto")
                tabla.add_column("Cantidad")
                tabla.add_column("Vence")
                for fila in resultados:
                    tabla.add_row(fila[0], str(fila[1]), str(fila[2]))
                console.print(tabla)

        except Exception as e:
            console.print(f"[red]Error al consultar alertas: {e}[/red]")
        finally:
            conn.close()