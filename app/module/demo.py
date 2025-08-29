from app import app,cursor,mydb
import os
import re
from flask import Flask,render_template,request,redirect,flash,url_for,session
import traceback




@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        firstname = request.form.get("firstname", "").strip()
        lastname = request.form.get("lastname", "").strip()
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "").strip()
        confirm = request.form.get("confirm", "").strip()
        email = request.form.get("email", "").strip()
        country_code = request.form.get("country_code", "").strip()
        mobile = request.form.get("phone", "").strip()
        dob = request.form.get("dob", "").strip()
        security_q = request.form.get("security", "").strip()
        answer = request.form.get("answer", "").strip()
        roles = request.form.get("roles", "").strip()

        #  Combine country code and phone
        full_mobile = country_code + mobile

        #  VALIDATIONS  #

        #  Required fields
        if not all([firstname, lastname, username, password, confirm, email, country_code, mobile, dob, security_q, answer, roles]):
            flash("All fields are required", "danger")
            return redirect(url_for('register'))

        #  Email validation (Gmail/Yahoo only)
        if not re.match(r'^[\w\.-]+@(gmail\.com|yahoo\.com)$', email):
            flash("Only Gmail and Yahoo email addresses are allowed", "danger")
            return redirect(url_for('register'))

        #  Password match
        if password != confirm:
            flash("Passwords do not match", "danger")
            return redirect(url_for('register'))

        #  Strong password check
        if not re.match(r'^(?=.*[A-Z])(?=.*[a-z])(?=.*\d)(?=.*[\W_]).{8,}$', password):
            flash("Password must be at least 8 characters, include uppercase, lowercase, number, and special character", "danger")
            return redirect(url_for('register'))

        #  Phone number check 
        if not re.match(r'^\d{5,15}$', mobile):
            flash("Phone number must be 5-15 digits only", "danger")
            return redirect(url_for('register'))

        #  Date of birth check
        if not re.match(r'^\d{4}-\d{2}-\d{2}$', dob):
            flash("Invalid date format. Use YYYY-MM-DD", "danger")
            return redirect(url_for('register'))

        #  database insert  #
        try:
            cursor.execute("""
                INSERT INTO register 
                (firstname, lastname, username, password, email, phone, dob, security_q, answer, roles)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (firstname, lastname, username, password, email, full_mobile, dob, security_q, answer, roles))
            mydb.commit()
            flash("Registration successful", "success")
            return redirect(url_for('login'))
        except Exception as e:
            print("Database Error:", e)
            flash(f"Error: {str(e)}", "danger")
            return redirect(url_for('register'))

    return render_template('register.html')
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form["username"]
        password = request.form["password"]

        # Initialize login attempts in session
        if 'login_attempts' not in session:
            session['login_attempts'] = 0

        # Check user credentials
        cursor.execute(
            "SELECT * FROM register WHERE username=%s AND password=%s",
            (username, password)
        )
        user = cursor.fetchone()

        if user:
            # Reset login attempts on successful login
            session['login_attempts'] = 0
            flash("Login successful")
            return redirect(url_for('index'))

        else:
            # Increase login attempt count
            session['login_attempts'] += 1  

            # If 3 failed attempts, redirect to forgot password page
            if session['login_attempts'] >= 3:
                flash("Too many failed attempts. Redirecting to forgot password.")
                session['login_attempts'] = 0  
                return redirect(url_for('forget_pass'))  

            flash(f"Invalid credentials. Attempt {session['login_attempts']} of 3.")
            return redirect(url_for('login'))

    return render_template('login.html')



@app.route('/forget_pass', methods=['GET', 'POST'])
def forget_pass():
    if request.method == 'POST':
        username = request.form.get('username')
        question = None

        #  If only username submitted, fetch security question
        if 'answer' not in request.form:
            cursor.execute("SELECT security_q FROM register WHERE username=%s", (username,))
            result = cursor.fetchone()
            if result:
                question = result[0]
                return render_template('forget_pass.html', username=username, question=question)
            else:
                flash("Username not found", "danger")
                return render_template('forget_pass.html')

        #  User submitted answer and new password(s)
        else:
            answer = request.form.get('answer')
            new_password = request.form.get('new_password')
            confirm_password = request.form.get('confirm_password')

            if new_password != confirm_password:
                flash("Passwords do not match", "danger")
                # To show question again in form
                cursor.execute("SELECT security_q FROM register WHERE username=%s", (username,))
                question = cursor.fetchone()[0]
                return render_template('forget_pass.html', username=username, question=question)

            cursor.execute("SELECT answer FROM register WHERE username=%s", (username,))
            result = cursor.fetchone()

            if result and answer.strip().lower() == result[0].lower():
                cursor.execute("UPDATE register SET password=%s WHERE username=%s", (new_password, username))
                mydb.commit()
                flash("Password reset successful! Please login.", "success")
                return redirect(url_for('login'))
            else:
                flash("Incorrect answer. Try again.", "danger")
                cursor.execute("SELECT security_q FROM register WHERE username=%s", (username,))
                question = cursor.fetchone()[0]
                return render_template('forget_pass.html', username=username, question=question)

   
    return render_template('forget_pass.html')




# @app.route('/forget_pass',methods=['GET','POST'])
# def forget_pass():
#     if request.method=='POST':
#          username = request.form['username']
#          return redirect(url_for('reset'))
#     return render_template('forget_pass.html')

# @app.route('/reset')
# def reset():
#      return render_template('reset.html')
# Inventory Page
@app.route('/inventory', methods=['GET', 'POST'])
def inventory():
    #  Role check
    if request.method == 'POST':
        item_id = request.form.get('id')  # for edit
        item_name = request.form['item_name']
        item_code = request.form['item_code']
        date = request.form['date']
        previous_qty = int(request.form['previous_qty'])
        today_qty = int(request.form['today_qty'])
        net_qty = previous_qty + today_qty
        per_unit_price = float(request.form['per_unit_price'])
        net_price = net_qty * per_unit_price
        category = request.form['category']
        location = request.form['location']

        if item_id:  # Edit
            cursor.execute("""
                UPDATE inventory SET
                    item_name=%s, item_code=%s, date=%s, previous_qty=%s,
                    today_qty=%s, net_qty=%s, per_unit_price=%s, net_price=%s,
                    category=%s, location=%s
                WHERE id=%s
            """, (item_name, item_code, date, previous_qty, today_qty,
                  net_qty, per_unit_price, net_price, category, location, item_id))
            flash("Item updated successfully!", "success")
        else:  # Add
            cursor.execute("""
                INSERT INTO inventory (item_name, item_code, date, previous_qty, today_qty,
                    net_qty, per_unit_price, net_price, category, location)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (item_name, item_code, date, previous_qty, today_qty,
                  net_qty, per_unit_price, net_price, category, location))
            flash("Item added successfully!", "success")

        mydb.commit()
        return redirect(url_for('inventory'))

    # Fetch inventory items
    cursor.execute("SELECT * FROM inventory ORDER BY id DESC")
    rows = cursor.fetchall()
    items = []
    for row in rows:
        items.append({
            'id': row[0],
            'item_name': row[1],
            'item_code': row[2],
            'date': row[3],
            'previous_qty': row[4],
            'today_qty': row[5],
            'net_qty': row[6],
            'per_unit_price': row[7],
            'net_price': row[8],
            'category': row[9],
            'location': row[10]
        })

    return render_template('inventory.html', items=items)


