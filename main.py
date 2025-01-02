import ttkbootstrap as ttk
from ttkbootstrap.constants import *
import tkinter.messagebox as messagebox
import sqlite3


# פונקציה לאתחל את בסיס הנתונים
def init_db():
    conn = sqlite3.connect("rates.db")
    cursor = conn.cursor()
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS rates (
            id INTEGER PRIMARY KEY,
            electricity_rate REAL,
            water_tier1_rate REAL,
            water_tier2_rate REAL,
            water_tier1_limit REAL
        )
        """
    )
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            electricity_consumption REAL,
            water_consumption REAL,
            electricity_cost REAL,
            water_cost REAL,
            total_cost REAL
        )
        """
    )
    # ערכים ברירת מחדל
    cursor.execute(
        """
        INSERT OR IGNORE INTO rates (id, electricity_rate, water_tier1_rate, water_tier2_rate, water_tier1_limit)
        VALUES (1, 0.6402, 7.5, 13.5, 3.5)
        """
    )
    conn.commit()
    conn.close()


# פונקציה לעדכן את התעריפים
# פונקציה לעדכון תעריפים
def update_rates(
    electricity_rate, water_tier1_rate, water_tier2_rate, water_tier1_limit, rate_labels
):
    conn = sqlite3.connect("rates.db")
    cursor = conn.cursor()
    cursor.execute(
        """
        UPDATE rates
        SET electricity_rate = ?, water_tier1_rate = ?, water_tier2_rate = ?, water_tier1_limit = ?
        WHERE id = 1
        """,
        (electricity_rate, water_tier1_rate, water_tier2_rate, water_tier1_limit),
    )
    conn.commit()
    conn.close()

    # עדכון התוויות עם התעריפים החדשים
    update_rate_labels(rate_labels)
    ttk.Messagebox.show_info(title="הצלחה", message="התעריפים עודכנו בהצלחה!")


# פונקציה להצגת התעריפים הנוכחיים
def update_rate_labels(rate_labels):
    conn = sqlite3.connect("rates.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM rates WHERE id = 1")
    rates = cursor.fetchone()
    conn.close()

    rate_labels["electricity"].config(
        text=f'תעריף חשמל נוכחי: {rates[1]:.2f} ש"ח/קוט"ש'
    )
    rate_labels["water_tier1"].config(
        text=f'תעריף מדרגה 1 למים: {rates[2]:.2f} ש"ח/מ"ק'
    )
    rate_labels["water_tier2"].config(
        text=f'תעריף מדרגה 2 למים: {rates[3]:.2f} ש"ח/מ"ק'
    )
    rate_labels["water_limit"].config(text=f'גבול מדרגה 1 למים: {rates[4]:.2f} מ"ק')


def calculate_costs(
    previous_electricity, current_electricity, previous_water, current_water, tree
):
    try:
        # Convert string inputs to float
        previous_electricity = float(previous_electricity)
        current_electricity = float(current_electricity)
        previous_water = float(previous_water)
        current_water = float(current_water)
    except ValueError:
        # Show error if conversion fails (e.g., if inputs are not numeric)
        messagebox.showerror(
            title="Error",
            message="Please ensure all fields are filled with numeric values.",
        )
        return

    # Fetch rates from the database
    conn = sqlite3.connect("rates.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM rates WHERE id = 1")
    rates = cursor.fetchone()
    conn.close()

    electricity_rate = rates[1]
    water_tier1_rate = rates[2]
    water_tier2_rate = rates[3]
    water_tier1_limit = rates[4]

    # Calculate consumption
    electricity_consumption = current_electricity - previous_electricity
    water_consumption = current_water - previous_water

    # Calculate electricity cost
    electricity_cost = electricity_consumption * electricity_rate

    # Calculate water cost
    if water_consumption <= water_tier1_limit:
        water_cost = water_consumption * water_tier1_rate
    else:
        tier1_cost = water_tier1_limit * water_tier1_rate
        tier2_cost = (water_consumption - water_tier1_limit) * water_tier2_rate
        water_cost = tier1_cost + tier2_cost

    total_cost = electricity_cost + water_cost

    # Save the calculation to history
    conn = sqlite3.connect("rates.db")
    cursor = conn.cursor()
    cursor.execute(
        """
        INSERT INTO history (electricity_consumption, water_consumption, electricity_cost, water_cost, total_cost)
        VALUES (?, ?, ?, ?, ?)
        """,
        (
            electricity_consumption,
            water_consumption,
            electricity_cost,
            water_cost,
            total_cost,
        ),
    )
    conn.commit()
    conn.close()

    # Update the history table in the UI
    show_history(tree)

    # Show a success message with the calculation results
    messagebox.showinfo(
        title="Results",
        message=f"Electricity Consumption: {electricity_consumption:.2f} kWh\n"
        f"Water Consumption: {water_consumption:.2f} m³\n"
        f"Electricity Cost: {electricity_cost:.2f} ILS\n"
        f"Water Cost: {water_cost:.2f} ILS\n"
        f"Total Cost: {total_cost:.2f} ILS",
    )


