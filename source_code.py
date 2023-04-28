import tkinter
import tkinter as tk
from tkinter import *
from tkinter import ttk
from tkinter.messagebox import showinfo, showerror

from PIL import ImageTk, Image
import psycopg2
import bcrypt # Library for hashing
import string
import base64 # Library for encoding

# connection to the database
# put the database name and the password here
connection = psycopg2.connect(
    host="localhost",
    database="Project",
    user="postgres",
    password="123"
)
# database cursor
cur = connection.cursor()


# create new text box
def createTextbox(root, label_name, row_num, col_num):
    # create box
    textBox = Entry(root, width=30)
    textBox.grid(row=row_num, column=(col_num + 1), padx=20)

    # create label for box
    textBox_label = Label(root, text=label_name)
    textBox_label.grid(row=row_num, column=col_num)
    return textBox


# create new button
def createButton(root, b_text, com_name, row_num, col_num):
    newButton = Button(root, text=b_text, command=com_name)
    newButton.grid(row=row_num, column=col_num,
                   columnspan=2, pady=10, padx=10, ipadx=100)
    return newButton


# clear text box input
def clearText(textboxName):
    textboxName.delete(0, END)

# function to verify length to fit database requirements and uniqueness of username to eliminate duplicate values
def unique_username(user_input):
    try:
        # check whether username already in use in database
        
        
        sql = "SELECT COUNT(username) FROM users WHERE username = '" + user_input + "';"
        
        cur.execute(sql)
        result = cur.fetchone()
        
        if result[0] == 0:
            return True

        else: 
            showerror(
            'Notification!', 'This usernmame is already in use!\n Please enter a new username')
            return False 
    
    except Exception:
        return False


# function to compare the user's entered password against the password policies
def password_policies(username, user_input):

    special_chars = string.punctuation

    # define password policies
    password_policy = [lambda user_input: len(user_input) >= 10,
                       lambda user_input: len(user_input) <= 35,
                       lambda user_input: not (username in user_input),
                       lambda char: any(char in special_chars for char in user_input),
                       lambda user_input: any(char.isdigit()
                                              for char in user_input),
                       lambda user_input: any(char.islower()
                                              for char in user_input),
                       lambda user_input: any(char.isupper() for char in user_input)]

    if all(policy(user_input) for policy in password_policy):
        return True

    else:
        return False


