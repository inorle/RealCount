import numpy as np
import pandas as pd
import statistics
import typer


app = typer.Typer()


a = pd.read_json('users.json')
c = pd.read_json('items.json')
b = pd.read_json('interactions.json')


#mapped values to matrix of item (x-axis) by user (y-axis)
map = {'view':1, 'like':2, 'purchase':3}
data = np.zeros((len(a), len(c)))
for i in range(len(b)):
    user_id = b.loc[i]['user_id']
    item_id = b.loc[i]['item_id']
    value = map[b.loc[i]['interaction_type']]
    data[user_id-1][item_id-1]= value


@app.callback()
def loading_callback():
    typer.echo("Loading Recommendations...")

@app.command()
def recommend():
    user_id = typer.prompt("What's your user id?")
    #weight based on similarities
    user_id = int(user_id) - 1
    distance = np.zeros((len(a), len(c)))
    distance_from = data[user_id]
    #preference weight based on previous purchases - category and avg price
    indexes_bought = [c.loc[index]['item_price'] for index, value in enumerate(distance_from) if value == 3]
    median_price = statistics.median(indexes_bought)
    categories = set([c.loc[index]['item_category'] for index, value in enumerate(distance_from) if value != 0])
    avg_others_users_influence = []
    for i in range(len(a)):
       for j in range(len(c)):
          distance[i][j] = 10-(data[i][j] - distance_from[j])**2
          #weight based on age/demographics
          if abs(a.loc[i]['user_age'] - a.loc[user_id]['user_age']) < 10:
              distance[i][j] += 2
          if abs(a.loc[i]['user_location'] == a.loc[user_id]['user_location']):
              distance[i][j] += 2
       avg_others_users_influence.append(sum(distance[i])/len(distance[i]))
    #    print(avg_others_users_influence)
    item_weight = np.zeros(len(c))
    for i in range(len(c)):
        #weight based on if item price is in range
        item_weight[i] -= .05*abs(c.loc[i]['item_price'] - median_price)
        #weight based on if it is similar to items they have bought or liked
        if c.loc[i]['item_category'] in categories:
            item_weight[i] += 2
        #weight based on popularity
    
    result_matrix = np.outer(distance, item_weight)

    
    # print(result_matrix)
    max_values = np.max(result_matrix, axis=0)
    # print(max_values)

    sorted_indices = np.argsort(max_values)[::-1]
    
    to_recommend = [c.loc[sorted_indices[index]] for index, value in enumerate(sorted_indices) if distance_from[value] == 0 and index < 5]
    df = pd.DataFrame(to_recommend)
    print((df))
    

if __name__ == "__main__":
    app()

