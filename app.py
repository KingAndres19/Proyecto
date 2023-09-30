from flask import Flask, request
import sett 
import services

app = Flask(__name__)

@app.route('/bienvenido', methods=['GET'])
def  bienvenido():
    return 'Hola mundo'

@app.route('/webhook', methods=['GET'])
def verificar_token():
    try:
        token = request.args.get('hub.verify_token')
        challenge = request.args.get('hub.challenge')

        if token == sett.token and challenge != None:
            return challenge
        else:
            return 'token incorrecto', 403
    except Exception as e:
        return e,403
    
@app.route('/webhook', methods=['POST'])
def recibir_mensajes():
    try:
        body = request.get_json()
        entry = body['entry'][0]
        changes = entry['changes'][0]
        value = changes['value']
        message = value['messages'][0]
        number = services.replace_start(message['from'])
        messageId = message['id']
        contacts = value['contacts'][0]
        name = contacts['profile']['name']
        text = services.obtener_Mensaje_whatsapp(message)

        services.administrar_chatbot(text, number,messageId,name)
        enviar_base(text, "", messageId, value, number )
        return 'enviado'

    except Exception as e:
        return 'no enviado ' + str(e)
    


def enviar_base(mensaje, respuesta, idWA, timestamp, telefonoCliente):
    import mysql.connector
    mydb = mysql.connector.connect(
        host = "mysql-javiertevillo.alwaysdata.net",
        user = "324312",
        password = "Mecatr0nica",
        database='javiertevillo_chat'
    )
    mycursor = mydb.cursor()
    query="SELECT count(id) AS cantidad FROM registro WHERE id_wa='" + idWA + "';"
    mycursor.execute("SELECT count(id) AS cantidad FROM registro WHERE id_wa='" + idWA + "';")

    cantidad, = mycursor.fetchone()
    cantidad=str(cantidad)
    cantidad=int(cantidad)
    if cantidad==0 :
        sql = ("INSERT INTO registro"+ "(mensaje_recibido,mensaje_enviado,id_wa      ,timestamp_wa   ,telefono_wa) VALUES "+"('"+mensaje+"'   ,'"+respuesta+"','"+idWA+"' ,'"+timestamp+"','"+telefonoCliente+"');")
        mycursor.execute(sql)
        mydb.commit()
        return jsonify({"status": "success"}, 200)


if __name__ == '__main__':
    app.run()
