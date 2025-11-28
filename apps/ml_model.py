import pandas as pd
from sklearn.linear_model import LogisticRegression
from .models import leaddata

def train_lead_model():
    leads = leaddata.objects.all().values('status','score','size','revenue')
    df = pd.DataFrame(leads)

    if df.empty:
        return None

    # Convert status to numeric
    status_map = {'new':0, 'contacted':1, 'follow_up':2, 'closed':3}
    df['status_num'] = df['status'].map(status_map).fillna(0)

    # Target: closed = 1, else = 0
    df['converted'] = df['status'].apply(lambda x: 1 if x=='closed' else 0)

    X = df[['status_num', 'score', 'size', 'revenue']].fillna(0)
    y = df['converted']

    model = LogisticRegression()
    model.fit(X, y)

    return model


def predict_conversion(model, lead_instance):
    status_map = {'new':0, 'contacted':1, 'follow_up':2, 'closed':3}
    data = {
        'status_num': status_map.get(lead_instance.status, 0),
        'score': lead_instance.score or 0,
        'size': lead_instance.size or 0,
        'revenue': float(lead_instance.revenue or 0),
    }

    df = pd.DataFrame([data])
    prediction = model.predict_proba(df)[0][1]  # probability of conversion
    return round(prediction * 100, 2)
