"""
SCREENSHOT-BASED TRADING LOG - Flask Backend
Author: Built for Sean Barrett
Date: January 1, 2026
"""

from flask import Flask, request, jsonify, render_template, send_from_directory
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os
import base64
from werkzeug.utils import secure_filename

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Configuration
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///trading_log.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = 'screenshots'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Initialize database
db = SQLAlchemy(app)

# Ensure upload folder exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# ============================================================================
# DATABASE MODELS
# ============================================================================

class Trade(db.Model):
    """Trade model - stores all trade metadata"""
    id = db.Column(db.Integer, primary_key=True)
    
    # Basic Info
    date = db.Column(db.DateTime, nullable=False)
    symbol = db.Column(db.String(10), nullable=False)
    strategy = db.Column(db.String(50), nullable=False)
    
    # Trade Details
    strike_long = db.Column(db.String(20))
    strike_short = db.Column(db.String(20))
    expiration = db.Column(db.DateTime)
    dte = db.Column(db.Integer)  # Days to expiration
    
    # Prices
    entry_price = db.Column(db.Float)
    exit_price = db.Column(db.Float)
    quantity = db.Column(db.Integer, default=1)
    
    # Results
    profit_loss = db.Column(db.Float)
    is_win = db.Column(db.Boolean)
    
    # Notes
    notes = db.Column(db.Text)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    screenshots = db.relationship('Screenshot', backref='trade', lazy=True, cascade='all, delete-orphan')
    
    def to_dict(self):
        """Convert trade to dictionary"""
        return {
            'id': self.id,
            'date': self.date.isoformat() if self.date else None,
            'symbol': self.symbol,
            'strategy': self.strategy,
            'strike_long': self.strike_long,
            'strike_short': self.strike_short,
            'expiration': self.expiration.isoformat() if self.expiration else None,
            'dte': self.dte,
            'entry_price': self.entry_price,
            'exit_price': self.exit_price,
            'quantity': self.quantity,
            'profit_loss': self.profit_loss,
            'is_win': self.is_win,
            'notes': self.notes,
            'screenshots': [s.to_dict() for s in self.screenshots],
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }


class Screenshot(db.Model):
    """Screenshot model - stores screenshot file paths"""
    id = db.Column(db.Integer, primary_key=True)
    trade_id = db.Column(db.Integer, db.ForeignKey('trade.id'), nullable=False)
    
    filename = db.Column(db.String(255), nullable=False)
    screenshot_type = db.Column(db.String(20))  # 'chart', 'entry', 'exit'
    order_num = db.Column(db.Integer)  # 1, 2, 3 for sorting
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        """Convert screenshot to dictionary"""
        return {
            'id': self.id,
            'filename': self.filename,
            'type': self.screenshot_type,
            'order': self.order_num,
            'url': f'/screenshots/{self.filename}'
        }


# ============================================================================
# API ROUTES
# ============================================================================

@app.route('/')
def index():
    """Serve the main page"""
    return render_template('index.html')


@app.route('/api/trades', methods=['GET'])
def get_trades():
    """Get all trades"""
    trades = Trade.query.order_by(Trade.date.desc()).all()
    return jsonify([trade.to_dict() for trade in trades])


@app.route('/api/trades/<int:trade_id>', methods=['GET'])
def get_trade(trade_id):
    """Get single trade by ID"""
    trade = Trade.query.get_or_404(trade_id)
    return jsonify(trade.to_dict())


@app.route('/api/trades', methods=['POST'])
def create_trade():
    """Create a new trade"""
    data = request.json
    
    # Calculate DTE if we have both dates
    dte = None
    expiration_date = None
    if data.get('expiration'):
        expiration_date = datetime.fromisoformat(data['expiration'])
        trade_date = datetime.fromisoformat(data['date'])
        dte = (expiration_date - trade_date).days
    
    trade = Trade(
        date=datetime.fromisoformat(data['date']),
        symbol=data['symbol'],
        strategy=data['strategy'],
        strike_long=data.get('strike_long'),
        strike_short=data.get('strike_short'),
        expiration=expiration_date,
        dte=dte,
        entry_price=data.get('entry_price'),
        exit_price=data.get('exit_price'),
        quantity=data.get('quantity', 1),
        profit_loss=data.get('profit_loss'),
        is_win=data.get('is_win'),
        notes=data.get('notes')
    )
    
    db.session.add(trade)
    db.session.commit()
    
    return jsonify(trade.to_dict()), 201


