import pandas as pd


def build_features_dict(field):
    if(isinstance(field, dict)):
        return field
    elif isinstance(field, list):
        if(isinstance(field[0], dict)):
            return field[0]
        elif(isinstance(field[0], str)):
            return {item: True for item in field}
        elif(len(field[0]) == 2):
            return {item[0]: item[1] for item in field}
        else:
            return {}
    else:
        return {}

def lower_case_features(field):
    return {key.lower(): value for key, value in field.items()}

def find_feature(row, key):
    return 1 if key in row['description'] or key in ''.join(row['features'].keys()) or key in ''.join(row['other_features'].keys()) else 0


def load_dataframe(path):
    df = pd.read_json(path, lines=True)

    # remove incomplete items
    df.dropna(subset=['price', 'surface'], how='any', inplace=True)
    df = df[(df['price'] > 0) & (df['surface'] > 0)]

    # fill empty values
    df['description'].fillna('', inplace=True)
    df['features'].fillna({}, inplace=True)
    df['other_features'].fillna({}, inplace=True)
    df['name'].fillna('', inplace=True)
    df['status'].fillna('usado', inplace=True)

    # format dictionaries
    df['features'] = df.apply(
        (lambda x: build_features_dict(x['features'])), axis=1)
    df['other_features'] = df.apply(
        (lambda x: build_features_dict(x['other_features'])), axis=1)

    # normalize strings
    df['description'] = df['description'].str.lower()
    df['name'] = df['name'].str.lower()
    df['status'] = df['status'].str.lower()
    df['city'] = df['city'].str.lower()
    df['property_type'] = df['property_type'].str.lower()
    df['features'] = df.apply(lambda x: lower_case_features(x['features']), axis=1)
    df['other_features'] = df.apply(lambda x: lower_case_features(x['other_features']), axis=1)

    # add extra features
    df['yard'] = df.apply(lambda x: find_feature(x, 'antejardin'), axis=1)
    df['backyard'] = df.apply(lambda x: find_feature(x, 'patio'), axis=1)
    df['remodeled'] = df.apply(lambda x: find_feature(x, 'remodelado'), axis=1)
    df['terrace'] = df.apply(lambda x: find_feature(x, 'terraza'), axis=1)
    df['residencial_building'] = df.apply(lambda x: find_feature(x, 'unidad'), axis=1)
    df['pool'] = df.apply(lambda x: find_feature(x, 'piscina'), axis=1)

    df = pd.get_dummies(df, columns=['status', 'city', 'property_type'])

if __name__ == "__main__":
    load_dataframe('../data/raw/result.jsonl')
