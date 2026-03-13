from config.database import obtener_conexion
from rich.console import Console
from rich.table import Table

console = Console()

class CuentaCobrar:

    def crear_cuenta(self, cliente_id, venta_id, monto_total, monto_pagado=0):
        conn = obtener_conexion()
        try:
            with conn.cursor() as cur:
                saldo = monto_total - monto_pagado

                cur.execute(
                    """INSERT INTO cuentas_cobrar (cliente_id, venta_id, monto_total, saldo)
                    VALUES (%s, %s, %s, %s) RETURNING id""",
                    (cliente_id, venta_id, monto_total, saldo)
                )
                cuenta_id = cur.fetchone()[0]

                # activar cliente automáticamente
                cur.execute(
                    "UPDATE clientes SET activo = TRUE WHERE id = %s",
                    (cliente_id,)
                )

                conn.commit()
                console.print(f"[green]Cuenta #{cuenta_id} creada — saldo pendiente: ${saldo}[/green]")
                return cuenta_id

        except Exception as e:
            conn.rollback()
            console.print(f"[red]Error al crear cuenta: {e}[/red]")
        finally:
            conn.close()

    def registrar_abono(self, cliente_id, monto):
        conn = obtener_conexion()
        try:
            with conn.cursor() as cur:
                # obtener cuentas pendientes ordenadas de más antigua a más reciente
                cur.execute(
                    """SELECT id, saldo FROM cuentas_cobrar
                    WHERE cliente_id = %s AND estado = 'pendiente'
                    ORDER BY id ASC""",
                    (cliente_id,)
                )
                cuentas = cur.fetchall()

                if not cuentas:
                    console.print("[yellow]El cliente no tiene cuentas pendientes[/yellow]")
                    return

                monto_restante = monto
                for cuenta_id, saldo in cuentas:
                    if monto_restante <= 0:
                        break

                    if monto_restante >= saldo:
                        # salda esta cuenta completamente
                        monto_restante -= saldo
                        cur.execute(
                            "UPDATE cuentas_cobrar SET saldo = 0, estado = 'pagada' WHERE id = %s",
                            (cuenta_id,)
                        )
                    else:
                        # abono parcial
                        cur.execute(
                            "UPDATE cuentas_cobrar SET saldo = saldo - %s WHERE id = %s",
                            (monto_restante, cuenta_id)
                        )
                        monto_restante = 0

                    # registrar el abono
                    cur.execute(
                        "INSERT INTO abonos (cuenta_id, monto) VALUES (%s, %s)",
                        (cuenta_id, monto)
                    )

                # verificar si el cliente saldó todas sus cuentas
                cur.execute(
                    "SELECT id FROM cuentas_cobrar WHERE cliente_id = %s AND estado = 'pendiente'",
                    (cliente_id,)
                )
                if not cur.fetchone():
                    cur.execute(
                        "UPDATE clientes SET activo = FALSE WHERE id = %s",
                        (cliente_id,)
                    )
                    console.print(f"[green]Cliente sin deudas pendientes — desactivado[/green]")

                conn.commit()
                console.print(f"[green]Abono registrado correctamente[/green]")

        except Exception as e:
            conn.rollback()
            console.print(f"[red]Error al registrar abono: {e}[/red]")
        finally:
            conn.close()

    def consultar_cuenta(self, termino):
        conn = obtener_conexion()
        try:
            with conn.cursor() as cur:
                cur.execute(
                    """SELECT cc.id, c.nombre, cc.monto_total, cc.saldo, cc.estado, cc.fecha
                    FROM cuentas_cobrar cc
                    JOIN clientes c ON c.id = cc.cliente_id
                    WHERE c.nombre ILIKE %s
                    ORDER BY cc.id ASC""",
                    (f"%{termino}%",)
                )
                resultados = cur.fetchall()

                if not resultados:
                    console.print("[yellow]No se encontraron cuentas[/yellow]")
                    return

                tabla = Table(title=f"Cuentas de {termino}")
                tabla.add_column("ID")
                tabla.add_column("Cliente")
                tabla.add_column("Total")
                tabla.add_column("Saldo")
                tabla.add_column("Estado")
                tabla.add_column("Fecha")
                for fila in resultados:
                    tabla.add_row(str(fila[0]), fila[1], f"${fila[2]}", f"${fila[3]}", fila[4], str(fila[5]))
                console.print(tabla)

        except Exception as e:
            console.print(f"[red]Error al consultar cuenta: {e}[/red]")
        finally:
            conn.close()

    def listar_pendientes(self):
        conn = obtener_conexion()
        try:
            with conn.cursor() as cur:
                cur.execute(
                    """SELECT c.nombre, COUNT(cc.id) as cuentas, SUM(cc.saldo) as total_deuda
                    FROM cuentas_cobrar cc
                    JOIN clientes c ON c.id = cc.cliente_id
                    WHERE cc.estado = 'pendiente'
                    GROUP BY c.nombre
                    ORDER BY total_deuda DESC"""
                )
                resultados = cur.fetchall()

                if not resultados:
                    console.print("[green]No hay cuentas pendientes[/green]")
                    return

                tabla = Table(title="Cuentas pendientes")
                tabla.add_column("Cliente")
                tabla.add_column("Cuentas")
                tabla.add_column("Total deuda")
                for fila in resultados:
                    tabla.add_row(fila[0], str(fila[1]), f"${fila[2]}")
                console.print(tabla)

        except Exception as e:
            console.print(f"[red]Error al listar pendientes: {e}[/red]")
        finally:
            conn.close()