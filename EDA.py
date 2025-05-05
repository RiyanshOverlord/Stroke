import pandas as pd

# Load the dataset 
# df = pd.read_csv('new_learning_dataset.csv')
df = pd.read_csv('modified_learning_dataset.csv')



print("Shape of dataset:", df.shape)
print(df.info())
print(df.describe())


missing_values = df.isnull().sum()
print("Missing values in each column:\n", missing_values)

import seaborn as sns
import matplotlib.pyplot as plt

plt.figure(figsize=(10, 6))
sns.heatmap(df.isnull(), cbar=False, cmap="viridis")
plt.title("Missing Values Heatmap")
plt.show()


sns.countplot(x='Gender',hue='Stroke Outcome', data=df)
plt.title("Distribution of Gender")
plt.show()

sns.countplot(x='Hypertension',hue='Stroke Outcome', data=df)
plt.title("Distribution of Hypertension")
plt.show()

sns.countplot(x='Heart Disease',hue='Stroke Outcome', data=df)
plt.title("Distribution of Heart Disease")
plt.show()

sns.countplot(x='Marital Status',hue='Stroke Outcome', data=df)
plt.title("Distribution of Martial Status")
plt.show()

sns.countplot(x='Work Status',hue='Stroke Outcome', data=df)
plt.title("Distribution of Work Status")
plt.show()

sns.countplot(x='Residence',hue='Stroke Outcome', data=df)
plt.title("Distribution of Residence")
plt.show()

sns.countplot(x='Smoking Status',hue='Stroke Outcome', data=df)
plt.title("Distribution of Smoking Status")
plt.show()

sns.countplot(x='Stroke Outcome', data=df)
plt.title("Stroke Occurrence Distribution")
plt.show()

print(df['Stroke Outcome'].value_counts())