# פונקציה להצגת ההיסטוריה
def show_history(tree):
    for row in tree.get_children():
        tree.delete(row)

    conn = sqlite3.connect("rates.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM history")
    rows = cursor.fetchall()
    conn.close()

    for row in rows:
        tree.insert("", END, values=row[1:])


# פונקציה למשוך את הקריאה הקודמת מההיסטוריה
def get_last_readings():
    conn = sqlite3.connect("rates.db")
    cursor = conn.cursor()
    cursor.execute(
        "SELECT electricity_consumption, water_consumption FROM history ORDER BY id DESC LIMIT 1"
    )
    last_reading = cursor.fetchone()
    conn.close()

    if last_reading:
        return last_reading[0], last_reading[1]
    else:
        # ערכים ברירת מחדל במקרה שאין היסטוריה
        return 0.0, 0.0


# פונקציה לעדכון תוויות תעריפים
def update_rate_labels(rate_labels):
    conn = sqlite3.connect("rates.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM rates WHERE id = 1")
    rates = cursor.fetchone()
    conn.close()

    rate_labels["electricity"].config(
        text=f'תעריף חשמל נוכחי: {rates[1]:.2f} ש"ח/קוט"ש'
    )
    rate_labels["water_tier1"].config(
        text=f'תעריף מדרגה 1 למים: {rates[2]:.2f} ש"ח/מ"ק'
    )
    rate_labels["water_tier2"].config(
        text=f'תעריף מדרגה 2 למים: {rates[3]:.2f} ש"ח/מ"ק'
    )
    rate_labels["water_limit"].config(text=f'גבול מדרגה 1 למים: {rates[4]:.2f} מ"ק')


