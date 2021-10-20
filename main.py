import json
from fastapi import FastAPI,HTTPException,Depends
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from auth.auth_bearer import JWTBearer
from auth.auth_handler import signJWT

with open("menu.json", "r") as read_file:
    data = json.load(read_file)
    
with open("login.json","r") as read_again_file:
    loginData = json.load(read_again_file)

app = FastAPI()

@app.get('/')
def root():
    return {'Menu':'Item'}

#get all item from list/array
@app.get('/menu', tags=["posts"])
async def get_all():
    return data

#get 1 item from list/array (parameter: id)
@app.get('/menu/{item_id}', tags=["posts"])
async def get(item_id: int):
    for menu_item in data['menu']:
        if menu_item['id'] == item_id:
            return menu_item
    raise HTTPException(
        status_code=404, detail=f'Item not found'
    )

#add item (parameter: id, name): add 1 item on the back of the list/array, id = +1 from last items id
@app.post('/menu', dependencies=[Depends(JWTBearer())], tags=["posts"])
async def add(name:str):
    id = 1
    if (len(data['menu'])>0):
        id = data['menu'][len(data['menu'])-1]['id']+1
    new_data = {'id':id,'name':name}
    data['menu'].append(dict(new_data))
    read_file.close()
    with open("menu.json", "w") as write_file:
        json.dump(data, write_file, indent = 4)
    write_file.close()
    return (new_data)

    raise HTTPException(
        status_code=500, detail=f'Internal Server Error'
    )

#update item (parameter: id, name): search matching id -> rewrite the item name -> update list/array
@app.put('/menu/{item_id}', dependencies=[Depends(JWTBearer())], tags=["posts"])
async def update(item_id:int, name:str):
    for menu_item in data['menu']:
        if menu_item['id'] == item_id:
            menu_item['name'] = name
            read_file.close()
            with open("menu.json", "w") as write_file:
                json.dump(data, write_file, indent = 4)
            write_file.close()
            return {"message":"Data updated successfully"}
    raise HTTPException(
        status_code=404, detail=f'Item not found'
    )   

#delete item (parameter: id): search matching id with inputted int (id wants to be deleted) 
#                            -> delete whole item (id and name) -> update list
@app.delete('/menu/{item_id}', dependencies=[Depends(JWTBearer())], tags=["posts"])
async def delete(item_id:int):
    for menu_item in data['menu']:
        if menu_item['id'] == item_id:
            data['menu'].remove(menu_item)
            read_file.close()
            with open("menu.json", "w") as write_file:
                json.dump(data, write_file, indent = 4)
            write_file.close()
            return {"message":"Data deleted successfully"}
    raise HTTPException(
        status_code=404, detail=f'Item not found'
    )   

#delete all item from list/array
@app.delete('/menu', dependencies=[Depends(JWTBearer())], tags=["posts"])
async def delete_all():
    new_data = data['menu'].clear()
    read_file.close()
    with open("menu.json", "w") as write_file:
        json.dump(new_data, write_file, indent = 4)
    write_file.close()
    return {"message":"All data has been successfully deleted"}

@app.post('/users', tags=["user"])
async def create_user(username:str, email: str, password: str):
    
    for users in loginData['login']:
        if users['username'] == username and users['email'] == email:
            return {"You already have an account"}

    new_data = {'username':username,'email':email, 'password':password}
    loginData['login'].append(dict(new_data))
    read_file.close()
    with open("login.json", "w") as write_file:
        json.dump(loginData, write_file, indent = 4)
    write_file.close()
    return (new_data)

    raise HTTPException(
        status_code=500, detail=f'Internal Server Error'
    )

def check_user (email: str, password: str):
    for users in loginData['login']:
        if users['email'] == email and users['password'] == password:
            return True
    return False

@app.post('/login/{email}', tags = ['user'])
async def user_LogIn (email: str, password:str):
    if check_user(email, password):
        user = loginData['login']
        return signJWT(user),{"Login Success"}
    return {"error": "Wrong login details!"}

@app.delete('/login',dependencies=[Depends(JWTBearer())], tags=["user"])
async def user_Delete (username: str):
     
    for users in loginData['login']:
        if users['username'] == username:
            loginData['login'].remove(users)
            read_file.close()
            with open("login.json", "w") as write_file:
                json.dump(loginData, write_file, indent = 4)
            write_file.close()
            return {"message":"Data deleted successfully"}
    raise HTTPException(
        status_code=404, detail=f'Item not found'
    ) 

@app.get('/login', dependencies=[Depends(JWTBearer())], tags=["user"])
async def show_users():
    return loginData