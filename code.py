# -*- coding: utf-8 -*-
"""Final_Project.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1v2ut1VanqulaC7Hgth5gnEkNX3HSrY4z
"""


import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error

def remove_columns_with_parentheses(df):
    '''
    This function removes columns with parentheses in their names.
    Parameters:
        df (DataFrame): The input DataFrame.
    Returns:
        DataFrame: The DataFrame with specified columns removed.
    '''
    df.columns = df.columns.astype(str)
    cols_to_drop = [col for col in df.columns if '(' in col or ')' in col]
    df = df.drop(columns=cols_to_drop)
    return df

def remove_columns_with_standard_error(df):
    '''
    This function removes columns that contain 'nan'.
    Parameters:
        df (DataFrame): The input DataFrame.
    Returns:
        DataFrame: The DataFrame with specified columns removed.
    '''
    df = df.loc[:, ~df.columns.str.contains('nan', case=False)]
    return df

def process_zillow_file(file_path):
    '''
    This function reads and processes the Zillow file, dropping unnecessary 
    columns.
    Parameters:
        file_path (str): The path to the Zillow CSV file.
    Returns:
        DataFrame: The processed DataFrame.
    '''
    df = pd.read_csv(file_path)
    df = df.drop(columns=['RegionID', 'SizeRank', 'RegionType', 'StateName'], 
                 errors='ignore')
    df = df.rename(columns={'RegionName': 'State'})
    df = df.dropna()
    return df

def clean_data(file_name):
    '''
    This function loads and cleans the household income data.
    Parameters:
        file_name (str): The path to the CSV file.
    Returns:
        DataFrame: The cleaned DataFrame.
    '''
    df = pd.read_csv(file_name, encoding="utf-8", on_bad_lines='skip')
    while df.iloc[0, 0] != "State":
        df = df.drop(0).reset_index(drop=True)
    df.columns = df.iloc[0]
    df = df.drop(0).reset_index(drop=True)
    df = df.dropna(subset=["State"]).reset_index(drop=True)
    df = remove_columns_with_parentheses(df)
    df = remove_columns_with_standard_error(df)
    numeric_cols = df.columns[1:]
    for col in numeric_cols:
        df[col] = df[col].replace(',', '', regex=True).astype(float)
    return df

def perform_linear_regression(df_2018, df_2023, state_input):
    '''
    This function performs linear regression and returns forecasted and actual
    2023 data.
    Parameters:
        df_2018 (DataFrame): The 2018 data DataFrame.
        df_2023 (DataFrame): The 2023 data DataFrame.
        state_input (str): The state for which to perform the regression.
    Returns:
        dict: A dictionary containing years, actual 2023 data, forecasted 
        years, and forecasted data.
    '''
    if state_input not in df_2018["State"].values:
        print(f"State '{state_input}' not found in the data.")
        return None

    state_data_2018 = df_2018[df_2018["State"] == state_input]
    state_data_2023 = df_2023[df_2023["State"] == state_input]

    if state_data_2018.empty or state_data_2023.empty:
        print(f"State '{state_input}' not found in the data.")
        return None

    years_2018 = df_2018.columns[1:].astype(int)
    y_actual_2018 = state_data_2018.iloc[0, 1:].values.astype(float)
    years_2023 = df_2023.columns[1:].astype(int)
    y_actual_2023 = state_data_2023.iloc[0, 1:].values.astype(float)

    x_actual = np.array(years_2018).reshape(-1, 1)
    model = LinearRegression()
    model.fit(x_actual, y_actual_2018)

    x_forecast = np.array(range(min(years_2018), 
                                max(years_2023) + 1)).reshape(-1, 1)
    y_forecast = model.predict(x_forecast)

    return {
        "years_2023": years_2023,
        "y_actual_2023": y_actual_2023,
        "x_forecast": x_forecast.flatten(),
        "y_forecast": y_forecast
    }

def plot_regression_results(results, state_input):
    '''
    This function plots actual and forecasted data for a state.
    Parameters:
        results (dict): The dictionary containing regression results.
        state_input (str): The state for which to plot the data.
    Returns:
        None
    '''
    if results is None:
        print("No data to plot.")
        return

    years_2023 = results["years_2023"]
    y_actual_2023 = results["y_actual_2023"]
    x_forecast = results["x_forecast"]
    y_forecast = results["y_forecast"]

    plt.figure(figsize=(10, 6))
    plt.plot(years_2023, y_actual_2023, marker="o", color="blue", 
             label="Actual 2023 Data")
    plt.plot(x_forecast, y_forecast, linestyle="--", color="red", 
             label="Forecast (2018 Model)")
    plt.xlabel("Year", fontsize=12)
    plt.ylabel("Household Income ($)", fontsize=12)
    plt.title(f"Household Income Comparison for {state_input} \
(Forecast vs. Actual)", fontsize=14)
    plt.legend(fontsize=10)
    plt.grid(True)
    plt.tight_layout()
    plt.show()

