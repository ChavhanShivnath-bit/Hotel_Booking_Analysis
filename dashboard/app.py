
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

st.set_page_config(
    page_title="Hotel Booking Analysis Dashboard",
    page_icon="🏨",
    layout="wide"
)

st.title("🏨 Hotel Booking Analysis Dashboard")
st.write("Analyze hotel reservations, cancellations, and booking trends.")

# Load dataset
@st.cache_data
def load_data():
    return pd.read_csv("data/raw/hotel_bookings.csv")

df = load_data()

# Basic data cleaning
df["is_canceled"] = pd.to_numeric(
    df["is_canceled"], errors="coerce"
)
df["adr"] = pd.to_numeric(df["adr"], errors="coerce")
df["lead_time"] = pd.to_numeric(df["lead_time"], errors="coerce")
df = df.dropna(subset=["hotel", "is_canceled"])

# Sidebar filters
st.sidebar.header("Dashboard Filters")

hotels = st.sidebar.multiselect(
    "Select Hotel Type",
    options=sorted(df["hotel"].unique()),
    default=sorted(df["hotel"].unique())
)

filtered_df = df[df["hotel"].isin(hotels)]

if filtered_df.empty:
    st.warning("Please select at least one hotel type.")
    st.stop()

# Key performance indicators
total_bookings = len(filtered_df)
cancellations = int((filtered_df["is_canceled"] == 1).sum())
cancellation_rate = (
    cancellations / total_bookings * 100
    if total_bookings else 0
)
average_adr = filtered_df["adr"].mean()

col1, col2, col3, col4 = st.columns(4)

col1.metric("Total Bookings", f"{total_bookings:,}")
col2.metric("Cancelled Bookings", f"{cancellations:,}")
col3.metric("Cancellation Rate", f"{cancellation_rate:.1f}%")
col4.metric(
    "Average Daily Rate",
    f"{average_adr:.2f}" if pd.notna(average_adr) else "N/A"
)

st.divider()

# Booking analysis
left, right = st.columns(2)

with left:
    st.subheader("Bookings by Hotel Type")
    booking_counts = filtered_df["hotel"].value_counts()

    fig, ax = plt.subplots()
    booking_counts.plot(kind="bar", ax=ax)
    ax.set_xlabel("Hotel Type")
    ax.set_ylabel("Number of Bookings")
    ax.tick_params(axis="x", rotation=0)
    st.pyplot(fig)
    plt.close(fig)

with right:
    st.subheader("Cancellation Distribution")

    cancellation_counts = (
        filtered_df["is_canceled"]
        .map({0: "Not Cancelled", 1: "Cancelled"})
        .value_counts()
    )

    fig, ax = plt.subplots()
    cancellation_counts.plot(kind="pie", autopct="%1.1f%%", ax=ax)
    ax.set_ylabel("")
    st.pyplot(fig)
    plt.close(fig)

# Monthly booking analysis
st.subheader("Monthly Booking Trends")

monthly = (
    filtered_df.groupby("arrival_date_month")
    .size()
    .rename("Bookings")
    .reset_index()
)

month_order = [
    "January", "February", "March", "April", "May", "June",
    "July", "August", "September", "October", "November", "December"
]

monthly["arrival_date_month"] = pd.Categorical(
    monthly["arrival_date_month"],
    categories=month_order,
    ordered=True
)

monthly = monthly.sort_values("arrival_date_month")

fig, ax = plt.subplots()
ax.plot(
    monthly["arrival_date_month"].astype(str),
    monthly["Bookings"],
    marker="o"
)
ax.set_xlabel("Month")
ax.set_ylabel("Number of Bookings")
ax.tick_params(axis="x", rotation=45)
fig.tight_layout()
st.pyplot(fig)
plt.close(fig)

# Data table
st.subheader("Booking Data")
st.dataframe(filtered_df, use_container_width=True)

st.caption(
    "Demo dashboard using sample data. Metrics describe the loaded "
    "records, not real hotel industry performance."
)
