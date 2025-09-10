"""
Database Configuration Module

This module provides database connectivity and configuration:
- Real Supabase client for production database operations
- Database operations (CRUD) for user management
- Persistent data storage with Supabase PostgreSQL

The implementation uses the real Supabase client for production use.
"""

import os
from typing import Optional

from dotenv import load_dotenv
from supabase import Client, create_client

# Load environment variables
load_dotenv()


class DatabaseConfig:
    def __init__(self):
        self.url = os.getenv("SUPABASE_URL")
        self.key = os.getenv("SUPABASE_KEY")

        # Validate environment variables
        if not self.url or not self.key:
            raise ValueError(
                "SUPABASE_URL and SUPABASE_KEY must be set in .env file. "
                "Please check your environment configuration."
            )

        # Create real Supabase client
        try:
            self.client: Client = create_client(self.url, self.key)
            print(f"✅ Connected to Supabase database: {self.url}")
        except Exception as e:
            raise ConnectionError(f"Failed to connect to Supabase: {str(e)}")

    def get_client(self) -> Client:
        """Get the Supabase client instance."""
        return self.client


# Global database instance
db_config = DatabaseConfig()
