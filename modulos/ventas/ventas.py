from config.database import obtener_conexion
from rich.console import Console
from rich.table import Table

console = Console()

class Venta:

    def crear_venta(self, cliente_id=None):
        conn = obtener_conexion()
        try:
            with conn.cursor() as cur:
                cur.execute(
                    """INSERT INTO ventas (cliente_id) 
                    VALUES (%s) RETURNING id""",
                    (cliente_id,)
                )
                venta_id = cur.fetchone()[0]
                conn.commit()
                console.print(f"[green]Venta #{venta_id} creada[/green]")
                return venta_id
        except Exception as e:
            conn.rollback()
            console.print(f"[red]Error al crear venta: {e}[/red]")
        finally:
            conn.close()

    def agregar_producto(self, venta_id, producto_id, cantidad):
        conn = obtener_conexion()
        try:
            with conn.cursor() as cur:
                # verificar que la venta esté pendiente
                cur.execute(
                    "SELECT estado FROM ventas WHERE id = %s",
                    (venta_id,)
                )
                venta = cur.fetchone()
                if not venta or venta[0] != 'pendiente':
                    console.print("[yellow]La venta no existe o no está pendiente[/yellow]")
                    return

                # obtener precio del producto
                cur.execute(
                    "SELECT precio_venta, nombre FROM productos WHERE id = %s AND activo = TRUE",
                    (producto_id,)
                )
                producto = cur.fetchone()
                if not producto:
                    console.print("[yellow]Producto no encontrado o inactivo[/yellow]")
                    return

                precio_unitario = producto[0]
                subtotal = precio_unitario * cantidad

                # insertar en detalle_ventas
                cur.execute(
                    """INSERT INTO detalle_ventas (venta_id, producto_id, cantidad, precio_unitario, subtotal)
                    VALUES (%s, %s, %s, %s, %s)""",
                    (venta_id, producto_id, cantidad, precio_unitario, subtotal)
                )

                # actualizar total de la venta
                cur.execute(
                    "UPDATE ventas SET total = total + %s WHERE id = %s",
                    (subtotal, venta_id)
                )

                conn.commit()
                console.print(f"[green]{producto[1]} agregado — subtotal: ${subtotal}[/green]")

        except Exception as e:
            conn.rollback()
            console.print(f"[red]Error al agregar producto: {e}[/red]")
        finally:
            conn.close()

    def eliminar_producto(self, venta_id, producto_id):
        conn = obtener_conexion()
        try:
            with conn.cursor() as cur:
                # verificar que la venta esté pendiente
                cur.execute(
                    "SELECT estado FROM ventas WHERE id = %s",
                    (venta_id,)
                )
                venta = cur.fetchone()
                if not venta or venta[0] != 'pendiente':
                    console.print("[yellow]La venta no existe o no está pendiente[/yellow]")
                    return

                # obtener el subtotal de la línea a eliminar
                cur.execute(
                    "SELECT subtotal FROM detalle_ventas WHERE venta_id = %s AND producto_id = %s",
                    (venta_id, producto_id)
                )
                detalle = cur.fetchone()
                if not detalle:
                    console.print("[yellow]Producto no encontrado en la venta[/yellow]")
                    return

                subtotal = detalle[0]

                # eliminar la línea del detalle
                cur.execute(
                    "DELETE FROM detalle_ventas WHERE venta_id = %s AND producto_id = %s",
                    (venta_id, producto_id)
                )

                # descontar del total de la venta
                cur.execute(
                    "UPDATE ventas SET total = total - %s WHERE id = %s",
                    (subtotal, venta_id)
                )

                conn.commit()
                console.print(f"[green]Producto eliminado de la venta[/green]")

        except Exception as e:
            conn.rollback()
            console.print(f"[red]Error al eliminar producto: {e}[/red]")
        finally:
            conn.close()

    def modificar_cantidad(self, venta_id, producto_id, nueva_cantidad, nuevo_precio=None):
        conn = obtener_conexion()
        try:
            with conn.cursor() as cur:
                # verificar que la venta esté pendiente
                cur.execute(
                    "SELECT estado FROM ventas WHERE id = %s",
                    (venta_id,)
                )
                venta = cur.fetchone()
                if not venta or venta[0] != 'pendiente':
                    console.print("[yellow]La venta no existe o no está pendiente[/yellow]")
                    return

                # obtener precio unitario y subtotal anterior
                cur.execute(
                    "SELECT precio_unitario, subtotal FROM detalle_ventas WHERE venta_id = %s AND producto_id = %s",
                    (venta_id, producto_id)
                )
                detalle = cur.fetchone()
                if not detalle:
                    console.print("[yellow]Producto no encontrado en la venta[/yellow]")
                    return

                precio_unitario = nuevo_precio if nuevo_precio else detalle[0]
                subtotal_anterior = detalle[1]
                nuevo_subtotal = precio_unitario * nueva_cantidad

                # actualizar detalle
                cur.execute(
                    """UPDATE detalle_ventas SET cantidad = %s, precio_unitario = %s, subtotal = %s
                    WHERE venta_id = %s AND producto_id = %s""",
                    (nueva_cantidad, precio_unitario, nuevo_subtotal, venta_id, producto_id)
                )

                # ajustar total de la venta
                cur.execute(
                    "UPDATE ventas SET total = total - %s + %s WHERE id = %s",
                    (subtotal_anterior, nuevo_subtotal, venta_id)
                )

                # si se pasó nuevo precio, actualizar también en la BD
                if nuevo_precio:
                    cur.execute(
                        "UPDATE productos SET precio_venta = %s WHERE id = %s",
                        (nuevo_precio, producto_id)
                    )

                conn.commit()
                console.print(f"[green]Cantidad actualizada — nuevo subtotal: ${nuevo_subtotal}[/green]")

        except Exception as e:
            conn.rollback()
            console.print(f"[red]Error al modificar cantidad: {e}[/red]")
        finally:
            conn.close()

    def registrar_pago(self, venta_id, metodo, monto_recibido):
        conn = obtener_conexion()
        try:
            with conn.cursor() as cur:
                # obtener total de la venta
                cur.execute(
                    "SELECT total, estado FROM ventas WHERE id = %s",
                    (venta_id,)
                )
                venta = cur.fetchone()
                if not venta or venta[1] != 'pendiente':
                    console.print("[yellow]La venta no existe o no está pendiente[/yellow]")
                    return

                total = venta[0]

                if metodo == 'efectivo' and monto_recibido < total:
                    console.print(f"[red]Monto insuficiente. Total: ${total}[/red]")
                    return

                cur.execute(
                    "INSERT INTO pagos_venta (venta_id, metodo, monto) VALUES (%s, %s, %s)",
                    (venta_id, metodo, total)
                )
                conn.commit()

                # mostrar resumen
                console.print(f"Total:          ${total}")
                console.print(f"Monto recibido: ${monto_recibido}")
                if metodo == 'efectivo':
                    vuelto = monto_recibido - total
                    console.print(f"Vuelto:         ${vuelto}")

        except Exception as e:
            conn.rollback()
            console.print(f"[red]Error al registrar pago: {e}[/red]")
        finally:
            conn.close()

    def completar_venta(self, venta_id):
        conn = obtener_conexion()
        try:
            with conn.cursor() as cur:
                # verificar que tenga pago registrado
                cur.execute(
                    "SELECT id FROM pagos_venta WHERE venta_id = %s",
                    (venta_id,)
                )
                if not cur.fetchone():
                    console.print("[yellow]La venta no tiene pago registrado[/yellow]")
                    return

                cur.execute(
                    "UPDATE ventas SET estado = 'completada' WHERE id = %s AND estado = 'pendiente'",
                    (venta_id,)
                )
                conn.commit()
                console.print(f"[green]Venta #{venta_id} completada[/green]")

        except Exception as e:
            conn.rollback()
            console.print(f"[red]Error al completar venta: {e}[/red]")
        finally:
            conn.close()

    def cancelar_venta(self, venta_id):
        conn = obtener_conexion()
        try:
            with conn.cursor() as cur:
                cur.execute(
                    "UPDATE ventas SET estado = 'cancelada' WHERE id = %s AND estado = 'pendiente' RETURNING id",
                    (venta_id,)
                )
                if not cur.fetchone():
                    console.print("[yellow]La venta no existe o no está pendiente[/yellow]")
                    return

                conn.commit()
                console.print(f"[green]Venta #{venta_id} cancelada[/green]")

        except Exception as e:
            conn.rollback()
            console.print(f"[red]Error al cancelar venta: {e}[/red]")
        finally:
            conn.close()