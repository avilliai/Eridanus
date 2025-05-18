import json
import os
import aiosqlite

#居然不能用相对路径？？
dbpath = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'data', 'dataBase', 'user_management.db'))

# 获取指定范围的用户信息
async def get_users_range(start, end, sort_by=None, sort_order=None):
    try:
        async with aiosqlite.connect(dbpath) as db:
            query = "SELECT * FROM users"
            params = []
            
            # 排序方向
            if sort_by:
                sort_order = sort_order.upper()
                if sort_order not in ["ASC", "DESC"]:
                    sort_order = "ASC"
                query += f" ORDER BY {sort_by} {sort_order}"
            
            # 分页
            query += " LIMIT ? OFFSET ?"
            params.extend([end - start, start])
            
            async with db.execute(query, params) as cursor:
                results = await cursor.fetchall()
                if not results:
                    return []
                
                column_names = [description[0] for description in cursor.description]
                users = []
                for result in results:
                    user_dict = dict(zip(column_names, result))
                    users.append(user_dict)
                return users
    except :
        return []

# 获取(模糊搜索id时的)用户总数
async def get_users_count(args=None):
    try:
        async with aiosqlite.connect(dbpath) as db:
            query = "SELECT COUNT(*) FROM users"
            params = None
            if args:
                query = "SELECT COUNT(*) FROM users WHERE CAST(user_id AS TEXT) LIKE ?"
                params = (f"%{args}%",)
            async with db.execute(query, params) as cursor:
                result = await cursor.fetchone()
                return result[0] if result else 0
    except :
        return 0

# 模糊搜索用户ID
async def search_users_by_id(search_str, start, end, sort_by=None, sort_order=None):
    try:
        search_pattern = f"%{search_str}%"
        async with aiosqlite.connect(dbpath) as db:
            query = "SELECT * FROM users WHERE CAST(user_id AS TEXT) LIKE ?"
            params = [search_pattern]
            
            # 排序
            if sort_by:
                sort_order = sort_order.upper()
                if sort_order not in ["ASC", "DESC"]:
                    sort_order = "ASC"
                query += f" ORDER BY {sort_by} {sort_order}"

            query += " LIMIT ? OFFSET ?"
            params.extend([end - start, start])
            
            async with db.execute(query, params) as cursor:
                results = await cursor.fetchall()
                if not results:
                    return []
                
                column_names = [description[0] for description in cursor.description]
                users = []
                for result in results:
                    user_dict = dict(zip(column_names, result))
                    users.append(user_dict)
                return users
    except :
        return []

# 获取签到排行榜前N名
async def get_user_signed_days(limit=10):
    try:
        async with aiosqlite.connect(dbpath) as db:
            # 获取所有用户的签到记录
            async with db.execute("SELECT user_id, signed_days FROM users") as cursor:
                results = await cursor.fetchall()
                if not results:
                    return []
                
                # 计算每个用户的签到天数
                user_signin_days = []
                for result in results:
                    user_id = result[0]
                    signed_days = json.loads(result[1]) if result[1] else []
                    days_count = len(signed_days)
                    user_signin_days.append((user_id, days_count))
                
                # 按签到天数排序，取前N名
                user_signin_days.sort(key=lambda x: x[1], reverse=True)
                top_users = user_signin_days[:limit]
                
                signin_rank = []
                for user_id, days in top_users:
                    signin_rank.append({
                        "userId": user_id,
                        "days": days
                    })
                return signin_rank
    except :
        return []
