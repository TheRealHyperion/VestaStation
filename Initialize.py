from BluetoothModule import BluetoothModule;
import Station;
from Firebase import firebase;
import importlib;
import time;
import threading;

sensors = ['TemperatureHumidity']

class Initializer():
    def bluetooth(self):
        bluetoothModule = BluetoothModule()
        bluetoothModule.initialize(1)
        print('Bluetooth initialized')

    def sendReadings(self):
        while True:
            for moduleName in sensors:
                module = importlib.import_module(moduleName)
                values = module.get()
                if not isinstance(values, list):
                    values = [values]
                for value in values:
                    value.update({ 'stationId': self.station['id'] })
                    firebase.send('readings', None, value)
                print(moduleName+' readings sent to firestore')
            time.sleep(self.station['settings']['readingsInterval'])

    def initialize(self):
        Station.initialize()
        self.station = Station.get()
        print('Station:')
        print(self.station)
        firebase.initialize()
        print('Firebase initialized')
        if not 'id' in self.station:
            document = firebase.send('stations', None, self.station)
            Station.set({
                'id': document.id
            })
            self.station['id'] = document.id
            print('New station added to online database')

        bluetoothThread = threading.Thread(target=self.bluetooth)
        bluetoothThread.start()
        readingsThread = threading.Thread(target=self.sendReadings)
        readingsThread.start()

initializer = Initializer()
initializer.initialize()