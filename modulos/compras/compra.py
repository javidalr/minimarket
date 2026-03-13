from config.database import obtener_conexion
from rich.console import Console
from rich.table import Table

console = Console()

class Compra:

    def crear_compra(self, proveedor):
        conn = obtener_conexion()
        try:
            with conn.cursor() as cur:
                cur.execute(
                    "INSERT INTO compras (proveedor) VALUES (%s) RETURNING id",
                    (proveedor,)
                )
                compra_id = cur.fetchone()[0]
                conn.commit()
                console.print(f"[green]Compra #{compra_id} creada[/green]")
                return compra_id
        except Exception as e:
            conn.rollback()
            console.print(f"[red]Error al crear compra: {e}[/red]")
        finally:
            conn.close()

    def agregar_producto(self, compra_id, producto_id, cantidad, precio_costo):
        conn = obtener_conexion()
        try:
            with conn.cursor() as cur:
                # verificar que la compra exista y esté pendiente
                cur.execute(
                    "SELECT estado FROM compras WHERE id = %s",
                    (compra_id,)
                )
                compra = cur.fetchone()
                if not compra or compra[0] != 'pendiente':
                    console.print("[yellow]La compra no existe o no está pendiente[/yellow]")
                    return

                subtotal = cantidad * precio_costo

                cur.execute(
                    """INSERT INTO detalle_compras (compra_id, producto_id, cantidad, precio_costo, subtotal)
                    VALUES (%s, %s, %s, %s, %s)""",
                    (compra_id, producto_id, cantidad, precio_costo, subtotal)
                )

                cur.execute(
                    "UPDATE compras SET total = total + %s WHERE id = %s",
                    (subtotal, compra_id)
                )

                conn.commit()
                console.print(f"[green]Producto agregado — subtotal: ${subtotal}[/green]")

        except Exception as e:
            conn.rollback()
            console.print(f"[red]Error al agregar producto: {e}[/red]")
        finally:
            conn.close()

    def completar_compra(self, compra_id):
        conn = obtener_conexion()
        try:
            with conn.cursor() as cur:
                # verificar que esté pendiente
                cur.execute(
                    "SELECT estado FROM compras WHERE id = %s",
                    (compra_id,)
                )
                compra = cur.fetchone()
                if not compra or compra[0] != 'pendiente':
                    console.print("[yellow]La compra no existe o no está pendiente[/yellow]")
                    return

                # obtener detalle de la compra
                cur.execute(
                    "SELECT producto_id, cantidad, precio_costo FROM detalle_compras WHERE compra_id = %s",
                    (compra_id,)
                )
                detalle = cur.fetchall()

                for producto_id, cantidad, precio_costo in detalle:
                    # agregar stock al inventario
                    cur.execute(
                        "INSERT INTO inventario (producto_id, cantidad) VALUES (%s, %s)",
                        (producto_id, cantidad)
                    )
                    # actualizar precio de costo en productos
                    cur.execute(
                        "UPDATE productos SET precio_costo = %s WHERE id = %s",
                        (precio_costo, producto_id)
                    )

                # marcar compra como completada
                cur.execute(
                    "UPDATE compras SET estado = 'completada' WHERE id = %s",
                    (compra_id,)
                )

                conn.commit()
                console.print(f"[green]Compra #{compra_id} completada — stock e inventario actualizados[/green]")

        except Exception as e:
            conn.rollback()
            console.print(f"[red]Error al completar compra: {e}[/red]")
        finally:
            conn.close()