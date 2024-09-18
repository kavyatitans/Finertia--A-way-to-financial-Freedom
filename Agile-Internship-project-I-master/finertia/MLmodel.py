import pandas as pd
import numpy as np
import joblib
from IPython.display import display
from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split, cross_val_score

credit_card_df = pd.read_csv('finertia/datasets/Credit_card.csv')
daily_household_transactions_df = pd.read_csv('finertia/datasets/Daily Household Transactions.csv')
loan_approval_df = pd.read_csv('finertia/datasets/loan_approval_dataset.csv')  # Load the loan approval dataset

# Define productive and non-productive categories
productive_categories = [
    'Transportation', 'Education', 'Healthcare', 'Groceries', 'Investment',
    'Utilities', 'Rent', 'Insurance', 'Savings', 'Household',
    'Public Provident Fund', 'Life Insurance', 'Interest', 'Tax refund',
    'Fixed Deposit', 'Recurring Deposit'
]
non_productive_categories = [
    'Entertainment', 'Dining out', 'Subscription', 'Luxury', 'Gambling',
    'Alcohol', 'Tobacco', 'Cosmetics', 'Fashion', 'Leisure',
    'Festivals', 'Apparel', 'Gift', 'Social Life', 'Tourism',
    'Beauty', 'Grooming'
]

# Redefine the function to label transactions
def label_transaction(row):
    if row['Category'] in productive_categories:
        return 'Productive'
    elif row['Category'] in non_productive_categories:
        return 'Non-Productive'
    else:
        return 'Unknown'

# Apply the labeling function
daily_household_transactions_df['Label'] = daily_household_transactions_df.apply(label_transaction, axis=1)

# Drop rows with 'Unknown' label
daily_household_transactions_df = daily_household_transactions_df[daily_household_transactions_df['Label'] != 'Unknown']

# Assign synthetic Ind_ID to daily household transactions
np.random.seed(42)  # for reproducibility
num_unique_ids = credit_card_df['Ind_ID'].nunique()
synthetic_ids = np.random.choice(credit_card_df['Ind_ID'].unique(), len(daily_household_transactions_df))

daily_household_transactions_df['Ind_ID'] = synthetic_ids

# Aggregate transaction data by synthetic Ind_ID
agg_transactions_df = daily_household_transactions_df.groupby('Ind_ID').agg({
    'Amount': ['sum', 'mean', 'std'],
    'Label': lambda x: (x == 'Productive').sum() / len(x)  # ratio of productive transactions
}).reset_index()

# Flatten the column hierarchy
agg_transactions_df.columns = ['Ind_ID', 'Total_Amount', 'Mean_Amount', 'Std_Amount', 'Productive_Ratio']

# Merge aggregated transaction data with credit card data
merged_df = pd.merge(credit_card_df, agg_transactions_df, on='Ind_ID', how='inner')

# Assuming there is no direct match to merge with the loan approval dataset, we will not merge but handle them separately

# Feature Engineering: Handle missing values and encode categorical variables

# Fill missing values for numerical columns with their mean
numerical_cols = ['Annual_income', 'Birthday_count', 'Std_Amount']
for col in numerical_cols:
    merged_df[col].fillna(merged_df[col].mean(), inplace=True)

# Fill missing values for categorical columns with the mode
categorical_cols = ['GENDER', 'Type_Occupation']
for col in categorical_cols:
    merged_df[col].fillna(merged_df[col].mode()[0], inplace=True)

# Encode categorical variables using one-hot encoding
merged_df = pd.get_dummies(merged_df, columns=['GENDER', 'Car_Owner', 'Propert_Owner', 'Type_Income', 'EDUCATION',
                                               'Marital_status', 'Housing_type', 'Type_Occupation'], drop_first=True)

# Select features and target variable
features = merged_df.drop(columns=['Ind_ID'])
target = merged_df['Productive_Ratio'].apply(lambda x: 1 if x > 0.5 else 0)  # Binary target based on productive ratio

# Split the data into training and testing sets using stratified sampling
X_train, X_test, y_train, y_test = train_test_split(features, target, test_size=0.2, stratify=target, random_state=42)

# Function to evaluate models using cross-validation
def evaluate_model(model, X_train, y_train):
    scores = cross_val_score(model, X_train, y_train, cv=5, scoring='accuracy')
    return np.mean(scores), np.std(scores)

# Initialize models
logistic_regression = LogisticRegression(max_iter=1000)
decision_tree = DecisionTreeClassifier(random_state=42)
random_forest = RandomForestClassifier(random_state=42)

# Evaluate models
logistic_regression_score = evaluate_model(logistic_regression, X_train, y_train)
decision_tree_score = evaluate_model(decision_tree, X_train, y_train)
random_forest_score = evaluate_model(random_forest, X_train, y_train)

