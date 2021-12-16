import selectors
import socket
import types
import os
import traceback

try:
    host = '0.0.0.0'
    #port = 5000
    #if 'PORT' in os.environ:
    port = int(os.environ['PORT'])

    sel = selectors.DefaultSelector()
    lsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    lsock.bind((host, port))
    lsock.listen()
    print('listening on', (host, port), flush=True)
    lsock.setblocking(False)
    sel.register(lsock, selectors.EVENT_READ, data=None)

    def accept_wrapper(sock):
        conn, addr = sock.accept()  # Should be ready to read
        print('accepted connection from', addr, flush=True)
        conn.setblocking(False)
        data = types.SimpleNamespace(addr=addr, inb=b'', outb=b'')
        events = selectors.EVENT_READ | selectors.EVENT_WRITE
        sel.register(conn, events, data=data)

    def service_connection(key, mask):
        sock = key.fileobj
        data = key.data
        if mask & selectors.EVENT_READ:
            recv_data = sock.recv(1024)  # Should be ready to read
            if recv_data:
                data.outb += recv_data
            else:
                print('closing connection to', data.addr, flush=True)
                sel.unregister(sock)
                sock.close()
        if mask & selectors.EVENT_WRITE:
            if data.outb:
                #data.outb = b"""HTTP/1.1 200 OK\r\nDate: Mon, 13 Dec 2021 20:13:43 GMT\r\nContent-Type: text/plain; charset=UTF-8\r\nContent-Length: 14\r\nConnection: keep-alive\r\nlast-modified: Mon, 19 Jul 2021 08:13:58 GMT\r\naccept-ranges: bytes\r\nx-xss-protection: 1; mode=block\r\nx-content-type-options: nosniff\r\nx-request-id: 9b45767c37cd9b9eb56895cade3a678a\r\nCF-Cache-Status: DYNAMIC\r\nReport-To: {"endpoints":[{"url":"https:\\/\\/a.nel.cloudflare.com\\/report\\/v3?s=BR8VpbF2a%2BS9ducMHOZlcay987EMtXw5OMeVABrMhUN0R0%2FUHN3fQVqsPpqqzWEX9KDlsxE0pmKsd%2BC%2BtZDCPo3bSL8sKG2YcRil%2BILFs7Quff7ghL1SWD940qyZKr0YJ8zlL6bMm5rJ"}],"group":"cf-nel","max_age":604800}\r\nNEL: {"success_fraction":0,"report_to":"cf-nel","max_age":604800}\r\nServer: cloudflare\r\nCF-RAY: 6bd1dac7ab45ee92-AKL\r\nalt-svc: h3=":443"; ma=86400, h3-29=":443"; ma=86400, h3-28=":443"; ma=86400, h3-27=":443"; ma=86400\r\n\r\nthis is a test"""
                print('echoing', repr(data.outb), 'to', data.addr, flush=True)
                sent = sock.send(data.outb)  # Should be ready to write
                data.outb = data.outb[sent:]

    while True:
        events = sel.select(timeout=None)
        for key, mask in events:
            if key.data is None:
                accept_wrapper(key.fileobj)
            else:
                service_connection(key, mask)
except Exception as e:
    print(traceback.format_exc())