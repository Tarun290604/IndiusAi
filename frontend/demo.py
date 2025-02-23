#!/usr/bin/env python3

import pandas as pd

def find_restaurant_with_highest_avg_calories(csv_file):
    try:
        df = pd.read_csv(csv_file)
        avg_calories = df.groupby('restaurant')['calories'].mean()
        restaurant_with_high_calorie_foods = avg_calories.idxmax()
        return restaurant_with_high_calorie_foods
    except FileNotFoundError:
        return "Error: CSV file not found."
    except Exception as e:
        return f"An error occurred: {str(e)}"

csv_file = 'files/fastfood.csv'
restaurant_name = find_restaurant_with_highest_avg_calories(csv_file)
print(restaurant_name)
