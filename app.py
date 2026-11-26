
import streamlit as st
import pandas as pd
from datetime import datetime

st.set_page_config(
    page_title="AI Payments Incident Assistant",
    page_icon="💳",
    layout="wide"
)

st.title("💳 AI Payments Incident Assistant")
st.caption("Version 2 | Synthetic data | Analyst-reviewed investigation")


scenario = st.selectbox(
    "Select payment incident scenario",
    [
        "ATM withdrawal timeouts",
        "POS payment declines",
        "Issuer host unavailable",
    ],
)

st.info(
    f"Scenario selected: {scenario}. "
    "The dashboard uses synthetic data for this scenario."
)


# Fictional five-period dataset.
# Counts are illustrative, not real production data.


if scenario == "ATM withdrawal timeouts":
    data = pd.DataFrame({
        "Period": ["09:00", "09:05", "09:10", "09:15", "09:20", "09:25"],
        "ATM Transactions": [100, 105, 98, 102, 100, 101],
        "Timeouts": [2, 3, 2, 4, 28, 35],
        "Average Transaction Amount": [100, 100, 100, 100, 100, 100],
    })

elif scenario == "POS payment declines":
    data = pd.DataFrame({
        "Period": ["09:00", "09:05", "09:10", "09:15", "09:20", "09:25"],
        "POS Transactions": [100, 105, 98, 102, 100, 101],
        "Declines": [3, 2, 4, 3, 18, 25],
        "Average Transaction Amount": [75, 75, 75, 75, 75, 75],
    })

else:
    data = pd.DataFrame({
        "Period": ["09:00", "09:05", "09:10", "09:15", "09:20", "09:25"],
        "Issuer Transactions": [100, 105, 98, 102, 100, 101],
        "Failed Responses": [1, 2, 1, 2, 45, 70],
        "Average Transaction Amount": [120, 120, 120, 120, 120, 120],
    })


if scenario == "ATM withdrawal timeouts":
    count_column = "Timeouts"
    transaction_column = "ATM Transactions"
    rate_label = "Timeout Rate (%)"

elif scenario == "POS payment declines":
    count_column = "Declines"
    transaction_column = "POS Transactions"
    rate_label = "Decline Rate (%)"

else:
    count_column = "Failed Responses"
    transaction_column = "Issuer Transactions"
    rate_label = "Failure Rate (%)"

data[rate_label] = (
    data[count_column] / data[transaction_column] * 100
)

# Configurable incident detection threshold
st.sidebar.header("Detection settings")
threshold = st.sidebar.slider(
    f"{rate_label.replace(' (%)', '')} alert threshold (%)",
    min_value=1,
    max_value=50,
    value=5
)

st.subheader(f"1. {rate_label.replace(' (%)', '')} monitoring")


latest = data.iloc[-1]
baseline = data.iloc[:4]

baseline_rate = (
    baseline[count_column].sum()
    / baseline[transaction_column].sum()
    * 100
)

latest_rate = latest[rate_label]
latest_count = int(latest[count_column])
# Estimate the transaction value affected
average_transaction_amount = latest["Average Transaction Amount"]

estimated_value_affected = (
    latest_count * average_transaction_amount
)

# Incident priority classification
if latest_rate >= 50 and latest_count >= 50:
    priority = "P1 - Critical"

elif latest_rate >= 20 and latest_count >= 20:
    priority = "P2 - High"

elif latest_rate >= 5:
    priority = "P3 - Medium"

else:
    priority = "P4 - Low"

# Explain why the priority was assigned
if priority == "P1 - Critical":
    priority_reason = (
        "Failure rate is at least 50% and failed transactions "
        "are at least 50. Immediate investigation recommended."
    )

elif priority == "P2 - High":
    priority_reason = (
        "Failure rate is at least 20% and failed transactions "
        "are at least 20. Urgent investigation recommended."
    )

elif priority == "P3 - Medium":
    priority_reason = (
        "Failure rate is at least 5%. Investigation and monitoring recommended."
    )

else:
    priority_reason = (
        "Failure rate is below 5%. Continue routine monitoring."
    )


c1, c2, c3, c4, c5, c6 = st.columns(6)
c1.metric(f"Baseline {rate_label}", f"{baseline_rate:.2f}%")
c2.metric(f"Latest {rate_label}", f"{latest_rate:.2f}%")
c3.metric(f"Latest {count_column}", latest_count)
c4.metric(
    "Change vs. baseline",
    f"{latest_rate - baseline_rate:+.2f} percentage points"
)
c5.metric("Incident Priority", priority)
c6.metric(
    "Estimated Value Affected",
    f"${estimated_value_affected:,.0f}"
)
st.info(f"Priority rationale: {priority_reason}")

