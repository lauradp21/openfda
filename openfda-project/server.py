import http.server
import json
import socketserver
import http.client



IP = "localhost"
PORT = 8000


#Esta es la clase que hereda del http.server
class testHTTPRequestHandler(http.server.BaseHTTPRequestHandler):

    #Creamos una funcion para obtener la informacion de openfda.
    def obtener_info (self, limit = 10):
        conexion_FDA = http.client.HTTPSConnection("api.fda.gov") #Establecemos conexion con el API de FDA, cliente y servidor
        conexion_FDA.request("GET","/drug/label.json" + "?limit="+str(limit))  #Enviamos la peticion tipo "GET" junto con lo que queremos que nos devuelva
        print ("/drug/label.json" + "?limit="+str(limit))

        respuesta = conexion_FDA.getresponse()
        leer_respuesta = respuesta.read().decode("utf8")
        informacion = json.loads(leer_respuesta) #Transformamos la informacion a diccionarios
        info_resultados = informacion['results']
        return info_resultados

    #Creo una funcion que te devuelva el formulario dentro de la pagina web
    def formulario_html(self):
        formulario_principal = """
            <html>
                <head>
                    <title>OpenFDA App</title>
                </head>
                <body style="background-color:lightpink">
                    <h2>Bienvenido a nuestra pagina web, seleccione lo que desea que le facilitemos</h2>

                    <form method="get" action="searchDrug">
                        Principio activo:<br>
                        <input type="text" name="active_ingredient">
                        <br><br>
                        Limite: <input type="text" name="limite" value = "">
                        <br><br>
                        <input type="submit" value="Buscar farmacos">
                        </input>
                        <br><br>
                    </form>

                    <form method="get" action="searchCompany">
                        Empresa:<br>
                        <input type="text" name="company">
                        <br><br>
                        Limite: <input type="text" name="limite" value = "">
                        <br><br>
                        <input type="submit" value="Buscar empresa">
                        </input>
                        <br><br>
                    </form>

                    <form method="get" action="listDrugs">
                        Si desea una lista de farmacos, rellene este espacio con el numero de farmacos que quiere que le aparezcan y pulse el boton "Listado de farmacos de FDA":<br>
                        <input type="text" name="limite" value = "">
                        <br><br>
                        <input type="submit" value="Listado de farmacos de FDA">
                        </input>
                        <br><br>
                    </form>

                    <form method="get" action="listCompanies">
                        Si desea una lista de empresas, rellene este espacio con el numero de empresas que quiere que le aparezcan y pulse el boton "Listado de empresas":<br>
                        <input type="text" name="limite" value = "">
                        <br><br>
                        <input type="submit" value="Listado de empresas">
                        </input>
                        <br><br>
                    </form>

                    <form method="get" action="listWarnings">
                        <input type="submit" value="Listado de advertencias">
                        </input>
                    </form>

                </body>
            </html>
                      """
        return formulario_principal

    def pagina_final (self, lista):
        pagina_recurso = """
            <html>
                <head>
                    <title>OpenFDA App</title>
                </head>
                <body style="background-color:lightpink">"""
        for i in lista:
            pagina_recurso += "<ul><li>" +i+ "</li></ul>"+"<br>"
        pagina_recurso += "</body></html>"
        return pagina_recurso
    #Esta funcion la hago para que al salir la segunda pagina web, una vez buscado el recurso, no me salga todo junto, sino separado y por puntos


    def do_GET(self):
        recurso_conexion = self.path.split("?") #Separar el path por la interrogacion
        #Comprobamos si el recurso que nos han solicitado contiene parametros
        if len(recurso_conexion) > 1:
            parametros = recurso_conexion[1]
        else:
            parametros = ""

        limit = 10 #Le damos el valor por defecto de 10

        #Queremos conseguir el valor de los parametros
        if parametros:
            limite_param = parametros.split("=")
            if limite_param[0] == "limit":
                limit = int(limite_param[1]) #En esta linea, lo que pretendo es asignar a la variable limite, el recurso introducido en el formulario de la web
                print("Limit: {}".format(limit))
        else:
            print("Los parametros no son correctos")


        #A continuacion tratamos las posibles peticiones,y las escogidas en el formulario.

        if self.path == "/":
            #Creamos la cabecera que se enviara al cliente.
            self.send_response(200)
            self.send_header("Content-type", "text/html") #Escribe un encabezado HTTP específico en el flujo de salida
            self.end_headers()

            resultado_html = self.formulario_html() #Se accede a la funcion creada anteriormente y devuelve la pagina web con el formulario.
            self.wfile.write(bytes(resultado_html, "utf8"))

        elif "searchDrug" in self.path:
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()

            limite = 10
            drug = self.path.split('=')[1]

            lista_principio_activo = []
            conexion_FDA= http.client.HTTPSConnection("api.fda.gov")

            conexion_FDA.request("GET", "/drug/label.json" + "?limit="+ str(limit) + "&search=active_ingredient:" + drug)
            respuesta = conexion_FDA.getresponse()
            leer_respuesta = respuesta.read().decode("utf8")
            informacion = json.loads(leer_respuesta)
            info_farmacos = informacion["results"]

            for i in info_farmacos:
                if ("generic_name" in i["openfda"]):
                    lista_principio_activo.append(i["openfda"]["generic_name"][0])
                else:
                    lista_principio_activo.append("Este principio activo no esta disponible")
            pagina_recurso = self.pagina_final(lista_principio_activo)
            self.wfile.write(bytes(pagina_recurso, "utf8"))

        elif "searchCompany" in self.path:
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()

            limite = 10
            company = self.path.split("=")[1]

            lista_empresa_solicitada = []
            conexion_FDA = http.client.HTTPSConnection("api.fda.gov")
            conexion_FDA.request("GET", "/drug/label.json" + "?limit=" + str(limit) + '&search=openfda.manufacturer_name:' + company)
            respuesta = conexion_FDA.getresponse()
            leer_respuesta = respuesta.read().decode("utf8")
            informacion = json.loads(leer_respuesta)
            info_empresas = informacion["results"]

            for i in info_empresas:
                if ("manufacturer_name" in i["openfda"]):
                    lista_empresa_solicitada.append(i["openfda"]["manufacturer_name"][0])
                else:
                    lista_empresa_solicitada.append("Esta empresa no esta disponible")
            pagina_recurso = self.pagina_final(lista_empresa_solicitada)
            self.wfile.write(bytes(pagina_recurso, "utf8"))


        elif "listDrugs" in self.path:
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()

            lista_farmacos = []
            contenido = self.obtener_info(limit) #Accede a la funcion creada anteriormente con la informacion obtenida de openfda.

            for i in contenido:
                if ("generic_name" in i["openfda"]):
                    lista_farmacos.append (i["openfda"]["generic_name"][0])
                else:
                    lista_farmacos.append("Este farmaco no esta disponible")
            pagina_recurso = self.pagina_final(lista_farmacos) #La pagina web que aparece es la creada en la funcion anterior ('pagina_web) y cuya variable sera la lista de medicamentos creada.
            self.wfile.write(bytes(pagina_recurso, "utf8"))

        elif "listCompanies" in self.path:
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()

            lista_empresas = []
            contenido = self.obtener_info(limit)
            for i in contenido:
                if ("manufacturer_name" in i["openfda"]):
                    lista_empresas.append (i["openfda"]["manufacturer_name"][0])
                else:
                    lista_empresas.append("Esta empresa no esta disponible")
            pagina_recurso = self.pagina_final(lista_empresas)
            self.wfile.write(bytes(pagina_recurso, "utf8"))

        elif "listWarnings" in self.path:
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()

            lista_advertencias = []
            contenido = self.obtener_info(limit)
            for i in contenido:
                if ("warnings" in i):
                    lista_advertencias.append (i["warnings"][0])
                else:
                    lista_advertencias.append("La advertencia de este farmaco no esta disponible")
            pagina_recurso = self.pagina_final(lista_advertencias)
            self.wfile.write(bytes(pagina_recurso, "utf8"))

        elif "redirect" in self.path:
            print("Redirigiendo a la pagina inicial")
            self.send_response(301)
            self.send_header("Location", "http://localhost:"+str(PORT))
            self.end_headers()

        elif "secret" in self.path: #La URL escrita no es la correcta
            self.send_error(401)
            self.send_header('WWW-Authenticate', 'Basic realm="Mi servidor"')
            self.end_headers()

        else: #Esta ultima extension aparecera si el recurso solicitado no esta en el servidor
            self.send_error(404)
            self.send_header("Content-type", "text/plain; charset=utf-8")
            self.end_headers()
            self.wfile.write("I don't know '{}'.".format(self.path).encode())
        return

socketserver.TCPServer.allow_reuse_address = True

Handler = testHTTPRequestHandler

httpd = socketserver.TCPServer((IP, PORT), Handler)
print("serving at port", PORT)

try:
    httpd.serve_forever() #El servidor esta esperando indefinidamente, hasta que lo paremos manualmente.
except KeyboardInterrupt:
    print("El servidor ha sido interrumpido por el cliente\n")

httpd.server_close()
print("")
print("El servidor ha sido interrumpido")
