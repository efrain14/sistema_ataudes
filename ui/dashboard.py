import customtkinter as ctk
from database.daos import AtaudDAO
from config import UMBRAL_USOS_CRITICO

class DashboardView(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        
        # Configurar grid principal del dashboard
        self.grid_columnconfigure((0, 1, 2), weight=1)
        self.grid_rowconfigure(2, weight=1) # El área de alertas crece

        # 1. Título
        self.lbl_titulo = ctk.CTkLabel(self, text="📊 Dashboard", font=ctk.CTkFont(size=26, weight="bold"))
        self.lbl_titulo.grid(row=0, column=0, columnspan=3, sticky="w", pady=(0, 20), padx=20)

        # 2. Contenedor de Tarjetas (Métricas)
        self.frame_tarjetas = ctk.CTkFrame(self, fg_color="transparent")
        self.frame_tarjetas.grid(row=1, column=0, columnspan=3, sticky="nsew", padx=20)
        for i in range(3):
            self.frame_tarjetas.grid_columnconfigure(i, weight=1)

        # Diccionario para guardar referencias a las etiquetas de las tarjetas
        self.tarjetas = {}
        self.crear_tarjetas_ui()

        # 3. Sección de Alertas Críticas
        self.lbl_alertas_titulo = ctk.CTkLabel(self, text="⚠️ Ataúdes con usos críticos", font=ctk.CTkFont(size=16, weight="bold"))
        self.lbl_alertas_titulo.grid(row=2, column=0, columnspan=3, sticky="w", pady=(20, 5), padx=20)

        self.frame_alertas = ctk.CTkScrollableFrame(self, height=150, fg_color="#3a1a1a")
        self.frame_alertas.grid(row=3, column=0, columnspan=3, sticky="nsew", pady=5, padx=20)

        # 4. Botón Refrescar
        self.btn_refrescar = ctk.CTkButton(self, text="🔄 Refrescar Datos", command=self.refrescar, width=200, height=40)
        self.btn_refrescar.grid(row=4, column=0, columnspan=3, pady=20)

        # Cargar datos iniciales
        self.cargar_datos()

    def crear_tarjetas_ui(self):
        """Crea la estructura visual de las tarjetas una sola vez."""
        configs = [
            ("Total", "#3498db"),
            ("Disponibles", "#27ae60"),
            ("En Uso", "#e67e22"),
            ("En Restauración", "#9b59b6"),
            ("Dados de Baja", "#7f8c8d"),
            ("⚠️ Críticos", "#c0392b"),
        ]
        for i, (titulo, color) in enumerate(configs):
            fila, col = divmod(i, 3)
            
            # Marco de la tarjeta
            card = ctk.CTkFrame(self.frame_tarjetas, corner_radius=12, fg_color=color)
            card.grid(row=fila, column=col, padx=10, pady=10, sticky="nsew")
            
            # Título de la tarjeta
            ctk.CTkLabel(card, text=titulo, font=ctk.CTkFont(size=14, weight="bold")).pack(pady=(15, 5))
            
            # Etiqueta del valor (la que actualizaremos)
            lbl_valor = ctk.CTkLabel(card, text="0", font=ctk.CTkFont(size=36, weight="bold"))
            lbl_valor.pack(pady=(0, 15))
            
            # Guardar referencia para actualizar después
            self.tarjetas[titulo] = lbl_valor

    def cargar_datos(self):
        """Obtiene datos de la BD y actualiza solo el texto de las etiquetas."""
        metricas = AtaudDAO.metricas()
        
        # Mapeo de métricas a las tarjetas
        self.tarjetas["Total"].configure(text=str(metricas["total"]))
        self.tarjetas["Disponibles"].configure(text=str(metricas["disponibles"]))
        self.tarjetas["En Uso"].configure(text=str(metricas["en_uso"]))
        self.tarjetas["En Restauración"].configure(text=str(metricas["restauracion"]))
        self.tarjetas["Dados de Baja"].configure(text=str(metricas["baja"]))
        self.tarjetas["⚠️ Críticos"].configure(text=str(metricas["criticos"]))

        # Actualizar lista de alertas
        for w in self.frame_alertas.winfo_children():
            w.destroy()
            
        criticos = [a for a in AtaudDAO.listar() if a["contador_usos"] >= UMBRAL_USOS_CRITICO and a["estado"] != "Dado de Baja"]
        
        if criticos:
            for a in criticos[:10]: # Mostrar máximo 10 para no saturar
                txt = f"• {a['codigo_qr']} — {a['tipo']} — {a['contador_usos']} usos"
                ctk.CTkLabel(self.frame_alertas, text=txt, text_color="#ff6b6b", anchor="w").pack(fill="x", padx=15, pady=2)
        else:
            ctk.CTkLabel(self.frame_alertas, text="✅ No hay alertas críticas en este momento.", text_color="#2ecc71").pack(pady=20)

    def refrescar(self):
        """Método seguro que solo actualiza datos sin destruir la interfaz."""
        self.cargar_datos()