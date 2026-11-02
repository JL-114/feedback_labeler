# Dress Rental Services — Customer Feedback & Owner Analytics

An interactive, instructor-aligned Streamlit application built for dress rental business owners. The app captures customer feedback, automatically categorizes sentiment and operational topics using the Groq API, and provides powerful owner analytics to surface key areas for improvement.

---

## Key Features

### 1. Customer Feedback Portal
* **Optional Rental Metadata:** Customers can optionally specify the dress/product name, color, and US size.
* **Required Experience Input:** Enforces strict validation requiring **both** a written comment and a star rating before submission.
* **Automated AI Labeling:** Leverages the Groq API (`openai/gpt-oss-20b`) behind the scenes to categorize feedback into operational categories.

### 2. Owner Analytics Dashboard
* **High-Level Metrics:** Total comments, top area for improvement, average star rating, and a triage count for reviews needing careful review.
* **Side-by-Side Visualizations:** 
  * **Number of Comments by Label** (Interactive Plotly Bar Chart).
  * **Overall Rating Proportion** (Interactive Plotly Donut Chart).
* **Dynamic Category Deep Dive:** 
  * Defaults to **"All"** to show average star ratings across all categories.
  * Allows the owner to select any specific category to view a dedicated breakdown of **star counts (1–5)**.
* **"Read These Carefully" Section:** Automatically flags critical reviews—including low ratings ($\\le 2$ stars), label-to-rating mismatches, and unclear labels—formatted with unique zero-padded comment IDs.
* **Data Management:** Full feedback data table expansion and CSV export functionality.

---

## Operational Categories & Labels

Customer comments (both positive and negative) are automatically classified into one of the following operational buckets:
* `fit & sizing` (Garment fit, size accuracy, alterations, length, stretch)
* `garment condition` (Cleanliness, stains, wear and tear, zippers, tears)
* `delivery & logistics` (Shipping speed, arrival timing, packaging, return labels)
* `style & inventory` (Dress availability, color match, designer selection)
* `pricing` (Rental rates, unexpected costs, deposits, value for money)
* `unclear` (Ambiguous, off-topic, or spam)

---

## Tech Stack

* **Frontend & Dashboard:** [Streamlit](https://streamlit.io/)
* **Data Manipulation:** [Pandas](https://pandas.pydata.org/)
* **Visualizations:** [Plotly Express](https://plotly.com/python/plotly-express/)
* **AI Labeling Engine:** Groq API via `requests` (`openai/gpt-oss-20b`)
* **Storage:** Local CSV (`feedback.csv`) with structured metadata

---
