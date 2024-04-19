from flask_sqlalchemy import SQLAlchemy
from pymongo import MongoClient

# Conexões com os bancos de dados MySQL
#app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:sua_senha@localhost/nome_do_banco_de_dados'
SQLALCHEMY_DATABASE_URI = 'mysql://root:UySg07mRR3KkyMi2fGTE@127.0.0.1:3306/dlopes_banco_web'
##mysql = SQLAlchemy(app)

# Conexão com MongoDB
cliente = MongoClient("mongodb://root:vT68leR8oxFz45CUX84K@localhost:27017") # conexão com servidor

mongodb = cliente["dlopes_banco_web"] # selecionando BD
pedidos_collection = mongodb["pedidos"] # selecionando collection
