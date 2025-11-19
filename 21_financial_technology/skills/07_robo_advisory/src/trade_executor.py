"""Trade Executor - Executes portfolio trades"""
from datetime import datetime
from typing import Dict, List


class TradeExecutor:
    """Manages trade execution"""

    def __init__(self):
        self.execution_log = []
        self.pending_orders = []

    def submit_order(self, symbol: str, quantity: float, side: str,
                    price: float = None) -> Dict:
        """Submit trade order"""
        order = {
            'order_id': len(self.execution_log) + 1,
            'symbol': symbol,
            'quantity': quantity,
            'side': side,  # BUY or SELL
            'price': price,
            'submitted_at': datetime.now(),
            'status': 'SUBMITTED'
        }
        self.pending_orders.append(order)
        return order

    def execute_order(self, order_id: int, execution_price: float) -> Dict:
        """Mark order as executed"""
        order = next((o for o in self.pending_orders if o['order_id'] == order_id), None)
        if order:
            order['status'] = 'EXECUTED'
            order['execution_price'] = execution_price
            order['executed_at'] = datetime.now()
            
            # Calculate execution cost
            cost = order['quantity'] * execution_price
            cost_basis = cost / order['quantity']
            
            self.execution_log.append(order)
            self.pending_orders.remove(order)
            
            return {
                'status': 'SUCCESS',
                'total_value': cost,
                'average_price': cost_basis
            }
        return {'status': 'ERROR', 'message': 'Order not found'}

    def get_execution_history(self) -> List[Dict]:
        """Get trade execution history"""
        return self.execution_log
