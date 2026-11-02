import os

import pandas as pd
import plotly.express as px
import streamlit as st

from labeler import label_comment

# ---- Settings ----------------------------------------------------------
TITLE = "Dress Rental Services"
LOW_RATING, HIGH_RATING = 2, 4       # 2 stars or fewer is low, 4 stars or more is high
CSV_FILE = "feedback.csv"
COLORS = {
    "fit & sizing": "#E07A5F",
    "garment condition": "#F2CC8F",
    "delivery & logistics": "#3D405B",
    "style & inventory": "#81B29A",
    "pricing": "#B5838D",
    "unclear": "#D0D0D0",
}
# ------------------------------------------------------------------------

st.set_page_config(page_title=TITLE, layout="wide")
st.title(TITLE)
st.caption("Customers leave rental feedback. The app labels it and saves it to help the owner analyze areas for improvement later.")

# ensure comment_id exists and columns follow the requested order
def process_dataframe(df_in):
    if df_in.empty:
        return pd.DataFrame(columns=["comment_id", "label", "rating", "comment", "dress_name", "color", "size"])
    
    # Assign sequential comment IDs if not present or during load
    df_in = df_in.copy()
    if "comment_id" not in df_in.columns or df_in["comment_id"].isnull().any():
        df_in["comment_id"] = [f"C-{i+1:03d}" for i in range(len(df_in))]
        
    # columns: ID, label, rating, comment, dress_name, color, size
    ordered_cols = ["comment_id", "label", "rating", "comment", "dress_name", "color", "size"]
    # Include any extra columns if they exist
    extra_cols = [c for c in df_in.columns if c not in ordered_cols]
    return df_in[ordered_cols + extra_cols]

# Load saved feedback or initialize empty DataFrame
if os.path.exists(CSV_FILE):
    raw_df = pd.read_csv(CSV_FILE)
    df = process_dataframe(raw_df)
else:
    df = process_dataframe(pd.DataFrame())

tab_customer, tab_owner = st.tabs(["Customer: Leave Feedback", "Owner: Feedback Analytics"])

# ---- Customer tab: type feedback, pick stars, get a label, save --------------
with tab_customer:
    st.subheader("Tell us about your rental experience")
    with st.form("feedback_form", clear_on_submit=True):
        col_a, col_b, col_c = st.columns(3)
        with col_a:
            dress_name = st.text_input("Dress / Product Name (optional)")
        with col_b:
            color = st.text_input("Color (optional)")
        with col_c:
            size = st.text_input("US Size (optional)")

        comment = st.text_area("Your comment (required)")
        stars = st.feedback("stars")           # nothing until clicked, then 0 to 4
        submitted = st.form_submit_button("Send feedback")

    if submitted:
        # Require a written comment and a star rating
        if not comment.strip() or stars is None:
            st.error("Please provide both a written comment and a star rating.")
        else:
            dress_val = dress_name.strip() if dress_name.strip() else "Not Specified"
            color_val = color.strip() if color.strip() else "Not Specified"
            size_val = size.strip() if size.strip() else "Not Specified"
            
            comment_text = comment.strip()
            rating_val = stars + 1
            
            label = label_comment(comment_text)
            
            # Generate next comment_id
            next_id = f"C-{len(df) + 1:03d}"
            
            new_row = pd.DataFrame([{
                "comment_id": next_id,
                "label": label,
                "rating": rating_val,
                "comment": comment_text,
                "dress_name": dress_val,
                "color": color_val,
                "size": size_val,
            }])
            
            updated_df = pd.concat([df, new_row], ignore_index=True)
            updated_df = process_dataframe(updated_df)
            updated_df.to_csv(CSV_FILE, index=False)
            df = updated_df
            
            st.success("Thank you for your feedback!")
            st.caption(f"Behind the scenes, the app assigned ID **{next_id}** and labeled it: **{label}**")

