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
        console.print("0. Volver")
        opcion = input("\nElige una opción: ")

        if opcion == "1":
            termino = input("Nombre o código de barra: ")
            producto.buscar(termino)
        elif opcion == "2":
            nombre = input("Nombre: ")
            categoria = input("Categoría: ")
            unidad = input("Unidad (un/kg): ")
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
        console.print("2. Agregar producto a venta")
        console.print("3. Eliminar producto de venta")
        console.print("4. Modificar cantidad")
        console.print("5. Registrar pago")
        console.print("6. Completar venta")
        console.print("7. Cancelar venta")
        console.print("0. Volver")
        opcion = input("\nElige una opción: ")

        if opcion == "1":
            cliente_id = input("ID del cliente (Enter para omitir): ")
            cliente_id = int(cliente_id) if cliente_id else None
            venta.crear_venta(cliente_id)
        elif opcion == "2":
            venta_id = int(input("ID de la venta: "))
            producto_id = int(input("ID del producto: "))
            cantidad = float(input("Cantidad: "))
            venta.agregar_producto(venta_id, producto_id, cantidad)
        elif opcion == "3":
            venta_id = int(input("ID de la venta: "))
            producto_id = int(input("ID del producto: "))
            venta.eliminar_producto(venta_id, producto_id)
        elif opcion == "4":
            venta_id = int(input("ID de la venta: "))
            producto_id = int(input("ID del producto: "))
            cantidad = float(input("Nueva cantidad: "))
            venta.modificar_cantidad(venta_id, producto_id, cantidad)
        elif opcion == "5":
            venta_id = int(input("ID de la venta: "))
            console.print("Métodos: efectivo / tarjeta / credito")
            metodo = input("Método de pago: ")
            monto = float(input("Monto recibido: "))
            venta.registrar_pago(venta_id, metodo, monto)
        elif opcion == "6":
            venta_id = int(input("ID de la venta: "))
            venta.completar_venta(venta_id)
        elif opcion == "7":
            venta_id = int(input("ID de la venta: "))
            venta.cancelar_venta(venta_id)
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
            pass  # menu_clientes()
        elif opcion == "5":
            pass  # menu_cuentas_cobrar()
        elif opcion == "6":
            pass  # menu_compras()
        elif opcion == "0":
            console.print("[green]Hasta luego[/green]")
            break

if __name__ == "__main__":
    menu_principal()
