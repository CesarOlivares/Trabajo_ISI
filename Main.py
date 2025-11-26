import flet as ft
import flet_map as fm

class GestorMapaB:
    def __init__(self, page: ft.Page):
        self.page = page
        self.page.title = "Mapa Final - Sin errores"
        self.page.theme_mode = ft.ThemeMode.LIGHT
        
        self.marcadores = []
        
        self.construir_interfaz()
        
        # Puntos iniciales
        self.agregar_punto(-33.4489, -70.6693, "Centro", ft.colors.PURPLE)
        self.page.update()

    def agregar_punto(self, lat, lon, tooltip_texto, color):
        nuevo_marcador = fm.Marker(
            content=ft.Icon(
                name="location_on",  # <--- CAMBIO AQUÍ: Usamos texto directo
                color=color, 
                size=40,
                tooltip=tooltip_texto
            ),
            coordinates=fm.MapLatitudeLongitude(lat, lon),
        )
        self.marcadores.append(nuevo_marcador)

    def al_tocar_mapa(self, e):
        # Manejo seguro de coordenadas
        try:
            # Intento 1: Coordenadas directas
            lat = e.coordinates.latitude
            lon = e.coordinates.longitude
        exceptAttributeError:
            try:
                # Intento 2: A veces vienen en 'e.data' (depende versión exacta)
                # Si falla, simplemente imprimimos el error y salimos para no cerrar la app
                print("No se pudieron leer coordenadas:", e)
                return
            except:
                return

        print(f"Clic en: {lat}, {lon}")
        self.agregar_punto(lat, lon, "Nuevo Punto", ft.colors.RED)
        
        # Refrescamos capas
        self.mapa.layers = [self.capa_base, fm.MarkerLayer(markers=self.marcadores)]
        self.mapa.update()

    def construir_interfaz(self):
        # 1. Capa Base
        self.capa_base = fm.TileLayer(
            url_template="https://tile.openstreetmap.org/{z}/{x}/{y}.png"
        )

        # 2. Mapa Principal
        self.mapa = fm.Map(
            expand=True,
            initial_center=fm.MapLatitudeLongitude(-33.4489, -70.6693),
            initial_zoom=12,
            on_tap=self.al_tocar_mapa,
            layers=[
                self.capa_base,
                fm.MarkerLayer(markers=self.marcadores)
            ]
        )

        # Botón limpiar
        btn_reset = ft.FloatingActionButton(
            icon="delete",  # <--- CAMBIO AQUÍ: Usamos texto directo
            bgcolor=ft.colors.RED_400,
            on_click=self.limpiar_mapa
        )

        self.page.add(
            ft.Stack(
                [
                    self.mapa,
                    ft.Container(content=btn_reset, bottom=20, right=20)
                ],
                expand=True
            )
        )

    def limpiar_mapa(self, e):
        self.marcadores.clear()
        self.mapa.layers = [self.capa_base, fm.MarkerLayer(markers=[])]
        self.mapa.update()

def main(page: ft.Page):
    app = GestorMapaB(page)

if __name__ == "__main__":
    ft.app(target=main)