def plot_zillow_data(df):
    '''
    This function plots Zillow data for either a single state or all 
    states based on user input.
    Parameters:
        df (DataFrame): The Zillow data DataFrame.
    Returns:
        None
    '''
    state_input = input("Enter the state you want to visualize, or type \
 'all' to visualize all states: ").strip()
    if state_input.lower() == 'all':
        df = df.reset_index()
        df["State"] = df["State"].astype(str).str.strip()
        time_series = df.set_index("State").T
        time_series.index = pd.to_datetime(time_series.index, errors='coerce',
                                           format='%Y-%m-%d')
        if time_series.index.isna().any():
            print("Warning: Some dates could not be converted correctly.")
            print("The invalid dates are:", 
                  time_series.index[time_series.index.isna()])
        custom_dates = ['2000-10-31', '2004-10-31', '2008-10-31',
                        '2012-10-31', '2016-10-31', '2020-10-31', '2024-10-31']
        custom_dates = pd.to_datetime(custom_dates)
        plt.figure(figsize=(12, 8))
        for state in time_series.columns:
            plt.plot(time_series.index, time_series[state], label=state,
                     linewidth=1, alpha=0.8)
        plt.xticks(custom_dates, labels=[date.strftime('%Y-%m-%d') 
                                         for date in custom_dates], 
                   rotation=45, fontsize=10)
        plt.title("Median Home Values Over Time for All States", fontsize=16)
        plt.xlabel("Time", fontsize=14)
        plt.ylabel("Median Home Value ($)", fontsize=14)
        plt.legend(fontsize=8, loc='upper left', bbox_to_anchor=(1, 1), ncol=1)
        plt.grid(True)
        plt.tight_layout()
        plt.show()
    else:
        if state_input not in df["State"].values:
            print(f"State '{state_input}' not found in the data.")
            return
        df_state = df[df["State"] == state_input]
        df_state = df_state.reset_index()
        df_state["State"] = df_state["State"].astype(str).str.strip()
        time_series = df_state.set_index("State").T
        time_series.index = pd.to_datetime(time_series.index, errors='coerce',
                                           format='%Y-%m-%d')
        if time_series.index.isna().any():
            print("Warning: Some dates could not be converted correctly.")
            print("The invalid dates are:", 
                  time_series.index[time_series.index.isna()])
        custom_dates = ['2000-10-31', '2004-10-31', '2008-10-31', '2012-10-31',
                        '2016-10-31', '2020-10-31', '2024-10-31']
        custom_dates = pd.to_datetime(custom_dates)
        plt.figure(figsize=(12, 8))
        plt.plot(time_series.index, time_series[state_input], 
                 label=state_input, linewidth=1, alpha=0.8)
        plt.xticks(custom_dates, labels=[date.strftime('%Y-%m-%d') 
                                         for date in custom_dates], 
                   rotation=45, fontsize=10)
        plt.title(f"Median Home Values Over Time for {state_input}", 
                  fontsize=16)
        plt.xlabel("Time", fontsize=14)
        plt.ylabel("Median Home Value ($)", fontsize=14)
        plt.legend(fontsize=8)
        plt.grid(True)
        plt.tight_layout()
        plt.show()
def zillow_regression(data, state):
    '''
    This function performs linear regression on Zillow data for a specific 
    state.
    Parameters:
        data (DataFrame): The Zillow data DataFrame.
        state (str): The state for which to perform the regression.
    Returns:
        dict: A dictionary containing regression coefficients, intercept, 
        predictions, time indices, and housing prices.
    '''
    state_data = data[data["State"] == state]
    if state_data.empty:
        print(f"State '{state}' not found in the dataset.")
        return None

    X = np.arange(len(state_data.columns[1:])).reshape(-1, 1)
    Y = state_data.iloc[0, 1:].values.astype(float)

    model = LinearRegression()
    model.fit(X, Y)

    return {
        "coef": model.coef_[0],
        "intercept": model.intercept_,
        "predicted": model.predict(X),
        "X": X.flatten(),
        "Y": Y
    }

