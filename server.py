from PyQt5.QtWidgets import QMainWindow, QApplication, QWidget, QGridLayout, QLabel, QPushButton, QLineEdit, \
    QTextEdit
import sys
import socket
import threading


class ServerWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        widget = QWidget()
        self.setWindowTitle("Le serveur de tchat")
        self.setCentralWidget(widget)
        self.__layout = QGridLayout()
        widget.setLayout(self.__layout)

        self.__startbutton = QPushButton()
        self.__startbutton.setText('Démarrage du server')
        self.__startbutton.clicked.connect(self.__demarrage)
        self.__LabelServer = QLabel('Serveur')
        self.__LineEditServer = QLineEdit('0.0.0.0')
        self.__LineEditServer.setPlaceholderText('Serveur')
        self.__LabelPort = QLabel('Port')
        self.__LineEditPort = QLineEdit('10000')
        self.__LineEditPort.setPlaceholderText('Port')
        self.__LabelMaxUsers = QLabel('Nombre de clients maximum')
        self.__LineEditMaxUsers = QLineEdit('5')
        self.__LineEditMaxUsers.setPlaceholderText('Max Users')
        self.__chatBox = QTextEdit()
        self.__chatBox.setReadOnly(True)
        self.__layout.setRowStretch(4, 0)
        self.__quitbutton = QPushButton('Quitter')
        self.__quitbutton.clicked.connect(self.__quitter)

        self.__layout.addWidget(self.__LabelServer, 0, 0)
        self.__layout.addWidget(self.__LineEditServer, 0, 1)
        self.__layout.addWidget(self.__LabelPort, 1, 0)
        self.__layout.addWidget(self.__LineEditPort, 1, 1)
        self.__layout.addWidget(self.__LabelMaxUsers, 2, 0)
        self.__layout.addWidget(self.__LineEditMaxUsers, 2, 1)
        self.__layout.addWidget(self.__startbutton, 3, 0, 1, 2)
        self.__layout.addWidget(self.__chatBox, 4, 0, 1, 2)
        self.__layout.addWidget(self.__quitbutton, 5, 0, 1, 2)

        self.__serverSocket = socket.socket()
        self.__force_stop = False
        self.__serverStarted = False
        self.__clients = []

    def __demarrage(self) -> None:
        if not self.__serverStarted:
            SERVER = self.__LineEditServer.text()
            PORT = self.__LineEditPort.text()
            USERS = self.__LineEditMaxUsers.text()
            if USERS.isdigit() and PORT.isdigit():
                PORT = int(PORT)
                USERS = int(USERS)
                self.__socket = socket.socket()
                try:
                    self.__socket.bind((SERVER, PORT))
                    self.__socket.listen(USERS)
                    self.__socket.setblocking(False)
                    self.__force_stop = False
                    accept_thread = threading.Thread(target=self.__accept)
                    accept_thread.start()
                    self.__LineEditServer.setDisabled(True)
                    self.__LineEditPort.setDisabled(True)
                    self.__LineEditMaxUsers.setDisabled(True)
                    self.__startbutton.setText('Arrêt du serveur')
                    self.__serverStarted = True
                except:
                    print("Erreur de demarrage du serveur!")
            else:
                print('SVP VEUILLEZ INSERER DES NUMEROS POUR LES CHAMPS: PORT et Clients Maximum!')
        else:
            self.__force_stop = True
            self.__serverStarted = False
            self.__LineEditServer.setDisabled(False)
            self.__LineEditPort.setDisabled(False)
            self.__LineEditMaxUsers.setDisabled(False)
            self.__startbutton.setText('Démarrage du Serveur')
            for i in self.__clients:
                try:
                    i.send('Server closed')
                except:
                    pass
                i.close()
            self.__socket.close()
            self.__socket = None
            self.__chatBox.setText('')
            self.__clients = []

    def __accept(self):
        while not self.__force_stop:
            try:
                conn, addr = self.__socket.accept()
                if conn is not None:
                    threading.Thread(target=self.__listen, args=[conn]).start()
                    self.__clients.append(conn)
            except:
                pass

    def __listen(self, conn):
        cleaned = ''
        while not self.__force_stop and cleaned != 'deco-server':
            try:
                data = conn.recv(1024)
                if data is not None:
                    cleaned = data.decode()
                    if len(cleaned) > 0:
                        self.__chatBox.append(cleaned)
                        for client in self.__clients:
                            if client != conn:
                                client.send(cleaned.encode())
            except:
                pass
        conn.close()
        self.__clients.remove(conn)

    def closeEvent(self, event):
        self.__force_stop = True
        if self.__serverStarted:
            self.__socket.close()
        event.accept()

    def __quitter(self):
        self.close()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = ServerWindow()
    window.show()
    app.exec()
