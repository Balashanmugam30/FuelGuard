"""
FuelGuard AI - Transaction Store
In-memory storage for fuel transactions.
"""

from datetime import datetime


class TransactionStore:
    """Simple in-memory transaction store backed by a Python list."""

    def __init__(self):
        self._transactions: list[dict] = []
        self._next_id: int = 1

    def add(self, analysis: dict) -> dict:
        """
        Persist a transaction analysis result.
        Adds an auto-incremented ID and a timestamp.
        Returns the complete transaction record.
        """
        record = {
            "transaction_id": self._next_id,
            **analysis,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        }
        self._transactions.append(record)
        self._next_id += 1
        return record

    def get_all(self) -> list[dict]:
        """Return all stored transactions (newest first)."""
        return list(reversed(self._transactions))

    def get_analytics(self) -> dict:
        """Compute aggregate analytics over all transactions."""
        total = len(self._transactions)
        if total == 0:
            return {
                "total_transactions": 0,
                "fraud_transactions": 0,
                "safe_transactions": 0,
                "fraud_percentage": 0.0,
                "average_shortage": 0.0,
                "highest_shortage": 0.0,
            }

        fraud_count = sum(1 for t in self._transactions if t["fraud_detected"])
        safe_count = total - fraud_count
        avg_shortage = round(
            sum(t["shortage_percentage"] for t in self._transactions) / total, 2
        )
        highest_shortage = round(
            max(t["shortage_percentage"] for t in self._transactions), 2
        )

        return {
            "total_transactions": total,
            "fraud_transactions": fraud_count,
            "safe_transactions": safe_count,
            "fraud_percentage": round((fraud_count / total) * 100, 2),
            "average_shortage": avg_shortage,
            "highest_shortage": highest_shortage,
        }

    def clear(self):
        """Reset all stored transactions."""
        self._transactions.clear()
        self._next_id = 1


# Singleton instance shared across the application
store = TransactionStore()