def plot_regression(results, state):
    '''
    This function plots actual values and linear regression for the 
    specified state.
    Parameters:
        results (dict): The dictionary containing regression results.
        state (str): The state for which to plot the data.
    Returns:
        None
    '''
    X = results["X"]
    Y = results["Y"]
    predicted = results["predicted"]

    plt.figure(figsize=(10, 6))
    plt.plot(X, Y, label="Actual Values", color="blue", marker="o")
    plt.plot(X, predicted, label="Regression Line", 
             color="red", linestyle="--")
    plt.axvline(x=len(Y) - 1, color="green", linestyle=":", 
                label="Split Point (End of Actual Data)")
    plt.title(f"Linear Regression for {state}")
    plt.xlabel("Time Index")
    plt.ylabel("Housing Prices")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.show()

def aggregate_to_yearly(df):
    '''
    This function aggregates monthly data into yearly averages using
    a for loop for each state.
    Parameters:
        df (DataFrame): The input DataFrame with a 'State' column 
        and date-based columns in the format 'YYYY-MM'.
    Returns:
        DataFrame: The DataFrame with yearly averages.
    '''
    df = df.copy()
    state_column = df["State"]
    numeric_data = df.drop(columns=["State"], errors="ignore")

    yearly_data = {}
    for col in numeric_data.columns:
        if "-" in col:
            year = col.split("-")[0]
            if year not in yearly_data:
                yearly_data[year] = []
            yearly_data[year].append(numeric_data[col])

    yearly_averages = pd.DataFrame({year: pd.concat(cols, axis=1).mean(axis=1) 
                                    for year, cols in yearly_data.items()})
    yearly_averages.insert(0, "State", state_column.values)
    return yearly_averages