# Delete Inventory Item
@app.route('/delete_inventory/<int:id>')
def delete_inventory(id):
    #  Role check

    cursor.execute("DELETE FROM inventory WHERE id=%s", (id,))
    mydb.commit()
    flash("Item deleted successfully!", "danger")
    return redirect(url_for('inventory'))


# Edit Inventory Item (pre-fill form)
@app.route('/edit/<int:id>')
def edit_inventory(id):
    #  Role chec

    cursor.execute("SELECT * FROM inventory WHERE id=%s", (id,))
    row = cursor.fetchone()
    if not row:
        flash("Item not found!", "danger")
        return redirect(url_for('inventory'))

    item = {
        'id': row[0],
        'item_name': row[1],
        'item_code': row[2],
        'date': row[3],
        'previous_qty': row[4],
        'today_qty': row[5],
        'net_qty': row[6],
        'per_unit_price': row[7],
        'net_price': row[8],
        'category': row[9],
        'location': row[10]
    }

    # Fetch all items for the table
    cursor.execute("SELECT * FROM inventory ORDER BY id DESC")
    rows = cursor.fetchall()
    items = []
    for r in rows:
        items.append({
            'id': r[0],
            'item_name': r[1],
            'item_code': r[2],
            'date': r[3],
            'previous_qty': r[4],
            'today_qty': r[5],
            'net_qty': r[6],
            'per_unit_price': r[7],
            'net_price': r[8],
            'category': r[9],
            'location': r[10]
        })

    return render_template('inventory.html', items=items, edit_item=item)


    