# פונקציה ראשית ליצירת ה-UI
def create_ui():
    app = ttk.Window(
        title="חישוב עלות חשמל ומים",
        themename="solar",
        size=(900, 800),
        resizable=(True, True),
    )

    # משיכת הקריאות האחרונות מהיסטוריה
    last_electricity, last_water = get_last_readings()

    # מסגרת קלטים
    input_frame = ttk.Frame(app, padding=20)
    input_frame.pack(fill=X, padx=10, pady=10)

    ttk.Label(input_frame, text='קריאה קודמת של חשמל (קוט"ש):', anchor=W).grid(
        row=0, column=0, padx=5, pady=5, sticky=W
    )
    previous_electricity_entry = ttk.Entry(input_frame)
    previous_electricity_entry.insert(
        0, str(last_electricity)
    )  # הכנסת הקריאה האחרונה לשדה
    previous_electricity_entry.grid(row=0, column=1, padx=5, pady=5)

    ttk.Label(input_frame, text='קריאה נוכחית של חשמל (קוט"ש):', anchor=W).grid(
        row=1, column=0, padx=5, pady=5, sticky=W
    )
    current_electricity_entry = ttk.Entry(input_frame)
    current_electricity_entry.grid(row=1, column=1, padx=5, pady=5)

    ttk.Label(input_frame, text='קריאה קודמת של מים (מ"ק):', anchor=W).grid(
        row=2, column=0, padx=5, pady=5, sticky=W
    )
    previous_water_entry = ttk.Entry(input_frame)
    previous_water_entry.insert(0, str(last_water))  # הכנסת הקריאה האחרונה לשדה
    previous_water_entry.grid(row=2, column=1, padx=5, pady=5)

    ttk.Label(input_frame, text='קריאה נוכחית של מים (מ"ק):', anchor=W).grid(
        row=3, column=0, padx=5, pady=5, sticky=W
    )
    current_water_entry = ttk.Entry(input_frame)
    current_water_entry.grid(row=3, column=1, padx=5, pady=5)

    # מסגרת להצגת תעריפים נוכחיים
    rate_frame = ttk.Frame(app, padding=20, borderwidth=2, relief="groove")
    rate_frame.pack(fill=X, padx=10, pady=10)

    ttk.Label(
        rate_frame, text="תעריפים נוכחיים:", anchor=W, font=("Helvetica", 14, "bold")
    ).pack(anchor=W, padx=5, pady=5)

    # יצירת תוויות לתעריפים
    rate_labels = {
        "electricity": ttk.Label(rate_frame),
        "water_tier1": ttk.Label(rate_frame),
        "water_tier2": ttk.Label(rate_frame),
        "water_limit": ttk.Label(rate_frame),
    }

    for label in rate_labels.values():
        label.pack(anchor=W, padx=5)

    # עדכון תוויות התעריפים עם הערכים הנוכחיים
    update_rate_labels(rate_labels)

    # מסגרת לעדכון תעריפים
    rate_update_frame = ttk.Frame(app, padding=20, borderwidth=2, relief="groove")
    rate_update_frame.pack(fill=X, padx=10, pady=10)

    ttk.Label(
        rate_update_frame,
        text="עדכון תעריפים:",
        anchor=W,
        font=("Helvetica", 14, "bold"),
    ).grid(row=0, column=0, columnspan=2, pady=10)

    ttk.Label(rate_update_frame, text='תעריף חדש לחשמל (ש"ח/קוט"ש):', anchor=W).grid(
        row=1, column=0, padx=5, pady=5
    )
    electricity_rate_entry = ttk.Entry(rate_update_frame)
    electricity_rate_entry.grid(row=1, column=1, padx=5, pady=5)

    ttk.Label(
        rate_update_frame, text='תעריף חדש למדרגה 1 למים (ש"ח/מ"ק):', anchor=W
    ).grid(row=2, column=0, padx=5, pady=5)
    water_tier1_entry = ttk.Entry(rate_update_frame)
    water_tier1_entry.grid(row=2, column=1, padx=5, pady=5)

    ttk.Label(
        rate_update_frame, text='תעריף חדש למדרגה 2 למים (ש"ח/מ"ק):', anchor=W
    ).grid(row=3, column=0, padx=5, pady=5)
    water_tier2_entry = ttk.Entry(rate_update_frame)
    water_tier2_entry.grid(row=3, column=1, padx=5, pady=5)

    ttk.Label(rate_update_frame, text='גבול חדש למדרגה 1 למים (מ"ק):', anchor=W).grid(
        row=4, column=0, padx=5, pady=5
    )
    water_limit_entry = ttk.Entry(rate_update_frame)
    water_limit_entry.grid(row=4, column=1, padx=5, pady=5)

    ttk.Button(
        rate_update_frame,
        text="עדכן תעריפים",
        bootstyle=WARNING,
        command=lambda: update_rates(
            float(electricity_rate_entry.get() or 0),
            float(water_tier1_entry.get() or 0),
            float(water_tier2_entry.get() or 0),
            float(water_limit_entry.get() or 0),
            rate_labels,
        ),
    ).grid(row=5, column=0, columnspan=2, pady=10)

    # כפתור חישוב
    ttk.Button(
        input_frame,
        text="חשב עלויות",
        bootstyle=SUCCESS,
        command=lambda: calculate_costs(
            previous_electricity_entry.get(),
            current_electricity_entry.get(),
            previous_water_entry.get(),
            current_water_entry.get(),
            tree,
        ),
    ).grid(row=4, column=0, columnspan=2, pady=10)

    # מסגרת להצגת היסטוריה
    history_frame = ttk.Frame(app, padding=20, borderwidth=2, relief="groove")
    history_frame.pack(fill=BOTH, expand=True, padx=10, pady=10)

    ttk.Label(
        history_frame, text="היסטוריית חישובים:", font=("Helvetica", 14, "bold")
    ).pack(anchor=W, padx=5, pady=5)

    tree = ttk.Treeview(
        history_frame,
        columns=(
            "electricity",
            "water",
            "electricity_cost",
            "water_cost",
            "total_cost",
        ),
        show="headings",
        bootstyle=INFO,
    )
    tree.heading("electricity", text='צריכת חשמל (קוט"ש)')
    tree.heading("water", text='צריכת מים (מ"ק)')
    tree.heading("electricity_cost", text='עלות חשמל (ש"ח)')
    tree.heading("water_cost", text='עלות מים (ש"ח)')
    tree.heading("total_cost", text='עלות כוללת (ש"ח)')
    tree.pack(fill=BOTH, expand=True)

    ttk.Button(
        history_frame,
        text="רענן היסטוריה",
        bootstyle=PRIMARY,
        command=lambda: show_history(tree),
    ).pack(pady=10)

    # הצגת היסטוריה ראשונית
    show_history(tree)

    app.mainloop()


if __name__ == "__main__":
    init_db()  # אתחול בסיס הנתונים
    create_ui()  # יצירת ממשק המשתמש
