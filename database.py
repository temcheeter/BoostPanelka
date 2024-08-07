import aiosqlite
import datetime

async def check_db():
    _datetime = datetime.datetime.now().strftime('%d.%m.%Y %H:%M')
    async with aiosqlite.connect('database.db', check_same_thread=False) as db:
        try:
            await db.execute('SELECT * FROM users')
            print('---- database was found ----')
        except aiosqlite.OperationalError:
            await db.execute('CREATE TABLE users(id INTEGER PRIMARY KEY, user_id INT, ref_id INT,'
                             'start_time TEXT NOT NULL, promotion INT NOT NULL, used_promo TEXT, wallet INT)')
            await db.execute('CREATE TABLE orders(id INTEGER PRIMARY KEY, user_id INT, order_id INT,'
                             'cost INT, quantity INT, status INT, service_id)')
            await db.execute('CREATE TABLE promo(id INTEGER PRIMARY KEY, service_id INT, name TEXT, activations INT, min_order INT)')
            await db.execute('CREATE TABLE checks(id INTEGER PRIMARY KEY, user_id INT, service_id INT, min_order INT, quantity INT)')
            await db.commit()
            print('---- database was create ----')
        print(f'---- {_datetime} ----')
        all_users = await get_all_users()
        if not all_users:
            print('--------   Users: 0   --------\n')
        else:
            print(f"--------   Users: {len(await get_all_users())}   --------\n")


async def get_all_users():
    async with aiosqlite.connect('database.db') as db:
        cur = await db.cursor()
        await cur.execute('SELECT user_id FROM users')
        return await cur.fetchall()


async def get_user_info(user_id):
    async with aiosqlite.connect('database.db') as db:
        cur = await db.cursor()
        try:
            await cur.execute('SELECT * FROM users WHERE user_id=?', (user_id,))
            result = await cur.fetchone()
            return result
        except:
            return None


async def add_user(user_id, promotion, wallet, ref_id=None):
    async with aiosqlite.connect('database.db') as db:
        await db.execute('INSERT INTO users(user_id, ref_id, start_time, promotion, wallet) VALUES(?, ?, datetime("now", "+3 hours"), ?, ?)',
                         (user_id, ref_id, promotion, wallet))
        await db.commit()


async def get_orders(user_id):
    async with aiosqlite.connect('database.db') as db:
        cur = await db.cursor()
        try:
            await cur.execute('SELECT () FROM orders WHERE user_id=?', (user_id,))
            return await cur.fetchall()[0]
        except:
            return


async def add_referal(user_id, referal_id):
    async with aiosqlite.connect('database.db') as db:
        cur = await db.cursor()
        await cur.execute('SELECT referals_id FROM users WHERE user_id = ?', (user_id,))
        old_data = await cur.fetchall()
        print(old_data)
        new_data = old_data[0][0] + ',' + referal_id
        await db.execute('UPDATE users SET referals_id = ? WHERE user_id = ?;', (new_data, user_id))
        print('ау')
        await db.commit()


async def get_checks(user_id):
    async with aiosqlite.connect('database.db') as db:
        cur = await db.cursor()
        await cur.execute('SELECT * FROM checks WHERE user_id = ?', (user_id,))
        return await cur.fetchall()


async def get_check(user_id, service_id):
    async with aiosqlite.connect('database.db') as db:
        cur = await db.cursor()
        await cur.execute('SELECT * FROM checks WHERE user_id, service_id = ?, ?', (user_id, service_id))
        return await cur.fetchall()


async def top_up_wallet(user_id, rub):
    async with aiosqlite.connect('database.db') as db:
        await db.execute(f'UPDATE users SET wallet = wallet + ? WHERE user_id = ?', (rub, user_id))
        await db.commit()

#id INTEGER PRIMARY KEY, user_id INT, order_id INT, cost INT, quantity INT, status INT, service_id
async def add_order(user_id, order_id, cost, quantity, status, service_id):
    async with aiosqlite.connect('database.db') as db:
        await db.execute('INSERT INTO orders (user_id, order_id, cost, quantity, status, service_id)'
                         'VALUES(?, ?, ?, ?, ?, ?)', (user_id, order_id, cost, quantity, status, service_id))
        await db.execute(f'UPDATE users SET wallet = wallet - ? WHERE user_id = ?', (cost, user_id))
        await db.commit()