import streamlit as st
import pandas as pd
from io import BytesIO

from matcher import compare_dataframes

# ----------------------------------------------------
# Page Configuration
# ----------------------------------------------------

st.set_page_config(
    page_title="Part Description Matcher",
    page_icon="🔍",
    layout="wide"
)

st.title("🔍 Part Description Matcher")
st.write(
    "Compare two BOMs using intelligent fuzzy matching."
)

st.divider()

# ----------------------------------------------------
# Upload Files
# ----------------------------------------------------

col1, col2 = st.columns(2)

with col1:

    main_file = st.file_uploader(
        "Upload Main BOM",
        type=["xlsx", "xls"],
        key="main"
    )

with col2:

    comparison_file = st.file_uploader(
        "Upload Comparison BOM",
        type=["xlsx", "xls"],
        key="comparison"
    )

# ----------------------------------------------------
# Wait until both uploaded
# ----------------------------------------------------

if main_file and comparison_file:

    # Read workbook

    main_excel = pd.ExcelFile(main_file)
    comparison_excel = pd.ExcelFile(comparison_file)

    # Sheet Selection

    st.subheader("Sheet Selection")

    col1, col2 = st.columns(2)

    with col1:

        main_sheet = st.selectbox(
            "Main Sheet",
            main_excel.sheet_names
        )

    with col2:

        comparison_sheet = st.selectbox(
            "Comparison Sheet",
            comparison_excel.sheet_names
        )

    # Read selected sheets

    main_df = pd.read_excel(
        main_file,
        sheet_name=main_sheet
    )

    comparison_df = pd.read_excel(
        comparison_file,
        sheet_name=comparison_sheet
    )

    st.divider()

    # Column Selection

    st.subheader("Description Columns")

    col1, col2 = st.columns(2)

    with col1:

        main_column = st.selectbox(
            "Main Description Column",
            main_df.columns
        )

    with col2:

        comparison_column = st.selectbox(
            "Comparison Description Column",
            comparison_df.columns
        )

    st.divider()

    col1, col2 = st.columns(2)

    with col1:

        top_matches = st.slider(
            "Top Matches",
            1,
            10,
            5
        )

    with col2:

        minimum_score = st.slider(
            "Minimum Match %",
            0,
            100,
            75
        )

    st.divider()

    # Compare Button

    if st.button(
        "🚀 Start Matching",
        use_container_width=True
    ):

        with st.spinner("Comparing descriptions..."):

            result_df = compare_dataframes(
                main_df,
                comparison_df,
                main_column,
                comparison_column,
                top_matches
            )

        # Filter

        result_df = result_df[
            result_df["Match %"] >= minimum_score
        ]

        st.success(
            f"Finished! {len(result_df)} matches found."
        )

        st.dataframe(
            result_df,
            use_container_width=True
        )

        # Download

        output = BytesIO()

        with pd.ExcelWriter(
            output,
            engine="openpyxl"
        ) as writer:

            result_df.to_excel(
                writer,
                index=False
            )

        st.download_button(
            label="📥 Download Results",
            data=output.getvalue(),
            file_name="Matched_BOM.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

else:

    st.info("Upload both Excel files to begin.")
