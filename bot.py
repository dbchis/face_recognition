from library import *

language = 'vi'
path = ChromeDriverManager().install()
wikipedia.set_lang('vi')
# Biến toàn cục để kiểm soát việc dừng lại và trạng thái lắng nghe
stop_reading = False
# Biến toàn cục để lưu trữ URL của YouTube
opened_youtube_url = None
# Xac thực chủ nhân
class FaceRecognitionFrame(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        
        # Initialize MTCNN and InceptionResnetV1
        self.mtcnn = MTCNN(image_size=160, margin=0, min_face_size=20)
        self.resnet = InceptionResnetV1(pretrained='vggface2').eval()
        
        # Initialize the camera
        self.cap = cv2.VideoCapture(0)
        
        # Create a label to display the video feed
        self.video_label = tk.Label(self)
        self.video_label.pack()
        
        # Create buttons for saving and verifying face
        self.save_button = tk.Button(self, text="Lưu", command=self.save_face)
        self.save_button.pack(side=tk.LEFT, padx=10, pady=10)
        
        self.verify_button = tk.Button(self, text="Xác thực", command=self.verify_face)
        self.verify_button.pack(side=tk.RIGHT, padx=10, pady=10)
        
        # Start the video feed
        self.update_video()

    def update_video(self):
        ret, frame = self.cap.read()
        if ret:
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            img = Image.fromarray(frame)
            imgtk = ImageTk.PhotoImage(image=img)
            self.video_label.imgtk = imgtk
            self.video_label.configure(image=imgtk)
        self.video_label.after(10, self.update_video)
    
    def save_face(self):
        ret, frame = self.cap.read()
        if ret:
            img = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
            img_cropped = self.mtcnn(img)
            if img_cropped is not None:
                img_embedding = self.resnet(img_cropped.unsqueeze(0)).detach().numpy()
                df = pd.DataFrame(img_embedding)
                df.to_csv('data/face_data.csv', index=False)
                messagebox.showinfo("Info", "Face data saved successfully!")
            else:
                messagebox.showwarning("Warning", "No face detected!")
    
    def verify_face(self):
        ret, frame = self.cap.read()
        if ret:
            img = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
            img_cropped = self.mtcnn(img)
            if img_cropped is not None:
                img_embedding = self.resnet(img_cropped.unsqueeze(0)).detach().numpy()
                saved_data = pd.read_csv('data/face_data.csv').values
                distance = np.linalg.norm(saved_data - img_embedding)
                if distance < 0.8:  # You can adjust the threshold
                    return 1
                    messagebox.showinfo("Info", "Chào chủ nhân!")
                else:
                    return 0
                    messagebox.showwarning("Warning", "Face not recognized!")
            else:
                return 0
                messagebox.showwarning("Warning", "No face detected!")
    
    def show(self):
        self.pack(fill=tk.BOTH, expand=True)
    
    def hide(self):
        self.pack_forget()
    
    def __del__(self):
        self.cap.release()
        cv2.destroyAllWindows()
# end xác thực
class Bot:
    def __init__(self,root):
        self.root = root
        self.root.title("Bot")
        # Load frames for talking and idle animations
        self.frames = []
        self.idle_frames = []
        self.frame_index = 0
        self.idle_frame_index = 0

        # Load talking GIF
        gif = Image.open("img/botbot.gif")
        while True:
            try:
                self.frames.append(gif.copy())
                gif.seek(len(self.frames))
            except EOFError:
                break

        # Load idle GIF
        idle_gif = Image.open("img/botbot.gif")
        while True:
            try:
                self.idle_frames.append(idle_gif.copy())
                idle_gif.seek(len(self.idle_frames))
            except EOFError:
                break
        # GUI setup
        self.image_label = tk.Label(root)
        self.image_label.pack()
        self.face_recognition_frame = FaceRecognitionFrame(root)
        threading.Thread(target=self.call_sen, args=()).start()
       
    
    def click_enter(self):
        global stop_reading
        keyboard.wait('enter')
        stop_reading = True
        print(stop_reading)
        print("bạn vừa nhấn enter")
    def speak(self,text):
        tts = gTTS(text=text, lang='vi')
        filename = "voice.mp3"
        tts.save(filename)
        pygame.mixer.init()
        pygame.mixer.music.load(filename)
        pygame.mixer.music.play()
        while pygame.mixer.music.get_busy():
            continue
        pygame.mixer.quit()
        if os.path.exists(filename):
            os.remove(filename)
        
        


    def get_voice(self):
        r = sr.Recognizer()
        with sr.Microphone() as source:
            print("Me: ", end = '')
            audio = r.listen(source, phrase_time_limit=5)
            try:
                text = r.recognize_google(audio, language="vi-VN")
                print(text)
                return text
            except:
                print("...")
                return 0

    def stop(self):
        self.speak("Hẹn gặp lại bạn nhé!")
        root.quit()
        
        
    def get_text(self):
        for i in range(3):
            text = self.get_voice()
            if text:
                return text.lower()
            elif i < 2:
                self.speak("Yorn không nghe rõ, bạn có thể nói lại không ?")
        time.sleep(10)
        self.stop()
        return 0

    def talk(self,name):
        day_time = int(strftime('%H'))
        if day_time < 12:
            self.speak("Chào buổi sáng {}. Chúc bạn ngày mới tốt lành!".format(name))
        elif day_time < 18:
            self.speak("Chào buổi chiều {}!".format(name))
        else:
            self.speak("Chào buổi tối {}!".format(name))
        time.sleep(5)
        self.speak("Bạn có khỏe không ?")
        time.sleep(3)
        ans = self.get_voice()
        if ans:
            if "có" in ans:
                self.speak("Thật là tốt!")
            else:
                self.speak("Vậy à, bạn nên nghỉ ngơi đi!")
                
    def open_website(self,text):
        regex = re.search ('mở (.+)', text)
        if regex:
            domain = regex.group(1)
            url = 'https://www.' + domain
            webbrowser.open(url)
            self.speak("Trang web của bạn đã được mở lên!")
            return True
        else:
            return False
        
        
    def google_search(self,text):
        search_for = text.split("kiếm", 1)[1]
        self.speak("Oke la")
        driver = webdriver.Chrome(path)
        driver.get("http://www.google.com")
        query = driver.find_element_by_xpath("//input[@name='q']")
        query.send_keys(str(search_for))
        query.send_keys(Keys.RETURN)

    def get_time(self,text):
        now = datetime.datetime.now()
        if "giờ" in text:
            self.speak("Bây giờ là %d giờ %d phút" % (now.hour, now.minute))
        elif "ngày" in text:
            self.speak("Hôm nay là ngày %d tháng %d năm %d " % (now.day, now.month, now.year))
        else:
            self.speak("Bot không hiểu")


    def play_youtube(self):
        global opened_youtube_url
        self.speak("Bạn nghe nhạc hay xem phim gì ạ")
        time.sleep(3)
        my_song = self.get_text()
        while True:
            result = YoutubeSearch(my_song, max_results = 10).to_dict()
            if result:
                break
        url = 'https://www.youtube.com' + result[0]['url_suffix']
        print(url)
        opened_youtube_url = url
        webbrowser.open(url)
        self.speak("Chúc bạn thưởng thức vui vẻ")
    def close_youtube(self):
        global opened_youtube_url
        if not opened_youtube_url:
            self.speak("Không có YouTube nào được mở bởi chương trình.")
            return

        # Lấy danh sách các cửa sổ đang mở
        windows = gw.getAllWindows()
        youtube_windows = [window for window in windows if 'YouTube' in window.title]

        for window in youtube_windows:
            # Kiểm tra xem tiêu đề cửa sổ có chứa từ khóa "YouTube" hay không
            if 'YouTube' in window.title:
                window.close()
                speak("Đã đóng YouTube.")
                return

        self.speak("Không tìm thấy YouTube đang mở bởi chương trình.")
    def search_google(self):
        self.speak("Xin mời bạn nhập thông tin cần tìm kiếm")
        time.sleep(3)
        query = get_text()
        url = f'https://www.google.com/search?q={query}'
        webbrowser.open(url)
        self.speak("Thông tin bạn cần tìm kiếm đã được mở trên Google Chrome!")   
        
        
    def weather(self):
        self.speak("Bạn muốn xem thời tiết ở đâu ạ!")
        time.sleep(1)
        url = "http://api.openweathermap.org/data/2.5/weather?"
        city = self.get_text()
        if not city:
            pass
        api_key = "fe8d8c65cf345889139d8e545f57819a"
        call_url = url + "appid=" + api_key + "&q=" + city + "&units=metric"
        response = requests.get(call_url)
        data = response.json()
        if data["cod"] != "404":
            city_res = data["main"]
            current_temp = city_res["temp"]
            current_pressure = city_res["pressure"]
            current_humidity = city_res["humidity"]
            sun_time  = data["sys"]
            sun_rise = datetime.datetime.fromtimestamp(sun_time["sunrise"])
            sun_set = datetime.datetime.fromtimestamp(sun_time["sunset"])
            wther = data["weather"]
            weather_des = wther[0]["description"]
            now = datetime.datetime.now()
            content = """
            Hôm nay là ngày {day} tháng {month} năm {year}
            Nhiệt độ trung bình là {temp} độ C
            Áp suất không khí là {pressure} héc tơ Pascal
            Độ ẩm là {humidity}%
            Trời hôm nay quang mây. Dự báo mưa rải rác ở một số nơi.""".format(day = now.day, month = now.month, year= now.year, hourrise = sun_rise.hour, minrise = sun_rise.minute,
                                                                            hourset = sun_set.hour, minset = sun_set.minute, 
                                                                            temp = current_temp, pressure = current_pressure, humidity = current_humidity)
            self.speak(content)
            time.sleep(1)
        else:
            self.speak("Không tìm thấy thành phố!")
            
            
    def open_application(self,text):
        if "google" in text:
            self.speak("Mở google chrome")
            os.startfile("C:\ProgramData\Microsoft\Windows\Start Menu\Programs\Google Chrome.lnk")
        elif "word" in text:
            self.speak("Mở Microsoft Word")
            os.startfile("C:\ProgramData\Microsoft\Windows\Start Menu\Programs\Microsoft Office\Microsoft Word 2010.lnk")
        elif "excel" in text:
            self.speak("Mở Microsoft Excel")
            os.startfile("C:\ProgramData\Microsoft\Windows\Start Menu\Programs\Microsoft Office\Microsoft Excel 2010.lnk")
        elif "powerpoint" in text:
            self.speak("Mở Microsoft PowerPoint")
            os.startfile("C:\ProgramData\Microsoft\Windows\Start Menu\Programs\Microsoft Office\Microsoft PowerPoint 2010.lnk")
        else:
            self.speak("Phần mềm của bạn chưa được cài đặt!")
    def close_word(self):
        # Tìm và kết thúc tiến trình của Microsoft Word
        for proc in psutil.process_iter(['pid', 'name']):
            if proc.info['name'] == 'WINWORD.EXE':
                proc.terminate()
                self.speak("Đã đóng Microsoft Word.")
                return
        self.speak("Không tìm thấy Microsoft Word đang chạy.")
    def close_excel(self):
        # Tìm và kết thúc tiến trình của Microsoft Excel
        for proc in psutil.process_iter(['pid', 'name']):
            if proc.info['name'] == 'EXCEL.EXE':
                proc.terminate()
                self.speak("Đã đóng Microsoft Excel.")
                return
        self.speak("Không tìm thấy Microsoft Excel đang chạy.")
    def tell_me(self):
        global stop_reading
        stop_reading = False  # Reset biến dừng lại
        enter = threading.Thread(target=self.click_enter, args=())
        enter.start()
        try:
            self.speak("Bạn muốn nghe về gì ạ!")
            text = self.get_text()
            contents = wikipedia.summary(text).split('\n')
            content0_parts = contents[0].split('. ')
            for part in content0_parts:
                if stop_reading:
                    self.speak("Đã dừng lại theo yêu cầu của bạn.")
                    return
                self.speak(part)
            # time.sleep(20)
            for content in contents[1:]:
                print(stop_reading)
                if stop_reading:
                    self.speak("Đã dừng lại theo yêu cầu của bạn.")
                    break
                self.speak("Bạn muốn nghe tiếp hay không ?")
                ans = self.get_text()
                if "không" in ans:
                    break
                self.speak(content)
                # time.sleep(20)
                
            if not stop_reading:
                self.speak("Cảm ơn bạn đã lắng nghe!")
        except:
            self.speak("Sen không định nghĩa được ngôn ngữ của bạn!")
    
    def help(self):
        self.speak("""Tôi có thể làm những việc sau:
        1. Chào hỏi
        2. Hiển thị giờ
        3. Mở website, application
        4. Tìm kiếm trên Google
        5. Dự báo thời tiết
        6. Mở video nhạc
        7. Đọc báo hôm nay
        8. Tìm định nghĩa """)
        time.sleep(20)



    def show_robot_talking(self):
        # global frame_index
        frame = self.frames[self.frame_index]
        photo_talking = ImageTk.PhotoImage(frame)
        self.image_label.configure(image=photo_talking)
        self.image_label.image = photo_talking
        self.frame_index = (self.frame_index + 1) % len(self.frames)
        self.image_label.after(100, self.show_robot_talking)

    def show_robot_idle(self):
        global idle_frame_index
        idle_frame = self.idle_frames[idle_frame_index]
        photo_idle = ImageTk.PhotoImage(idle_frame)
        self.image_label.configure(image=photo_idle)
        self.image_label.image = photo_idle
        idle_frame_index = (idle_frame_index + 1) % len(self.idle_frames)
        self.image_label.after(100, self.show_robot_idle)
    def open_facebook(self):
        url = "https://www.facebook.com"
        webbrowser.open(url)
        self.speak("Facebook đã được mở")
    def call_sen(self):
        self.show_robot_talking()
        time.sleep(5)
        self.speak("Chào bạn, bạn vui lòng nhìn thẳng để tôi xác thực")
        # name = get_text()
        while True:
            if self.face_recognition_frame.verify_face() == 1:
                name = "Chí"
                self.speak("Xác thực thành công, Chào Admin")
                break
            else:
                self.speak("Xác thực không thành công!")
            time.sleep(1)  # Wait for 1 second before the next verification attempt
        
        if name:
            # speak("Chào bạn {}".format(name))
            # time.sleep(1)
            self.speak("admin cần gì?")
            
            while True:
                text = self.get_text()
                if not text:
                    break
                elif "trò chuyện" in text or "nói chuyện" in text:
                    self.talk(name)
                elif "dừng" in text or "thôi" in text:
                    self.stop()
                    break
                elif "mở" in text:
                    if "mở google và tìm kiếm" in text:
                        self.google_search(text)
                    elif "." in text:
                        self.open_website(text)
                    elif "word" in text or "excell" in text or "vscode" in text:
                        self.open_application(text)       
                elif "ngày" in text  or "giờ" in text:
                    self.get_time(text)
                elif "chơi nhạc" in text or "nghe nhạc" in text or "xem phim" in text:
                    self.play_youtube()
                elif "thời tiết" in text:
                    self.weather()
                elif "định nghĩa" in text:
                    self.tell_me()
                elif "có thể làm gì" in text:
                    self.help()
                elif "tìm kiếm" in text:
                    self.search_google()
                elif "không xem" in text or "đóng youtube" in text:
                    self.close_youtube()
                elif "close word" in text:
                    self.close_word()
                elif "close excel" in text:
                    self.close_excel()
                elif "facebook" in text or "Facebook" in text:
                    self.open_facebook()




if __name__ == "__main__":
    root = tk.Tk()
    client1 = Bot(root)
    root.mainloop()

           