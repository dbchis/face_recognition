from library import *
from face_recognition import FaceRecognitionFrame
language = 'vi'
path = ChromeDriverManager().install()
wikipedia.set_lang('vi')
stop_reading = False
opened_youtube_url = None



class Bot:
    def __init__(self, root):
        self.root = root
        self.root.title("Bot")
        self.root.configure(bg='#fcfefc')
         # Đặt kích thước cửa sổ
        width = 498
        height = 498
        self.root.geometry(f"{width}x{height}")

        # Tính toán vị trí để cửa sổ nằm chính giữa màn hình
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        x = (screen_width // 2) - (width // 2)
        y = (screen_height // 2) - (height // 2)
        self.root.geometry(f"{width}x{height}+{x}+{y}")
        self.root.resizable(False, False)
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        # Load frames for talking and idle animations
        self.frames = []
        self.idle_frames = []
        self.frame_index = 0
        self.idle_frame_index = 0
        self.running = False
        self.showing_gif = False
        self.verify = False
        self.commands = self.load_commands()
        # Determine base path for assets
        if getattr(sys, 'frozen', False):
            base_path = sys._MEIPASS  # Path when running from .exe
        else:
            base_path = os.path.dirname(__file__)  # Path when running from IDE

        # Load talking GIF
        gif_path = os.path.join(base_path, "img", "robot_talking.gif")
        gif = Image.open(gif_path)
        while True:
            try:
                self.frames.append(gif.copy())
                gif.seek(len(self.frames))
            except EOFError:
                break

        # Load idle GIF
        idle_gif = Image.open(gif_path)  # Use the same path
        while True:
            try:
                self.idle_frames.append(idle_gif.copy())
                idle_gif.seek(len(self.idle_frames))
            except EOFError:
                break
        
        # GUI setup
        self.image_label = tk.Label(root)
        self.image_label.place(relx=0.5, rely=0.5, anchor='center')
        self.face_recognition_frame = FaceRecognitionFrame(root)
        threading.Thread(target=self.call_sen, args=()).start()
       
    def load_commands(self):
        # Determine base path for assets
        if getattr(sys, 'frozen', False):
            base_path = sys._MEIPASS  # Path when running from .exe
        else:
            base_path = os.path.dirname(__file__)  # Path when running from IDE
        
        # Construct the full path to the commands.json file
        commands_path = os.path.join(base_path, 'commands.json')

        # Load the JSON file
        with open(commands_path, 'r', encoding='utf-8') as file:
            return json.load(file)
    def click_enter(self):
        global stop_reading
        keyboard.wait('enter')
        stop_reading = True
        print(stop_reading)
        print("bạn vừa nhấn enter")
    def speak(self,text):
        self.show_robot_talking()
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
        self.show_robot_idle()
        r = sr.Recognizer()
        with sr.Microphone() as source:
            print("Me: ", end = '')
            audio = r.listen(source, phrase_time_limit=5)
            try:
                text = r.recognize_google(audio, language="vi-VN")
                text=text.lower()
                print(text)
                return text
            except:
                print("...")
                return 0

    def stop(self):
        self.speak("Hẹn gặp lại bạn nhé!")
        self.root.quit()
        sys.exit()
    
        
        
    def get_text(self):
        
        for i in range(3):
            if(self.running==False):
                self.stop()
                return 0
            text = self.get_voice()
            if text:
                text = text.lower()
                return text
            elif i < 2:
                self.speak("Yorn không nghe rõ, bạn có thể nói lại không ?")
        time.sleep(10)
        self.stop()
        return 0

    def talk(self):
        day_time = int(strftime('%H'))
        if day_time < 12:
            self.speak("Chào buổi sáng {}. Chúc bạn ngày mới tốt lành!")
        elif day_time < 18:
            self.speak("Chào buổi chiều {}!")
        else:
            self.speak("Chào buổi tối {}!")
        time.sleep(5)
        self.speak("Bạn có khỏe không ?")
        time.sleep(3)
        ans = self.get_voice()
        if ans:
            if "có" in ans:
                self.speak("Thật là tốt!")
            else:
                self.speak("Vậy à, bạn nên nghỉ ngơi đi!")
        
    def get_time(self):
        now = datetime.datetime.now()
        self.speak("Bây giờ là %d giờ %d phút" % (now.hour, now.minute))
        self.speak("Ngày %d tháng %d năm %d " % (now.day, now.month, now.year))
    def weather(self):
        self.speak("Bạn muốn xem thời tiết ở đâu!")
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
    def tell_me(self):
        global stop_reading
        stop_reading = False  # Reset biến dừng lại
        enter = threading.Thread(target=self.click_enter, args=())
        enter.start()
        try:
            self.speak("Bạn muốn nghe về gì ạ!")
            text = self.get_text()
            contents = wikipedia.summary(text).split('\n')
            self.speak("Bạn hãy nhấn Enter nếu không muốn nghe nữa.")
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
            self.speak("Yorn không định nghĩa được ngôn ngữ của bạn!")   
    def search_google(self):
        self.speak("Bạn muốn tìm kiếm thông tin gì?")
        time.sleep(3)
        query = self.get_text()
        url = f'https://www.google.com/search?q={query}'
        webbrowser.open(url)
        self.speak("Thông tin bạn cần tìm kiếm đã được mở trên Google Chrome!")   
    def play_youtube(self):
        global opened_youtube_url
        self.speak("Bạn nghe nhạc hay xem phim gì")
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
                self.speak("Đã đóng YouTube.")
                return

        self.speak("Không tìm thấy YouTube đang mở bởi chương trình.")
    def open_chrome(self):
        url = "https://www.google.com"
        webbrowser.open(url)
    def open_facebook(self):
        url = "https://www.facebook.com"
        webbrowser.open(url)
        self.speak("Facebook đã được mở")
    def show_robot_talking(self):
        self.showing_gif = True
        self.frame_index = 0  
        self.update_talking_gif()
    def update_talking_gif(self):
        if self.showing_gif: 
            frame = self.frames[self.frame_index]
            photo_talking = ImageTk.PhotoImage(frame)
            self.image_label.configure(image=photo_talking)
            self.image_label.image = photo_talking
            self.frame_index = (self.frame_index + 1) % len(self.frames)
            self.image_label.after(100, self.update_talking_gif)  
    def show_robot_idle(self):
        self.showing_gif = False
        idle_frame = self.idle_frames[self.idle_frame_index]
        photo_idle = ImageTk.PhotoImage(idle_frame)
        self.image_label.configure(image=photo_idle)
        self.image_label.image = photo_idle
    def greet_admin(self):
        # Lấy thời gian hiện tại
        current_time = datetime.datetime.now()
        hour = current_time.hour

        # Xác định thời gian trong ngày
        if 1 <= hour < 11:
            self.speak("Chào buổi sáng, Admin")
        elif 11 <= hour < 13:
            self.speak("Chào buổi trưa, Admin")
        elif 13 <= hour < 18:
            self.speak("Chào buổi chiều, Admin")
        elif 18 <= hour < 22:
            self.speak("Chào buổi tối, Admin")
        else:
            self.speak("Chào buổi khuya, Admin")
    def help(self):
        self.speak("""Tôi có thể làm những việc sau:
        1. Chào hỏi, trò chuyện
        2. Thông tin ngày giờ
        3. Thông tin thời tiết
        4. Thông tin về 1 đối tượng
        5. Tìm kiếm thông tin
        6. Mở hoặc đóng nhạc + phim trên youtube
        7. Mở trình duyệt""")
        time.sleep(3)
    def call_sen(self):
        self.running = True
        ads = [
            "Yorn sẵn sàng lắng nghe lệnh từ Admin.",
            "Tôi đang ở đây để giúp đỡ, Admin.",
            "Có điều gì tôi có thể làm cho Admin không?",
            "Admin cần tôi làm gì?",
            "Tôi luôn sẵn sàng, Admin!"
        ]
        self.show_robot_idle()
        time.sleep(2)
        self.speak("Bạn vui lòng nhìn thẳng vào camera")
        # name = get_text()
        while True:
            if self.face_recognition_frame.verify_face() == 1:
                self.verify = True
                self.greet_admin()
                break
            else:
                self.speak("Bạn không phải là Admin")
            time.sleep(1)
        
        if self.verify:
            while self.running:
                self.speak(random.choice(ads))
                text = self.get_text()
                if not text:
                    break
                action_found = False
                for key, action in self.commands.items():
                    if key in text:
                        getattr(self, action)()  # Gọi hàm tương ứng
                        action_found = True
                        break
                if not action_found:
                    self.speak("Tôi không hiểu yêu cầu của bạn.")

    def on_closing(self):
        self.running = False

if __name__ == "__main__":
    root = tk.Tk()
    bot = Bot(root)
    root.mainloop()
   
   
    

           