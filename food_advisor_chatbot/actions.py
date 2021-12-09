# This files contains your custom actions which can be used to run
# custom Python code.
#
# See this guide on how to implement these action:
# https://rasa.com/docs/rasa/custom-actions


# This is a simple example for a custom action which utters "Hello World!"

from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet
from rasa_sdk.events import AllSlotsReset
import requests
import json
import pandas as pd
import re
from os import path
from sklearn.preprocessing import StandardScaler
from scipy.spatial.distance import euclidean
import math

df_restaurant = pd.read_csv('cleaned_tripadvisor1.csv')

class ActionSuggestFood(Action):
    def name(self) -> Text:
        return "action_suggest_food"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        df = pd.read_csv("food_recipes.csv")
        table = df.describe()

        carbohydrate = tracker.get_slot("nutrition_carbohydrate")
        calories = tracker.get_slot("nutrition_calories")
        cholesterol = tracker.get_slot("nutrition_cholesterol")
        sugar = tracker.get_slot("nutrition_sugar")
        protein = tracker.get_slot("nutrition_protein")
        recipe_category = tracker.get_slot("recipe_category")



        if "less" in calories:
            mask_calories = df["Calories"] < table.loc["50%"]["Calories"]
        elif "more" in calories:
            mask_calories = df["Calories"] > table.loc["50%"]["Calories"]
        elif calories.isalnum():
            value = re.findall("\d+\.?\d+", calories)
            if len(value) > 1:
                mask_calories = (df["Calories"] > float(min(value))) & (df["Calories"] < float(max(value)))
            elif len(value) == 1:
                mask_calories = df["Calories"] == float(value[0])
        else:
            mask_calories = True
        
        if "less" in carbohydrate:
            mask_carbohydrate = df["CarbohydrateContent"] < table.loc["50%"]["CarbohydrateContent"]
        elif "more" in carbohydrate:
            mask_carbohydrate = df["CarbohydrateContent"] > table.loc["50%"]["CarbohydrateContent"]
        elif carbohydrate.isalnum():
            value = re.findall("\d+\.?\d+", carbohydrate)
            if len(value) > 1:
                mask_carbohydrate = (df["CarbohydrateContent"] > float(min(value))) & (df["CarbohydrateContent"] < float(max(value)))
            elif len(value) == 1:
                mask_carbohydrate = df["CarbohydrateContent"] == float(value[0])
        else:
            mask_carbohydrate = True

        if "less" in cholesterol:
            mask_cholesterol = df["CholesterolContent"] < table.loc["50%"]["CholesterolContent"]
        elif "more" in cholesterol:
            mask_cholesterol = df["CholesterolContent"] > table.loc["50%"]["CholesterolContent"]
        elif cholesterol.isalnum():
            value = re.findall("\d+\.?\d+", cholesterol)
            if len(value) > 1:
                mask_cholesterol = (df["CholesterolContent"] > float(min(value))) & (df["CholesterolContent"] < float(max(value)))
            elif len(value) == 1:
                mask_cholesterol = df["CholesterolContent"] == float(value[0])
        else:
            mask_cholesterol = True

        if "less" in sugar:
            mask_sugar = df["SugarContent"] < table.loc["50%"]["SugarContent"]
        elif "more" in sugar:
            mask_sugar = df["SugarContent"] > table.loc["50%"]["SugarContent"]
        elif sugar.isalnum():
            value = re.findall("\d+\.?\d+", sugar)
            if len(value) > 1:
                mask_sugar = (df["SugarContent"] > float(min(value))) & (df["SugarContent"] < float(max(value)))
            elif len(value) == 1:
                mask_sugar = df["SugarContent"] == float(value[0])
        else:
            mask_sugar = True

        if "less" in protein:
            mask_protein = df["ProteinContent"] < table.loc["50%"]["ProteinContent"]
        elif "more" in protein:
            mask_protein = df["ProteinContent"] > table.loc["50%"]["ProteinContent"]
        elif protein.isalnum():
            value = re.findall("\d+\.?\d+", protein)
            if len(value) > 1:
                mask_protein = (df["ProteinContent"] > float(min(value))) & (df["ProteinContent"] < float(max(value)))
            elif len(value) == 1:
                mask_protein = df["ProteinContent"] == float(value[0])
        else:
            mask_protein = True        

        if df[df["RecipeCategory"] == recipe_category].empty:
            mask_category = True
        else:
            mask_category = df["RecipeCategory"] == recipe_category

        df_result = df[mask_calories & mask_carbohydrate & mask_cholesterol & mask_sugar & mask_protein & mask_category]
        if df_result.empty:
            dispatcher.utter_message("No matching result")
        else:
            dispatcher.utter_message("Here is your result: \n" + df_result["Name"].iloc[0])

        list_search_result = [df_result["Name"].iloc[i] for i in range(len(df_result["Name"]))]
        return [SlotSet("food_search_result", list_search_result), SlotSet("choice_count", 0), SlotSet("food_selection", df_result["Name"].iloc[0]), SlotSet("flag_action", "Searching")]

