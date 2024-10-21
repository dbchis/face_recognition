import tkinter as tk
from tkinter import messagebox
import cv2
from PIL import Image, ImageTk
import pandas as pd
import numpy as np
from facenet_pytorch import MTCNN, InceptionResnetV1
import torch

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
        
        button_frame = tk.Frame(self)
        button_frame.pack(expand=True)

        self.save_button = tk.Button(button_frame, text="Save", command=self.save_face)
        self.save_button.pack(side=tk.LEFT, padx=10, pady=10)
        
        self.verify_button = tk.Button(button_frame, text="Verify", command=self.verify_face)
        self.verify_button.pack(side=tk.LEFT, padx=10, pady=10)
        
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
                    messagebox.showinfo("Verify success", "Welcome Admin!")
                else:
                    messagebox.showwarning("Warning", "Face not recognized!")
            else:
                messagebox.showwarning("Warning", "No face detected!")
    
    def show(self):
        self.pack(fill=tk.BOTH, expand=True)
    
    def hide(self):
        self.pack_forget()
    
    def __del__(self):
        self.cap.release()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    root = tk.Tk()
    root.title("Face Recognition")
    
    face_recognition_frame = FaceRecognitionFrame(root)
    face_recognition_frame.pack(fill=tk.BOTH, expand=True)
    
    root.mainloop()