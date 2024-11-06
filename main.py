import sys
import os
from PySide2.QtWidgets import *
from PySide2.QtCore import *
from PySide2.QtGui import *
from qt_material import *
import psutil
from interface import *
import PySide2extn
from multiprocessing import cpu_count
import datetime
import platform
import shutil
from time import sleep
from threading import Thread

platforms = {
    'linux':'Linux',
    'linux1' : 'Linux',
    'linux2':'Linux',
    'darwin':'OS X',
    'win32':'Windows'
}

class MainWindow(QMainWindow):
    def __init__(self):
        QMainWindow.__init__(self)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        #apply_stylesheet(app, theme = 'dark_cyan.xml')

        self.setWindowFlags(QtCore.Qt.FramelessWindowHint)
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground)

        self.shadow = QGraphicsDropShadowEffect(self)
        self.shadow.setBlurRadius(50)
        self.shadow.setXOffset(0)
        self.shadow.setYOffset(0)
        self.shadow.setColor(QtGui.QColor(0,92,157,550))
        self.ui.centralwidget.setGraphicsEffect(self.shadow)

        self.setWindowTitle("UTIL Manager")
        self.setWindowIcon(QtGui.QIcon(r":/icons/icons/airplay.svg"))

        QSizeGrip(self.ui.grip_size)
        self.ui.minimize_window_button.clicked.connect(lambda :self.showMinimized())
        self.ui.close_window_button.clicked.connect(lambda :self.close2())
        self.ui.restore_window_button.clicked.connect(lambda :self.resotre_or_maximize_window())

        self.ui.cpu_page_btn.clicked.connect(lambda :self.ui.stackedWidget.setCurrentWidget(
            self.ui.cpu_and_memory
        ))
        self.ui.battery_page_btn.clicked.connect(lambda: self.ui.stackedWidget.setCurrentWidget(
            self.ui.battery
        ))
        self.ui.system_inf_pag_btn.clicked.connect(lambda: self.ui.stackedWidget.setCurrentWidget(
            self.ui.system_info
        ))
        self.ui.activity_btn.clicked.connect(lambda: self.ui.stackedWidget.setCurrentWidget(
            self.ui.activity
        ))
        self.ui.sensor_page_btn.clicked.connect(lambda: self.ui.stackedWidget.setCurrentWidget(
            self.ui.sensors
        ))
        self.ui.network_page_btn.clicked.connect(lambda: self.ui.stackedWidget.setCurrentWidget(
            self.ui.network
        ))
        self.ui.storage_btn.clicked.connect(lambda: self.ui.stackedWidget.setCurrentWidget(
            self.ui.storage
        ))

        def moveWindow(e):
            if not self.isMaximized():
                if e.buttons() == QtCore.Qt.LeftButton:
                    self.move(self.pos() + e.globalPos() - self.clickPosition)
                    self.clickPosition = e.globalPos()
                    e.accept()

        self.ui.header.mouseMoveEvent = moveWindow
        self.ui.menu_button.clicked.connect(lambda: self.slideLeftMenu())
        for w in self.ui.menu_fram.findChildren(QPushButton):
            w.clicked.connect(self.applyButtonStyle)

        #self.threadpool = QThreadPool()

        self.show()
        #self.battery()
        #self.cpu_ram()
        self.systemInformation()
        self.processes()
        self.storage()
        self.sensors()
        self.networks()
        self.flag = True    # for terminating the loop
        self.psutil_thread()

    def psutil_thread(self):
        self.t1 = Thread(target= self.cpu_ram)
        self.t2 = Thread(target= self.battery)
        self.t1.start()
        self.t2.start()
    def mousePressEvent(self, event):
        self.clickPosition = event.globalPos()
    def resotre_or_maximize_window(self):
        if self.isMaximized():
            self.showNormal()
            self.ui.restore_window_button.setIcon(QtGui.QIcon(":/icons/icons/maximize-2.svg"))

        else:
            self.showMaximized()
            self.ui.restore_window_button.setIcon(QtGui.QIcon(":/icons/icons/minimize-2.svg"))
    def close2(self):
        self.flag = False   # stop loop of cpu_ram and battery
        self.t1.join()  # stop thread
        self.t2.join()
        self.close()    # close the main window
    def slideLeftMenu(self):

        width = self.ui.left_menu_cont.width()
        if width == 40:
            newWidth = 160
        else:
            newWidth = 40

        self.animate = QtCore.QPropertyAnimation(self.ui.left_menu_cont, b'minimumWidth')
        self.animate.setDuration(250)
        self.animate.setStartValue(width)
        self.animate.setEndValue(newWidth)
        self.animate.setEasingCurve(QtCore.QEasingCurve.InOutQuart)
        self.animate.start()
    def applyButtonStyle(self):
        for w in self.ui.menu_fram.findChildren(QPushButton):
            if w.objectName() != self.sender().objectName():
                w.setStyleSheet('border-bottom: none;')

        self.sender().setStyleSheet('border-bottom: 2px solid;')
        return
    def create_table_widget(self, rowPosition, columnPosition, text, tableName):
        """this function is now for nothing"""
        qtablewidgetitem = QTableWidgetItem()
        getattr(self.ui, tableName).setItem(rowPosition, columnPosition, qtablewidgetitem)
        qtablewidgetitem = getattr(self.ui, tableName).item(rowPosition, columnPosition)
        qtablewidgetitem.setText(text)

    def battery(self):
        while self.flag:
            battery = psutil.sensors_battery()
            if not hasattr(psutil, 'sensors_battery'):
                self.ui.label_37.setText("Platform not supported")
            if battery is None:
                self.ui.label_37.setText("No battery installed")
            if battery.power_plugged:
                self.ui.label_38.setText(str(round(battery.percent, 2)) +"%")
                self.ui.label_39.setText("N/A")
                if battery.percent < 100:
                    self.ui.label_37.setText("Charging")
                else:
                    self.ui.label_37.setText("Fully Charged")
                self.ui.label_40.setText("Yes")
            else:
                self.ui.label_38.setText(str(round(battery.percent, 2)) +"%")
                self.ui.label_39.setText(self.secs2hours(battery.secsleft))
                if battery.percent < 100:
                    self.ui.label_37.setText("Discharging")
                else:
                    self.ui.label_37.setText("Full charged")
                self.ui.label_40.setText("No")


            self.ui.battery_usage.rpb_setMaximum(100)
            self.ui.battery_usage.rpb_setValue(battery.percent)
            self.ui.battery_usage.rpb_setBarStyle('Hybrid2')
            self.ui.battery_usage.rpb_setLineColor((255,30,99))
            self.ui.battery_usage.rpb_setPieColor((47, 74, 83))
            self.ui.battery_usage.rpb_setTextColor((255, 255, 255))
            self.ui.battery_usage.rpb_setInitialPos('West')
            self.ui.battery_usage.rpb_setTextFormat('percentage')
            self.ui.battery_usage.rpb_setLineWidth(15)
            self.ui.battery_usage.rpb_setPathWidth(15)
            self.ui.battery_usage.rpb_setLineCap('RoundCap')

            sleep(1)
    def secs2hours(self, sec):
        mn, ss = divmod(sec, 60)
        hr, mn = divmod(mn, 60)
        return "%d:%02d:%02d (H:M:S)" % (hr, mn, ss)

    def cpu_ram(self):
        _translate = QtCore.QCoreApplication.translate
        while self.flag:
            totalRam = 1.0
            totalRam = psutil.virtual_memory()[0] * totalRam
            totalRam = totalRam / (1024*1024*1024)
            #self.ui.label_27.setText(str("{:.4f}".format(totalRam)) + " GB")
            self.ui.label_27.setText(_translate("MainWindow",
            "<html><head/><body><p><span style=\" color:rgb(6,233,38);\">"+str("{:.4f}".format(totalRam)) + " GB"+"</span></p></body></html>"))

            avilableRam = 1.0
            avilableRam = psutil.virtual_memory()[1] * avilableRam
            avilableRam = avilableRam / (1024 * 1024 * 1024)
            #self.ui.label_28.setText(str("{:.4f}".format(avilableRam))+ " GB")
            self.ui.label_28.setText(_translate("MainWindow",
            "<html><head/><body><p><span style=\" color:rgb(6,201,233);\">"+str("{:.4f}".format(avilableRam))+ " GB"+"</span></p></body></html>"))

            ramUsed = 1.0
            ramUsed = psutil.virtual_memory()[3] * ramUsed
            ramUsed = ramUsed / (1024 * 1024 * 1024)
            #self.ui.label_29.setText(str("{:.4f}".format(ramUsed)) + " GB")
            self.ui.label_29.setText(_translate("MainWindow",
            "<html><head/><body><p><span style=\" color:rgb(233,6,201);\">" + str("{:.4f}".format(ramUsed)) + " GB"+ "</span></p></body></html>"))

            ramFree = 1.0
            ramFree = psutil.virtual_memory()[4] * ramFree
            ramFree = ramFree / (1024 * 1024 * 1024)
            self.ui.label_30.setText(str("{:.4f}".format(ramFree)) + " GB")

            rameusage = str(psutil.virtual_memory()[2]) + '%'
            self.ui.label_31.setText(rameusage)

            core = cpu_count()
            self.ui.label_17.setText(str(core))

            cpuPer = psutil.cpu_percent()
            self.ui.label_19.setText(str(cpuPer)+" %")

            cpu_main_core = psutil.cpu_count(logical= False)
            self.ui.label_21.setText(str(cpu_main_core))

            self.ui.cpu_usage.rpb_setMaximum(100)
            self.ui.cpu_usage.rpb_setValue(cpuPer)
            self.ui.cpu_usage.rpb_setBarStyle('Hybrid2')
            self.ui.cpu_usage.rpb_setLineColor((255, 30, 99))
            self.ui.cpu_usage.rpb_setPieColor((47, 74, 83))
            self.ui.cpu_usage.rpb_setTextColor((255, 255, 255))
            self.ui.cpu_usage.rpb_setInitialPos('West')
            self.ui.cpu_usage.rpb_setTextFormat('percentage')
            self.ui.cpu_usage.rpb_setTextFont('Arial')
            self.ui.cpu_usage.rpb_setLineWidth(15)
            self.ui.cpu_usage.rpb_setPathWidth(15)
            self.ui.cpu_usage.rpb_setLineCap('RoundCap')

            self.ui.ram_usage.spb_setMinimum((0,0,0))
            self.ui.ram_usage.spb_setMaximum((totalRam, totalRam, totalRam))
            self.ui.ram_usage.spb_setValue((avilableRam, ramUsed, ramFree))
            self.ui.ram_usage.spb_lineColor(((6,233,38), (6,201,233), (233,6,201)))
            self.ui.ram_usage.spb_setInitialPos(('West', 'West', 'West'))
            self.ui.ram_usage.spb_lineWidth(15)
            self.ui.ram_usage.spb_lineStyle(('SolidLine', 'SolidLine', 'SolidLine'))
            self.ui.ram_usage.spb_lineCap(('RoundCap', 'RoundCap', 'RoundCap'))
            self.ui.ram_usage.spb_setPathHidden(True)
            sleep(1)
    def systemInformation(self):
        time = datetime.datetime.now().strftime("%H: %M: %S")
        self.ui.system_time.setText(str(time))
        date = datetime.datetime.now().strftime("%Y-%m-%d")
        self.ui.system_date.setText(str(date))

        self.ui.machine.setText(platform.machine())
        self.ui.version.setText(platform.version())
        self.ui.platform.setText(platform.platform())
        self.ui.operating_system.setText(platform.system())
        self.ui.processor.setText(platform.processor())
    def processes(self):
        self.ui.tableWidget.horizontalHeader().setStyleSheet("color: rgb(255, 255, 255)"
                    "background-color: rgb(50, 54, 60);")
        for process in psutil.process_iter():
            pid = process.pid
            if pid == 0:
                continue
            rowPosition = self.ui.tableWidget.rowCount()
            self.ui.tableWidget.insertRow(rowPosition)
            try:
                try:
                    create_time = datetime.datetime.fromtimestamp(process.create_time())
                except OSError:
                    create_time = datetime.datetime.fromtimestamp(psutil.boot_time())
                cpu_percentage = process.cpu_percent()
                try:
                    process_priorty = str(int(process.nice()))
                except psutil.AccessDenied:
                    process_priorty = 0
                try:
                    memory_usage = process.memory_full_info().uss
                except psutil.AccessDenied:
                    memory_usage = 0
                io_counters = process.io_counters()
                read_bytes = io_counters.read_bytes
                write_bytes = io_counters.write_bytes

                n_thread = process.num_threads()
                try:
                    username = process.username()
                except psutil.AccessDenied:
                    username = 'N/A'
                #self.create_table_widget(rowPosition, 0, str(process.pid), "tableWidget")
                #self.create_table_widget(rowPosition, 1, process.name(), "tableWidget")
                #self.create_table_widget(rowPosition, 2, process.status(), "tableWidget")
                #self.create_table_widget(rowPosition, 3, str(datetime.datetime.utcfromtimestamp(process.create_time()).strftime("%Y-%m-%d %H:%M:%S")), "tableWidget")

                self.ui.tableWidget.setItem(rowPosition, 0, QTableWidgetItem(str(process.pid)))
                self.ui.tableWidget.setItem(rowPosition, 1, QTableWidgetItem(str(process.name())))
                self.ui.tableWidget.setItem(rowPosition, 2, QTableWidgetItem(str(process.status())))
                self.ui.tableWidget.setItem(rowPosition, 3, QTableWidgetItem(str(datetime.datetime.utcfromtimestamp(process.create_time()).strftime("%Y-%m-%d %H:%M:%S"))))
                self.ui.tableWidget.setItem(rowPosition, 4, QTableWidgetItem(str(cpu_percentage)))
                self.ui.tableWidget.setItem(rowPosition, 5, QTableWidgetItem(str(process_priorty)))
                self.ui.tableWidget.setItem(rowPosition, 6, QTableWidgetItem(str(memory_usage)+' mb'))
                self.ui.tableWidget.setItem(rowPosition, 7, QTableWidgetItem(str(read_bytes)))
                self.ui.tableWidget.setItem(rowPosition, 8, QTableWidgetItem(str(write_bytes)))
                self.ui.tableWidget.setItem(rowPosition, 9, QTableWidgetItem(str(n_thread)))
                self.ui.tableWidget.setItem(rowPosition, 10, QTableWidgetItem(str(username)))

                """
                suspend_btn = QPushButton(self.ui.tableWidget)
                suspend_btn.setText('Suspend')
                suspend_btn.setStyleSheet("color:brown")
                self.ui.tableWidget.setCellWidget(rowPosition, 11, suspend_btn)
                suspend_btn.clicked.connect(lambda ch='', pros=psutil.Process(pid):self.suspend(pros))

                resume_btn = QPushButton(self.ui.tableWidget)
                resume_btn.setText('Resume')
                resume_btn.setStyleSheet("color:green")
                self.ui.tableWidget.setCellWidget(rowPosition, 12, resume_btn)
                resume_btn.clicked.connect(lambda ch='', pros=psutil.Process(pid):self.resume(pros))
                """

                kill_btn = QPushButton(self.ui.tableWidget)
                kill_btn.setText('Kill')
                kill_btn.setStyleSheet("color:red")
                self.ui.tableWidget.setCellWidget(rowPosition, 11, kill_btn)
                kill_btn.clicked.connect(lambda ch='', pros=psutil.Process(pid), row = rowPosition:self.kill(pros, row))
            except Exception as e:
                print(e)
        self.ui.activity_search.textChanged.connect(lambda :self.findName())
    def kill(self, pros, row):
        pros.kill()
        self.ui.tableWidget.removeRow(row)
        self.ui.activity_search.clear()
        
    def findName(self):
        name = self.ui.activity_search.text().lower()
        for row in range(self.ui.tableWidget.rowCount()):
            item = self.ui.tableWidget.item(row, 1)
            self.ui.tableWidget.setRowHidden(row, name not in item.text().lower())
    def storage(self):
        #this one has problem
        global platforms
        storage_device = psutil.disk_partitions(all = False)
        z = 0
        for x in storage_device:
            rowPosition = self.ui.storage_table.rowCount()
            self.ui.storage_table.insertRow(rowPosition)

            #self.create_table_widget(rowPosition, 0, x.device, "storage_table")
            #self.create_table_widget(rowPosition, 1, x.mountpoint, "storage_table")
            #self.create_table_widget(rowPosition, 2, x.fstype, "storage_table")
            #self.create_table_widget(rowPosition, 3, x.opts, "storage_table")
            self.ui.storage_table.setItem(rowPosition, 0, QTableWidgetItem(str(x.device)))
            self.ui.storage_table.setItem(rowPosition, 1, QTableWidgetItem(str(x.mountpoint)))
            self.ui.storage_table.setItem(rowPosition, 2, QTableWidgetItem(str(x.fstype)))
            self.ui.storage_table.setItem(rowPosition, 3, QTableWidgetItem(str(x.opts)))

            if sys.platform == 'linux' or sys.platform == 'linux1' or sys.platform == 'linux2':
                #self.create_table_widget(rowPosition, 4, str(x.maxfile), "storage_table")
                #self.create_table_widget(rowPosition, 5, str(x.maxpath), "storage_table")
                self.ui.storage_table.setItem(rowPosition, 4, QTableWidgetItem(str(x.maxfile)))
                self.ui.storage_table.setItem(rowPosition, 5, QTableWidgetItem(str(x.maxpath)))
            else:
                #self.create_table_widget(rowPosition, 4, "Function not available on "+platforms[sys.platform], "storage_table")
                #self.create_table_widget(rowPosition, 5, "Function not available on "+platforms[sys.platform], "storage_table")
                self.ui.storage_table.setItem(rowPosition, 4, QTableWidgetItem("function not available on"))
                self.ui.storage_table.setItem(rowPosition, 5, QTableWidgetItem("function not available on"))
            print(x.mountpoint)
            if os.path.exists(x.mountpoint):
                disk_usage = psutil.disk_usage(x.mountpoint)
                #self.create_table_widget(rowPosition, 6, str((disk_usage.total / (1024 * 1024 * 1024))) + 'GB',
                 #                        'storage_table')
                #self.create_table_widget(rowPosition, 7, str((disk_usage.free / (1024 * 1024 * 1024))) + 'GB',
                 #                        'storage_table')
                #self.create_table_widget(rowPosition, 8, str((disk_usage.used / (1024 * 1024 * 1024))) + 'GB',
                 #                        'storage_table')

                self.ui.storage_table.setItem(rowPosition, 6, QTableWidgetItem(str((disk_usage.total / (1024 * 1024 * 1024))) + ' GB'))
                self.ui.storage_table.setItem(rowPosition, 7, QTableWidgetItem(str((disk_usage.free / (1024 * 1024 * 1024))) + ' GB'))
                self.ui.storage_table.setItem(rowPosition, 8, QTableWidgetItem(str((disk_usage.used / (1024 * 1024 * 1024))) + ' GB'))

                full_disk = (disk_usage.used / disk_usage.total) *100
                progressBar = QProgressBar(self.ui.storage_table)
                progressBar.setObjectName('progressBar')
                progressBar.setValue(full_disk)
                self.ui.storage_table.setCellWidget(rowPosition, 9, progressBar)

        #print(os.path.exists('F:\\'))
    def sensors(self):
        if sys.platform == 'linux' or sys.platform == 'linux1' or sys.platform == 'linux2':
            for x in psutil.sensors_temperatures():
                for y in psutil.sensors_temperatures()[x]:
                    rowPosition = self.ui.sensor_table.rowCount()
                    self.ui.sensor_table.insertRow(rowPosition)

                    #self.create_table_widget(rowPosition, 0, x, 'sensor_table')
                    #self.ui.sensor_table.setItem(rowPosition, 0, x)
                    #self.create_table_widget(rowPosition, 1, y.label, 'sensor_table')
                    #self.create_table_widget(rowPosition, 2, str(y.current), 'sensor_table')
                    #self.create_table_widget(rowPosition, 3, str(y.high), 'sensor_table')
                    #self.create_table_widget(rowPosition, 4, str(y.critical), 'sensor_table')

                    self.ui.sensor_table.setItem(rowPosition, 0, QTableWidgetItem(x))
                    self.ui.sensor_table.setItem(rowPosition, 0, QTableWidgetItem(y.label))
                    self.ui.sensor_table.setItem(rowPosition, 0, QTableWidgetItem(str(y.current)))
                    self.ui.sensor_table.setItem(rowPosition, 0, QTableWidgetItem(str(y.high)))
                    self.ui.sensor_table.setItem(rowPosition, 0, QTableWidgetItem(str(y.critical)))

                    temp_per = (y.current / y.high) * 100
                    progressBar = QProgressBar(self.ui.sensor_table)
                    progressBar.setObjectName('progressBar')
                    progressBar.setValue(temp_per)
                    self.ui.sensor_table.setCellWidget(rowPosition, 5, progressBar)
        else:
            global platforms
            rowPosition = self.ui.sensor_table.rowCount()
            self.ui.sensor_table.insertRow(rowPosition)
            #self.create_table_widget(rowPosition, 0, 'Function not supported on '+platforms[sys.platform] , 'sensor_table')
            #self.create_table_widget(rowPosition, 1, "N/A", 'sensor_table')
            #self.create_table_widget(rowPosition, 2, "N/A", 'sensor_table')
            #self.create_table_widget(rowPosition, 3, "N/A", 'sensor_table')
            #self.create_table_widget(rowPosition, 4, "N/A", 'sensor_table')
            #self.create_table_widget(rowPosition, 5, "N/A", 'sensor_table')

            self.ui.sensor_table.setItem(rowPosition, 0, QTableWidgetItem(str('Function not supported on '+platforms[sys.platform])))
            self.ui.sensor_table.setItem(rowPosition, 1, QTableWidgetItem("N/A"))
            self.ui.sensor_table.setItem(rowPosition, 2, QTableWidgetItem("N/A"))
            self.ui.sensor_table.setItem(rowPosition, 3, QTableWidgetItem("N/A"))
            self.ui.sensor_table.setItem(rowPosition, 4, QTableWidgetItem("N/A"))
            self.ui.sensor_table.setItem(rowPosition, 5, QTableWidgetItem("N/A"))
    def networks(self):
        for x in psutil.net_if_stats():
            z = psutil.net_if_stats()
            rowPosition = self.ui.net_stat_table.rowCount()
            self.ui.net_stat_table.insertRow(rowPosition)

            #self.create_table_widget(rowPosition, 0, x, 'net_stat_table')
            #self.create_table_widget(rowPosition, 1, str(z[x].isup), 'net_stat_table')
            #self.create_table_widget(rowPosition, 2, str(z[x].duplex), 'net_stat_table')
            #self.create_table_widget(rowPosition, 3, str(z[x].speed), 'net_stat_table')
            #self.create_table_widget(rowPosition, 4, str(z[x].mtu), 'net_stat_table')

            self.ui.net_stat_table.setItem(rowPosition, 0, QTableWidgetItem(x))
            self.ui.net_stat_table.setItem(rowPosition, 1, QTableWidgetItem(str(z[x].isup)))
            self.ui.net_stat_table.setItem(rowPosition, 2, QTableWidgetItem(str(z[x].duplex)))
            self.ui.net_stat_table.setItem(rowPosition, 3, QTableWidgetItem(str(z[x].speed)))
            self.ui.net_stat_table.setItem(rowPosition, 4, QTableWidgetItem(str(z[x].mtu)))

        for x in psutil.net_io_counters(pernic= True):
            z = psutil.net_io_counters(pernic=True)

            rowPosition = self.ui.net_io_counter.rowCount()
            self.ui.net_io_counter.insertRow(rowPosition)
            """
            self.create_table_widget(rowPosition, 0, x, 'net_io_counter')
            self.create_table_widget(rowPosition, 1, str(z[x].bytes_sent), 'net_io_counter')
            self.create_table_widget(rowPosition, 2, str(z[x].bytes_recv), 'net_io_counter')
            self.create_table_widget(rowPosition, 3, str(z[x].packets_sent), 'net_io_counter')
            self.create_table_widget(rowPosition, 4, str(z[x].packets_recv), 'net_io_counter')
            self.create_table_widget(rowPosition, 5, str(z[x].errin), 'net_io_counter')
            self.create_table_widget(rowPosition, 6, str(z[x].errout), 'net_io_counter')
            self.create_table_widget(rowPosition, 7, str(z[x].dropin), 'net_io_counter')
            self.create_table_widget(rowPosition, 8, str(z[x].dropout), 'net_io_counter')
            """
            self.ui.net_io_counter.setItem(rowPosition, 0, QTableWidgetItem(x))
            self.ui.net_io_counter.setItem(rowPosition, 1, QTableWidgetItem(str(z[x].bytes_sent)))
            self.ui.net_io_counter.setItem(rowPosition, 2, QTableWidgetItem(str(z[x].bytes_recv)))
            self.ui.net_io_counter.setItem(rowPosition, 3, QTableWidgetItem(str(z[x].packets_sent)))
            self.ui.net_io_counter.setItem(rowPosition, 4, QTableWidgetItem(str(z[x].packets_recv)))
            self.ui.net_io_counter.setItem(rowPosition, 5, QTableWidgetItem(str(z[x].errin)))
            self.ui.net_io_counter.setItem(rowPosition, 6, QTableWidgetItem(str(z[x].errout)))
            self.ui.net_io_counter.setItem(rowPosition, 7, QTableWidgetItem(str(z[x].dropin)))
            self.ui.net_io_counter.setItem(rowPosition, 8, QTableWidgetItem(str(z[x].dropout)))


        for x in psutil.net_if_addrs():
            z = psutil.net_if_addrs()
            for y in z[x]:
                rowPosition = self.ui.net_address.rowCount()
                self.ui.net_address.insertRow(rowPosition)
                """
                self.create_table_widget(rowPosition, 0, str(x), 'net_address')
                self.create_table_widget(rowPosition, 1, str(y.family), 'net_address')
                self.create_table_widget(rowPosition, 2, str(y.address), 'net_address')
                self.create_table_widget(rowPosition, 3, str(y.netmask), 'net_address')
                self.create_table_widget(rowPosition, 4, str(y.broadcast), 'net_address')
                self.create_table_widget(rowPosition, 5, str(y.ptp), 'net_address')
                """
                self.ui.net_address.setItem(rowPosition, 0, QTableWidgetItem(str(x)))
                self.ui.net_address.setItem(rowPosition, 1, QTableWidgetItem(str(y.family)))
                self.ui.net_address.setItem(rowPosition, 2, QTableWidgetItem(str(y.address)))
                self.ui.net_address.setItem(rowPosition, 3, QTableWidgetItem(str(y.netmask)))
                self.ui.net_address.setItem(rowPosition, 4, QTableWidgetItem(str(y.broadcast)))
                self.ui.net_address.setItem(rowPosition, 5, QTableWidgetItem(str(y.ptp)))

        for x in psutil.net_connections():
            #z = psutil.net_connections()
            rowPosition = self.ui.net_connection.rowCount()
            self.ui.net_connection.insertRow(rowPosition)
            """
            self.create_table_widget(rowPosition, 0, str(x.fd), 'net_connection')
            self.create_table_widget(rowPosition, 1, str(x.family), 'net_connection')
            self.create_table_widget(rowPosition, 2, str(x.type), 'net_connection')
            self.create_table_widget(rowPosition, 3, str(x.laddr), 'net_connection')
            self.create_table_widget(rowPosition, 4, str(x.status), 'net_connection')
            self.create_table_widget(rowPosition, 5, str(x.pid), 'net_connection')
            """
            self.ui.net_connection.setItem(rowPosition, 0, QTableWidgetItem(str(x.fd)))
            self.ui.net_connection.setItem(rowPosition, 1, QTableWidgetItem(str(x.family)))
            self.ui.net_connection.setItem(rowPosition, 2, QTableWidgetItem(str(x.type)))
            self.ui.net_connection.setItem(rowPosition, 3, QTableWidgetItem(str(x.laddr)))
            self.ui.net_connection.setItem(rowPosition, 4, QTableWidgetItem(str(x.raddr)))
            self.ui.net_connection.setItem(rowPosition, 5, QTableWidgetItem(str(x.status)))
            self.ui.net_connection.setItem(rowPosition, 6, QTableWidgetItem(str(x.pid)))
            print(x.pid)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    sys.exit(app.exec_())