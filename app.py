import os
from flask import Flask, jsonify, request, make_response
from services.receipt_processor import ReceiptProcessor
from models.receipt import Receipt

DEBUG = os.getenv('DEBUG', 'False').lower() == 'true'
PORT = int(os.getenv('PORT', 5000))

app = Flask(__name__)
processor = ReceiptProcessor()  # global for now, inject later if needed

def error_response(message, status_code):
    # TODO: add error codes/types when we have more error cases
    return make_response(
        jsonify({'error': message}),
        status_code
    )

@app.route('/receipts/process', methods=['POST'])
def process_receipt():
    # TODO: add request validation middleware
    if not request.is_json:
        return error_response('Content-Type must be application/json', 415)
    
    data = request.get_json()
    
    required = ['retailer', 'purchaseDate', 'purchaseTime', 'items', 'total']
    if not all(field in data for field in required):
        return error_response(f'Missing required fields: {required}', 400)
    
    try:
        receipt = Receipt(**data)
    except ValueError as e:
        return error_response(str(e), 400)
    except Exception as e:
        app.logger.error(f'Failed to create receipt: {str(e)}')
        return error_response('Invalid receipt data', 400)

    try:
        receipt_id = processor.process_receipt(receipt)
        return jsonify({'id': receipt_id})
    except Exception as e:
        app.logger.error(f'Failed to process receipt: {str(e)}')
        return error_response('Failed to process receipt', 500)

@app.route('/receipts/<receipt_id>/points', methods=['GET'])
def get_points(receipt_id):
    if not receipt_id:
        return error_response('Receipt ID is required', 400)
    
    try:
        points = processor.get_points(receipt_id)
        return jsonify({'points': points})
    except ValueError:  # receipt not found
        return error_response('Receipt not found', 404)
    except Exception as e:
        app.logger.error(f'Error getting points for receipt {receipt_id}: {str(e)}')
        return error_response('Failed to get points', 500)

if __name__ == '__main__':
    # TODO: use proper WSGI server for prod
    app.run(
        host='0.0.0.0',  # bind to all interfaces
        port=PORT,
        debug=DEBUG
    )