if latest_rate >= threshold:
    st.error(
        f"ALERT: Latest {rate_label.lower()} is "
        f"{latest_rate:.2f}%, above the configured "
        f"threshold of {threshold}%."
    )
else:
    st.success(
        f"Latest {rate_label.lower()} is below the "
        "configured threshold."
    )
st.subheader(f"2. {rate_label.replace(' (%)', '')} trend")

st.line_chart(
    data.set_index("Period")[[rate_label]]
)

st.subheader("3. Transaction volumes")

st.bar_chart(
    data.set_index("Period")[[transaction_column, count_column]]
)


st.dataframe(data, use_container_width=True, hide_index=True)

st.caption(
    "Detection uses a configurable threshold, not a trained AI model. "
    "The baseline is the first four periods; the latest period is assessed "
    "against that baseline. All data is synthetic."
)



st.subheader("Incident intelligence summary")

if latest_rate >= threshold:
    st.warning(
        f"An elevated {rate_label.lower()} was detected at "
        f"{latest['Period']}. The latest rate is {latest_rate:.2f}%, "
        f"compared with a baseline of {baseline_rate:.2f}%."
    )
else:
    st.success(
        f"The latest {rate_label.lower()} is {latest_rate:.2f}%, "
        f"within the configured threshold of {threshold}%."
    )

rate_change = latest_rate - baseline_rate

st.markdown("**What changed?**")
st.write(
    f"The {rate_label.lower()} changed by "
    f"{rate_change:+.2f} percentage points relative to the baseline. "
    f"The latest period contains {latest_count} "
    f"{count_column.lower()}."
)

st.markdown("**What do we know?**")
st.write(
    f"The synthetic transaction data shows activity in "
    f"{scenario.lower()}. The data does not confirm the root cause "
    "or establish actual financial losses."
)

st.markdown("**What should the analyst investigate?**")

if scenario == "ATM withdrawal timeouts":
    st.write(
        "1. Check ATM terminal connectivity.\n"
        "2. Review ATM switch response times.\n"
        "3. Investigate issuer-host timeouts.\n"
        "4. Check network latency and switch queues.\n"
        "5. Validate affected transaction outcomes."
    )

elif scenario == "POS payment declines":
    st.write(
        "1. Analyze authorization response codes.\n"
        "2. Compare issuer and acquirer response times.\n"
        "3. Check transaction routing and configuration.\n"
        "4. Identify patterns by merchant or terminal.\n"
        "5. Validate whether declined transactions were subsequently approved."
    )

else:
    st.write(
        "1. Check issuer-host availability and health.\n"
        "2. Review switch-to-issuer connectivity.\n"
        "3. Analyze failed response codes and timeouts.\n"
        "4. Check issuer processing queues.\n"
        "5. Confirm transaction outcomes before retrying payments."
    )


st.subheader("4. Incident details")

col1, col2 = st.columns(2)

with col1:
    incident_type = st.selectbox(
        "Incident type",
        [
            "ATM withdrawal timeouts",
            "POS payment declines",
            "Issuer unavailable",
            "Settlement discrepancy",
        ],
    )
    severity = st.selectbox(
        "Initial severity",
        ["P3 - Low", "P2 - Moderate", "P1 - High", "P0 - Critical"],
        index=1,
    )

with col2:
    affected_system = st.selectbox(
        "Affected system",
        ["ATM switch", "Payment switch", "Issuer host", "Settlement system"],
    )
    description = st.text_area(
        "Incident description",
        "Bank reports increased ATM withdrawal timeouts.",
    )

st.subheader("5. Investigation assistant")