@app.route('/sales', methods=['GET', 'POST'])
def sales():
    if request.method == 'POST':
        sale_id = request.form.get('sale_id')  # hidden field for update
        customer_name = request.form['customer_name']
        customer_contact = request.form['customer_contact']
        product_name = request.form['product_name']
        product_code = request.form['product_code']
        quantity = int(request.form['quantity'])
        price_per_unit = float(request.form['price_per_unit'])
        discount = float(request.form['discount']) if request.form['discount'] else 0
        gst = float(request.form['gst']) if request.form['gst'] else 0
        remarks = request.form['remarks']

        # Calculations
        gross_total = quantity * price_per_unit
        discount_amount = (discount / 100) * gross_total
        subtotal = gross_total - discount_amount
        gst_amount = (gst / 100) * subtotal
        total_amount = subtotal + gst_amount

        if sale_id:  # Update existing sale
            cursor.execute("""
                UPDATE sales SET
                    customer_name=%s, customer_contact=%s, product_name=%s, product_code=%s,
                    quantity=%s, price_per_unit=%s, discount=%s, gst=%s, remarks=%s, total_amount=%s
                WHERE id=%s
            """, (customer_name, customer_contact, product_name, product_code,
                  quantity, price_per_unit, discount, gst, remarks, total_amount, sale_id))
        else:  # Insert new sale
            cursor.execute("""
                INSERT INTO sales (
                    customer_name, customer_contact, product_name, product_code,
                    quantity, price_per_unit, discount, gst, remarks, total_amount
                ) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
            """, (customer_name, customer_contact, product_name, product_code,
                  quantity, price_per_unit, discount, gst, remarks, total_amount))
        mydb.commit()
        return redirect(url_for('sales'))

    # GET request - fetch sales
    cursor.execute("SELECT * FROM sales ORDER BY id DESC")
    sales_data = cursor.fetchall()
    return render_template('sales.html', sales_data=sales_data, edit_data=None)


# Edit sale
@app.route('/sales/edit/<int:sale_id>')
def edit_sale(sale_id):
    cursor.execute("SELECT * FROM sales WHERE id=%s", (sale_id,))
    record = cursor.fetchone()
    cursor.execute("SELECT * FROM sales ORDER BY id DESC")
    sales_data = cursor.fetchall()
    return render_template('sales.html', sales_data=sales_data, edit_data=record)


# Delete sale
@app.route('/sales/delete/<int:sale_id>', methods=['POST'])
def delete_sale(sale_id):
    cursor.execute("DELETE FROM sales WHERE id=%s", (sale_id,))
    mydb.commit()
    return redirect(url_for('sales'))



@app.route('/product', methods=['GET', 'POST'])
def product():
    if request.method == 'POST':
        product_id = request.form.get('product_id')
        product_name = request.form['product_name']
        product_code = request.form['product_code']
        category = request.form.get('category')
        brand = request.form.get('brand')
        unit = request.form.get('unit')
        price = request.form.get('price')
        stock_qty = request.form.get('stock_qty')
        min_stock = request.form.get('min_stock')
        description = request.form.get('description')

        if product_id:  # Update product
            cursor.execute("""
                UPDATE product 
                SET product_name=%s, product_code=%s, category=%s, brand=%s, unit=%s, 
                    price=%s, stock_qty=%s, min_stock=%s, description=%s
                WHERE id=%s
            """, (product_name, product_code, category, brand, unit,
                  price, stock_qty, min_stock, description, product_id))
            flash("Product updated successfully!", "info")
        else:  #  Add new product
            cursor.execute("""
                INSERT INTO product (product_name, product_code, category, brand, unit, price, stock_qty, min_stock, description)
                VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)
            """, (product_name, product_code, category, brand, unit,
                  price, stock_qty, min_stock, description))
            flash("Product added successfully!", "success")

        mydb.commit()
        return redirect(url_for('product'))

    #  Fetch all products
    cursor.execute("SELECT * FROM product")
    product_data = cursor.fetchall()
    return render_template("product.html", product_data=product_data, product=None)
