#!/usr/bin/env python3
'''
Copyright (c) F4HWN Armel. All rights reserved.
Licensed under the MIT license. See LICENSE file in the project root for full license information.
Usage: ./icom_civ_proxy.py [<port>]
'''

from http.server import BaseHTTPRequestHandler, HTTPServer
import cgi
import serial

client_serial = '/dev/ttyUSB2'
client_baudrate = 115900

class S(BaseHTTPRequestHandler):
    def _set_response(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()

    def do_GET(self):
        self._set_response()

        civ = str(self.path).split('=')
        civ = civ[1]

        usb = serial.Serial(client_serial, client_baudrate, timeout=0.02)
        usb.setDTR(False)
        usb.setRTS(False)

        #civ = 'fe,fe,a4,e0,00,56,34,12,07,00,fd,'  # Debug trace
        #civ = 'fe,fe,a4,e0,03,fd,'                 # Debug trace

        # Send command
        civ = civ[:-1]
        civ = civ.split(',')
        command = []

        for value in civ:
            command.append(int(value, 16))

        usb.write(serial.to_bytes(command))

        # Receive response
        response = ''

        data = usb.read(size=16) # Set size to something high
        for value in data:
            response += '{:02x}'.format(value)

        # End properly
        self.send_response(200)
        self.wfile.write("{}".format(response).encode('utf-8'))

    def log_message(self, format, *args):
        return

def run(server_class=HTTPServer, handler_class=S, port=1234):
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)
    print('Starting httpd on port :', port)
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    httpd.server_close()
    print('Stopping httpd...\n')

if __name__ == '__main__':
    from sys import argv

    if len(argv) == 2:
        run(port=int(argv[1]))
    else:
        run()