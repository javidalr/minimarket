from config.database import obtener_conexion
from rich.console import Console
from modulos.productos.producto import Producto
from modulos.clientes.clientes import Cliente
from modulos.inventario.inventario import Inventario
from modulos.ventas.ventas import Venta
from modulos.cuentas_cobrar.cuenta_cobrar import CuentaCobrar
from modulos.compras.compra import Compra

console = Console()

producto = Producto()
cliente = Cliente()
inventario = Inventario()
venta = Venta()
cuenta_cobrar = CuentaCobrar()
compra = Compra()

def menu_productos():
    while True:
        console.print("\n=== PRODUCTOS ===")
        console.print("1. Buscar producto")
        console.print("2. Crear producto")
        console.print("3. Actualizar precio")
        console.print("4. Activar/Desactivar producto")
        console.print("5. Eliminar producto")
        console.print("0. Volver")
        opcion = input("\nElige una opción: ")

        if opcion == "1":
            termino = input("Nombre o código de barra: ")
            producto.buscar(termino)
        elif opcion == "2":
            nombre = input("Nombre: ")
            console.print("\nCategorías:")
            for i, cat in enumerate(producto.CATEGORIAS, 1):
                console.print(f"{i}. {cat}")
            opcion_cat = int(input("Elige categoría: ")) - 1
            categoria = producto.CATEGORIAS[opcion_cat]
            console.print("\n1. Unidad (un)\n2. Kilogramo (kg)")
            unidad = "un" if input("Unidad: ") == "1" else "kg"
            precio_venta = float(input("Precio venta: "))
            precio_costo = float(input("Precio costo: "))
            codigo_barra = input("Código de barra (opcional): ") or None
            producto.crear(nombre, categoria, unidad, precio_venta, precio_costo, codigo_barra)
        elif opcion == "3":
            termino = input("Nombre o código de barra: ")
            precio = float(input("Nuevo precio: "))
            producto.actualizar_precio(termino, precio)
        elif opcion == "4":
            termino = input("Nombre o código de barra: ")
            producto.desactivar(termino)
        elif opcion == "5":
            termino = input("Nombre o código de barra: ")
            producto.eliminar(termino)
        elif opcion == "0":
            break

def menu_inventario():
    while True:
        console.print("\n=== INVENTARIO ===")
        console.print("1. Consultar stock")
        console.print("2. Agregar stock")
        console.print("3. Eliminar stock")
        console.print("4. Alertas de caducidad")
        console.print("0. Volver")
        opcion = input("\nElige una opción: ")

        if opcion == "1":
            termino = input("Nombre o código de barra: ")
            inventario.consultar_stock(termino)
        elif opcion == "2":
            producto_id = int(input("ID del producto: "))
            cantidad = float(input("Cantidad: "))
            fecha = input("Fecha caducidad (YYYY-MM-DD) o Enter para omitir: ") or None
            inventario.agregar_stock(producto_id, cantidad, fecha)
        elif opcion == "3":
            producto_id = int(input("ID del producto: "))
            cantidad = float(input("Cantidad a eliminar: "))
            inventario.eliminar_stock(producto_id, cantidad)
        elif opcion == "4":
            inventario.alertas_caducidad()
        elif opcion == "0":
            break

