from tkinter import *
import shelvE
import time
import win32api as win32
import win32con
import os
from PIL import ImageGrab
import ast

tutorial = """CALIBRAGEM DE TRAVE\n
        1. Marque a opção "Ball" antes de começar\n
        2. Colocar a bola no chão ao meio da trave e colocar a câmera centralizada, fazendo com que xReal = 0 e yReal = 0\n
        3. Colocar a bola em frente a trave da esquerda e direita, verificar o valor do xReal no simulador, adicionar os mesmos nos campos adequados\n
        4. Colocar a bola em frente a trave superior, verificar o valor yReal e adicionar ao campo adequado\n
        5. Caso ainda falte um pouco para chegar ao ponto correto, adicione ou tire valores baixos (Exemplo: xReal - 10) ao xReal ou yReal, até que ele se encaixe corretamente nas posições desejadas\n
        """

tutorial_verificacao = True
contPrints = 0

class App(object):
    def __init__(self):
        """Classe de criação da aplicação, frames e atributos ( Botoes, campos, textos, checkbuttons ... )"""

        self.root = Tk()
        self.root.title('Goalkeeper Simulator')
        #self.root.geometry('700x700')
        self.root.resizable(False, False)
        self.angulo = 0

        #Cores
        self.corGoleiro = '#e2c498'
        self.corRede = '#6b6b6b'
        self.corBola = '#e26f4f'

        self.xReal = 0
        self.yReal = 0
        self.x = 0
        self.y = 0
        self.raio = 0
        self.raioDefesa = 60

        #TAMANHO DO SIMULADOR <<<<<<<<<<<<<<<<<<<<<<<<<<<   #PADRAO 200x200
        self.heightCanvas = 400
        self.widthCanvas = 400
        self.tamanhoBola = (5*self.heightCanvas) / 200

        #IMPORTANTE <<<<< É O TAMANHO DA TRAVE NA WEBCAM (600x450 PEGA A WEBCAM TODA COMO REFERENCIA)
        self.xTotalGol = 600
        self.yTotalGol = 450

        #Frame
        self.frameGoleiro = Frame(self.root)
        self.frameGoleiro.pack()
        self.frame1 = Frame(self.root)
        self.frame1.pack(side='top')
        self.frame2 = Frame(self.root)
        self.frame2.pack(side='top')
        self.frame3 = Frame(self.root)
        self.frame3.pack(side='top')
        self.frame4 = Frame(self.root)
        self.frame4.pack(side='top', padx=5, pady=10)
        self.frame5 = Frame(self.root)
        self.frame5.pack(side='top', pady=5)

        #Canvas
        self.canvas = Canvas(self.frameGoleiro, bg='grey', height=self.heightCanvas, width=self.widthCanvas)
        self.canvas.pack()
        self.escala = self.heightCanvas/200

        #Atributos
            #BotaoOn
        self.botaoOn = Button(self.frame1, text='On', width=10, bg='#bababa', command=self.comecar)
        self.rodando = False
        self.botaoOn.pack(pady=10, padx=10, side='left')
            #BotaoReset
        self.botaoReset = Button(self.frame1, text='Reset', width=10, bg='#bababa', command=self.resetar)
        self.botaoReset.pack(side='left')
            #BotaoCalibrar
        self.botaoCalibrar = Button(self.frame1, text='Calibrar', width=10, bg='#bababa', command=self.calibrar)
        self.botaoCalibrar.pack(side='left', padx=10)
            #BotaoConfigurarCorBola
        self.botaoCor = Button(self.frame1, text='Cor Bola', width=10, bg='#bababa', command=self.calibrarCorBola)
        self.botaoCor.pack(side='left')
            #CheckButton Bola ligada
        self.bolaLigada = False
        self.checkbutton = Checkbutton(self.frame1, text='Ball', command=self.habilitarBola)
        self.checkbutton.pack(padx=10, pady=10, side='top')
            #Entradas de calibragem
        self.tituloEsquerda = Label(self.frame2, text='xReal Esquerda:')
        self.tituloEsquerda.pack(side='left')
        self.xCalibrarTraveEsquerda = Entry(self.frame2, width=5)
        self.xCalibrarTraveEsquerda.pack(pady=5, side='left', padx=10)
        self.tituloDireita = Label(self.frame2, text='xReal Direita:')
        self.tituloDireita.pack(side='left')
        self.xCalibrarTraveDireita = Entry(self.frame2, width=5)
        self.xCalibrarTraveDireita.pack(pady=5, side='left', padx=10)
        self.tituloAltura = Label(self.frame2, text='Altura (0 ~ 450):')
        self.tituloAltura.pack(side='left')
        self.yCalibrarTraveAltura = Entry(self.frame2, width=5)
        self.yCalibrarTraveAltura.pack(pady=5, side='top', padx=10)
            #Entrada do raio de defesa
        self.tituloRaio = Label(self.frame3, text='Raio de defesa (Padrão 60):')
        self.tituloRaio.pack(side='left', pady=5, padx=10)
        self.CamporaioDefesa = Entry(self.frame3, width=5)
        self.CamporaioDefesa.pack(side='left')
        self.botaoRaio = Button(self.frame3, text='Enter Raio', bg='#bababa', command=self.validarRaio)
        self.botaoRaio.pack(pady=5, padx=10, side='left')
            #CheckButton p/ porta serial
        self.serialLigada = False
        self.checkbuttonSerial = Checkbutton(self.frame3, text='Send in Serial', variable=self.serialLigada, command=self.sendSerial)
        self.checkbuttonSerial.pack(side='left')
            #Botão p/ abrir o software de reconhecimento
        self.botaoOpenSoftware = Button(self.frame4, text='Abrir Software de reconhecimento', bg='#bababa', command=self.abrirSoftwareReconhecimento)
        self.botaoOpenSoftware.pack(side='left', padx=10)
            #Botão PauseOnGoal
        self.pausarNoGolLigado = False
        self.botaoPauseOnGoal = Button(self.frame4, text='Printscreen: Off', bg='#d32c2c', command=self.printScreenOnGoal)
        self.botaoPauseOnGoal.pack()

            #Campo para caminho printscreen
        self.textPrint = Label(self.frame5, text='Save Print Path: ')
        self.textPrint.pack(side='left')
        self.caminhoPrintScreen = Entry(self.frame5, width=50)
        self.caminhoPrintScreen.pack(side='left')


        #Inicio do simulador
        self.criarSimulador()
        self.root.mainloop()

    def criarSimulador(self):
        """Criar os elementos principais do canvas no simulador"""
        #Trave
        self.canvas.create_rectangle((3*self.escala, 80*self.escala), (200*self.escala, 210*self.escala), fill='white', tag='trave')
        self.canvas.create_rectangle((9*self.escala, 86*self.escala), (192*self.escala, 210*self.escala), fill='black', tag='trave')
        self.canvas.create_polygon((24*self.escala, 95*self.escala), (180*self.escala, 95*self.escala), (180*self.escala, 210*self.escala), (24*self.escala, 210*self.escala), outline='white', width=2, tag='trave')
        self.canvas.create_line((3*self.escala, 80*self.escala), (24*self.escala, 95*self.escala), fill='white', width=3, tag='trave')
        self.canvas.create_line((196*self.escala, 83*self.escala), (180*self.escala, 95*self.escala), fill='white', width=3, tag='trave')

        horizontal = 18
        vertical = 89

        #Rede
        for i in range(20):
            self.canvas.create_line((horizontal*self.escala, 95*self.escala), (horizontal*self.escala, 210*self.escala), fill=self.corRede, width=1, tag='trave')
            self.canvas.create_line((5*self.escala, vertical*self.escala), (200*self.escala, vertical*self.escala), fill=self.corRede, width=1, tag='trave')
            vertical += 10
            horizontal += 10

        p1 = 10*self.escala
        p2 = 30*self.escala

        for i in range(18):
            self.canvas.create_line((p1*self.escala, 80*self.escala), (p2*self.escala, 95*self.escala), fill=self.corRede, width=1, tag='trave')
            self.canvas.create_line((24*self.escala, vertical*self.escala), (180*self.escala, vertical*self.escala), fill=self.corRede, width=1, tag='trave')
            p1 += 10*self.escala
            p2 += 10*self.escala

        #Grama
        self.canvas.create_rectangle((88*self.escala, 180*self.escala), (110*self.escala, 205*self.escala), fill='#707070', outline='black')
        self.canvas.create_line((0*self.escala, 200*self.escala), (250*self.escala, 200*self.escala), fill='green', width=(5*self.heightCanvas) / 200)

        #Textos
        self.canvas.create_text((35*self.escala, 70*self.escala), text='Trave', fill='white', font=('Verdana', 10, 'bold'))
        self.canvas.create_text((60*self.escala, 10*self.escala), text='xReal: {}'.format(self.xReal), fill='white', font=('Verdana', 10, 'bold'), tag='xreal')
        self.canvas.create_text((60*self.escala, 30*self.escala), text='yReal: {}'.format(self.yReal), fill='white', font=('Verdana', 10, 'bold'), tag='yreal')

        self.canvas.create_text((140*self.escala, 10*self.escala), text='x: {}'.format(self.x), fill='white', font=('Verdana', 10, 'bold'), tag='x')
        self.canvas.create_text((140*self.escala, 30*self.escala), text='y: {}'.format(self.y), fill='white', font=('Verdana', 10, 'bold'), tag='y')
        self.canvas.create_text((100*self.escala, 60*self.escala), text='Raio: {}'.format(self.raio), fill='white',font=('Verdana', 10, 'bold'), tag='raio')

        #Goleiro
        self.angulo=90
        self.goleiro = self.canvas.create_arc((7*self.escala, 75*self.escala), (190*self.escala, 300*self.escala), start=-(170 + (self.angulo + 1)), extent=-20, fill=self.corGoleiro, tag='goleiro')
        self.texto = self.canvas.create_text((150*self.escala, 70*self.escala), text='Goleiro: {}º'.format(self.angulo), fill='white', font=('Verdana', 10, 'bold'), tag='textoangulo')

    def calibrarCorBola(self):
        """ Vai abrir o range-detector.py para poder calibrar a cor da bola
        o script precisa estar no mesmo diretorio deste programa """

        path = os.path.abspath("") + '\\range-detector.py'
        os.system(f'py {path} -f HSV -w')


    def abrirSoftwareReconhecimento(self):
        """ Vai abrir o software com o 'os', o script precisa estar no mesmo diretorio deste programa ... (goalkeeper.py) """

        #path = os.path.abspath("") + '\\goalkeeper.py'
        #os.system(f'py {path}')
        win32.WinExec('goalkeeper.bat', win32con.SW_HIDE)

    def printScreenOnGoal(self):
        self.pausarNoGolLigado = not self.pausarNoGolLigado
        if self.pausarNoGolLigado:
            import time
            folderName = time.localtime()
            save_path = os.path.abspath("")
            os.system(f'mkdir {save_path}\\Screenshots\\{str(folderName[3])}-{str(folderName[4])}-{str(folderName[5])}')
            self.pathScreenshot = save_path + f'\\Screenshots\\{str(folderName[3])}-{str(folderName[4])}-{str(folderName[5])}'
            print('Pause on Goal Ligado')
            self.botaoPauseOnGoal['bg'] = '#72d119'
            self.botaoPauseOnGoal['text'] = 'Printscreen: On'
        else:
            print('Pause on Goal Desligado')
            self.botaoPauseOnGoal['bg'] = '#d32c2c'
            self.botaoPauseOnGoal['text'] = 'Printscreen: Off'

    def calibrar(self):
        ''' Vai receber os valores dos campos de calibração e calibrar as traves '''
        # Apresentar Tutorial
        global tutorial_verificacao
        if tutorial_verificacao:
            tutorial_verificacao = not tutorial_verificacao
            win32.MessageBeep(1)
            win32.MessageBox(0, tutorial, 'Tutorial Calibragem')
            try:
                self.xTotalGol = abs(int(self.xCalibrarTraveEsquerda.get())) + abs(int(self.xCalibrarTraveDireita.get()))
                self.yTotalGol = 450 - abs(int(self.yCalibrarTraveAltura.get()))
            except:
                win32.MessageBeep(1)
                win32.MessageBox(0, 'Error: Argumentos em falta...', 'Error')

        else:
            try:
                self.xTotalGol = abs(int(self.xCalibrarTraveEsquerda.get())) + abs(int(self.xCalibrarTraveDireita.get()))
                self.yTotalGol = 450 - abs(int(self.yCalibrarTraveAltura.get()))
            except:
                win32.MessageBeep(1)
                win32.MessageBox(0, 'Error: Argumentos em falta...', 'Error')

    def habilitarBola(self):
        """ Vai ligar a simulação em tempo real da bola, pelo checkbutton 'ball' """
        self.bolaLigada = not self.bolaLigada
        if self.bolaLigada:
            self.xbola = 100*self.escala + ((int(self.xReal)*self.escala * 200*self.escala) / self.xTotalGol*self.escala)  # 600 -> X total da webcam
            self.ybola = 200*self.escala - (int(self.yReal)*self.escala * 200*self.escala) / self.yTotalGol*self.escala  # 450 -> Y total da webcam
            self.bolaSimulacao = self.canvas.create_oval(self.xbola - self.tamanhoBola,
                                                         self.ybola - self.tamanhoBola,
                                                         self.xbola + self.tamanhoBola,
                                                         self.ybola + self.tamanhoBola,
                                                         fill=self.corBola, tag='bola')
        else:
            self.canvas.delete('bola')

    def resetar(self):
        """ Função do botão reset: Descalibrar tudo, retornar tudo ao padrão """

        self.rodando = False
        self.angulo = 90
        self.botaoOn['text'] = 'On'
        self.xTotalGol = 600
        self.yTotalGol = 450
        self.xReal, self.yReal, self.x, self.y, self.raio, self.raioDefesa = '0', '0', '0', '0', '0', 60
        self.canvas.delete('bola')
        self.desenhar()

    def comecar(self):
        """ Botao on: Vai dizer se o programa está rodando ou em pause, caso pause ele ira trava na ultima posicao """

        self.rodando = not self.rodando
        if self.rodando:
            self.botaoOn['text'] = 'Pause'
        else:
            self.botaoOn['text'] = 'On'
        self.aplicar()

    def aplicar(self):
        """ Se o programa estiver rodando (def comecar) ele irá fazer o loop com todas as funções necessarias """
        if self.rodando:
            self.update()
            self.desenhar()
            self.root.after(10, self.aplicar)

    def desenhar(self):
        """ Função que redesenha os itens com novas posições e novos dados, Aqui tmb será tirado o printscreen caso ativado """

        self.canvas.itemconfig('goleiro', start=-(170 + (self.angulo + 1)), extent=-20)
        self.canvas.itemconfig('textoangulo', text='Goleiro: {}º'.format(self.angulo))
        self.canvas.itemconfig('xreal', text='xReal: {}'.format(self.xReal))
        self.canvas.itemconfig('yreal', text='yReal: {}'.format(self.yReal))
        self.canvas.itemconfig('x', text='x: {}'.format(self.x))
        self.canvas.itemconfig('y', text='y: {}'.format(self.y))
        self.canvas.itemconfig('raio', text='Raio: {}'.format(self.raio))
        #self.canvas.move('bola', self.xbola, self.ybola)
        if self.bolaLigada:
            global contPrints
            self.canvas.delete(self.bolaSimulacao)
            try:
                if self.raio > 0 and self.raio < self.raioDefesa and int(self.x) > 0 and int(self.y) > 0:
                    """Caso o raio seja menor do que o indicado, a bola ficara verde e será habilitada a defesa"""
                    self.bolaSimulacao = self.canvas.create_oval(self.xbola - self.tamanhoBola,
                                                                 self.ybola - self.tamanhoBola,
                                                                 self.xbola + self.tamanhoBola,
                                                                 self.ybola + self.tamanhoBola, fill='green',
                                                                 tag='bola')
                    print('Defender: {}'.format(self.angulo))

                    if self.pausarNoGolLigado and self.yReal > -10:
                        win32.MessageBeep(1)
                        img = ImageGrab.grab()
                        #img.show()
                        try:
                            #Getting path of the program
                            img.save("{}\\goalPhoto{}.jpg".format(self.pathScreenshot, contPrints))
                            contPrints += 1

                        except:
                            win32.MessageBox(0, 'Caminho inválido', 'Erro Print')
                            self.comecar()

                        time.sleep(0.3)

                else:
                    self.bolaSimulacao = self.canvas.create_oval(self.xbola - self.tamanhoBola,
                                                                 self.ybola - self.tamanhoBola,
                                                                 self.xbola + self.tamanhoBola,
                                                                 self.ybola + self.tamanhoBola, fill=self.corBola,
                                                                 tag='bola')
            except:
                pass

    def validarRaio(self):
        """ Função do botao do RAIO, que vai receber o novo raio de atuação """
        self.raioDefesa = int(self.CamporaioDefesa.get())

    def update(self):
        """ Função que irá atualizar os dados para poder passar para a parte do redesenho, recebe os dados do banco shelve e passa para as outras funções """

        try:
            banco = shelvE.open('dados.db')
            #Angulo Refined
            self.angulo = int(banco.get('angulo'))
            cinco = int(self.angulo / 5) #Devolve os angulos de 5 em cinco
            self.angulo = cinco * 5

            if self.angulo <= 5 and self.angulo > -20:
                self.angulo = 5
            elif self.angulo <= -170 or self.angulo > 175:
                self.angulo = 175
            elif self.angulo <= -20:
                self.angulo = 90

            self.xReal = banco.get('xreal')
            self.yReal = banco.get('yreal')
            self.x = banco.get('x')
            self.y = banco.get('y')
            self.raio = banco.get('raio')
            self.xbola = (100 + ((int(self.xReal) * 200) / self.xTotalGol))*self.escala
            self.ybola = (200 - ((int(self.yReal) * 200) / self.yTotalGol))*self.escala
            #print('angulo: {}'.format(self.angulo))

            if self.xReal != None and self.yReal != None and self.x != None and self.y != None and self.raio != None:
                self.xReal = int(self.xReal)
                self.yReal = int(self.yReal)
                self.x = int(self.x)
                self.y = int(self.y)
                self.raio = int(self.raio)
            else:
                print('Refazendo update')
                self.update()
        except:
            pass
        finally:
            #time.sleep(0.1)
            try:
                banco.close()
            except:
                print('Evitando erro nao fechamento do banco')
                pass

    def sendSerial(self):
        #TODO Implementação do envio de angulo para arduino.
        self.serialLigada = not self.serialLigada
        if self.serialLigada:
            print('Serial Ligada')
        else:
            print('Serial desativada')
        pass

if __name__ == '__main__':
    App()



