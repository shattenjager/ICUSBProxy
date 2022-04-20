#!/usr/bin/env python3
'''
Copyright (c) F4HWN Armel. All rights reserved.
Licensed under the MIT license. See LICENSE file in the project root for full license information.
Usage: ./ICUSBProxy.py [<port>]
'''

from http.server import BaseHTTPRequestHandler, HTTPServer
import logging
import cgi
import serial

name = "ICUSBProxy"
version = "0.0.3"

client_timeout = 0.02

class S(BaseHTTPRequestHandler, verbose):
    def _set_response(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()

    def _set_error(self):
        self.send_response(404)
        self.send_header('Content-type', 'text/html')
        self.end_headers()

    def do_GET(self):
        if verbose > 1:        
            logging.info("GET request,\nPath: %s\nHeaders:\n%s\n", str(self.path), str(self.headers))

        civ = str(self.path).split('=')
        civ = civ[1]

        #civ = 'fe,fe,a4,e0,00,56,34,12,07,00,fd,115900,/dev/ttyUSB2'  # Debug trace
        #civ = 'fe,fe,a4,e0,03,fd,115900,/dev/ttyUSB2'                 # Debug trace

        civ = civ.split(',')

        client_serial = civ.pop()
        client_baudrate = civ.pop()
        client_adresse = civ[2]

        try:
            usb = serial.Serial(client_serial, client_baudrate, timeout=client_timeout)
            usb.setDTR(False)
            usb.setRTS(False)            

            # Send command
            command = []

            for value in civ:
                command.append(int(value, 16))

            usb.write(serial.to_bytes(command))

            # Receive response
            response = ''

            data = usb.read(size=16) # Set size to something high
            for value in data:
                response += '{:02x}'.format(value)

            # Check if bad response    
            if(response == "fefee0" + client_adresse + "fafd"):
                response = ''
        except:
            if verbose > 0:
                print('Check if serial device ' + client_serial + ' at ' + client_baudrate + ' is up...')
            self._set_error()

        # End properly
        try:
            self._set_response()
            self.wfile.write("{}".format(response).encode('utf-8'))
        except:
            self._set_error()

    def log_message(self, format, *args):
        return

def run(server_class=HTTPServer, handler_class=S, port=1234, verbose=0):
    if verbose > 1:
        logging.basicConfig(level=logging.INFO)
    server_address = ('', port)
    httpd = server_class(server_address, handler_class, verbose)
    print('Starting ' + name + ' v' + version + ' HTTPD on Port', port)
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    httpd.server_close()
    print('Stopping ' + name + ' v' + version + ' HTTPD...\n')

if __name__ == '__main__':
    from sys import argv

    if len(argv) == 2:
        run(port=int(argv[1]))
    elif len(argv) == 3:
        run(port=int(argv[1]), verbose=int(argv[2]))
    else:
        run()