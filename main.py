import numpy as np
import pandas as pd
import statistics
import typer

#creates instance of typer class
app = typer.Typer()

#reads three json files and parses them into dataframe format
users = pd.read_json('users.json')
items = pd.read_json('items.json')
interactions = pd.read_json('interactions.json')


#create data which is a np matrix with users as x and items as y with value of 0 if user hasn't interacted with product
map = {'view':1, 'like':2, 'purchase':3}
data = np.zeros((len(users), len(items)))
for i in range(len(interactions)):
    #find the user_id and item_id associated with each interaction
    user_id = interactions.loc[i]['user_id']
    item_id = interactions.loc[i]['item_id']
    #map value of interaction type 
    value = map[interactions.loc[i]['interaction_type']]
    #since both the user_id and the item_id start at 1 and not 0 we need to map this to an array with a 0 based index
    #if we were to delete items from the database or users so we no longer had the [-1] userid = len(users), we would need to adjust this approach
    data[user_id-1][item_id-1]= value

#prints Loading Recommendations... to the screen
@app.callback()
def loading_callback():
    typer.echo("Loading Recommendations...")

@app.command()
def recommend():
    user_id = typer.prompt("What's your user id?")
    #since our dataset starts at user_id 1, we need to map this to an array that will start at index 0
    user_id = int(user_id) - 1
    #create distance matrix to measure the distance other users are in habbits to current user
    distance = np.zeros((len(users), len(items)))
    distance_from = data[user_id]
    #preference weight based on previous habbits - category set based on likes/views/purchases and median price based on purchases
    indexes_bought = [items.loc[index]['item_price'] for index, value in enumerate(distance_from) if value == 3]
    median_price = statistics.median(indexes_bought)
    categories = set([items.loc[index]['item_category'] for index, value in enumerate(distance_from) if value != 0])
    #loop through users to find the users who are most similar in interaction type/age/geography to current user
    avg_others_users_influence = []
    for i in range(len(users)):
       for j in range(len(items)):
          #weight based on the difference in interaction type between users and one item
          distance[i][j] = 10-(data[i][j] - distance_from[j])**2
          #weight based on age/demographics
          if abs(users.loc[i]['user_age'] - users.loc[user_id]['user_age']) < 10:
              distance[i][j] += 2
          if abs(users.loc[i]['user_location'] == users.loc[user_id]['user_location']):
              distance[i][j] += 2
       avg_others_users_influence.append(sum(distance[i])/len(distance[i]))
    #    print(avg_others_users_influence)
    #initialize item_weight np array to be 0 for each possible item
    item_weight = np.zeros(len(items))
    for i in range(len(items)):
        #weight based on if item price is in range
        item_weight[i] -= .05*abs(items.loc[i]['item_price'] - median_price)
        #weight based on if it is similar to items they have bought or liked
        if items.loc[i]['item_category'] in categories:
            item_weight[i] += 4
    #multiply the two weights per user and per item together
    result_matrix = np.outer(distance, item_weight)

    # print(result_matrix)
    max_values = np.max(result_matrix, axis=0)
    # print(max_values)
    #sort the indicies of the max values in descending order
    sorted_indices = np.argsort(max_values)[::-1]
    
    #add top 5 to recomended if a user hasn't looked at this item/liked/purchased it
    to_recommend = [items.loc[sorted_indices[index]] for index, value in enumerate(sorted_indices) if distance_from[value] == 0 and index < 5]
    df = pd.DataFrame(to_recommend)
    print((df))
    

#invokes app if main is called
if __name__ == "__main__":
    app()