@app.route('/api/trades/<int:trade_id>', methods=['PUT'])
def update_trade(trade_id):
    """Update an existing trade"""
    trade = Trade.query.get_or_404(trade_id)
    data = request.json
    
    # Update fields
    if 'date' in data:
        trade.date = datetime.fromisoformat(data['date'])
    if 'symbol' in data:
        trade.symbol = data['symbol']
    if 'strategy' in data:
        trade.strategy = data['strategy']
    if 'strike_long' in data:
        trade.strike_long = data['strike_long']
    if 'strike_short' in data:
        trade.strike_short = data['strike_short']
    if 'expiration' in data:
        trade.expiration = datetime.fromisoformat(data['expiration']) if data['expiration'] else None
    if 'entry_price' in data:
        trade.entry_price = data['entry_price']
    if 'exit_price' in data:
        trade.exit_price = data['exit_price']
    if 'quantity' in data:
        trade.quantity = data['quantity']
    if 'profit_loss' in data:
        trade.profit_loss = data['profit_loss']
    if 'is_win' in data:
        trade.is_win = data['is_win']
    if 'notes' in data:
        trade.notes = data['notes']
    
    # Recalculate DTE if dates changed
    if trade.expiration and trade.date:
        trade.dte = (trade.expiration - trade.date).days
    
    db.session.commit()
    return jsonify(trade.to_dict())


@app.route('/api/trades/<int:trade_id>', methods=['DELETE'])
def delete_trade(trade_id):
    """Delete a trade"""
    trade = Trade.query.get_or_404(trade_id)
    
    # Delete associated screenshot files
    for screenshot in trade.screenshots:
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], screenshot.filename)
        if os.path.exists(filepath):
            os.remove(filepath)
    
    db.session.delete(trade)
    db.session.commit()
    
    return '', 204


@app.route('/api/trades/<int:trade_id>/screenshots', methods=['POST'])
def upload_screenshot(trade_id):
    """Upload a screenshot for a trade"""
    trade = Trade.query.get_or_404(trade_id)
    
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    # Generate unique filename
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f"{trade_id}_{timestamp}_{secure_filename(file.filename)}"
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    
    # Save file
    file.save(filepath)
    
    # Create screenshot record
    screenshot = Screenshot(
        trade_id=trade_id,
        filename=filename,
        screenshot_type=request.form.get('type', 'chart'),
        order_num=len(trade.screenshots) + 1
    )
    
    db.session.add(screenshot)
    db.session.commit()
    
    return jsonify(screenshot.to_dict()), 201


@app.route('/screenshots/<filename>')
def serve_screenshot(filename):
    """Serve a screenshot file"""
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)


@app.route('/api/analytics', methods=['GET'])
def get_analytics():
    """Get trading analytics"""
    trades = Trade.query.all()
    
    total_trades = len(trades)
    winning_trades = len([t for t in trades if t.is_win])
    losing_trades = total_trades - winning_trades
    
    total_pnl = sum([t.profit_loss for t in trades if t.profit_loss is not None])
    avg_winner = sum([t.profit_loss for t in trades if t.is_win and t.profit_loss]) / winning_trades if winning_trades > 0 else 0
    avg_loser = sum([t.profit_loss for t in trades if not t.is_win and t.profit_loss]) / losing_trades if losing_trades > 0 else 0
    
    win_rate = (winning_trades / total_trades * 100) if total_trades > 0 else 0
    
    # Best and worst trades
    best_trade = max(trades, key=lambda t: t.profit_loss or 0) if trades else None
    worst_trade = min(trades, key=lambda t: t.profit_loss or 0) if trades else None
    
    # Strategy breakdown
    strategy_stats = {}
    for trade in trades:
        if trade.strategy not in strategy_stats:
            strategy_stats[trade.strategy] = {'count': 0, 'wins': 0, 'pnl': 0}
        strategy_stats[trade.strategy]['count'] += 1
        if trade.is_win:
            strategy_stats[trade.strategy]['wins'] += 1
        if trade.profit_loss:
            strategy_stats[trade.strategy]['pnl'] += trade.profit_loss
    
    return jsonify({
        'total_trades': total_trades,
        'winning_trades': winning_trades,
        'losing_trades': losing_trades,
        'win_rate': round(win_rate, 1),
        'total_pnl': round(total_pnl, 2),
        'avg_winner': round(avg_winner, 2),
        'avg_loser': round(avg_loser, 2),
        'best_trade': best_trade.to_dict() if best_trade else None,
        'worst_trade': worst_trade.to_dict() if worst_trade else None,
        'strategy_stats': strategy_stats
    })


# ============================================================================
# INITIALIZE DATABASE
# ============================================================================

with app.app_context():
    db.create_all()
    print("Database initialized!")


# ============================================================================
# RUN APP
# ============================================================================

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
