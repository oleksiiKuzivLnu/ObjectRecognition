from mtcnn import MTCNN
import cv2

img = cv2.cvtColor(cv2.imread("D:/1.jpg"), cv2.COLOR_BGR2RGB)
detector = MTCNN()
res = detector.detect_faces(img)
print(res)


keypoints = res[0]['keypoints']

left_eye = keypoints['left_eye']
right_eye = keypoints['right_eye']
nose = keypoints['nose']
mouth_left = keypoints['mouth_left']
mouth_right = keypoints['mouth_right']

formatted_keypoints = [
    f"{left_eye[0]:.2f}\t{left_eye[1]:.2f}",
    f"{right_eye[0]:.2f}\t{right_eye[1]:.2f}",
    f"{nose[0]:.2f}\t{nose[1]:.2f}",
    f"{mouth_left[0]:.2f}\t{mouth_left[1]:.2f}",
    f"{mouth_right[0]:.2f}\t{mouth_right[1]:.2f}"
]

keypoints_array = []

for point in formatted_keypoints:
    keypoints_array.append(point)

print(keypoints_array)