class ourApp(tk.Tk):
    """baseline of our application"""

    def __init__(self, *args, **kwargs):
        """initialize widgets """

        tk.Tk.__init__(self, *args, **kwargs)
        # initialize the application frame
        self.geometry("500x512")
        self.title('ONLINE FORUM')
        container = tk.Frame(self)
        container.pack(side="top", fill="both", expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        self.frames = {}
        # all pages
        for f in (mainMenu, login, signButton):
            frame = f(container, self)
            self.frames[f] = frame
            # nsew = stretches everything to the center
            frame.grid(row=0, column=0, sticky='nsew')

        self.show_frame(mainMenu)

    def show_frame(self, cont):
        # show the frame on top of all frames
        frame = self.frames[cont]
        frame.tkraise()


class mainMenu(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)

         # mainMenu picture
        self.canvas = tkinter.Canvas(self, height=550, width=500)
        self.image_file = tkinter.PhotoImage(file='2.gif')
        self.image = self.canvas.create_image(
            0, 0, anchor='nw', image=self.image_file)
        self.canvas.pack(side='top')

        # label the page
        title = tk.Label(self, text='Welcome to Our ExpressYourself',
                         font=('Times New Roman', 20, "bold italic"))
        title.pack()
        title.place(x=60, y=320)

        slogan = tk.Label(self, text='Your Thoughts Matter with ExpressYourself',
                          font=('Times New Roman', 9, "bold italic"))
        slogan.pack()
        slogan.place(x=130, y=350)

        # create button
        button1 = tk.Button(self, text="Explore More", width=12, height=2,
                            command=lambda: controller.show_frame(
                                login))  # use lambda and controller to pass parameters and navigate between pages

        # style and place of the button
        button1.pack()
        button1.place(x=200, y=380)


class login(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)

        # login picture
        self.canvas = tkinter.Canvas(self, height=500, width=500)
        self.image_file = tkinter.PhotoImage(file='Welcome_Back.gif')
        self.image = self.canvas.create_image(
            0, 0, anchor='nw', image=self.image_file)
        self.canvas.pack()
        self.canvas.place(x=0, y=0)

        # create id label
        id_label = tk.Label(self, text="Enter your User Name: ")
        id_label.pack()
        id_label.place(x=65, y=240)

        # create id entry
        id_entry = tk.Entry(self, width=25)
        id_entry.pack()
        id_entry.place(x=200, y=240)

        # create password label
        password_label = tk.Label(self, text="Password: ")
        password_label.pack()
        password_label.place(x=65, y=270)

        # create password entry
        password_entry = tk.Entry(self, width=25, show="*")
        password_entry.pack()
        password_entry.place(x=200, y=270)

        def message():
            # window successfully logged
            # search for user name and its password here
            user_name = id_entry.get()
            try:
                sql ="SELECT * FROM users WHERE username = '" + user_name + "';"
                cur.execute(sql)
                hashed_password_b64 = cur.fetchone()[1] # get the user's hashed password

                if hashed_password_b64 is None:
                    showerror('Notification!', 'The user name you entered is not in the database!\n Please enter a valid username')
                    cur.rollback()
                    return
            except Exception:
                showerror('Notification!', f'Username {user_name} does not exist !')
                print("An error occurred, please try again.")
                connection.rollback()
                return
            user_unique_password = (user_name+password_entry.get()).encode('utf-8') # create a unique password with user name and password
            # Decode hashed password from base64
            hashed_password_bytes = base64.b64decode(hashed_password_b64) # decrypt the hashed password

            # Check if entered password matches hashed password
            if bcrypt.checkpw(user_unique_password, hashed_password_bytes): # check if the given login password matches
                showinfo('Notification!', 'Successfully logged in!')
            else:
                showerror('Notification!', f'You entered invalid password for the user {user_name} !')

        button1 = tk.Button(self, text="LOGIN", width=12, height=2,
                            command=message)
        button1.pack()
        button1.place(x=55, y=330)

        # create sign up button
        button2 = tk.Button(self, text="SIGN UP", width=12, height=2,
                            command=lambda: controller.show_frame(signButton))
        button2.pack()
        button2.place(x=210, y=330)

        # create return button
        button3 = tk.Button(self, text="RETURN HOME", width=12, height=2,
                            command=lambda: controller.show_frame(mainMenu))
        button3.pack()
        button3.place(x=360, y=330)


class signButton(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        # Name
        label = tk.Label(self, text="Sign up with new account",
                         font=('Times New Roman', 20, "bold italic"))
        label.place(x=55, y=20)
        label.pack(pady=20, padx=10)

        # create id label
        id_label = tk.Label(self, text="Enter your ID:")
        id_label.pack()
        id_label.place(x=95, y=90)

        # create id entry
        id_entry = tk.Entry(self, width=25)
        id_entry.pack()
        id_entry.place(x=205, y=90)

        # create password label
        password_label = tk.Label(self, text="Password:")
        password_label.pack()
        password_label.place(x=95, y=120)

        # create password entry
        password_entry = tk.Entry(self, width=25, show="*")
        password_entry.pack()
        password_entry.place(x=205, y=120)

        def message():
            if not unique_username(id_entry.get()): # check if username already in database
                return
            elif len(password_entry.get()) < 10:    # check if password too short
                showerror(
                    'Notification!', 'The password you entered is too short!\n Please enter a new pasword')
                return
            elif not password_policies(id_entry.get(), password_entry.get()):   # if al password policies not fulfilled
                showerror(
                    'Notification!', 'The password should contain:\nuppercase letters, lowercase letters, numerical digits, special characters, and it should not contain your username\nPlease enter a new password')
                return
            else:  # If successfull
                # HASHING STARTS
                user_id = id_entry.get()
                user_password = password_entry.get()
                user_unique_password = (user_id+user_password).encode('utf-8') # encode the user unique password to be ready to hashing
                hashed_password_bytes = bcrypt.hashpw(user_unique_password, bcrypt.gensalt()) # hash the password by generating salt

                # Encode hashed password as base64
                hashed_password_b64 = base64.b64encode(hashed_password_bytes)

                try:
                    cur.execute("INSERT INTO users VALUES ('"+id_entry.get()+"','"+hashed_password_b64.decode()+"');") # insert the new user's id and hashed password as string
                    connection.commit()
                    showinfo('Notification!', f'User {id_entry.get()} successfully created!')
                    return controller.show_frame(login)
                except Exception as ex:
                    print(ex)
                    connection.rollback()
                    return

        button2 = tk.Button(self, text="SIGN UP", width=12, height=2,
                            command=message)
        button2.pack()
        button2.place(x=70, y=150)

        button3 = tk.Button(self, text="RETURN HOME", width=12, height=2,
                            command=lambda: controller.show_frame(mainMenu))
        button3.pack()
        button3.place(x=270, y=150)


# running our app
app = ourApp()
app.mainloop()

# closing cursor and connection to database
cur.close()
connection.close()