def compute_per_state_correlation_aligned(df_income, df_zillow):
    '''
    This function computes the correlation between median household income 
    and home values for each state, using aligned yearly data.
    Parameters:
        df_income (DataFrame): The DataFrame containing income data.
        df_zillow (DataFrame): The DataFrame containing Zillow data.
    Returns:
        dict: A dictionary of state correlations sorted from highest to lowest.
    '''
    df_merged = pd.merge(df_income, df_zillow, on="State", 
                         suffixes=('_income', '_home_value'))

    income_years = set(df_income.columns[1:].astype(str))
    zillow_years = set(df_zillow.columns[1:].astype(str))
    common_years = list(income_years & zillow_years)
    common_years.sort()

    df_income_common = df_income[["State"] + common_years]
    df_zillow_common = df_zillow[["State"] + common_years]

    df_merged = pd.merge(df_income_common, df_zillow_common, on="State",
                         suffixes=('_income', '_home_value'))

    state_correlations = {}
    for state in df_merged["State"].unique():
        state_data = df_merged[df_merged["State"] == state]
        income_data = state_data.iloc[:,
                                      1:len(common_years)+1].values.flatten()
        home_value_data = state_data.iloc[:,
                                          len
                                          (common_years)+1:].values.flatten()
        if len(income_data) > 1 and len(home_value_data) > 1:
            correlation = np.corrcoef(income_data, home_value_data)[0, 1]
        else:
            correlation = np.nan
        state_correlations[state] = correlation

    sorted_state_correlations = {k: v for k, v in 
                                 sorted(state_correlations.items(),
                                        key=lambda item: item[1], 
                                        reverse=True)}

    print("Correlation between median household income and median home 
          values by state (sorted from highest to lowest):")
    for state, corr in sorted_state_correlations.items():
        print(f"{state}: {corr:.2f}" if not np.isnan(corr) 
              else f"{state}: Insufficient data")

    return sorted_state_correlations

def plot_correlation_heatmap(correlations):
    '''
    This function plots a heatmap of state correlations, sorted from
    highest to lowest.
    Parameters:
        correlations (dict): Dictionary of state correlations.
    Returns:
        None
    '''
    corr_df = pd.DataFrame(list(correlations.items()), 
                           columns=['State', 'Correlation'])
    corr_df = corr_df.set_index('State')
    corr_df = corr_df.sort_values(by='Correlation', ascending=False)

    plt.figure(figsize=(12, 8))
    sns.heatmap(corr_df, annot=True, cmap='coolwarm', cbar=True, fmt=".2f", 
                annot_kws={"size": 10})
    plt.title('Correlation Heatmap: Household Income vs. Median Home Values',
              fontsize=16)
    plt.ylabel('State', fontsize=14)
    plt.yticks(rotation=0)
    plt.tight_layout()
    plt.show()

def plot_residuals(df_2018, df_2023, state_input):
    '''
    This function performs linear regression and plots residuals for a
    given state.
    Parameters:
        df_2018 (DataFrame): The 2018 data DataFrame.
        df_2023 (DataFrame): The 2023 data DataFrame.
        state_input (str): The state for which to plot the residuals.
    Returns:
        None
    '''
    if state_input not in df_2018["State"].values:
        print(f"State '{state_input}' not found in the data.")
        return None

    state_data_2018 = df_2018[df_2018["State"] == state_input]
    state_data_2023 = df_2023[df_2023["State"] == state_input]

    if state_data_2018.empty or state_data_2023.empty:
        print(f"State '{state_input}' not found in the data.")
        return None

    years_2018 = df_2018.columns[1:].astype(int)
    y_actual_2018 = state_data_2018.iloc[0, 1:].values.astype(float)
    years_2023 = df_2023.columns[1:].astype(int)
    y_actual_2023 = state_data_2023.iloc[0, 1:].values.astype(float)

    x_actual = np.array(years_2018).reshape(-1, 1)
    model = LinearRegression()
    model.fit(x_actual, y_actual_2018)

    x_forecast = np.array(range(min(years_2018), 
                                max(years_2023) + 1)).reshape(-1, 1)
    y_forecast = model.predict(x_forecast)

    residuals = y_actual_2023 - model.predict(np.array(years_2023).reshape
                                              (-1, 1))

    plt.figure(figsize=(10, 6))
    plt.scatter(years_2023, residuals, color='blue', label='Residuals')
    plt.axhline(y=0, color='red', linestyle='--', label='Zero Error Line')
    plt.xlabel("Year", fontsize=12)
    plt.ylabel("Residuals", fontsize=12)
    plt.title(f"Residuals for {state_input} (Actual vs. Predicted)", 
              fontsize=14)
    plt.legend(fontsize=10)
    plt.grid(True)
    plt.tight_layout()
    plt.show()


def main():
    # File paths for the data
    file_2018 = 'household_income_2018.csv'
    file_2023 = 'household_income_2023.csv'
    zillow_file = 'zillow_data.csv'

    # Clean the 2018 data
    print("Cleaning 2018 data...")
    df_2018 = clean_data(file_2018)

    # Clean the 2023 data
    print("Cleaning 2023 data...")
    df_2023 = clean_data(file_2023)

    # Process Zillow data
    print("Processing Zillow data...")
    df_zillow = process_zillow_file(zillow_file)

    # Aggregate Zillow data to yearly averages
    print("Aggregating Zillow data to yearly averages...")
    df_zillow_yearly = aggregate_to_yearly(df_zillow)

    # User input for the state for income comparison
    state_input = input("Enter the state you want to compare\
 for income: ").strip()

    # Perform linear regression for the state and generate results
    print("\nPerforming linear regression for income data...")
    results = perform_linear_regression(df_2018, df_2023, state_input)

    # Plot the regression results (Income comparison)
    if results:
        print("\nPlotting income comparison results...")
        plot_regression_results(results, state_input)
    else:
        print(f"Could not perform regression for {state_input}.")

    # Plot residuals for the regression model
    print("\nPlotting residuals for the regression model...")
    plot_residuals(df_2018, df_2023, state_input)

    # Plot Zillow data (user chooses a state or all states)
    print("\nPlotting Zillow data...")
    plot_zillow_data(df_zillow)

    # Ask user for a state to perform regression on for Zillow data
    state_input_zillow = input("Enter a state to perform regression on (or \
 'all' for all states): ").strip()

    # Perform linear regression for Zillow data
    print(f"\nPerforming linear regression on Zillow data for \
 {state_input_zillow}...")
    zillow_results = zillow_regression(df_zillow, state_input_zillow)

    # Plot regression results for Zillow data
    if zillow_results:
        print("\nPlotting Zillow regression results...")
        plot_regression(zillow_results, state_input_zillow)
    else:
        print(f"Could not perform regression for {state_input_zillow}.")

    # Compute correlations between income and Zillow data
    print("\nComputing correlations between income and Zillow data...")
    state_correlations = compute_per_state_correlation_aligned(
        df_2023, df_zillow_yearly)

    # Generate heatmap
    print("\nGenerating heatmap of correlations...")
    plot_correlation_heatmap(state_correlations)

if __name__ == "__main__":
    main()