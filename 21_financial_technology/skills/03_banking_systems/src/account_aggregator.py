import asyncio
from typing import List, Dict

class AccountAggregator:
    def __init__(self, api_clients: Dict):
        self.clients = api_clients

    async def aggregate_accounts(self, customer_id: str) -> List[Dict]:
        tasks = [
            self.clients['bank1'].get_accounts(customer_id),
            self.clients['bank2'].get_accounts(customer_id),
            self.clients['bank3'].get_accounts(customer_id)
        ]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        accounts = []
        for result in results:
            if isinstance(result, list):
                accounts.extend(result)
        
        return accounts

    async def aggregate_balances(self, customer_id: str) -> Dict:
        accounts = await self.aggregate_accounts(customer_id)
        total_balance = sum(a['balance'] for a in accounts)
        return {
            'total': total_balance,
            'accounts': accounts,
            'currency': 'USD'
        }