def menu_ventas():
    while True:
        console.print("\n=== VENTAS ===")
        console.print("1. Nueva venta")
        console.print("2. Ver detalle de venta")
        console.print("3. Cancelar venta")
        console.print("4. Eliminar venta")
        console.print("0. Volver")
        opcion = input("\nElige una opción: ")

        if opcion == "1":
            venta_id = venta.crear_venta()
            if not venta_id:
                continue

            while True:
                console.print("\n[cyan]Agregar producto (Enter para terminar)[/cyan]")
                termino = input("Nombre o código de barra: ")
                if not termino:
                    break
                resultado = venta.buscar_producto(termino)
                if not resultado:
                    continue
                producto_id, nombre, precio = resultado
                cantidad = float(input(f"Cantidad ({nombre} - ${precio}): "))
                venta.agregar_producto(venta_id, producto_id, cantidad)

            total = venta.obtener_total(venta_id)
            pendiente = total
            console.print(f"\n[bold]Total: ${total:.0f}[/bold]")

            metodos = {"1": "efectivo", "2": "tarjeta", "3": "credito"}

            while pendiente > 0:
                console.print(f"\n[cyan]Pendiente: ${pendiente:.0f}[/cyan]")
                console.print("1. Efectivo  2. Tarjeta  3. Crédito")
                opcion_pago = input("Método de pago: ")
                metodo = metodos.get(opcion_pago)
                if not metodo:
                    console.print("[red]Opción no válida[/red]")
                    continue

                if metodo == 'efectivo':
                    monto_recibido = float(input(f"Monto recibido: "))
                    if monto_recibido <= 0:
                        console.print("[red]Monto inválido[/red]")
                        continue
                    monto_pago = min(monto_recibido, pendiente)
                    venta.registrar_pago(venta_id, metodo, monto_pago)
                    vuelto = monto_recibido - pendiente
                    if vuelto > 0:
                        console.print(f"[green]Vuelto: ${vuelto:.0f}[/green]")
                    pendiente -= monto_pago

                elif metodo == 'tarjeta':
                    venta.registrar_pago(venta_id, metodo, pendiente)
                    pendiente = 0

                elif metodo == 'credito':
                    cliente_id = venta.seleccionar_cliente(cliente)
                    if cliente_id:
                        venta.asignar_cliente(venta_id, cliente_id)
                    venta.registrar_pago(venta_id, metodo, pendiente)
                    pendiente = 0

            venta.completar_venta(venta_id)


        elif opcion == "2":
            from datetime import date, timedelta
            console.print("\n¿Qué ventas quieres ver?")
            console.print("1. Hoy")
            console.print("2. Esta semana")
            console.print("3. Este mes")
            console.print("4. Rango de fechas")
            console.print("5. Todas")
            filtro = input("Filtro: ")

            hoy = date.today()
            fecha_desde = None
            fecha_hasta = None

            if filtro == "1":
                fecha_desde = hoy
                fecha_hasta = hoy
            elif filtro == "2":
                fecha_desde = hoy - timedelta(days=hoy.weekday())
                fecha_hasta = hoy
            elif filtro == "3":
                fecha_desde = hoy.replace(day=1)
                fecha_hasta = hoy
            elif filtro == "4":
                fecha_desde = input("Fecha desde (YYYY-MM-DD): ")
                fecha_hasta = input("Fecha hasta (YYYY-MM-DD): ")
            # filtro == "5": sin fechas, trae todo

            venta.listar_ventas(fecha_desde=fecha_desde, fecha_hasta=fecha_hasta)
            venta_id_str = input("\nID de la venta a ver (Enter para cancelar): ")
            if venta_id_str:
                venta.ver_detalle(int(venta_id_str))

        elif opcion == "3":
            venta_id = int(input("ID de la venta: "))
            venta.cancelar_venta(venta_id)

        elif opcion == "4":
            venta_id = int(input("ID de la venta: "))
            venta.eliminar_venta(venta_id)

        elif opcion == "0":
            break

def menu_clientes():
    while True:
        console.print("\n=== CLIENTES ===")
        console.print("1. Buscar cliente")
        console.print("2. Crear cliente")
        console.print("3. Activar/Desactivar cliente")
        console.print("4. Ver historial de compras")
        console.print("0. Volver")
        opcion = input("\nElige una opción: ")

        if opcion == "1":
            termino = input("Nombre o ID: ")
            cliente.buscar(termino)
        elif opcion == "2":
            nombre = input("Nombre: ")
            cliente.crear(nombre)
        elif opcion == "3":
            termino = input("Nombre o ID: ")
            cliente.desactivar(termino)
        elif opcion == "4":
            termino = input("Nombre o ID del cliente: ")
            if cliente.ver_historial(termino):
                venta_id_str = input("\nID de venta a ver en detalle (Enter para cancelar): ")
                if venta_id_str:
                    venta.ver_detalle(int(venta_id_str))
        elif opcion == "0":
            break

def menu_principal():
    while True:
        console.print("\n=== MINIMARKET ===")
        console.print("1. Productos")
        console.print("2. Inventario")
        console.print("3. Ventas")
        console.print("4. Clientes")
        console.print("5. Cuentas por cobrar")
        console.print("6. Compras")
        console.print("0. Salir")
        opcion = input("\nElige una opción: ")

        if opcion == "1":
            menu_productos()
        elif opcion == "2":
            menu_inventario()
        elif opcion == "3":
            menu_ventas()
        elif opcion == "4":
            menu_clientes()
        elif opcion == "5":
            pass  # menu_cuentas_cobrar()
        elif opcion == "6":
            pass  # menu_compras()
        elif opcion == "0":
            console.print("[green]Hasta luego[/green]")
            break

if __name__ == "__main__":
    menu_principal()
