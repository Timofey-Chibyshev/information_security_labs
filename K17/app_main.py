from fastapi import FastAPI, Request, Form, HTTPException
from fastapi.responses import HTMLResponse
import sqlite3
import uvicorn

app = FastAPI()

# HTML-форма для входа
login_form = """
<html>
<body>
<form method="post">
    <input type="text" name="username" placeholder="Логин" required><br>
    <input type="password" name="password" placeholder="Пароль" required><br>
    <button type="submit">Войти</button>
</form>
<p>{message}</p>
</body>
</html>
"""

@app.get("/", response_class=HTMLResponse)
async def login_page():
    return login_form.format(message="")

@app.post("/", response_class=HTMLResponse)
async def login(
    username: str = Form(...),
    password: str = Form(...)
):
    conn = sqlite3.connect('vulnerable.db')
    cursor = conn.cursor()
    message = ""
    
    try:
        query = f"SELECT * FROM users WHERE username='{username}' AND password='{password}'"
        cursor.execute(query)
        
        users = cursor.fetchall()  
        
        if users:
            user_list = "<br>".join([f"Добро пожаловать, {user[1]}! (Данные: {user})" for user in users])
            message = f"Успешный вход!<br>{user_list}"
        else:
            message = "Ошибка авторизации!"
            
    except Exception as e:
        message = f"Ошибка: {str(e)}"
    finally:
        conn.close()

    return login_form.format(message=message)

@app.get("/safety", response_class=HTMLResponse)  
async def safety_login_page():
    return login_form.format(message="Используйте безопасную форму входа")

@app.post("/safety", response_class=HTMLResponse)
async def login_safety(
    username: str = Form(...),
    password: str = Form(...)
):
    conn = sqlite3.connect('vulnerable.db')
    cursor = conn.cursor()
    
    try:
        query = "SELECT * FROM users WHERE username=? AND password=?"
        cursor.execute(query, (username, password))
        
        user = cursor.fetchone()
        message = f"Добро пожаловать, {user[1]}!" if user else "Ошибка авторизации!"
            
    except Exception as e:
        message = f"Ошибка: {str(e)}"
    finally:
        conn.close()

    return login_form.format(message=message)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
    