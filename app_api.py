from datetime import datetime
from flask import Flask, request, jsonify, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from flask_restx import Api, Resource, fields, reqparse
from flask_cors import CORS
import os

app = Flask(__name__)
# Konfigurace DB (soubor app.db vedle app.py)
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'app.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Enable CORS for all routes
CORS(app)

db = SQLAlchemy(app)
api = Api(app,
          version='1.0',
          title='Simple Items API',
          description='REST API with Flask, SQLite and Swagger UI (flask-restx)',
          doc='/'  # Swagger UI na rootu: http://localhost:5000/
          )

ns = api.namespace('items', description='Operations on items')

class ItemModel(db.Model):
    __tablename__ = 'items'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=True)
    done = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'done': self.done,
            'created_at': self.created_at.isoformat() + 'Z' if self.created_at else None
        }

# Swagger model
item_model = api.model('Item', {
    'id': fields.Integer(readOnly=True, description='Unique identifier'),
    'title': fields.String(required=True, description='Title of the item'),
    'description': fields.String(description='Description'),
    'done': fields.Boolean(description='Completion status'),
    'created_at': fields.DateTime(readOnly=True, description='Creation timestamp')
})

create_item_model = api.model('ItemCreate', {
    'title': fields.String(required=True, description='Title of the item'),
    'description': fields.String(description='Description'),
    'done': fields.Boolean(description='Completion status'),
})

# Simple parser for optional pagination
list_parser = reqparse.RequestParser()
list_parser.add_argument('limit', type=int, required=False, help='Limit number of items')
list_parser.add_argument('offset', type=int, required=False, help='Offset for items')

@ns.route('')
class ItemList(Resource):
    @ns.expect(list_parser)
    @ns.marshal_list_with(item_model)
    def get(self):
        """Get list of items (with optional ?limit=&offset=)"""
        args = list_parser.parse_args()
        query = ItemModel.query.order_by(ItemModel.created_at.desc())
        if args.get('offset'):
            query = query.offset(args['offset'])
        if args.get('limit'):
            query = query.limit(args['limit'])
        items = query.all()
        return [i.to_dict() for i in items], 200

    @ns.expect(create_item_model, validate=True)
    @ns.marshal_with(item_model)
    @ns.response(201, 'Item created')
    def post(self):
        """Create a new item"""
        data = api.payload
        title = data.get('title')
        if not title or title.strip() == '':
            api.abort(400, "title is required")
        item = ItemModel(title=title.strip(),
                         description=data.get('description'),
                         done=bool(data.get('done', False)))
        db.session.add(item)
        db.session.commit()
        return item.to_dict(), 201

@ns.route('/<int:id>')
@ns.response(404, 'Item not found')
@ns.param('id', 'The item identifier')
class ItemResource(Resource):
    @ns.marshal_with(item_model)
    def get(self, id):
        """Get a single item by id"""
        item = ItemModel.query.get_or_404(id)
        return item.to_dict(), 200

    @ns.expect(create_item_model, validate=True)
    @ns.marshal_with(item_model)
    def put(self, id):
        """Replace an existing item"""
        item = ItemModel.query.get_or_404(id)
        data = api.payload
        title = data.get('title')
        if not title or title.strip() == '':
            api.abort(400, "title is required")
        item.title = title.strip()
        item.description = data.get('description')
        item.done = bool(data.get('done', False))
        db.session.commit()
        return item.to_dict(), 200

    def delete(self, id):
        """Delete an item"""
        item = ItemModel.query.get_or_404(id)
        db.session.delete(item)
        db.session.commit()
        return '', 204

# Serve the frontend
@app.route('/app')
def serve_frontend():
    return send_from_directory('.', 'index.html')

@app.route('/')
def index():
    return send_from_directory('.', 'index.html')

if __name__ == '__main__':
    # Vytvoří DB a tabulky pokud neexistují
    with app.app_context():
        db.create_all()
    app.run(host='0.0.0.0', port=5000, debug=True)