# Edit Product
@app.route('/product/edit/<int:id>', methods=['GET'])
def edit_product(id):
    cursor.execute("SELECT * FROM product WHERE product_id=%s", (id,))
    product = cursor.fetchone()

    cursor.execute("SELECT * FROM product")
    product_data = cursor.fetchall()

    return render_template("product.html", product_data=product_data, product=product)

# Delete Product

@app.route('/product/delete/<int:id>', methods=['POST'])
def delete_product(id):
    cursor.execute("DELETE FROM products WHERE id=%s", (id,))
    mydb.commit()
    flash("Product deleted successfully!", "danger")
    return redirect(url_for('product'))

@app.route('/purchase', methods=['GET', 'POST'])
def purchase():
    if request.method == 'POST':
        purchase_id = request.form.get('purchase_id')  # hidden field for update
        supplier_name = request.form['supplier_name']
        item_name = request.form['item_name']
        item_code = request.form['item_code']
        purchase_date = request.form['purchase_date']
        quantity = int(request.form['quantity'])
        unit_price = float(request.form['unit_price'])
        total_price = quantity * unit_price
        status = request.form['status']

        if purchase_id:  # update
            cursor.execute("""
                UPDATE purchases SET
                    supplier_name=%s, item_name=%s, item_code=%s,
                    purchase_date=%s, quantity=%s, unit_price=%s, total_price=%s, status=%s
                WHERE purchase_id=%s
            """, (supplier_name, item_name, item_code, purchase_date,
                  quantity, unit_price, total_price, status, purchase_id))
        else:  # insert
            cursor.execute("""
                INSERT INTO purchases (supplier_name, item_name, item_code, purchase_date,
                                       quantity, unit_price, total_price, status)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """, (supplier_name, item_name, item_code, purchase_date,
                  quantity, unit_price, total_price, status))
        mydb.commit()
        return redirect(url_for('purchase'))

    # GET request - fetch all purchases
    cursor.execute("SELECT * FROM purchases")
    data = cursor.fetchall()
    return render_template("purchase.html", purchases=data, edit_data=None)


# Edit purchase
@app.route('/purchase/edit/<int:purchase_id>')
def edit_purchase(purchase_id):
    cursor.execute("SELECT * FROM purchases WHERE purchase_id=%s", (purchase_id,))
    record = cursor.fetchone()
    cursor.execute("SELECT * FROM purchases")
    data = cursor.fetchall()
    return render_template("purchase.html", purchases=data, edit_data=record)


# Delete purchase
@app.route('/purchase/delete/<int:purchase_id>', methods=['POST'])
def delete_purchase(purchase_id):
    cursor.execute("DELETE FROM purchases WHERE purchase_id=%s", (purchase_id,))
    mydb.commit()
    return redirect(url_for('purchase'))

# HR Main Route (Insert / Update / Search / View All)
@app.route('/hr', methods=['GET', 'POST'])
def hr():
    if request.method == "POST":
        # --- Search Request ---
        search_phone = request.form.get("search_phone")
        if search_phone:   # if user entered a phone number in search box
            cursor.execute("SELECT * FROM hr WHERE phone = %s", (search_phone,))
            employees = cursor.fetchall()
            return render_template("hr.html", employees=employees, edit_data=None, search_value=search_phone)

        # --- Save or Update Request ---
        emp_id = request.form.get("emp_id")  # hidden field for update
        name = request.form.get("name")
        email = request.form.get("email")
        phone = request.form.get("phone")
        department = request.form.get("department")
        designation = request.form.get("designation")
        joining_date = request.form.get("joining_date")
        salary = request.form.get("salary")

        if name and email and phone:
            if emp_id:  # Update existing record
                cursor.execute("""
                    UPDATE hr SET
                        name=%s, email=%s, phone=%s, department=%s,
                        designation=%s, joining_date=%s, salary=%s
                    WHERE emp_id=%s
                """, (name, email, phone, department, designation, joining_date, salary, emp_id))
            else:  # Insert new record
                cursor.execute("""
                    INSERT INTO hr (name, email, phone, department, designation, joining_date, salary)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                """, (name, email, phone, department, designation, joining_date, salary))

            mydb.commit()
            return redirect(url_for('hr'))

    # --- Default: GET request → fetch all records ---
    cursor.execute("SELECT * FROM hr")
    employees = cursor.fetchall()
    return render_template("hr.html", employees=employees, edit_data=None, search_value="")