if st.button("Analyze incident", type="primary"):

    st.markdown("### Observed evidence")

    st.write(
        f"- Baseline {rate_label.lower()}: {baseline_rate:.2f}%."
    )
    st.write(
        f"- Latest {rate_label.lower()}: {latest_rate:.2f}%."
    )
    st.write(
        f"- Latest period contains {latest_count} "
        f"{count_column.lower()} from "
        f"{int(latest[transaction_column])} "
        f"{transaction_column.lower()}."
    )

    st.markdown("### Possible causes to investigate")

    if scenario == "ATM withdrawal timeouts":
        st.write(
            "- ATM terminal connectivity issues.\n"
            "- ATM switch processing delays.\n"
            "- Issuer-host response timeouts.\n"
            "- Network latency or switch queue congestion."
        )

    elif scenario == "POS payment declines":
        st.write(
            "- Issuer authorization declines.\n"
            "- Acquirer-to-issuer connectivity problems.\n"
            "- Incorrect transaction routing or configuration.\n"
            "- Increased authorization response times."
        )

    else:
        st.write(
            "- Issuer host outage or service degradation.\n"
            "- Network connectivity failure between switch and issuer.\n"
            "- Issuer processing queue congestion.\n"
            "- Recent issuer-side deployment or configuration changes."
        )

    st.markdown("### Recommended diagnostic checks")

    if scenario == "ATM withdrawal timeouts":
        st.write(
            "1. Check ATM terminal connectivity and communication logs.\n"
            "2. Compare ATM switch response times with the normal baseline.\n"
            "3. Review timeout messages and transaction timestamps.\n"
            "4. Check network latency, switch queues, and issuer availability.\n"
            "5. Verify whether timed-out withdrawals were debited before retrying."
        )

    elif scenario == "POS payment declines":
        st.write(
            "1. Analyze authorization response codes and decline patterns.\n"
            "2. Compare acquirer and issuer response times.\n"
            "3. Check merchant, terminal, and transaction routing patterns.\n"
            "4. Review connectivity issues and recent configuration changes.\n"
            "5. Verify whether declined transactions were subsequently approved."
        )

    else:
        st.write(
            "1. Check issuer-host availability and service health.\n"
            "2. Review switch-to-issuer connectivity and response times.\n"
            "3. Analyze failed responses and transaction timestamps.\n"
            "4. Check issuer processing queues and recent deployments.\n"
            "5. Confirm transaction outcomes before retrying payments."
        )

    report = f"""
PAYMENTS INCIDENT REPORT
Generated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

Incident: {incident_type}
Initial severity: {severity}
Assigned priority: {priority}
Priority rationale: {priority_reason}
Affected system: {affected_system}
Description: {description}

DETECTION
Scenario: {scenario}
Baseline {rate_label}: {baseline_rate:.2f}%
Latest {rate_label}: {latest_rate:.2f}%
Latest {count_column}: {latest_count}
Configured alert threshold: {threshold}%
Alert status: {"ALERT - Threshold exceeded" if latest_rate >= threshold else "Within threshold"}
Change vs. baseline: {latest_rate - baseline_rate:+.2f} percentage points

POTENTIAL CAUSES
{chr(10).join(
    "- " + cause for cause in (
        [
            "ATM terminal connectivity issues",
            "ATM switch processing delays",
            "Issuer-host response timeouts",
            "Network latency or switch queue congestion"
        ] if scenario == "ATM withdrawal timeouts" else
        [
            "Issuer authorization declines",
            "Acquirer-to-issuer connectivity problems",
            "Incorrect transaction routing or configuration",
            "Increased authorization response times"
        ] if scenario == "POS payment declines" else
        [
            "Issuer-host outage or service degradation",
            "Network connectivity failure between switch and issuer",
            "Issuer processing queue congestion",
            "Recent issuer-side deployment or configuration changes"
        ]
    )
)}

NEXT STEPS
{chr(10).join(
    "- " + step for step in (
        [
            "Check ATM terminal connectivity and switch response times",
            "Review timeout messages and transaction logs",
            "Investigate network latency and issuer availability",
            "Verify withdrawal outcomes before retrying",
            "Escalate confirmed issues to the responsible teams"
        ] if scenario == "ATM withdrawal timeouts" else
        [
            "Analyze authorization response codes and decline patterns",
            "Compare acquirer and issuer response times",
            "Review merchant and terminal routing",
            "Verify transaction outcomes before retrying",
            "Escalate confirmed issues to the responsible teams"
        ] if scenario == "POS payment declines" else
        [
            "Check issuer-host availability and service health",
            "Review switch-to-issuer connectivity",
            "Analyze failed responses and processing queues",
            "Confirm transaction outcomes before retrying",
            "Escalate confirmed issues to the responsible teams"
        ]
    )
)}

Status: Root cause not confirmed.
Data: Synthetic demonstration data only.
"""

    st.download_button(
        "Download incident report",
        data=report,
        file_name="payment_incident_report.txt",
        mime="text/plain",
    )

st.divider()
st.caption(
    "Educational prototype only. Not connected to live payment systems."
)