# Print evaluation scores
print("Logistic Regression Score:", logistic_regression_score)
print("Decision Tree Score:", decision_tree_score)
print("Random Forest Score:", random_forest_score)

# Train the best performing model (Random Forest in this case)
best_model = random_forest
best_model.fit(X_train, y_train)

# Feature importance analysis
feature_importances = best_model.feature_importances_
features_df = pd.DataFrame({'Feature': X_train.columns, 'Importance': feature_importances})
features_df = features_df.sort_values(by='Importance', ascending=False)

print(features_df.head(10))


# Load the trained model
model_filename = 'finertia/ML Model/model.pkl'
best_model = joblib.load(model_filename)

def classify_financial_status_and_suggest_plan(form_data):
    # Convert form data to the same format used for model training
    input_data = {
        'Annual_income': form_data['annual_income'],
        'Birthday_count': form_data['birthday_count'],
        'Employed_days': form_data['employed_days'],
        'Mobile_phone': int(form_data['mobile_phone']),
        'Work_Phone': int(form_data['work_phone']),
        'Phone': int(form_data['phone']),
        'EMAIL_ID': int(form_data['email_id']),
        'Family_Members': form_data['family_members'],
        'Total_Amount': form_data['total_amount'],
        'Mean_Amount': form_data['mean_amount'],
        'Std_Amount': form_data['std_amount'],
        'Productive_Ratio': form_data['productive_ratio'],
        'GENDER_F': int(form_data['gender_f']),
        'Car_Owner_Y': int(form_data['car_owner_y']),
        'Propert_Owner_Y': int(form_data['propert_owner_y']),
        'Type_Income_' + form_data['type_income']: 1,
        'EDUCATION_' + form_data['education']: 1,
        'Marital_status_' + form_data['marital_status']: 1,
        'Housing_type_' + form_data['housing_type']: 1,
        'Type_Occupation_' + form_data['type_occupation']: 1
    }

    # Ensure all necessary columns are present
    missing_cols = set(features.columns) - set(input_data.keys())
    for col in missing_cols:
        input_data[col] = 0

    input_df = pd.DataFrame([input_data])

    # Reorder columns to match the training data
    input_df = input_df[features.columns]

    # Predict using the trained model
    prediction = best_model.predict(input_df)
    stability = 'Financially Stable' if prediction[0] == 1 else 'Not Financially Stable'

    # Determine loan eligibility and suggested loan amount
    cibil_score = form_data['cibil_score']
    bank_assets_value = form_data['bank_assets_value']
    loan_eligibility = 'Eligible'
    if stability == 'Financially Stable' and cibil_score > 650:
        loan_eligibility = 'Eligible'
        suggested_loan_amount = (0.2 * form_data['annual_income'] + 0.5 * bank_assets_value) / 2
    else:
        loan_eligibility = 'Not Eligible'
        suggested_loan_amount = 0



    # Generate a dynamic step-by-step financial plan
    steps = []
    if stability == 'Not Financially Stable':
        steps.append("1. **Reduce Non-Productive Expenses:** Focus on cutting down spending in non-essential categories.")
        if form_data['productive_ratio'] < 0.3:
            steps.append("2. **Increase Productive Spending:** Ensure essential needs like healthcare and education are prioritized.")
        if form_data['annual_income'] < 30000:
            steps.append("3. **Increase Income:** Consider strategies like upskilling, taking up a side job, or seeking a raise.")
        if bank_assets_value < 5000:
            steps.append("4. **Build Savings:** Start by setting aside a small portion of your income each month to build an emergency fund.")
        if cibil_score < 650:
            steps.append("5. **Improve Credit Score:** Pay off outstanding debts, avoid late payments, and reduce credit utilization.")
        steps.append("6. **Track and Monitor:** Regularly review your expenses and savings. Use budgeting tools or apps to keep track of your financial progress.")

    else:
        steps.append("1. **Maintain Financial Stability:** Continue with your current financial habits to maintain stability.")
        if cibil_score < 700:
            steps.append("2. **Improve Credit Score:** Even though you are financially stable, a higher credit score can provide better loan options. Consider reducing credit card balances and ensuring timely payments.")
        if form_data['total_amount'] > form_data['annual_income'] * 0.5:
            steps.append("3. **Optimize Spending:** Your current expenses are over half of your income. Consider optimizing your spending to ensure more is directed towards savings and investments.")
        steps.append("4. **Invest for the Future:** Explore investment options like retirement accounts, mutual funds, or low-risk savings plans to grow your wealth.")
        steps.append("5. **Plan for Long-Term Goals:** Start planning for significant financial goals such as buying a house, funding education, or retirement.")

    # Convert the steps list into a readable format
    plan_text = "\n".join(steps)

    return stability, loan_eligibility, suggested_loan_amount, plan_text
