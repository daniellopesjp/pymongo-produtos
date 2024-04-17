from bson import ObjectId
from config import SQLALCHEMY_DATABASE_URI, pedidos_collection
from flask import Flask, jsonify, render_template, request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import String, Float, Integer, Date

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = SQLALCHEMY_DATABASE_URI
mysql = SQLAlchemy(app)

# Definindo as classes para Produtos, Clientes e Pedidos
# Definindo seus modelos de produto e cliente (SQL)
class Produtos(mysql.Model):
    id_produtos = mysql.Column(Integer, primary_key=True)
    nome = mysql.Column(String, nullable=False)
    descricao = mysql.Column(String, nullable=False)
    preco = mysql.Column(Float, nullable=False)
    categoria = mysql.Column(Date, nullable=False)

    def serialize(self):
        return {
            'id_produtos': self.id_produtos,
            'nome': self.nome,
            'descricao': self.descricao,
            'preco': self.preco,
            'categoria': self.categoria,
        }

class Clientes(mysql.Model):
    id_clientes = mysql.Column(Integer, primary_key=True)
    nome = mysql.Column(String, nullable=False)
    email = mysql.Column(String, nullable=False)
    cpf = mysql.Column(String, nullable=False)
    data_nascimento = mysql.Column(Date, nullable=False)

    def serialize(self):
        return {
            "id_clientes": self.id_clientes,
            "nome": self.nome,
            "email": self.email,
            "cpf": self.cpf,
            "data_nascimento": self.data_nascimento
        }
# Definindo a classe PEDIDOS
# Será persistida no MongoDB
# Aqui utilizados o Contrutor para definir os atributos da classe

class Pedidos:
    def __init__(self, id_cliente, id_produtos, data_pedido, valor_pedido):
        self.id_produtos = None
        self.id_cliente = id_cliente
        self.id_produtos = id_produtos
        self.data_pedido = data_pedido
        self.valor_pedido = valor_pedido

    def serialize(self):
        return {
            "id_cliente": self.id_cliente,
            "id_produtos": self.id_produtos,
            "data_pedido": self.data_pedido,
            "valor_pedido": self.valor_pedido,
        }

# Rotas para CRUD de produtos (MySQL)

@app.route('/')
def index():
    return render_template("index.html")

@app.route("/produtos", methods=['GET'])
def get_produtos():
    produtos = Produtos.query.all()
    return jsonify([produto.serialize() for produto in produtos])

@app.route("/produtos", methods=['POST'])
def set_produtos():
    try:
        dados = request.get_json()
        produto = Produtos(
            nome=dados['nome'],
            descricao=dados['descricao'],
            preco=dados['preco'],
            categoria=dados['categoria'],
        )
        mysql.session.add(produto)
        mysql.session.commit()
        return jsonify(produto.serialize()), 201
    except Exception as e:
        print(e)
        return jsonify({'error': str(e)}), 400

@app.route("/produtos/<int:id>", methods=['PUT'])
def update_produtos(id):
    try:
        dados = request.get_json()
        produto = mysql.session.query(Produtos).filter_by(id_produtos=id).first()
        produto.nome = dados['nome']
        produto.descricao = dados['descricao']
        produto.preco = dados['preco']
        produto.categoria = dados['categoria']

        mysql.session.commit()
        return jsonify(produto.serialize()), 201
    except Exception as e:
        print(e)
        return jsonify({'Erro ao alterar dados de produtos: ': str(e)}), 400

@app.route("/produtos/<int:id>", methods=['DELETE'])
def delete_produtos(id):
    try:
        produto = mysql.session.query(Produtos).filter_by(id_produtos=id).first()
        mysql.session.delete(produto)
        mysql.session.commit()
        return jsonify("Produto deletado com sucesso!"), 204
    except Exception as e:
        print(e)
        return jsonify("Erro ao deletar dados de produtos: " + str(e)), 400

# Rotas para CRUD de clientes (MySQL)
@app.route("/clientes", methods=['GET'])
def get_clientes():
    clientes = Clientes.query.all()
    return jsonify([cliente.serialize() for cliente in clientes])