class ActionProvideOtherFoodChoices(Action):

    def name(self):
        return "action_provide_other_food_choices"

    def run(self, dispatcher,
             tracker,
             domain):
        
        choice_count = tracker.get_slot("choice_count")
        choice_count += 1
        flag_action = tracker.get_slot("flag_action")

        if flag_action == "Searching":
            list_search_result = tracker.get_slot("food_search_result")
            if choice_count <= (len(list_search_result) - 1):
                dispatcher.utter_message("Here is the result: \n" + list_search_result[choice_count])
                return [SlotSet("choice_count", choice_count), SlotSet("food_selection", list_search_result[choice_count])]
        elif flag_action == "Recommendation":
            recommended_recipes = tracker.get_slot("recommended_recipes")
            if choice_count <= (len(recommended_recipes) - 1):
                dispatcher.utter_message("Here is the result: \n" + recommended_recipes[choice_count])
                return [SlotSet("choice_count", choice_count), SlotSet("food_selection", recommended_recipes[choice_count])]
        return [SlotSet("choice_count", choice_count)]

class ActionSelectFood(Action):

    def name(self):
        return "action_select_food"

    def run(self, dispatcher,
             tracker,
             domain):

        food_selection = tracker.get_slot("food_selection")

        df = pd.read_csv("food_recipes.csv")
        df_select = df[df["Name"] == food_selection]

        if path.exists("user_record.csv"):
            df_select.to_csv("user_record.csv", mode='a', header=False)
        else: 
            df_select.to_csv("user_record.csv")
        return []

class ActionRecommendFood(Action):

    def name(self):
        return "action_recommend_food"

    def run(self, dispatcher,
             tracker,
             domain):
        recipe_category = tracker.get_slot("recipe_category")

        df = pd.read_csv("food_recipes.csv")
        df_sample = pd.read_csv("user_record.csv")

        df = df.set_index("RecipeId")
        df_all = df[df["RecipeCategory"] == recipe_category].drop(columns=["RecipeCategory", "Name", "RecipeServings", "HighScore"])
        df_sample = df_sample.set_index("RecipeId")
        df_sample = df_sample.drop(columns=["id", "RecipeCategory", "Name", "RecipeServings", "HighScore"])

        std = StandardScaler()
        df_all_scaled = std.fit_transform(df_all)
        df_sample_scaled = std.transform(df_sample)

        df_all_scaled = pd.DataFrame(df_all_scaled)
        df_sample_scaled = pd.DataFrame(df_sample_scaled)

        df_all_scaled.columns = df_all.columns
        df_all_scaled.index = df_all.index
        df_sample_scaled.columns = df_sample.columns
        df_sample_scaled.index = df_sample.index

        row_in_user_record = list(set(df_sample_scaled.index.tolist()))
        row_to_drop = []
        for item in row_in_user_record:
            if item in df_all_scaled.index.tolist():
                row_to_drop.append(item)
        df_sample_scaled = df_sample_scaled.describe().loc["mean"]

        df_all_scaled = df_all_scaled.drop(row_to_drop)
        df_distance = pd.DataFrame(data=df_all_scaled.index)
        df_distance["distance"] = df_distance["RecipeId"].apply(lambda x: euclidean(df_all_scaled.loc[x], df_sample_scaled))
        df_distance.sort_values(by='distance',inplace=True)

        recipeId = df_distance.iloc[0]["RecipeId"]
        dispatcher.utter_message("Here is the result: \n" + df.loc[recipeId]["Name"])

        recommended_recipes = [df.loc[df_distance.iloc[i]["RecipeId"]]["Name"] for i in range(len(df_distance["RecipeId"]))]

        return [SlotSet("recommended_recipes", recommended_recipes), SlotSet("food_selection", df.loc[df_distance.iloc[0]["RecipeId"]]["Name"]), SlotSet("choice_count", 0), SlotSet("flag_action", "Recommendation")]