# Edit HR
@app.route('/hr/edit/<int:emp_id>')
def edit_hr(emp_id):
    cursor.execute("SELECT * FROM hr WHERE emp_id=%s", (emp_id,))
    record = cursor.fetchone()
    cursor.execute("SELECT * FROM hr")
    employees = cursor.fetchall()
    return render_template("hr.html", employees=employees, edit_data=record, search_value="")


# Delete HR
@app.route('/hr/delete/<int:emp_id>', methods=['POST'])
def delete_hr(emp_id):
    cursor.execute("DELETE FROM hr WHERE emp_id=%s", (emp_id,))
    mydb.commit()
    return redirect(url_for('hr'))




@app.route('/account', methods=['GET', 'POST'])
def account():
    edit_data = None

    if request.method == 'POST':
        acc_id = request.form.get('acc_id')
        date = request.form['date']
        transaction_type = request.form['transaction_type']
        amount = float(request.form.get('amount', 0))
        description = request.form.get('description')
        category = request.form.get('category')
        product_name = request.form.get('product_name')
        quantity = int(request.form.get('quantity', 0))
        unit_price = float(request.form.get('unit_price', 0))

        # Calculate total_amount automatically for sales/purchase/product
        if category in ['sales', 'purchase', 'product']:
            total_amount = quantity * unit_price
        else:
            total_amount = amount

        if acc_id:  # Update
            cursor.execute("""
                UPDATE accounts 
                SET date=%s, transaction_type=%s, amount=%s, description=%s,
                    category=%s, product_name=%s, quantity=%s, unit_price=%s, total_amount=%s
                WHERE acc_id=%s
            """, (date, transaction_type, amount, description, category, product_name, quantity, unit_price, total_amount, acc_id))
            flash("Transaction updated successfully!", "success")
        else:      # Add new
            cursor.execute("""
                INSERT INTO accounts (date, transaction_type, amount, description, category, product_name, quantity, unit_price, total_amount)
                VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)
            """, (date, transaction_type, amount, description, category, product_name, quantity, unit_price, total_amount))
            flash("Transaction added successfully!", "success")

        mydb.commit()
        return redirect(url_for('account'))

    # If edit requested via query parameter
    edit_id = request.args.get('edit_id')
    if edit_id:
        cursor.execute("SELECT * FROM accounts WHERE acc_id=%s", (edit_id,))
        edit_data = cursor.fetchone()

    # Fetch all transactions
    cursor.execute("SELECT * FROM accounts ORDER BY acc_id DESC")
    accounts = cursor.fetchall()

    return render_template("account.html", accounts=accounts, edit_data=edit_data)

# Edit route (just redirects to account page with edit_id)
@app.route('/accounts/edit/<int:acc_id>', methods=['POST'])
def edit_account(acc_id):
    return redirect(url_for('account', edit_id=acc_id))

# Delete route
@app.route('/accounts/delete/<int:acc_id>', methods=['POST'])
def delete_account(acc_id):
    cursor.execute("DELETE FROM accounts WHERE acc_id=%s", (acc_id,))
    mydb.commit()
    flash("Transaction deleted successfully!", "success")
    return redirect(url_for('account'))


@app.route("/contact_us", methods=["GET", "POST"])
def contact_us():
    if request.method == "POST":
        name = request.form["name"]
        email = request.form["email"]
        phone = request.form["phone"]
        message = request.form["message"]

        try:
            cursor.execute("""
                INSERT INTO contact (name, email, phone, message)
                VALUES (%s, %s, %s, %s)
            """, (name, email, phone, message))
            mydb.commit()
            flash("Your message has been sent successfully!", "success")
        except Exception as e:
            flash(f"Error: {e}", "danger")

        return redirect(url_for("contact_us"))

    # Fetch all contact messages
    cursor.execute("SELECT * FROM contact ORDER BY created_at DESC")
    contacts = cursor.fetchall()

    return render_template("contact_us.html", items=contacts)





