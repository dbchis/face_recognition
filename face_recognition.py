from library import *
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
    def get_data_path(self):
        if getattr(sys, 'frozen', False):
            base_path = sys._MEIPASS  # Đường dẫn khi chạy từ .exe
        else:
            base_path = os.path.dirname(__file__)  # Đường dẫn khi chạy từ IDE
        return os.path.join(base_path, 'data', 'face_data.csv')

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
                    data_path = self.get_data_path()
                    df.to_csv(data_path, index=False)
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
                data_path = self.get_data_path()
                
                if os.path.exists(data_path):
                    saved_data = pd.read_csv(data_path).values
                    distance = np.linalg.norm(saved_data - img_embedding)
                    if distance < 0.8:  # Có thể điều chỉnh ngưỡng
                        # messagebox.showinfo("Info", "Chào chủ nhân!")
                        return 1
                    else:
                        # messagebox.showwarning("Warning", "Face not recognized!")
                        return 0
                else:
                    # messagebox.showwarning("Warning", "Face data file not found!")
                    return 0
            else:
                # messagebox.showwarning("Warning", "No face detected!")
                return 0
    
    def show(self):
        self.pack(fill=tk.BOTH, expand=True)
    
    def hide(self):
        self.pack_forget()
    
    def __del__(self):
        self.cap.release()
        cv2.destroyAllWindows()
# end xác thực