class ActionRecordComplaint(Action):

    def name(self):
        return "action_record_complaint"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        txt = tracker.get_slot("complain_details")
        complain_name  = tracker.get_slot("complain_name")
        complain_aspect = tracker.get_slot("complain_aspect")
        complain_target = tracker.get_slot("complain_target")

        d = {'Type': [complain_target], 'Name': [complain_name], 'Aspect': [complain_aspect], 'Details': [txt]}
        df = pd.DataFrame(data=d)
        
        if path.exists("user_complain_record.csv"):
            df.to_csv("user_complain_record.csv", mode='a', header=False)
        else: 
            df.to_csv("user_complain_record.csv")

        return []

class ActionRecommendRestaurant(Action):
    def name(self):
        return "action_recommend_restaurant"

    def run(self, dispatcher, tracker, domain):
        dispatcher.utter_message(text="looking for restaurants")
        quality=tracker.get_slot("quality")
        city=tracker.get_slot("city")
        cuisine=tracker.get_slot("primary_cus")
        
        df_selected=df_restaurant[(df_restaurant['city']==city) & (df_restaurant['primary_cus']==cuisine)].sort_values(by='ratio', ascending=True)
        
        if df_selected.shape[0] == 0:
            choice = 'No good choice now, please change options.'
        else:
            if quality == 'top':
                choice = df_selected.iloc[0:math.ceil(df_selected.shape[0]/5)].sample(1)
            elif quality == 'daily':
                choice = df_selected.iloc[int(df_selected.shape[0]/3):(df_selected.shape[0]-1)].sample(1)
            else:
                choice = df_selected.sample(1)              
            dispatcher.utter_message(text="here's what I found:")
            dispatcher.utter_message(text='Recomend restaurant: name '+ choice['name'].values[0] +' Primary cuisine:'
                                    +choice['primary_cus'].values[0] + ' Address:' + choice['address'].values[0])
            
        return [SlotSet("restaurant_name", choice['name'].values[0]),SlotSet("primary_cus",choice['primary_cus'].values[0]),
                SlotSet("address", choice['address'].values[0]), SlotSet("restaurant_id", choice['ID_TA'].values[0])]

class ActionSearcchRestaurant(Action):
    def name(self):
        return "action_search_restaurant"
    def run(self, dispatcher, tracker, domain):

        dispatcher.utter_message(text="searching for restaurants")
        restaurant=tracker.get_slot("restaurant_name")
        city=tracker.get_slot("city")
        attribute=tracker.get_slot("attribute")
        
        choice=df_restaurant[(df_restaurant['city']==city) & (df_restaurant['name']==restaurant)]
        
        if choice.shape[0] == 0:
            choice = 'No good choice now, please change options.'
        else:
            choice = choice.sample(1)             
            dispatcher.utter_message(text="here's what I found:")
            dispatcher.utter_message(text='The restaurant: name '+ choice['name'].values[0] +' information needed:'
                                    +str(choice[attribute].values[0]))
            
        return [SlotSet("restaurant_name", choice['name'].values[0]),SlotSet("restaurant_id", choice['ID_TA'].values[0])] 

