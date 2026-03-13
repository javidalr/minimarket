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
            pass  # menu_inventario()
        elif opcion == "3":
            pass  # menu_ventas()
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
