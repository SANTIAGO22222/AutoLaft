import sys
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QTreeWidget, QTreeWidgetItem, QProgressBar, QWidget, QFileDialog, QMessageBox,
    QStyleFactory
)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QPalette, QColor, QFont
import pandas as pd
from datetime import datetime

class DarkPalette(QPalette):
    def __init__(self):
        super().__init__()
        self.setColor(QPalette.Window, QColor(53, 53, 53))
        self.setColor(QPalette.WindowText, Qt.white)
        self.setColor(QPalette.Base, QColor(25, 25, 25))
        self.setColor(QPalette.AlternateBase, QColor(53, 53, 53))
        self.setColor(QPalette.ToolTipBase, Qt.white)
        self.setColor(QPalette.ToolTipText, Qt.white)
        self.setColor(QPalette.Text, Qt.white)
        self.setColor(QPalette.Button, QColor(53, 53, 53))
        self.setColor(QPalette.ButtonText, Qt.white)
        self.setColor(QPalette.BrightText, Qt.red)
        self.setColor(QPalette.Link, QColor(42, 130, 218))
        self.setColor(QPalette.Highlight, QColor(42, 130, 218))
        self.setColor(QPalette.HighlightedText, Qt.black)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Autolaft - Sistema Automático de Validación de Datos")
        self.setGeometry(100, 100, 1000, 700)

        # Variables
        self.df = None
        self.archivo_cargado = ""

        # Layout principal
        self.main_widget = QWidget()
        self.setCentralWidget(self.main_widget)
        self.layout = QVBoxLayout()
        self.main_widget.setLayout(self.layout)

        # Título
        self.titulo_label = QLabel("Sistema Automático de Validación de Datos para SAGRILAFT", self)
        self.titulo_label.setAlignment(Qt.AlignCenter)
        self.titulo_label.setStyleSheet("font-size: 22px; font-weight: bold; margin: 20px 0;")
        self.layout.addWidget(self.titulo_label)

        # Tabla Historial
        self.tree_historial = QTreeWidget(self)
        self.tree_historial.setHeaderLabels(["Personas", "ID", "Resultado", "Fecha de Consulta"])
        self.tree_historial.setStyleSheet("""
            QTreeWidget {
                border: 1px solid #3A3A3A;
                border-radius: 4px;
            }
            QTreeWidget::item {
                padding: 5px;
            }
            QHeaderView::section {
                background-color: #2A2A2A;
                padding: 5px;
                border: 1px solid #3A3A3A;
            }
        """)
        self.layout.addWidget(self.tree_historial)

        # Barra de búsqueda
        self.search_layout = QHBoxLayout()
        self.search_label = QLabel("Buscar:")
        self.search_entry = QLineEdit()
        self.search_entry.setStyleSheet("""
            QLineEdit {
                padding: 5px;
                border: 1px solid #3A3A3A;
                border-radius: 4px;
                background-color: #2A2A2A;
            }
        """)
        self.search_button = QPushButton("Buscar")
        self.search_button.clicked.connect(self.buscar_historial)
        self.search_button.setStyleSheet("""
            QPushButton {
                padding: 5px 15px;
                background-color: #0D47A1;
                color: white;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #1565C0;
            }
        """)

        self.search_layout.addWidget(self.search_label)
        self.search_layout.addWidget(self.search_entry)
        self.search_layout.addWidget(self.search_button)
        self.layout.addLayout(self.search_layout)

        # Barra de progreso
        self.progreso = QProgressBar(self)
        self.progreso.setValue(0)
        self.progreso.setStyleSheet("""
            QProgressBar {
                border: 1px solid #3A3A3A;
                border-radius: 4px;
                text-align: center;
            }
            QProgressBar::chunk {
                background-color: #1565C0;
            }
        """)
        self.layout.addWidget(self.progreso)

        # Indicadores de progreso
        self.label_progreso = QLabel("0% completado", self)
        self.layout.addWidget(self.label_progreso)

        # Estadísticas
        self.estadisticas_label = QLabel("", self)
        self.layout.addWidget(self.estadisticas_label)

        # Botones
        self.button_layout = QHBoxLayout()
        self.btn_cargar = QPushButton("Cargar Archivo")
        self.btn_cargar.clicked.connect(self.abrir_archivo)
        self.btn_consulta = QPushButton("Realizar Consulta")
        self.btn_consulta.clicked.connect(self.realizar_consulta)
        self.btn_consulta.setEnabled(False)  # Deshabilitado hasta que se cargue un archivo

        self.btn_nuevo_proceso = QPushButton("Nuevo Proceso")
        self.btn_nuevo_proceso.clicked.connect(self.nuevo_proceso)
        self.btn_nuevo_proceso.setEnabled(False)

        for btn in [self.btn_cargar, self.btn_consulta, self.btn_nuevo_proceso]:
            btn.setStyleSheet("""
                QPushButton {
                    padding: 8px 20px;
                    background-color: #1565C0;
                    color: white;
                    border-radius: 4px;
                }
                QPushButton:hover {
                    background-color: #1976D2;
                }
                QPushButton:disabled {
                    background-color: #555555;
                    color: #888888;
                }
            """)

        self.button_layout.addWidget(self.btn_cargar)
        self.button_layout.addWidget(self.btn_consulta)
        self.button_layout.addWidget(self.btn_nuevo_proceso)
        self.layout.addLayout(self.button_layout)

        # Archivo cargado
        self.label_archivo = QLabel("No se ha cargado ningún archivo", self)
        self.layout.addWidget(self.label_archivo)

    # Función para buscar en la tabla
    def buscar_historial(self):
        search_term = self.search_entry.text().lower()
        for i in range(self.tree_historial.topLevelItemCount()):
            item = self.tree_historial.topLevelItem(i)
            match = any(search_term in item.text(col).lower() for col in range(self.tree_historial.columnCount()))
            self.tree_historial.setItemHidden(item, not match)

    # Función para abrir archivo Excel
    def abrir_archivo(self):
        file_dialog = QFileDialog(self)
        file_path, _ = file_dialog.getOpenFileName(self, "Cargar Archivo", "", "Archivos Excel (*.xlsx)")
        if file_path:
            try:
                self.df = pd.read_excel(file_path)
                self.archivo_cargado = file_path
                self.label_archivo.setText(f"Archivo cargado: {file_path.split('/')[-1]}")
                self.btn_consulta.setEnabled(True)
                self.btn_nuevo_proceso.setEnabled(False)
            except Exception as e:
                QMessageBox.critical(self, "Error", f"No se pudo cargar el archivo: {str(e)}")

    # Función para realizar consulta (simulación)
    def realizar_consulta(self):
        if self.df is None:
            QMessageBox.critical(self, "Error", "Primero debes cargar un archivo.")
            return

        total = len(self.df)
        self.progreso.setValue(0)
        resultados_positivos = 0

        # Simulación de consulta
        for i, row in self.df.iterrows():
            QApplication.processEvents()  # Permite que la interfaz se actualice
            person_id = row['ID']
            person_name = row['Personas']
            results_text = "No results" if i % 2 == 0 else "Resultado positivo"

            # Insertar datos en la tabla
            item = QTreeWidgetItem([person_name, str(person_id), results_text, datetime.now().strftime("%Y-%m-%d")])
            self.tree_historial.addTopLevelItem(item)

            self.progreso.setValue(int((i + 1) / total * 100))
            self.label_progreso.setText(f"{int((i + 1) / total * 100)}% completado")

            if results_text != "No results":
                resultados_positivos += 1

        # Actualizar estadísticas
        self.estadisticas_label.setText(f"Consultas Positivas: {resultados_positivos} / {total}")
        self.btn_nuevo_proceso.setEnabled(True)

    # Función para iniciar nuevo proceso
    def nuevo_proceso(self):
        respuesta = QMessageBox.warning(self, "Advertencia", 
            "Recuerde descargar los datos antes de realizar un nuevo proceso. ¿Desea continuar?", 
            QMessageBox.Ok | QMessageBox.Cancel)

        if respuesta == QMessageBox.Ok:
            self.tree_historial.clear()
            self.label_archivo.setText("No se ha cargado ningún archivo")
            self.progreso.setValue(0)
            self.label_progreso.setText("0% completado")
            self.estadisticas_label.setText("")
            self.btn_consulta.setEnabled(False)
            self.btn_nuevo_proceso.setEnabled(False)
            self.df = None
            self.archivo_cargado = ""

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle(QStyleFactory.create("Fusion"))
    app.setPalette(DarkPalette())
    app.setFont(QFont("Segoe UI", 10))
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())