@app.route("/clientes", methods=['POST'])
def set_clientes():
    try:
        dados = request.get_json()
        cliente = Clientes(
            nome=dados['nome'],
            email=dados['email'],
            cpf=dados['cpf'],
            data_nascimento=dados['data_nascimento']
        )
        mysql.session.add(cliente)
        mysql.session.commit()
        return jsonify(cliente.serialize()), 201
    except Exception as e:
        print(e)
        return jsonify({'error': str(e)}), 400

@app.route("/clientes/<int:id>", methods=['PUT'])
def update_clientes(id):
    try:
        dados = request.get_json()
        cliente = mysql.session.query(Clientes).filter_by(id_clientes=id).first()
        cliente.nome = dados['nome']
        cliente.email = dados['email']
        cliente.cpf = dados['cpf']
        cliente.data_nascimento = dados['data_nascimento']

        mysql.session.commit()
        return jsonify(cliente.serialize()), 201
    except Exception as e:
        print(e)
        return jsonify({'Erro ao alterar dados de clientes: ': str(e)}), 400

@app.route("/clientes/<int:id>", methods=['DELETE'])
def delete_clientes(id):
    try:
        cliente = mysql.session.query(Clientes).filter_by(id_clientes=id).first()
        mysql.session.delete(cliente)
        mysql.session.commit()
        return jsonify("Cliente deletado com sucesso!"), 204
    except Exception as e:
        print(e)
        return jsonify("Erro ao deletar dados de Clientes: " + str(e)), 400

# Rotas para CRUD de Pedidos
# Rotas feitas para manipular os dados através do MongoDB

@app.route("/pedido", methods=["GET"])
def get_pedidos():
    try:
        pedidos = pedidos_collection.find()

        # Convertendo ObjectId em strings para serialização
        pedidos_serializaveis = []
        for pedido in pedidos:
            pedido['_id'] = str(pedido['_id'])
            pedidos_serializaveis.append(pedido)

        return jsonify(pedidos_serializaveis), 200
    except Exception as e:
        print(f"Erro: {e}")
        return "Erro ao listar pedidos.", 500

# Rotas para Create, Update e Delete de pedidos)
@app.route("/pedido", methods=["POST"])
def set_pedido():
    try:
        dados = request.get_json()
        novo_pedido = Pedidos(
            id_produtos=dados["id_produtos"],
            id_cliente=dados['id_cliente'],
            data_pedido=dados["data_pedido"],
            valor_pedido=dados["valor_pedido"]
        )
        resultado = pedidos_collection.insert_one(novo_pedido.serialize())
        if resultado.inserted_id:
            # Retorna o pedido recém-criado e o status 201
            novo_pedido.id_pedido = str(resultado.inserted_id)
            return jsonify(novo_pedido.serialize()), 201
        else:
            return "Erro ao inserir pedido.", 500
    except Exception as e:
        print(f"Erro: {e}")
        return "Erro ao inserir pedido.", 400

@app.route("/pedido/<pedido_id>", methods=['DELETE'])
def delete_pedido(pedido_id):
    try:
        resultado = pedidos_collection.delete_one({"_id": ObjectId(pedido_id)})

        # Verifica se o pedido foi encontrado e excluído
        if resultado.deleted_count == 1:
            return jsonify({"message": f"Pedido com ID {pedido_id} excluído com sucesso."}), 200
        else:
            return jsonify({"message": f"Pedido com ID {pedido_id} não encontrado."}), 404
    except Exception as e:
        return jsonify({"error": f"Erro ao excluir pedido: {e}"}), 500

@app.route("/pedido/<pedido_id>", methods=["PUT"])
def update_pedido(pedido_id):
    try:
        if not ObjectId.is_valid(pedido_id):
            return "ID de pedido inválido.", 400

        # Obtém os novos dados do pedido do corpo da solicitação
        dados = request.get_json()

        # Atualiza o pedido no banco de dados
        resultado = pedidos_collection.update_one(
            {"_id": ObjectId(pedido_id)},
            {"$set": dados}  # Use $set para atualizar apenas os campos fornecidos
        )

        # Verifica se o pedido foi encontrado e atualizado
        if resultado.modified_count == 1:
            return f"Pedido com ID {pedido_id} atualizado com sucesso.", 200
        else:
            return f"Pedido com ID {pedido_id} não encontrado ou nenhum dado foi modificado.", 404
    except Exception as e:
        return f"Erro ao atualizar pedido: {e}", 500

if __name__ == "__main__":
    app.run(debug=True)