# ---- Owner tab: analyze the feedback ----------------------------------------
with tab_owner:
    if df.empty:
        st.info("No feedback yet. Switch to the customer tab and add the first comment.")
    else:
        positive_labels = ["fit & sizing", "garment condition", "delivery & logistics", "style & inventory", "pricing"]
        valid_ratings = df["rating"].dropna()
        
        # Flag logic for review
        flag = (df["rating"] <= LOW_RATING) \
             | ((df["label"].isin(positive_labels)) & (df["rating"] <= LOW_RATING)) \
             | (df["label"] == "unclear")

        st.subheader("Customer Experience at A Glance")
        m1, m2, m3, m4 = st.columns(4)
       
        m1.metric("Total Number Comments", len(df))
        m2.metric("Needs Review", int(flag.sum()))

        avg_stars = f"{valid_ratings.mean():.1f}" if not valid_ratings.empty else "N/A"
        m3.metric("Total Ratings Average", avg_stars)
        
        low_friction_df = df[(df["rating"] <= LOW_RATING) & (df["label"] != "unclear")]
        top_friction = low_friction_df["label"].mode()[0].title() if not low_friction_df.empty else "N/A"
        m4.metric("Top Improvement Area", top_friction)
        
        st.markdown("---")

        # Graph 1-2: Number of comments by label & Overall rating proportion donut chart
        col1, col2 = st.columns(2)

        with col1:
            st.caption("Number of comments by category")
            counts = df["label"].value_counts().rename_axis("label").reset_index(name="count")
            fig1 = px.bar(counts, x="label", y="count", color="label", text="count",
                          color_discrete_map=COLORS)
            fig1.update_layout(showlegend=False, xaxis_title=None, yaxis_title="Comments")
            st.plotly_chart(fig1, width="stretch")

        with col2:
            st.caption("Overall ratings")
            if not valid_ratings.empty:
                rating_counts = valid_ratings.value_counts().reset_index()
                rating_counts.columns = ["rating", "count"]
                rating_counts = rating_counts.sort_values("rating")
                
                fig2 = px.pie(rating_counts, names="rating", values="count", hole=0.4,
                              color_discrete_sequence=px.colors.qualitative.Pastel)
                fig2.update_layout(legend_title_text="Stars")
                st.plotly_chart(fig2, width="stretch")
            else:
                st.info("No ratings available for chart.")

        st.markdown("---")

        # Graph 3: Dropdown for Category view 
        st.subheader("Ratings By Category")
        categories = ["All"] + list(COLORS.keys())
        selected_category = st.selectbox("Select category:", categories)

        if selected_category == "All":
            st.caption("Average Ratings by Category")
            avg = df.groupby("label")["rating"].mean().round(1).reset_index()
            fig_avg = px.bar(avg, x="label", y="rating", color="label", text="rating",
                             color_discrete_map=COLORS, range_y=[0, 5])
            fig_avg.update_layout(showlegend=False, xaxis_title=None, yaxis_title="Average stars")
            st.plotly_chart(fig_avg, width="stretch")
        else:
            cat_df = df[df["label"] == selected_category]
            if not cat_df.empty:
                all_stars = pd.DataFrame({"rating": [1, 2, 3, 4, 5]})
                cat_ratings = cat_df["rating"].value_counts().reset_index()
                cat_ratings.columns = ["rating", "count"]
                
                cat_ratings = pd.merge(all_stars, cat_ratings, on="rating", how="left").fillna(0)
                cat_ratings = cat_ratings.sort_values("rating")
                
                fig_cat = px.bar(cat_ratings, x="rating", y="count", text="count",
                                 color_discrete_sequence=[COLORS.get(selected_category, "#3D405B")])
                fig_cat.update_layout(xaxis_title="Star Rating", yaxis_title="Count of Reviews", showlegend=False, xaxis=dict(tickmode='linear', dtick=1))
                st.plotly_chart(fig_cat, width="stretch")
            else:
                st.info(f"No reviews recorded yet for '{selected_category}'.")

        st.markdown("---")

        # Manual Review: 
        st.subheader("Requires Further Review")
        st.caption("This section highlights comments requiring attention: reviews with 2 or fewer stars, positive operational categories that received unusually low ratings or vice versa, or unclear comments AI could not confidently label and require human review.")
        st.dataframe(df[flag], hide_index=True, width="stretch")

        with st.expander("All feedback"):
            st.dataframe(df, hide_index=True, width="stretch")
        st.download_button("Download CSV", df.to_csv(index=False), file_name="feedback.csv")
        st.caption("On the free Streamlit Cloud, the saved file can disappear when the app restarts. "
                   "Download your CSV to keep it.")
