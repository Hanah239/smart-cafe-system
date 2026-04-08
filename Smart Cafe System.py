import mysql.connector
import tkinter as tk

db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="pOi0(876",
    database="smart_cafe"
)

cursor = db.cursor()
cursor.execute("DELETE FROM cart")
db.commit()
cursor.close()

window = tk.Tk()
window.title("Cafe")
window.geometry("400x500")


def calculate_bill():
    cursor = db.cursor()
    cursor.execute("SELECT price, quantity FROM cart")
    items = cursor.fetchall()

    subtotal = 0
    for item in items:
        subtotal += item[0] * item[1]

    vat = subtotal * 0.15
    grand_total = subtotal + vat
    cursor.close()
    return subtotal, vat, grand_total


def show_bill():
    subtotal, vat, grand_total = calculate_bill()
    bill_text = f"Subtotal: Rs.{subtotal}\nVAT: Rs.{vat}\nTotal: Rs.{grand_total}"
    bill_label.config(text=bill_text)


def update_display():
    cursor = db.cursor()
    cursor.execute("SELECT item_name, price, quantity FROM cart")
    items = cursor.fetchall()

    cart_text = "Cart:\n"
    for item in items:
        cart_text += f"- {item[0]} Rs.{item[1]}\n"
    cart_label.config(text=cart_text)

    subtotal, vat, grand_total = calculate_bill()
    total_label.config(text=f"Running Total: Rs.{grand_total}")
    cursor.close()


def customize_drink(name, base_price):
    popup = tk.Toplevel(window)
    popup.title(f"Customize {name}")
    popup.geometry("250x150")

    tk.Label(popup, text=f"Customize {name}").pack(pady=10)

    size_var = tk.StringVar(value="Regular")
    tk.Label(popup, text="Size:").pack()
    tk.OptionMenu(popup, size_var, "Regular", "Large").pack()

    def add_customized():
        final_price = base_price
        if size_var.get() == "Large":
            final_price += 50

        custom_name = f"{name} ({size_var.get()})"

        cursor = db.cursor()
        cursor.execute("SELECT stock_quantity FROM inventory WHERE item_name=%s", (name,))
        stock = cursor.fetchone()

        if stock and stock[0] > 0:

            cursor.execute("INSERT INTO cart (item_name, price, quantity) VALUES (%s, %s, %s)",
                           (custom_name, final_price, 1))
            cursor.execute("UPDATE inventory SET stock_quantity=stock_quantity-1 WHERE item_name=%s", (name,))
            db.commit()
            update_display()  # Refresh from database
        else:
            cart_label.config(text=f"{name} out of stock!")

        cursor.close()
        popup.destroy()

    tk.Button(popup, text="Add to Cart", command=add_customized).pack(pady=10)


def add_item(name, price):
    cursor = db.cursor()
    cursor.execute("SELECT stock_quantity FROM inventory WHERE item_name=%s", (name,))
    stock = cursor.fetchone()

    if stock and stock[0] > 0:

        cursor.execute("INSERT INTO cart (item_name, price, quantity) VALUES (%s, %s, %s)",
                       (name, price, 1))
        cursor.execute("UPDATE inventory SET stock_quantity=stock_quantity-1 WHERE item_name=%s", (name,))
        db.commit()
        update_display()  # Refresh from database
    else:
        cart_label.config(text=f"{name} out of stock!")

    cursor.close()


def add_espresso():
    customize_drink("Espresso", 300)


def add_latte():
    customize_drink("Latte", 500)


def add_sandwich():
    add_item("Sandwich", 300)


def add_cake():
    add_item("Cake", 350)


tk.Button(window, text="Espresso - Rs.300", command=add_espresso).pack(pady=5)
tk.Button(window, text="Latte - Rs.500", command=add_latte).pack(pady=5)
tk.Button(window, text="Sandwich - Rs.300", command=add_sandwich).pack(pady=5)
tk.Button(window, text="Cake - Rs.350", command=add_cake).pack(pady=5)

cart_label = tk.Label(window, text="Cart: Empty")
cart_label.pack(pady=10)

total_label = tk.Label(window, text="Running Total: Rs.0")
total_label.pack(pady=5)

tk.Button(window, text="Calculate Final Bill", command=show_bill).pack(pady=5)
bill_label = tk.Label(window, text="")
bill_label.pack(pady=5)


def checkout():
    show_bill()
    print("Checkout Complete")

    cursor = db.cursor()
    cursor.execute("DELETE FROM cart")  # Clear cart after checkout
    db.commit()
    cursor.close()

    update_display()


tk.Button(window, text="Checkout", command=checkout).pack(pady=10)

update_display()

window.mainloop()

