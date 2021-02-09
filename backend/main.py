from fastapi import FastAPI

import pickle

import uvicorn
import pandas as pd

MODEL_NAME = 'KernelMF_n5000_k50_l20.005_lr0.01'

with open(f'models/gridsearch/{MODEL_NAME}/model.p', 'rb') as f:
    model = pickle.load(f)
    print(f'Model loaded successfully.')
    
app = FastAPI()

@app.get('/')
async def root():
    return {'message': str(model)}

@app.get('/model_users')
async def get_model_users():
    known_users = model.known_users
    return {'count': len(known_users), 'items': known_users}

@app.get('/model_items')
async def get_model_items():
    known_items = model.known_items
    return {'count': len(known_items), 'items': known_items}
    
@app.post('/get_recommendations/user={user}&item_list={item_list}&rating_list={rating_list}')
async def get_recommendations(user:str, item_list:str, rating_list:str):
    item_list = item_list.split(',')
    rating_list = [float(x) for x in rating_list.split(',')]
    X_new = pd.DataFrame([{'user_id':user, 'item_id':item} for item in item_list])
    y_new = pd.DataFrame([{'rating':rating} for rating in rating_list])
    
    model.update_users(X_new, y_new, lr=0.01, n_epochs=10, verbose=0)
    recs = model.recommend(user=user, items_known=X_new['item_id'], amount=-1, bound_ratings=True)
    recs = [{'member':x[0], 'film':x[1], 'prediction':x[2]} for x in recs.values]
    
    return {'results': recs}

if __name__ == '__main__':
    uvicorn.run('main:app', host='0.0.0.0', port=8000)