import streamlit as st
import pandas as pd

# ---------- TAX SETTINGS ----------
SERVICE_CHARGE_RATE = 0.06  # Lo Comienzo only has 6% service charge
SST_RATE = 0  # No SST

# ---------- MENU WITH PRICES ----------
menu = {
    "Beef Birria Tacos": {"price": 27.9, "image": ""},
    "Beef Birria Quesadilla": {"price": 33.9, "image": ""},
    "Lamb Birria Tacos": {"price": 31.9, "image": ""},
    "Lamb Birria Quesadilla": {"price": 38.9, "image": ""},
    "Chicken Birria Tacos": {"price": 24.9, "image": ""},
    "Chicken Birria Quesadilla": {"price": 30.9, "image": ""},
    "Mixed Tacos Beef & Chicken": {"price": 26.4, "image": ""},
    "Mixed Tacos Lamb & Beef": {"price": 29.9, "image": ""},
    "Mixed Tacos Chicken & Lamb": {"price": 29.9, "image": ""},
    "Pasta Lamb Ragu": {"price": 24.9, "image": ""},
    "Pasta Carbonara": {"price": 26.9, "image": ""},
    "Pasta Vongole": {"price": 27.9, "image": ""},
    "Iced Americano": {"price": 9, "image": ""},
    "Iced Yuzu Americano": {"price": 12, "image": ""},
    "Iced Latte": {"price": 11, "image": ""},
    "Flavoured Latte": {"price": 14, "image": ""},
    "Mocha": {"price": 13, "image": ""},
    "Chocolate": {"price": 11, "image": ""},
    "Flavoured Chocolate": {"price": 14, "image": ""},
    "Soda Cucumber": {"price": 11, "image": ""},
    "Soda Mojito": {"price": 11, "image": ""},
    "Soda Passionfruit Mojito": {"price": 11, "image": ""},
    "Soda Hibiscus Lime": {"price": 11, "image": ""},
}

st.title("🍴 Lo Comienzo Order App")

# ---------- SESSION INIT ----------
if "step" not in st.session_state:
    st.session_state.step = 0
if "persons" not in st.session_state:
    st.session_state.persons = []
if "current_person" not in st.session_state:
    st.session_state.current_person = 0

# ---------- STEP 1 ----------
if st.session_state.step == 0:
    num = st.number_input("How many Persons?", min_value=1, step=1)
    if st.button("Next"):
        st.session_state.persons = [{"name": "", "orders": []} for _ in range(num)]
        st.session_state.step = 1
        st.rerun()

# ---------- STEP 2 ----------
elif st.session_state.step == 1:
    st.header("Enter Names")
    for i in range(len(st.session_state.persons)):
        st.session_state.persons[i]["name"] = st.text_input(
            f"Name for Person {i+1}", key=f"name_input_{i}"
        )
    if st.button("Start Ordering"):
        if all(p["name"].strip() for p in st.session_state.persons):
            st.session_state.step = 2
            st.rerun()
        else:
            st.warning("Please enter all names.")

# ---------- STEP 3 (ORDERING) ----------
elif st.session_state.step == 2:
    person = st.session_state.persons[st.session_state.current_person]
    st.header(f"Ordering for {person['name']}")

    cols = st.columns(2)

    for idx, (item_name, item_data) in enumerate(menu.items()):
        with cols[idx % 2]:
            selected = any(o["name"] == item_name for o in person["orders"])

            if selected:
                st.markdown(
                    f'<div style="opacity:0.4; border-radius:10px; padding:5px;">{item_name}</div>',
                    unsafe_allow_html=True
                )
            else:
                st.markdown(f"{item_name} — RM {item_data['price']:.2f}")

            # Invisible button as "click to select"
            if st.button(" ", key=f"{person['name']}_{item_name}", use_container_width=True):
                if selected:
                    person["orders"] = [o for o in person["orders"] if o["name"] != item_name]
                else:
                    price = item_data["price"]
                    service_charge = price * SERVICE_CHARGE_RATE
                    sst = 0
                    final_price = price + service_charge
                    person["orders"].append({
                        "name": item_name,
                        "price_before_tax": price,
                        "service_charge": service_charge,
                        "sst": sst,
                        "final_price": final_price
                    })
                st.rerun()

    # ---------- SELECTED ITEMS ----------
    st.markdown("---")
    st.subheader("Selected Items")
    total = sum(i['final_price'] for i in person["orders"])
    if person["orders"]:
        df = pd.DataFrame(person["orders"])
        df_display = df[["name", "price_before_tax", "service_charge", "final_price"]]
        df_display.columns = ["Item", "Price Before Tax", "Service Charge (6%)", "Price After Service Charge"]
        st.table(df_display.style.format({
            "Price Before Tax": "{:.2f}",
            "Service Charge (6%)": "{:.2f}",
            "Price After Service Charge": "{:.2f}"
        }))
    st.write(f"**Current Total: RM {total:.2f}**")
    st.markdown("---")

    col1, col2 = st.columns(2)
    with col1:
        if st.button("Next Person"):
            if st.session_state.current_person < len(st.session_state.persons) - 1:
                st.session_state.current_person += 1
                st.rerun()
            else:
                st.session_state.step = 3
                st.rerun()
    with col2:
        if st.button("View Receipt"):
            st.session_state.step = 3
            st.rerun()

# ---------- STEP 4 (RECEIPTS WITH TABLE) ----------
elif st.session_state.step == 3:
    st.header("🧾 Receipts (Detailed Breakdown)")
    overall_rows = []

    for person in st.session_state.persons:
        st.subheader(person["name"])
        if not person["orders"]:
            st.write("No items selected.")
            st.markdown("---")
            continue

        df = pd.DataFrame(person["orders"])
        df_display = df[["name", "price_before_tax", "service_charge", "final_price"]]
        df_display.columns = ["Item", "Price Before Tax", "Service Charge (6%)", "Price After Service Charge"]

        st.table(df_display.style.format({
            "Price Before Tax": "{:.2f}",
            "Service Charge (6%)": "{:.2f}",
            "Price After Service Charge": "{:.2f}"
        }))

        subtotal = df["final_price"].sum()
        st.write(f"**Subtotal for {person['name']}: RM {subtotal:.2f}**")
        st.markdown("---")

        overall_rows.append(df_display)

    # ---------- OVERALL TOTAL ----------
    if overall_rows:
        overall_df = pd.concat(overall_rows).sum(numeric_only=True)
        st.header("💰 Overall Total Breakdown")
        st.table(pd.DataFrame({
            "Price Before Tax": [overall_df["Price Before Tax"]],
            "Service Charge (6%)": [overall_df["Service Charge (6%)"]],
            "Price After Service Charge": [overall_df["Price After Service Charge"]]
        }).style.format({
            "Price Before Tax": "{:.2f}",
            "Service Charge (6%)": "{:.2f}",
            "Price After Service Charge": "{:.2f}"
        }))

    if st.button("Start Over"):
        st.session_state.clear()
        st.rerun()