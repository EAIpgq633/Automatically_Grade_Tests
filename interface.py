from tkinter import *
from PIL import Image, ImageTk
from tkinter import filedialog, messagebox

import pandas as pd
import numpy as np
import cv2
import precess_img
import process_img_sbd_mdt


def resize_image(image, max_width, max_height):
    """
        Convert the aspect ratio of the original image

        Args: 
            image: Image
            max_width: Max Width
            max_lenght: Max lenght
        Returns:
            The image has been converted to the aspect ratio of the original image.
            
    """
    # Get the current size of the image
    width, height = image.size
    
    # Calculate new rate
    aspect_ratio = width / height
    if width > max_width:
        width = max_width
        height = int(width / aspect_ratio)
    if height > max_height:
        height = max_height
        width = int(height * aspect_ratio)
    
    # Resize image
    return image.resize((width, height), Image.LANCZOS)


def interface():
    """
        Create interface windows and functions
    """

    # Create window interface and settings interface
    win = Tk()
    win.title("Chấm điểm thi trắc nghiệm tự động")
    win.geometry("1100x800")
    win.attributes("-topmost", True)

    name1 = Label(win,text= "File Đáp án:", font= ("Arival", 15))
    name1.place(x = 30, y = 30)

    name2 = Label(win, text="File Ảnh     :",font= ("Arival", 15))
    name2.place(x= 30, y = 80)

    bg_kq = Label(win, text= "Bài Thi" ,width= 50, height= 50, font= ("Arival", 15), bg = '#33FFFF')
    bg_kq.place(x = 510, y = 0)
    bg_kq.config(justify='center')


    #
    entry_result_file = Entry(win,width= 10, font=("Times New Roman", 15))
    entry_result_file.insert(0, "result_file")
    entry_result_file.place(x = 300,  y = 30)

    def click_result():
        global result_flie
        result_flie = "" + entry_result_file.get()
        label = Label(win, text= "Xác nhận file lưu: "+ result_flie  + ".csv" , font= ("Arival", 10), fg= 'green')
        label.place(x = 300 , y = 55 )

    but_result  = Button(win, text= "Xác nhận",command= click_result,
                font=("Arival", 10), bg = '#33FFFF')
    but_result.place(x = 300, y = 80)
    

    # Create Button
    def clicked1():
        
        bg_white =Label(win, text="",width= 40, height= 30, font=("Arial", 10),)
        bg_white.place(x =  20, y = 220)

        global sbd, mdt, total_true, img
        bg = Label(win, text= "" ,width= 30, height= 9, font= ("Arival", 15), bg = '#33FFFF')
        bg.place(x = 20, y = 220)

        name_kq = Label(win, text= "Kết Quả" , font= ("Arival", 15), bg = '#33FFFF')
        name_kq.place(x=150, y = 225)

        name_sbd = Label(win, text= "SBD  :" , font= ("Arival", 15), bg = '#33FFFF')
        name_sbd.place(x = 30, y =250)
        sbd_bg = Label(win, text= "" +  sbd,  font= ("Arival", 15), bg = '#33FFFF')
        sbd_bg.place(x = 100, y = 250 )


        name_mdt = Label(win, text= "MDT  :" , font= ("Arival", 15), bg = '#33FFFF')
        name_mdt.place(x = 30, y = 300)
        mdt_bg =  Label(win, text= "" + mdt , font= ("Arival", 15), bg = '#33FFFF')
        mdt_bg.place(x= 100, y = 300 )

        name_score = Label(win, text= "Điểm :" , font= ("Arival", 15), bg = '#33FFFF')
        name_score.place(x = 30, y = 350)
        score = Label(win, text="" + str(total_true), font= ("Arival", 15), bg = '#33FFFF')
        score.place(x = 100, y = 350)
        
        # Convert image from BGR to RGB
        image_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        
        # Convert numpy array to Pillow Image
        image_pil = Image.fromarray(image_rgb)

        # Maximum image size
        max_width = 600
        max_height = 800

        # Change image size
        resized_image = resize_image(image_pil, max_width, max_height)

        # Convert images to a usable Tkinter format
        photo = ImageTk.PhotoImage(resized_image)

        # Create a label to contain the image
        label = Label(win, image=photo)
        label.photo = photo 
        label.place(x = 510, y = 0)

        def clicked2():
            global sbd, mdt, total_true, img, list_sbd, list_score
            bg_white = Label(win, text= "",width= 20, height= 8, font= ("Arival", 15), fg = 'red')
            bg_white.place(x=50, y = 520)

            # Save value to list
            if sbd != "":
                notice = Label(win, text= f"Đã Lưu \nSBD : {sbd} \n Điểm : {total_true}", font= ("Arival", 15), fg = 'red')
                notice.place(x=50, y = 520)

                list_sbd.append(sbd)
                list_score.append(total_true)

            # Reset values ​​after saving
            mdt =""
            sbd = ""
            total_true = 0
            img = np.array([0])

        but2 = Button(win, text= "Lưu", width= 10, height= 2,command = clicked2,
                font=("Times New Roman", 15), bg = '#33FFFF')
        but2.place(x = 150, y = 450)


    but1 = Button(win, text= "Chấm Điểm", width= 10, height= 2,command= clicked1,
                font=("Times New Roman", 15), bg = '#33FFFF')
    but1.place(x = 150, y = 150)

    # FUNCTION TO GET CSV FILE
    def upload_file():
        global ANSWER_KEY
        file_path = filedialog.askopenfilename(
            filetypes=[("CSV Files", "*.csv")]
        )
        # DATA PROCESSING SECTION TO GET ANSWERS
        if file_path:
            try:
                ANSWER_KEY = []
                # Đọc dữ liệu từ file CSV
                with open(file_path, newline='', encoding='utf-8') as csvfile:
                    data = pd.read_csv(csvfile)   
                    # Get the answer column
                    ANSWER_KEY = data.iloc[:, -1].tolist()
                notice =  Label(win, text= "Đọc file thành công" , font= ("Arival", 10), fg= 'green')
                notice.place(x = 150, y = 60)
  
            except Exception as e:
                messagebox.showerror("Error", f"An error occurred: {e}")

        else:
            messagebox.showwarning("No File", "No file was selected")

    but_choice_csv = Button(win, text="Choose CSV File", command= upload_file,
                    font=("Arial", 10), bg='#FF6666', fg='white')
    but_choice_csv.place(x = 150, y= 30)


    # FUNCTION TO GET IMAGE FILE
    def upload_image():
        global img
        file_path = filedialog.askopenfilename(
            filetypes=[("Image Files", "*.png;*.jpg;*.jpeg;*.gif")]
        )
        
        if file_path:
            try:
                # Open image with opencv
                img = cv2.imread(file_path)
                
                # Perform image processing operations
                img_height, img_width, img_chanels = img.shape
                max_weight = 1630
                max_height = 2323

                # crop_sbd = (60, 686, 1450, 1475)
                crop_1_120 = (int(60 / max_weight * img_width),
                            int(700 / max_height * img_height), 
                            int(1465 / max_weight * img_width),
                            int(1500 / max_height * img_height))
                
                # crop_sbd = (1150, 200, 231, 480 )
                crop_sbd = (int(1150 / max_weight * img_width),
                            int(200 / max_height * img_height), 
                            int(231 / max_weight * img_width),
                            int(480 / max_height * img_height))
                
                # crop_sbd = (1420, 200, 130, 480 )
                crop_mdt = (int(1410 / max_weight * img_width),
                            int(200 / max_height * img_height), 
                            int(130 / max_weight * img_width),
                            int(480 / max_height * img_height))


                # IMAGE PROCESSING SECTION OF THE TEST
                x1, y1, w1, h1 = crop_1_120
                img_answer = img[y1: y1 + h1, x1: x1 + w1]
                # Crop image into 4 columns
                sorted_and_blocks = precess_img.crop_image(img_answer)
                # Get the position of the text in the advice reply box and sort it in order from 1->480
                list_location_one_text = precess_img.location_answer(sorted_and_blocks)
                # User selection list
                list_choice_candidate = precess_img.get_answer_candidate(list_location_one_text, img_answer)
                # Check selection and color cells
                global total_true
                total_true = precess_img.check_and_draw(list_choice_candidate, list_location_one_text, ANSWER_KEY, img_answer)

                # SBD PART IMAGE PROCESSING
                x2, y2, w2, h2 = crop_sbd
                img_sbd = img[y2: y2 + h2, x2: x2 + w2]
                ans_block_sbd = process_img_sbd_mdt.crop_img(img_sbd)
                location_box_sbd = process_img_sbd_mdt.location_box_text_sbd(ans_block_sbd)
                sbd_l = process_img_sbd_mdt.check_and_draw_sbd_mdt(location_box_sbd, img_sbd)
                global sbd 
                for n in sbd_l:
                    sbd = sbd + str(n)

                # MDT PART IMAGE PROCESSING
                x3, y3, w3, h3 = crop_mdt
                img_mdt = img[y3: y3 + h3, x3: x3 + w3]

                ans_block_mdt = process_img_sbd_mdt.crop_img(img_mdt)
                location_box_mdt = process_img_sbd_mdt.location_box_text_mdt(ans_block_mdt)
                mdt_l = process_img_sbd_mdt.check_and_draw_sbd_mdt(location_box_mdt, img_mdt)

                global mdt 
                for n in mdt_l:
                    mdt = mdt + str(n)

                notice =  Label(win, text= "Đọc file thành công" , font= ("Arival", 10), fg= 'green')
                notice.place(x = 150, y = 110)

            except Exception as e:
                messagebox.showerror("Error", f"An error occurred: {e} or No response data or Inappropriate photo")
        else:
            messagebox.showwarning("No File", "No file was selected")

                
    but_choice_csv = Button(win, text="Choose Image file", command= upload_image,
                    font=("Arial", 10), bg='#FF6666', fg='white')
    but_choice_csv.place(x = 150, y= 80)


    # Create an "Exit" button
    def exit_program():
        win.destroy()
    exit_button = Button(win, text="Thoát", command=exit_program,
                    font=("Arial", 15), bg='#FF6666', fg='white')
    exit_button.place(x = 20, y = 750 )

    win.mainloop()


if __name__ == "__main__":
    ANSWER_KEY = []
    mdt =""
    sbd = ""
    result_flie = ""
    total_true = 0
    list_sbd = []
    list_score = []
    img = np.array([0])
    interface()
    data = {
        'SBD': list_sbd,
        'Score': list_score
    }
    # Tạo DataFrame
    df = pd.DataFrame(data)
    # Lưư kết quả thành file CSV  
    df.to_csv( result_flie + '.csv', index=False, encoding='utf-8')
    print(result_flie)
   

    