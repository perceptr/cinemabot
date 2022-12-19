import logging

import asyncpg


class DBHandler:
    @classmethod
    async def create(cls, user, password, host, port, database):
        self = DBHandler()
        self.conn = await asyncpg.connect(
            user=user, password=password, database=database, host=host, port=port
        )
        return self

    async def execute_query_with_return(self, query: str) -> list:
        try:
            res = await self.conn.fetch(query)
            await self.conn.close()
            return res
        except Exception as e:
            logging.error(e)
            await self.conn.close()
            return []

    async def execute_query_without_return(self, query: str) -> None:
        try:
            await self.conn.execute(query)
            await self.conn.close()
        except Exception as e:
            logging.error(e)
            await self.conn.close()
