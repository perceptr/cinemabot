import asyncio

import asyncpg

from db_handler import DBHandler


class Statistics:
    def __init__(self, database: asyncpg) -> None:
        self.__database = database

    async def get_history_for_user(self, user_id: int):
        query = (
            f"SELECT search_query " f"FROM stats " f"WHERE telegram_user_id = {user_id}"
        )

        return await self.__database.execute_query_with_return(query)

    async def get_films_count_for_user(self, user_id: int):
        query = (
            f"SELECT response, count(*) "
            f"FROM stats "
            f"WHERE telegram_user_id = {user_id} "
            f"GROUP BY response "
            f"ORDER BY count(*) "
            f"DESC;"
        )

        return await self.__database.execute_query_with_return(query)


#
#
# async def run():
#     database = await DBHandler.create(
#         'postgres', 'cine123bot',
#         '5.188.142.77', '5435',
#         'postgres'
#     )
#
#     statter = Statistics(database)
#     res = await statter.get_history_for_user(123)
#     res = [i[0] for i in res]
#     print(res)
#     res2 = await statter.get_films_count_for_user(123)
#     res2 = [(i[0], i[1]) for i in res2]
#     print(res2)
#
#
# asyncio.run(run())
