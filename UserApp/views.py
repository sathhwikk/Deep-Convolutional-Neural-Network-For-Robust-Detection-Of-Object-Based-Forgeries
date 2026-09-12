from django.shortcuts import render
import pymysql
import cv2
import os
from sklearn.model_selection import train_test_split
import numpy as np
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Conv2D, MaxPooling2D, Flatten, Dense, Dropout
from django.conf import settings

# Create your views here.
def index(request):
    return render(request,'index.html')
def Admin(request):
    return render(request,'User.html')


def Register(request):
    return render(request,'Register.html')
def RegAction(request):
      name=request.POST['name']
      email=request.POST['email']
      mobile=request.POST['mobile']
      address=request.POST['address']
      password=request.POST['password']

      con=pymysql.connect(host="localhost",user="root",password="",database="forgery",charset='utf8')
      cur=con.cursor()
      cur.execute("select * from user where email='"+email+"'")
      data=cur.fetchall()
      if data is not None:
          i=cur.execute("insert into user values(null,'"+name+"','"+email+"','"+mobile+"','"+address+"','"+password+"')")
          con.commit()
          if i>0:
            context={'data':'Registration Successful...!!'}
            return render(request,'Register.html',context)
          else:
            context={'data','Registration Failed...!!'}
            return render(request,'Register.html',context)
      else:
        context={'data','Email Id Already Exist...!!'}
        return render(request,'Register.html',context)

def LogAction(request):
  username=request.POST['email']
  password=request.POST['password']
  con=pymysql.connect(host="localhost",user="root",password="",database="forgery",charset='utf8')
  cur=con.cursor()
  cur.execute("select *  from user where email='"+username+"'and password='"+password+"'")
  data=cur.fetchone()
  if data is not None:
    request.session['user']=username
    request.session['userid']=data[0]
    return render(request,'UserHome.html')
  else:
    context={'data':'Login Failed ....!!'}
    return render(request,'User.html',context)

def Home(request):
    return render(request,'UserHome.html')

# Function to extract frames from video
def extract_frames(video_path, label, frame_size=(128, 128)):
    frames = []
    cap = cv2.VideoCapture(video_path)
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
        frame = cv2.resize(frame, frame_size)  # Resize frames
        frames.append((frame, label))  # Add label (real or fake)
    cap.release()
    return frames


global real_video_path,fake_video_path
def LoadDataset(request):
    global real_video_path,fake_video_path

    # Path to your video dataset
    dataset_path="Dataset/Clone"
    real_video_path = os.path.join(dataset_path, 'real')
    fake_video_path = os.path.join(dataset_path, 'fake')    

    context={'data':'Dataset loaded Successfully..!!!'}
    return render(request,'UploadDataset.html',context)
# CNN Model Architecture
def build_model(input_shape=(128, 128, 3)):
    model = Sequential()
    model.add(Conv2D(32, (3, 3), activation='relu', input_shape=input_shape))
    model.add(MaxPooling2D((2, 2)))

    model.add(Conv2D(64, (3, 3), activation='relu'))
    model.add(MaxPooling2D((2, 2)))

    model.add(Conv2D(128, (3, 3), activation='relu'))
    model.add(MaxPooling2D((2, 2)))

    model.add(Flatten())
    model.add(Dense(128, activation='relu'))
    model.add(Dropout(0.5))  # Dropout to prevent overfitting
    model.add(Dense(1, activation='sigmoid'))  # Binary classification (real/fake)

    model.compile(optimizer='adam', loss='binary_crossentropy', metrics=['accuracy'])

    return model

global X_train, X_val, y_train, y_val
def ProcessImage(request):
    global X_train, X_val, y_train, y_val

    # Extract frames for both real and fake videos
    real_frames = []
    fake_frames = []

    # Loop through real and fake video files to extract frames
    for video_file in os.listdir(real_video_path):
        video_path = os.path.join(real_video_path, video_file)
        real_frames.extend(extract_frames(video_path, label=0))  # 0 for real

    for video_file in os.listdir(fake_video_path):
        video_path = os.path.join(fake_video_path, video_file)
        fake_frames.extend(extract_frames(video_path, label=1))  # 1 for fake

    # Combine real and fake frames
    frames = real_frames + fake_frames

    # Prepare the data
    X = []
    y = []

    # Convert frames to numpy arrays
    for frame, label in frames:
        X.append(frame)
        y.append(label)

    # Convert lists to numpy arrays
    X = np.array(X)
    y = np.array(y)

    # Normalize the pixel values to range [0, 1]
    X = X / 255.0

    # Split the dataset into training and validation sets
    X_train, X_val, y_train, y_val = train_test_split(X, y, test_size=0.2, random_state=42)

    context={'noof':len(X),'train':len(X_train),'test':len(y_val)}
    return render(request,'PreprocessImage.html',context)

global model
def GenerateModel(request):
    global model
    model = build_model()
    output=""
    # Train the model
    if os.path.exists("Model\\forgeryDetect_model.h5"):
        model.load_weights('Model/forgeryDetect_model.h5')
        output="CNN Model Successfully Loaded..!!"
    else:
        model.fit(X_train, y_train, validation_data=(X_val, y_val), epochs=50 , batch_size=16)
        model.save_weights('Model/forgeryDetect_model.h5')
        output="CNN Model Successfully Generated..!!"

    context={'data':output}
    return render(request,'GenerateModel.html',context)


def Detect(request):
    return render(request,'Detect.html')

def predict_frame(frame, model):
    frame = cv2.resize(frame, (128, 128))  # Resize to the model input size
    frame = np.expand_dims(frame, axis=0)  # Add batch dimension
    frame = frame / 255.0  # Normalize
    prediction = model.predict(frame)
    return 'Fake' if prediction[0] > 0.5 else 'Real'


def DetectFAction(request):
    output=''
    if request.method == 'POST' and request.FILES.get('input_video'):
        video_file = request.FILES['input_video'].name

        # video_path = os.path.join(settings.MEDIA_ROOT, 'uploaded_videos', video_file.name)
        # video_filename=video_file.name
        video_path="inputvideos/"+video_file
        
        cap = cv2.VideoCapture(video_path)

    while cap.isOpened():
        ret, frame = cap.read()
        print(frame)
        if not ret:
            break
        model.load_weights('Model/forgeryDetect_model.h5')
        label = predict_frame(frame, model)
        print(f'Frame label: {label}')
        output=label

        # Optionally, display the frame with prediction
        cv2.putText(frame, label, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2, cv2.LINE_AA)
        cv2.imshow('Frame', frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

    context={'data':output}
    return render(request,'DetectStatus.html',context)