class ActionGetHistoryRecord(Action):
    
    def name(self):
        return "action_get_history_record"
    def run(self, dispatcher, tracker, domain):

        dispatcher.utter_message(text="searching your last restaurant ID")
        customer_id=int(tracker.get_slot("customer_id"))
        transaction = pd.read_csv('transaction.csv')
        
        choice=transaction[transaction['customer_id']==customer_id].sort_values(by='booking_time', ascending=False)
        
        if choice.shape[0] == 0:
            choice = 'No historical transaction now, please change customer id, or I can recomend restaurant for you.'
        else:          
            dispatcher.utter_message(text="I found your last consumed restuarant:")
            dispatcher.utter_message(text='The restaurant is: '+ choice['restaurant_name'].values[0])
            
        return [SlotSet("restaurant_name", choice['restaurant_name'].values[0]),SlotSet("restaurant_id", choice['restaurant_id'].values[0])] 

class ActionBookRestaurant(Action):
    
    def name(self):
        return "action_book_restaurant"

    def run(self, dispatcher, tracker, domain):
        dispatcher.utter_message(text="Recording booking information for you")
        customer_name=tracker.get_slot("name")
        restaurant_id=tracker.get_slot("restaurant_id")
        restaurant_name=tracker.get_slot("restaurant_name")
        num_people=tracker.get_slot("num_people")
        date=tracker.get_slot("date")
        time=tracker.get_slot("time")
        
        if restaurant_id is None:
            restaurant_id = df_restaurant[df_restaurant["name"] == restaurant_name]["ID_TA"].values[0]
            print(restaurant_id)

        transaction = pd.read_csv('transaction.csv')
        customer_id=max(transaction['customer_id'])+1
        dict = {'customer_id':customer_id,
        'customer_name':customer_name,
        'restaurant_id':restaurant_id,
        'restaurant_name':restaurant_name,
        'num_people':num_people,
        'date':date, 'time':time,'booking_time':pd.Timestamp.now()
       }

        df2=pd.DataFrame(dict,index=[0])
        df3=pd.concat([transaction,df2],ignore_index=True)
        df3.to_csv('transaction.csv',index = False)

        dispatcher.utter_message(text="Please remember your customer ID" + str(customer_id))
            
        return [SlotSet("customer_id", str(customer_id))] 

class ActionCancelBooking(Action):
    
    def name(self):
        return "action_cancel_booking"

    def run(self, dispatcher, tracker, domain):
        dispatcher.utter_message(text="Canceling the reservation for you now")
        customer_id=int(tracker.get_slot("customer_id"))
        transaction = pd.read_csv('transaction.csv')
        
        transaction=transaction.sort_values(by='booking_time', ascending=False)

        for i in range(transaction.shape[0]):
            if transaction.at[i,'customer_id']==customer_id:
                transaction.at[i,'cancel_time']=pd.Timestamp.now()
                restuarant=transaction.at[i,'restaurant_name']
                transaction.to_csv('transaction.csv',index = False)      
                break

        dispatcher.utter_message(text="Have canceled your booking or no booking at all")
        dispatcher.utter_message(text='Previous booking restaurant' + restuarant)
            
        return [] 

class ActionRating(Action):
    
    def name(self):
        return "action_rating"

    def run(self, dispatcher, tracker, domain):
        dispatcher.utter_message(text="Record rating and suggestion for you now")
        customer_id=int(tracker.get_slot("customer_id"))
        transaction = pd.read_csv('transaction.csv')
        transaction["suggestion"] = transaction["suggestion"].astype(str)
        
        transaction=transaction.sort_values(by='booking_time', ascending=False)
                        
        for i in range(transaction.shape[0]):
            if transaction.at[i,'customer_id']==customer_id:
                transaction.at[i,'rating_score']=tracker.get_slot("rating_score")
                transaction.at[i,'suggestion']=tracker.get_slot("suggestion")
                restuarant=transaction.at[i,'restaurant_name']
                transaction.to_csv('transaction.csv',index = False)      
                break

        dispatcher.utter_message(text="Have rated your booking or no booking at all")
        dispatcher.utter_message(text='Being evaluated restaurant: ' + restuarant)
            
        return []

class ActionClearAllSlot(Action):

    def name(self):
        return "action_clear_all_slot"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        #dispatcher.utter_message(text="Reset all slots")
        return [AllSlotsReset()]