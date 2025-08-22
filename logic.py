# inventory
'''
start
function check_stock(opening_stock,purchase,sold,recorder_level):
calculation of final stock
final-stock=opening_stock+purchase
    Set
       final_stock = opening_stock + purchased - sold

    Print "Final Stock:", final_stock

    if final_stock is less than or equal to reorder_level then
        Print "Low Stock Alert!"
    else
        Print "Stock is Sufficient."
    function call
    check_stock(enter inputs from users :- opening,purchased,sold,record level)
'''
# def check_stock(opening_stock, purchased, sold, reorder_level,today_qty,pre_qty,qty,defective_qty):
#     final_stock = opening_stock + purchased - sold
#     print("Final Stock:", final_stock)
#     if final_stock <= reorder_level:
#         print("Low Stock Alert!")
#     else: 
#         print("Stock is Sufficient.")

#     qty_arrived =today_qty-defective_qty
#     print("quantity arrived is :",qty_arrived)

#     final_qty = qty_arrived+pre_qty
#     print("thye final quantity is :",final_qty)

#     print(opening_stock)
#     print( purchased)
#     print(sold)
#     print(reorder_level)
#     print(final_stock)
#     print(qty)
#     print(defective_qty)
#     print(qty_arrived)
#     print(pre_qty)
#     print(final_qty)

    
# opening_stock=int(input("enter the openoing stock :"))
# purchased=int(input("total purchase is :"))
# sold=int(input("the sold stock is:"))
# reorder_level=int(input("the recoder level is"))
# today_qty=int(input("enter the today quantity:"))
# pre_qty=int(input("enter the previous qty:"))
# qty=int(input("enter the net qty "))
# defective_qty=int(input("enter the defective qty:"))
    
   

# check_stock(
#     opening_stock=opening_stock,
#     purchased=purchased,
#     sold=sold,
#     reorder_level=reorder_level,
#     today_qty=today_qty,
#     pre_qty=pre_qty,
#     qty=qty,
#     defective_qty=defective_qty
# )

def calculate_inventory(opening_stock, purchased, sold, reorder_level, today_qty, pre_qty, defective_qty):
    # Calculate stock after purchase and sale
    final_stock = opening_stock + purchased - sold

    # Low stock warning
    low_stock = final_stock <= reorder_level

    # Quantity that arrived today 
    qty_arrived = today_qty - defective_qty

    final_qty = qty_arrived + pre_qty

    return {
        "opening_stock": opening_stock,
        "purchased": purchased,
        "sold": sold,
        "reorder_level": reorder_level,
        "final_stock": final_stock,
        "low_stock": low_stock,
        "today_qty": today_qty,
        "defective_qty": defective_qty,
        "qty_arrived": qty_arrived,
        "pre_qty": pre_qty,
        "final_qty": final_qty
    }




#sales
'''
start
function calculate_final_price =>price, qty, discount_percent, gst_percent=18:
calculations 
for gross total
 gross_total = price * qty
for Discount Amount
discount_amount = discount_percent % gross_total
for Subtotal after Discount
subtotal = gross_total - discount_amount
for gst ammount
gst_amount = gst_percent % subtotal
for final price
final_price = subtotal + gst_amount
display all the details
enter the input form the user
price , quantity, discount_percent
function call
end
'''
# def calculate_final_price(price, qty, discount_percent, gst_percent=18):
     # Gross Total
    # gross_total = price * qty

    #  Discount Amount
    # discount_amount = (discount_percent / 100) * gross_total

    #  Subtotal after Discount
    # subtotal = gross_total - discount_amount

    #  GST Amount
    # gst_amount = (gst_percent / 100) * subtotal

    #  Final Price
    # final_price = subtotal + gst_amount

    # Display 
    # print("\n Price Calculation:")
    # print(" Unit Price: ₹", price)
    # print(" Quantity:", qty)
    # print(" Gross Total: ", gross_total)
    # print(f"Discount ({discount_percent}%): {discount_amount}")
    # print(" Subtotal: ", subtotal)
    # print(f"GST ({gst_percent}%): {gst_amount}")
    # print(" Final Price: ", final_price)

# price = float(input("Enter Unit Price : "))
# qty = int(input("Enter Quantity: "))
# discount_percent = float(input("Enter Discount Percentage (%): "))

# calculate_final_price(price, qty, discount_percent)



#product or service
'''
start
fuction show_product_details=name, p_type, hsn, price, tax_percent:
calculate tac ammount
tax_amount = tax_percent %  price
final price including tax
final_price = price + tax_amount
display all the detail including calculations
enter the  all values from user input
funtion call
end 
'''
# def show_product_details(name, p_type, hsn, price, tax_percent):
    #  Calculate tax amount
    # tax_amount = (tax_percent / 100) * price

    #  Final price = price + tax
    # final_price = price + tax_amount

    #  Display all details
    # print(" Product Name:", name)
    # print(" Type:", p_type)
    # print(" HSN Code:", hsn)
    # print(" Base Price: ", price)
    # print(" Tax (%):", tax_percent)
    # print(" Tax Amount: ", tax_amount)
    # print(" Final Price (with tax): ", final_price)

# product_name = input("Enter Product Name: ")
# product_type = input("Enter Type (Product or Service): ")
# hsn_code = input("Enter HSN Code: ")
# price = float(input("Enter Base Price : "))
# tax_percent = 18

# show_product_details(product_name, product_type, hsn_code, price, tax_percent)

