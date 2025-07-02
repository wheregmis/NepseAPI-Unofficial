#!/usr/bin/env python3
"""
Validation utilities for NEPSE API
Provides validation for stock symbols and index names
"""

import json
import os
from pathlib import Path
from typing import Dict, List, Optional, Set

class NepseValidator:
    """Validator for NEPSE stock symbols and index names"""

    def __init__(self):
        self.base_path = Path(__file__).parent
        self._stock_symbols: Optional[Set[str]] = None
        self._index_names: Optional[Set[str]] = None
        self._stock_data: Optional[Dict] = None

    def _load_stock_data(self) -> Dict:
        """Load stock data from stockmap.json"""
        if self._stock_data is None:
            stockmap_path = self.base_path / "stockmap.json"
            try:
                with open(stockmap_path, 'r', encoding='utf-8') as f:
                    self._stock_data = json.load(f)
            except FileNotFoundError:
                print(f"Warning: stockmap.json not found at {stockmap_path}")
                self._stock_data = {}
            except json.JSONDecodeError as e:
                print(f"Warning: Error parsing stockmap.json: {e}")
                self._stock_data = {}
        return self._stock_data

    def _load_index_names(self) -> Set[str]:
        """Load index names from indexmap.py or define them directly"""
        if self._index_names is None:
            # Define the valid NEPSE indices directly
            self._index_names = {
                "Banking SubIndex",
                "Development Bank Index",  # Note: corrected from "Development Bank Ind."
                "Finance Index",
                "Hotels And Tourism Index",  # Note: corrected from "Hotels And Tourism"
                "HydroPower Index",
                "Investment Index",  # Note: corrected from "Investment"
                "Life Insurance",
                "Manufacturing And Processing",  # Note: corrected from "Manufacturing And Pr."
                "Microfinance Index",
                "Mutual Fund",
                "NEPSE Index",
                "Non Life Insurance",
                "Others Index",
                "Trading Index",
                # Additional common variations
                "Banking SubIndex",
                "Development Bank Ind.",  # Keep original for compatibility
                "Hotels And Tourism",     # Keep original for compatibility
                "Investment",              # Keep original for compatibility
                "Manufacturing And Pr.",   # Keep original for compatibility
            }
        return self._index_names

    def get_valid_stock_symbols(self) -> Set[str]:
        """Get all valid stock symbols"""
        if self._stock_symbols is None:
            stock_data = self._load_stock_data()
            self._stock_symbols = set(stock_data.keys())
        return self._stock_symbols

    def get_valid_index_names(self) -> Set[str]:
        """Get all valid index names"""
        return self._load_index_names()

    def is_valid_stock_symbol(self, symbol: str) -> bool:
        """Check if a stock symbol is valid"""
        if not symbol or not isinstance(symbol, str):
            return False
        return symbol.upper() in self.get_valid_stock_symbols()

    def is_valid_index_name(self, index_name: str) -> bool:
        """Check if an index name is valid"""
        if not index_name or not isinstance(index_name, str):
            return False
        return index_name in self.get_valid_index_names()

    def get_stock_info(self, symbol: str) -> Optional[Dict]:
        """Get stock information for a valid symbol"""
        if not self.is_valid_stock_symbol(symbol):
            return None
        stock_data = self._load_stock_data()
        return stock_data.get(symbol.upper())

    def validate_stock_symbol(self, symbol: str) -> Dict:
        """Validate stock symbol and return result"""
        if not symbol:
            return {
                "valid": False,
                "error": "Stock symbol is required",
                "symbol": None
            }

        symbol = symbol.upper().strip()

        if self.is_valid_stock_symbol(symbol):
            stock_info = self.get_stock_info(symbol)
            return {
                "valid": True,
                "symbol": symbol,
                "info": stock_info
            }
        else:
            return {
                "valid": False,
                "error": f"Stock symbol '{symbol}' not found. Please check if it's a valid NEPSE listed company.",
                "symbol": symbol,
                "suggestions": self._get_similar_symbols(symbol)
            }

    def validate_index_name(self, index_name: str) -> Dict:
        """Validate index name and return result"""
        if not index_name:
            return {
                "valid": False,
                "error": "Index name is required",
                "index_name": None
            }

        index_name = index_name.strip()

        if self.is_valid_index_name(index_name):
            return {
                "valid": True,
                "index_name": index_name
            }
        else:
            return {
                "valid": False,
                "error": f"Index '{index_name}' not found.",
                "index_name": index_name,
                "available_indices": list(self.get_valid_index_names())
            }

    def _get_similar_symbols(self, symbol: str, max_suggestions: int = 5) -> List[str]:
        """Get similar stock symbols for suggestions"""
        if not symbol:
            return []

        symbol = symbol.upper()
        valid_symbols = self.get_valid_stock_symbols()

        # Find symbols that start with the same letters
        similar = []
        for valid_symbol in valid_symbols:
            if valid_symbol.startswith(symbol[:2]):  # Match first 2 characters
                similar.append(valid_symbol)
            if len(similar) >= max_suggestions:
                break

        return similar[:max_suggestions]

    def get_stats(self) -> Dict:
        """Get validation statistics"""
        return {
            "total_stocks": len(self.get_valid_stock_symbols()),
            "total_indices": len(self.get_valid_index_names()),
            "sample_stocks": list(self.get_valid_stock_symbols())[:10],
            "available_indices": list(self.get_valid_index_names())
        }

# Global validator instance
validator = NepseValidator()

# Convenience functions
def validate_stock_symbol(symbol: str) -> Dict:
    """Validate a stock symbol"""
    return validator.validate_stock_symbol(symbol)

def validate_index_name(index_name: str) -> Dict:
    """Validate an index name"""
    return validator.validate_index_name(index_name)

def is_valid_stock(symbol: str) -> bool:
    """Quick check if stock symbol is valid"""
    return validator.is_valid_stock_symbol(symbol)

def is_valid_index(index_name: str) -> bool:
    """Quick check if index name is valid"""
    return validator.is_valid_index_name(index_name)

if __name__ == "__main__":
    # Test the validator
    print("NEPSE Validator Test")
    print("=" * 40)

    # Test stock validation
    test_stocks = ["NABIL", "INVALID", "ADBL", "xyz"]
    for stock in test_stocks:
        result = validate_stock_symbol(stock)
        print(f"Stock '{stock}': {result}")

    print("\n" + "=" * 40)

    # Test index validation
    test_indices = ["Banking SubIndex", "Invalid Index", "NEPSE Index"]
    for index in test_indices:
        result = validate_index_name(index)
        print(f"Index '{index}': {result}")

    print("\n" + "=" * 40)
    print("Validator Stats:")
    print(validator.get_stats())
