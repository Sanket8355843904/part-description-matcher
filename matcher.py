from rapidfuzz import fuzz
import pandas as pd

from utils import (
    clean_description,
    sorted_tokens,
    common_words,
    engineering_score,
    number_score
)


# -------------------------------------------------------
# Hybrid Score
# -------------------------------------------------------

def calculate_score(text1, text2):

    text1 = clean_description(text1)
    text2 = clean_description(text2)

    token_sort = fuzz.token_sort_ratio(text1, text2)

    token_set = fuzz.token_set_ratio(text1, text2)

    eng_score = engineering_score(text1, text2)

    num_score = number_score(text1, text2)

    final_score = (
        token_sort * 0.45 +
        token_set * 0.25 +
        eng_score * 0.20 +
        num_score * 0.10
    )

    return round(final_score, 2)


# -------------------------------------------------------
# Compare One Description
# -------------------------------------------------------

def find_best_matches(main_description,
                      comparison_descriptions,
                      top_n=5):

    results = []

    for comp in comparison_descriptions:

        score = calculate_score(main_description, comp)

        common = ", ".join(common_words(main_description, comp))

        results.append({
            "Match Description": comp,
            "Match %": score,
            "Common Words": common
        })

    results = sorted(
        results,
        key=lambda x: x["Match %"],
        reverse=True
    )

    return results[:top_n]


# -------------------------------------------------------
# Compare Entire DataFrame
# -------------------------------------------------------

def compare_dataframes(
        main_df,
        comparison_df,
        main_column,
        comparison_column,
        top_n=5):

    output = []

    comparison_list = comparison_df[comparison_column] \
        .fillna("") \
        .astype(str) \
        .tolist()

    total = len(main_df)

    for i, row in main_df.iterrows():

        desc = str(row[main_column])

        matches = find_best_matches(
            desc,
            comparison_list,
            top_n
        )

        record = row.to_dict()

        if len(matches) > 0:

            best = matches[0]

            record["Best Match"] = best["Match Description"]
            record["Match %"] = best["Match %"]
            record["Matched Words"] = best["Common Words"]

        else:

            record["Best Match"] = ""
            record["Match %"] = 0
            record["Matched Words"] = ""

        # Store Top 5

        for j in range(top_n):

            if j < len(matches):

                record[f"Top {j+1}"] = matches[j]["Match Description"]
                record[f"Top {j+1} %"] = matches[j]["Match %"]

            else:

                record[f"Top {j+1}"] = ""
                record[f"Top {j+1} %"] = ""

        output.append(record)

    return pd.DataFrame(output)
